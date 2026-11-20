from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_open_print_label_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Print Label",
            "res_model": "cdp.print.product.label.stock",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_cdp_move_id": self.id,
                # "default_cdp_print_label_qty": self.quantity,
            },
        }
