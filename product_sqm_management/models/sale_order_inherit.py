from odoo import models, fields, api
from odoo import api, fields, models, _, Command
from odoo.osv import expression
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import frozendict

from collections import defaultdict
import math
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    qty_price = fields.Float(string='Quantity * Price')
    gross_amount = fields.Float(string='Gross Amount', compute='_compute_gross_amount', store=True)
    amount_tax = fields.Monetary(string='VAT/Tax', currency_field='currency_id', compute='_compute_amount_tax', store=True)

    # vat_tax = fields.Float(string='VAT/Tax')
    after_tax_amount = fields.Float(string='After Tax Amount', compute='_compute_after_tax_amount', store=True)
    delivery_charges = fields.Float(string='Delivery Charges')
    other_charges = fields.Float(string='Other Charges')
    net_amount = fields.Float(string='Net Amount', compute='_compute_net_amount', store=True)
    total_discount = fields.Monetary(string='Discount', compute='_compute_total_discount')
    state = fields.Selection(
        selection=[
            ('draft', "Sale Order"),
            ('sent', "Sale Order Sent"),
            ('sale', "Sales Order"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Fully Paid')
    ], string='Payment Status', compute='_compute_payment_status', store=True)

    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_payment_status(self):
        for order in self:
            paid_invoices = order.invoice_ids.filtered(lambda i: i.state == 'paid')
            if not paid_invoices:
                order.payment_status = 'unpaid'
            elif all(invoice.amount_total == invoice.amount_residual for invoice in paid_invoices):
                order.payment_status = 'paid'
            else:
                order.payment_status = 'partially_paid'

    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        self._compute_payment_status()


    @api.depends('order_line.tax_id', 'gross_amount')
    def _compute_amount_tax(self):
        for order in self:
            # total_amount = sum(line.price_subtotal for line in order.order_line)
            total_tax = 0.0
            for line in order.order_line:
                total_tax += (order.gross_amount * line.tax_id.amount) / 100
            order.amount_tax = total_tax
    @api.depends('order_line.product_uom_qty', 'order_line.price_unit', 'order_line.discount')
    def _compute_total_amount(self):
        for order in self:
            total_amount = sum(line.product_uom_qty * line.price_unit for line in order.order_line )
            order.total_amount = total_amount

    # @api.depends('total_amount', 'vat_tax')
    @api.depends('total_amount')
    def _compute_gross_amount(self):
        for order in self:
            order.gross_amount = order.total_amount - order.total_discount

    @api.depends('gross_amount', 'amount_tax')
    def _compute_after_tax_amount(self):
        for order in self:
            after_tax_amount = order.gross_amount + order.amount_tax
            order.after_tax_amount = after_tax_amount
            # order.after_tax_amount = order.gross_amount + order.vat_tax

    @api.depends('after_tax_amount', 'delivery_charges', 'other_charges')
    def _compute_net_amount(self):
        for order in self:
            net_amount = order.after_tax_amount + order.delivery_charges + order.other_charges
            order.amount_total = net_amount
            order.net_amount = net_amount
            # order.tax_totals['amount_untaxed']=order.tax_totals['amount_untaxed']+self.delivery_charges+self.other_charges
            # order.tax_totals['amount_total']=order.tax_totals['amount_total']+self.delivery_charges+self.other_charges

            # order.tax_totals=net_amount



    @api.depends('order_line.discount', 'order_line.price_unit', 'order_line.product_uom_qty',
                 'order_line.discount_fixed')
    def _compute_total_discount(self):
        for order in self:
            total_discount = 0.0
            for line in order.order_line:
                line_discount = (line.price_unit * line.product_uom_qty * line.discount / 100)
                total_discount += line_discount + line.discount_fixed  # Add discount_fixed value
            order.total_discount = total_discount


    @api.onchange('order_line.product_id')
    def _onchange_product_id(self):
        # Update SQM field in sale order line based on selected product's SQM
        for line in self.order_line:
            if line.product_id:
                line.product_sqm = line.product_id.sqm * line.product_uom_qty
            else:
                line.product_sqm = 0.0

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'delivery_charges', 'other_charges')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            res = super(SaleOrder, order)._compute_amounts()  # Call the parent method
            # Add delivery charges and other charges to the subtotal
            subtotal = order.amount_untaxed + order.amount_tax + order.delivery_charges + order.other_charges
            order.amount_total = subtotal
            return res

    def write(self, vals):
        if 'delivery_charges' in vals or 'other_charges' in vals:
            for order in self:
                for invoice in order.invoice_ids:
                    invoice_vals = {}
                    if 'delivery_charges' in vals:
                        invoice_vals['delivery_charges'] = vals['delivery_charges']
                    if 'other_charges' in vals:
                        invoice_vals['other_charges'] = vals['other_charges']
                    if 'total_discount' in vals:
                        invoice_vals['total_discount'] = vals['total_discount']

                    invoice.write(invoice_vals)


        return super(SaleOrder, self).write(vals)

    @api.depends('order_line.price_total','net_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        res = super(SaleOrder, self)._amount_all()  # Call parent method
        for order in self:
            order.update({
                'amount_total': 222,
            })

        return res

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'net_amount')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        res = super(SaleOrder, self)._compute_amounts()
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            order.amount_untaxed = sum(order_lines.mapped('price_subtotal'))
            order.amount_untaxed=order.amount_untaxed+self.delivery_charges+self.other_charges
            order.amount_tax = sum(order_lines.mapped('price_tax'))
            # order.amount_total = 444

        return res

    @api.depends('order_line.price_total','order_line.product_uom_qty')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        for rec in self:
            if rec.amount_total:
                rec.amount_total = rec.amount_total + rec.delivery_charges
        return res

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     for order in self:
    #         amount_untaxed = amount_tax = amount_discount = 0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #             amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
    #         order.update({
    #             'amount_untaxed': amount_untaxed,
    #             'amount_tax': amount_tax,
    #             'amount_discount': amount_discount,
    #             'amount_total': amount_untaxed + amount_tax,
    #         })

