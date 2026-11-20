from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    has_smaller_chatter = fields.Boolean(string="move chatter to bottom", default=False)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["has_smaller_chatter"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["has_smaller_chatter"]
