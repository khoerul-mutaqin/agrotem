# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    print_format = fields.Selection(
        selection_add=[
            ("10x8cm", "10 x 8 cm"),
        ],
        ondelete={"10x8cm": "set default"},
    )
    cdp_qty = fields.Float(
        string="Q'ty",
        digits=(16, 2),
        required=True,
        default=1,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_model = self.env.context.get("active_model")

        if active_model == "stock.picking":
            res["print_format"] = "10x8cm"
        else:
            res.setdefault("print_format", "dymo")

        res["move_quantity"] = "custom"

        if active_model in ["product.template", "product.product"]:
            res["custom_quantity"] = 1
        else:
            res.setdefault("custom_quantity", 1)

        return res

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if self.print_format != "10x8cm":
            return xml_id, data

        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])

        if active_model == "stock.picking":
            xml_id = "agrotem_product_print_label.report_stock_picking_label_10x8cm"
        elif active_model in ["product.template", "product.product"]:
            xml_id = "agrotem_product_print_label.report_product_template_label_10x8cm"
        else:
            return xml_id, data

        is_product_page = active_model in ["product.template", "product.product"]
        picking_vals = {}

        if active_model == "stock.picking" and active_ids:
            picking = self.env["stock.picking"].browse(active_ids[0])
            if picking.exists():
                picking_vals = {
                    "id": picking.id,
                    "date_done": picking.date_done,
                    "origin": picking.origin,
                    "name": picking.name,
                }

        if self.product_ids:
            products = self.product_ids
        elif self.product_tmpl_ids:
            products = self.product_tmpl_ids.product_variant_ids
        else:
            raise UserError(_("No product selected."))

        quantity = {}

        for product in products:
            barcode = product.barcode or product.default_code
            if not barcode:
                continue

            qty = 0

            if self.move_quantity == "move" and not is_product_page:
                if not active_ids:
                    continue

                picking = self.env["stock.picking"].browse(active_ids[0])
                if not picking.exists():
                    continue

                moves = picking.move_ids_without_package.filtered(
                    lambda m: m.product_id == product
                )
                qty = sum(
                    m.quantity if m.quantity else m.product_uom_qty for m in moves
                )
                qty = int(qty)

            else:
                qty = int(self.custom_quantity or (0 if is_product_page else 1))

            if qty <= 0 and not is_product_page:
                continue

            quantity[str(product.id)] = {
                "barcode": barcode,
                "qty": qty,
                "move_qty": qty,
                "cdp_qty": self.cdp_qty,
            }

        if not quantity:
            raise UserError(_("No valid product quantity to print label."))

        data.clear()
        data.update(
            {
                "docids": active_ids,
                "quantity": quantity,
                "picking": picking_vals,
                "is_product_page": is_product_page,
                "print_date": fields.Date.today().strftime("%Y-%m-%d"),
            }
        )

        return xml_id, data
