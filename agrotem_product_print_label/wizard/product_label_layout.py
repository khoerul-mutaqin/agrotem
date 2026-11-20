# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError


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
        move_ids = self.env.context.get("default_move_ids") or []

        # Transfer / MO (also reached through the Lot/SN "picking.label.type" step)
        if move_ids or active_model in ("stock.picking", "mrp.production"):
            res["print_format"] = "10x8cm"
            moves = self.env["stock.move"].browse(move_ids).exists()
            if len(moves.product_id) == 1:
                res["cdp_qty"] = self._cdp_get_move_qty(moves)
        else:
            res.setdefault("print_format", "dymo")

        res["move_quantity"] = "custom"
        res["custom_quantity"] = 1
        return res

    @api.model
    def _cdp_get_move_qty(self, moves):
        return sum(m.quantity or m.product_uom_qty for m in moves)

    def _cdp_get_source_vals(self):
        """Header info (date / origin / name) of the transfer or MO behind the moves."""
        moves = self.move_ids
        picking = moves.picking_id[:1]
        if picking:
            return {
                "date": picking.date_done and picking.date_done.strftime("%Y-%m-%d") or "",
                "origin": picking.origin or "",
                "name": picking.name or "",
            }
        production = (
            moves.production_id[:1] if "production_id" in moves._fields else False
        )
        if production:
            date = production.date_finished or production.date_start
            return {
                "date": date and date.strftime("%Y-%m-%d") or "",
                "origin": production.origin or "",
                "name": production.name or "",
            }
        return {}

    def _prepare_report_data(self):
        if self.print_format != "10x8cm":
            return super()._prepare_report_data()

        is_product_page = not self.move_ids
        use_move_qty = self.move_quantity == "move" and not is_product_page

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

            if use_move_qty:
                moves = self.move_ids.filtered(lambda m: m.product_id == product)
                label_qty = self._cdp_get_move_qty(moves)
                # one label per unit, at least one label
                print_count = max(int(label_qty), 1) if label_qty else 0
            else:
                label_qty = self.cdp_qty
                print_count = self.custom_quantity

            if print_count <= 0:
                continue

            quantity[str(product.id)] = {
                "barcode": barcode,
                "qty": print_count,
                "label_qty": label_qty,
            }

        if not quantity:
            raise UserError(_("No valid product quantity to print label."))

        data = {
            "quantity": quantity,
            "source": {} if is_product_page else self._cdp_get_source_vals(),
            "is_product_page": is_product_page,
            "print_date": fields.Date.context_today(self).strftime("%Y-%m-%d"),
        }
        if self.move_ids.picking_id:
            # stock.picking report -> PDF named after the transfer
            xml_id = "agrotem_product_print_label.report_stock_picking_label_10x8cm"
        else:
            xml_id = "agrotem_product_print_label.report_product_template_label_10x8cm"
        return xml_id, data
