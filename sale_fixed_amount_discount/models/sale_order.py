# Copyright 2017-20 kbizsoft
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from decimal import Decimal, ROUND_HALF_UP


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Disc Amt",
        digits="Product Price",
        help="Fixed amount discount.",
    )
    is_fixed_discount = fields.Boolean(string='Is Fixed', default=False)

    @api.onchange('fixed_discount')
    def _onchange_fixed_discount(self):
        for line in self:
            if line.fixed_discount:
                line.is_fixed_discount = True
            else:
                line.is_fixed_discount = False

    @api.depends('product_uom_qty', 'discount','discount_fixed', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            # Compute the subtotal with the existing logic
            super(SaleOrderLine, line)._compute_amount()

            # Update the subtotal with the discounted amount
            if line.discount_fixed:


                # Calculate the discounted total
                total_before_discount = line.price_unit * line.product_uom_qty
                total_after_discount = total_before_discount - line.discount_fixed

                # Ensure total_after_discount is not negative
                if total_after_discount >= 0:
                    line.update({
                        'price_subtotal': total_after_discount,
                    })



  #todo 


    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({
            "discount_fixed": self.discount_fixed,
        })
        return res

    def _prepare_invoice_line(self, **optional_values):
        # Remove the unexpected keyword argument 'sequence' from the method call
        optional_values.pop('sequence', None)
        res = super()._prepare_invoice_line(**optional_values)

        res.update({
            "discount_fixed": self.discount_fixed,
        })
        return res

