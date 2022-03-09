from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_remitentes = fields.Char("Email Remitentes", )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            email_remitentes=self.env["ir.config_parameter"].sudo().get_param("email_remitentes"),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param("email_remitentes", record.email_remitentes)
