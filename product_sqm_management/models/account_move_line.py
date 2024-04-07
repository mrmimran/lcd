from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_fixed = fields.Float(string='Disc Amt')

    product_sqm = fields.Float(string='Product SQM', readonly=True, store=True)
    product_qty_available = fields.Float(string='QoH', related='product_id.qty_available',readonly=True)
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('vat', 'Taxable'),
        ('sample', 'Sample')
    ], string='Tr. Type',  default='cash')

    is_tax_readonly = fields.Boolean(string='Tax Readonly', default=False)

    @api.onchange('payment_type', 'tax_id')
    def _onchange_payment_type(self):
        for line in self:
            if line.payment_type == 'cash':
                # line.tax_id = False  # Clear tax_id if payment_type is cash
                # line.is_tax_readonly = True  # Make tax_id field readonly
                if line.tax_ids:
                    # raise ValidationError(_("You cannot select tax for cash payment type."))
                    line.tax_ids = False
            else:
                line.is_tax_readonly = False  # Make tax_id field editable
                if not line.tax_ids and line.product_id:
                    # If tax is not manually selected and product is set, apply automatic tax
                    taxes = line.product_id.taxes_id.filtered(lambda r: r.company_id == self.env.company)
                    if taxes:
                        line.tax_ids = taxes
                    else:
                        # If no taxes are found for the product, reset tax_id to prompt user selection
                        line.tax_ids = False

    @api.onchange('discount_fixed', 'discount')
    def _onchange_discount_line(self):
        # Update SQM field in sale order line based on selected product's SQM
        for line in self:
            if line.discount_fixed and line.discount:
                raise ValidationError(_("You can only select one discount for each line."))

    @api.onchange('quantity', 'product_id')
    def _onchange_product_uom_qty(self):
        # Update SQM field in sale order line based on selected product's SQM
        for line in self:
            if line.product_id:
                line.product_sqm = line.product_id.sqm * line.quantity
            else:
                line.product_sqm = 0.0