class InhertTax(models.Model):
    _inherit = 'account.tax'
    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        """ Compute the tax totals details for the business documents.
        :param base_lines:  A list of python dictionaries created using the '_convert_to_tax_base_line_dict' method.
        :param currency:    The currency set on the business document.
        :param tax_lines:   Optional list of python dictionaries created using the '_convert_to_tax_line_dict' method.
                            If specified, the taxes will be recomputed using them instead of recomputing the taxes on
                            the provided base lines.
        :return: A dictionary in the following form:
            {
                'amount_total':                 The total amount to be displayed on the document, including every total
                                                types.
                'amount_untaxed':               The untaxed amount to be displayed on the document.
                'formatted_amount_total':       Same as amount_total, but as a string formatted accordingly with
                                                partner's locale.
                'formatted_amount_untaxed':     Same as amount_untaxed, but as a string formatted accordingly with
                                                partner's locale.
                'groups_by_subtotals':          A dictionary formed liked {'subtotal': groups_data}
                                                Where total_type is a subtotal name defined on a tax group, or the
                                                default one: 'Untaxed Amount'.
                                                And groups_data is a list of dict in the following form:
                    {
                        'tax_group_name':                   The name of the tax groups this total is made for.
                        'tax_group_amount':                 The total tax amount in this tax group.
                        'tax_group_base_amount':            The base amount for this tax group.
                        'formatted_tax_group_amount':       Same as tax_group_amount, but as a string formatted accordingly
                                                            with partner's locale.
                        'formatted_tax_group_base_amount':  Same as tax_group_base_amount, but as a string formatted
                                                            accordingly with partner's locale.
                        'tax_group_id':                     The id of the tax group corresponding to this dict.
                    }
                'subtotals':                    A list of dictionaries in the following form, one for each subtotal in
                                                'groups_by_subtotals' keys.
                    {
                        'name':                             The name of the subtotal
                        'amount':                           The total amount for this subtotal, summing all the tax groups
                                                            belonging to preceding subtotals and the base amount
                        'formatted_amount':                 Same as amount, but as a string formatted accordingly with
                                                            partner's locale.
                    }
                'subtotals_order':              A list of keys of `groups_by_subtotals` defining the order in which it needs
                                                to be displayed
            }
        """

        # ==== Compute the taxes ====

        to_process = []
        for base_line in base_lines:
            to_update_vals, tax_values_list = self._compute_taxes_for_single_line(base_line)
            to_process.append((base_line, to_update_vals, tax_values_list))

        def grouping_key_generator(base_line, tax_values):
            source_tax = tax_values['tax_repartition_line'].tax_id
            return {'tax_group': source_tax.tax_group_id}

        global_tax_details = self._aggregate_taxes(to_process, grouping_key_generator=grouping_key_generator)

        tax_group_vals_list = []
        for tax_detail in global_tax_details['tax_details'].values():
            tax_group_vals = {
                'tax_group': tax_detail['tax_group'],
                'base_amount': tax_detail['base_amount_currency'],
                'tax_amount': tax_detail['tax_amount_currency'],
            }

            # Handle a manual edition of tax lines.
            if tax_lines is not None:
                matched_tax_lines = [
                    x
                    for x in tax_lines
                    if x['tax_repartition_line'].tax_id.tax_group_id == tax_detail['tax_group']
                ]
                if matched_tax_lines:
                    tax_group_vals['tax_amount'] = sum(x['tax_amount'] for x in matched_tax_lines)

            tax_group_vals_list.append(tax_group_vals)

        tax_group_vals_list = sorted(tax_group_vals_list, key=lambda x: (x['tax_group'].sequence, x['tax_group'].id))

        # ==== Partition the tax group values by subtotals ====

        amount_untaxed = global_tax_details['base_amount_currency']
        amount_tax = 0.0

        subtotal_order = {}
        groups_by_subtotal = defaultdict(list)
        for tax_group_vals in tax_group_vals_list:
            tax_group = tax_group_vals['tax_group']

            subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
            sequence = tax_group.sequence

            subtotal_order[subtotal_title] = min(subtotal_order.get(subtotal_title, float('inf')), sequence)
            groups_by_subtotal[subtotal_title].append({
                'group_key': tax_group.id,
                'tax_group_id': tax_group.id,
                'tax_group_name': tax_group.name,
                'tax_group_amount': tax_group_vals['tax_amount'],
                'tax_group_base_amount': tax_group_vals['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, tax_group_vals['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, tax_group_vals['base_amount'], currency_obj=currency),
            })



        # ==== Build the final result ====
        other_charges=0
        if 'params' in self.env.context:
            sale_order = self.env['sale.order'].browse(self.env.context.get('params', {}).get('id'))
            other_charges += sale_order.delivery_charges + sale_order.other_charges
            #
            # sale_order=self.env['sale.order'].search([('id','=',self.env.context['params']['id'])])
            # other_charges=other_charges+sale_order.delivery_charges+sale_order.other_charges
            amount_untaxed=amount_untaxed+sale_order.delivery_charges+sale_order.other_charges
        subtotals = []
        for subtotal_title in sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]):
            amount_total = amount_untaxed + amount_tax
            subtotals.append({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': formatLang(self.env, amount_total, currency_obj=currency),
            })
            amount_tax += sum(x['tax_group_amount'] for x in groups_by_subtotal[subtotal_title])

        amount_total = amount_untaxed + amount_tax+other_charges

        display_tax_base = (len(global_tax_details['tax_details']) == 1 and currency.compare_amounts(tax_group_vals_list[0]['base_amount'], amount_untaxed) != 0)\
                           or len(global_tax_details['tax_details']) > 1

        return {
            'amount_untaxed': currency.round(amount_untaxed) if currency else amount_untaxed,
            'amount_total': currency.round(amount_total) if currency else amount_total,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals,
            'subtotals_order': sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]),
            'display_tax_base': display_tax_base
        }




