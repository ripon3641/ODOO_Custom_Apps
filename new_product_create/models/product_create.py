from odoo import api, fields, models
from odoo.tools.translate import _

class ProductCreate(models.Model):
    _name = "product.create"
    _description = "Product Create"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "reference_no"

    reference_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    product_category = fields.Many2one('product.category', string="Product Category", tracking=True)
    product_name = fields.Char(string="Product Name", tracking=True)
    uom_ids = fields.Many2one('uom.uom', string='Unit of Measure', tracking=True)
    product_attribute = fields.Many2one('product.attribute', string='Attribute', tracking=True)
    attribute_value = fields.Char(string='Attribute Value', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'),
        ('validate', 'Created'),
        ('cancel', 'Cancel')], string='Status', default='draft', invisible='1', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'product.create') or _('New')
        res = super(ProductCreate, self).create(vals)
        return res

    def button_confirm(self):
        self.write({
            'state': 'confirm'
        })

    def button_approved(self):
        self.write({
            'state': 'approved'
        })

    def button_validate(self):
        self.ensure_one()
        product_obj = self.env['product.product']
        vals = {
            'name': self.product_name,
            'uom_id': self.uom_ids.id,
            'uom_po_id': self.uom_ids.id,
            'categ_id': self.product_category.id,
        }
        product = product_obj.create(vals)
        self.write({'state': 'validate'})

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

    def button_reset_to_draft(self):
        self.write({
            'state': "draft"
        })


