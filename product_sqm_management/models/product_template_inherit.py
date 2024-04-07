from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sqm = fields.Float(string='SQM')
    landing_cost = fields.Char(string='Lading Cost')
    discount = fields.Char(string='Discount %')
    thickness = fields.Char(string='Thickness')
    origin_origin = fields.Many2one('origin.origin', string='Origin')
    color_color = fields.Many2one('color.color', string='Color')
    size_size = fields.Many2one('size.size', string='Size')
    group_group = fields.Many2one('group.group', string='Group')
    thickness_thickness = fields.Many2one('thickness.thickness', string='Thickness')
    mfg_code = fields.Char(string='Mfg Code')