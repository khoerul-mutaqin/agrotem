from odoo import fields, models, api


class PrintProductLabelStock(models.TransientModel):
    _name = "cdp.print.product.label.stock"
    _description = "Print Product Label Stock"

    cdp_product_id = fields.Many2one(
        "product.product",
        string="Product",
        readonly=True,
    )
    cdp_qty = fields.Float(
        string="Q'ty",
        digits=(16, 2),
        required=True,
        default=1.0,
    )
    cdp_print_label_qty = fields.Integer(
        string="Print Label Quantity",
        required=True,
        default=1,
    )
    cdp_move_id = fields.Many2one("stock.move")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        move_id = self.env.context.get("default_cdp_move_id")

        if move_id:
            move = self.env["stock.move"].browse(move_id)
            res.update(
                {
                    "cdp_product_id": move.product_id.id,
                    "cdp_move_id": move.id,
                }
            )

        return res

    def action_print_label(self):
        self.ensure_one()

        return self.env.ref(
            "agrotem_product_print_label.action_report_label_10x8cm"
        ).report_action(self)
