from odoo import api, fields, models, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    @api.onchange('product_template_id')
    def _product_change(self):
        self.name = self.product_template_id.name
        # self.category_id = self.product_template_id.categ_id.id
        self.partner_ref = self.product_template_id.default_code
        # self.serial_no = self.product_template_id.default_code


    product_template_id = fields.Many2one('product.template', string='Producto', required=True)
    creado = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        vals_list[0]['creado'] = True
        products = super(MaintenanceEquipment, self).create(vals_list)
        return products



