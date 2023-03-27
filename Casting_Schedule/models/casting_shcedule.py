from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime


class CastingSchedule(models.Model):
    _name = 'casting.schedule'
    _description = 'Casting Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference_no'

    reference_no = fields.Char(string='Serial No', required=True,
                               readonly=True, default=lambda self: _('New'))
    partner = fields.Many2one('res.partner', string='Party Name', required=True)
    sale_order = fields.Many2one('sale.order', string='Sales Order', domain="[('partner_id', '=', partner)]")
    delivery_address = fields.Text(string='Delivery Address')
    warehouse_location = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    total_qty = fields.Float(compute='_compute_total_qty', string='Total Quantity', store=True)
    delivered_qty = fields.Float(compute='_compute_delivered_qty', string='Delivered Quantity', store=True)
    product_id = fields.Many2one('product.product', string='Product', compute='_compute_product_', store=True)
    cs_qty = fields.Float(compute='_compute_cs_qty', string='Quantity (CM)', readonly=False)
    delivery_date = fields.Date(string='Delivery Date', default=datetime.today())
    delivery_mode = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night'),
    ], default='day', string="Delivery Mode", required=True)
    # pumping_status = fields.One2many(compute='_compute_pumping_status', string='Pumping Status', store=True, readonly=False)
    pumping_status = fields.Selection([
        ('withpump', 'With Pump'),
        ('nonpump', 'Non Pump'),
        ], string='Pumping Status', required=True)

    state = fields.Selection([
        ('new', 'New'),
        ('plantapprove', 'Plant Approve'),
        ('approve', 'Approved'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled'),
    ], default='new', string="Status", invisible='1', required=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'casting.schedule') or _('New')
        res = super(CastingSchedule, self).create(vals)
        return res

    @api.depends('sale_order.order_line.product_uom_qty')
    def _compute_total_qty(self):
        for schedule in self:
            schedule.total_qty = sum(schedule.sale_order.mapped('order_line.product_uom_qty'))

    @api.depends('sale_order.order_line.product_uom_qty')
    def _compute_delivered_qty(self):
        for schedule in self:
            schedule.delivered_qty = sum(schedule.sale_order.mapped('order_line.qty_delivered'))

    @api.depends('sale_order.order_line.product_id')
    def _compute_product_(self):
        for schedule in self:
            schedule.product_id = schedule.sale_order.mapped('order_line.product_id')

    @api.depends('total_qty', 'delivered_qty')
    def _compute_cs_qty(self):
        for record in self:
            record.cs_qty = record.total_qty - record.delivered_qty

    # def _compute_pumping_status(self):
    #     for record in self:
    #         record.pumping_status = record.sale_order.pumping_status

    def button_plantapprove(self):
        self.write({
            'state': "plantapprove"
        })

    def button_approve(self):
        self.write({
            'state': "approve"
        })

    def button_reset_to_draft(self):
        self.write({
            'state': "new"
        })

    def button_cancel(self):
        self.write({
            'state': "cancel"
        })

