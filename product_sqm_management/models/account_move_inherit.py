from odoo import models, fields, api, _
class AccountMove(models.Model):
    _inherit = 'account.move'

    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', compute='_compute_total_amount', store=True)
    total_discount = fields.Monetary(string='Total Discount', currency_field='currency_id')
    # total_discount = fields.Monetary(string='Total Discount', currency_field='currency_id', compute='_compute_total_discount')
    gross_amount = fields.Monetary(string='Gross Amount', currency_field='currency_id', compute='_compute_gross_amount', store=True)
    amount_tax = fields.Monetary(string='VAT/Tax', currency_field='currency_id', compute='_compute_amount_tax', store=True)
    # amount_tax = fields.Monetary(string='VAT/Tax', currency_field='currency_id', store=True)
    vat_tax = fields.Monetary(string='VAT Tax', currency_field='currency_id', invisible=True)
    after_tax_amount = fields.Monetary(string='After Tax Amount', currency_field='currency_id', compute='_compute_after_tax_amount', store=True)
    # delivery_charges = fields.Monetary(string='Delivery Charges', currency_field='currency_id', compute='_compute_delivery_charges')
    delivery_charges = fields.Monetary(string='Delivery Charges', currency_field='currency_id', )
    other_charges = fields.Monetary(string='Other Charges', currency_field='currency_id')
    # other_charges = fields.Monetary(string='Other Charges', currency_field='currency_id', compute='_compute_other_charges')
    net_amount = fields.Monetary(string='Net Amount', currency_field='currency_id', compute='_compute_net_amount', store=True)

    @api.depends('invoice_line_ids.tax_ids', 'gross_amount')
    def _compute_amount_tax(self):
        for order in self:
            # total_amount = sum(line.price_subtotal for line in order.order_line)
            total_tax = 0.0
            for line in order.invoice_line_ids:
                total_tax += (order.gross_amount * line.tax_ids.amount) / 100
            order.amount_tax = total_tax

    @api.model
    def create(self, vals):
        if vals.get('invoice_origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                vals['delivery_charges'] = sale_order.delivery_charges
                vals['other_charges'] = sale_order.other_charges
                vals['total_discount'] = sale_order.total_discount
        return super(AccountMove, self).create(vals)



    @api.depends('total_amount', 'vat_tax')
    def _compute_gross_amount(self):
        for order in self:
            order.gross_amount = order.total_amount - order.total_discount

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit')
    def _compute_total_amount(self):
        for move in self:
            total = sum(line.quantity * line.price_unit for line in move.invoice_line_ids )
            move.total_amount = total

    @api.depends('invoice_line_ids.discount', 'invoice_line_ids.price_unit', 'invoice_line_ids.quantity', 'invoice_line_ids.discount_fixed')
    def _compute_total_discount(self):
        for order in self:
            total_discount = 0.0
            for line in order.invoice_line_ids:
                line_discount = (line.price_unit * line.quantity * line.discount / 100)
                total_discount += line_discount + line.discount_fixed  # Add discount_fixed value
            order.total_discount = total_discount

    # @api.depends('invoice_line_ids.price_subtotal')
    # def _compute_amount_tax(self):
    #     for move in self:
    #         move.amount_tax = sum(line.tax_ids.amount for line in move.invoice_line_ids)

    @api.depends('gross_amount', 'amount_tax')
    def _compute_after_tax_amount(self):
        for move in self:
            move.after_tax_amount = move.gross_amount + move.amount_tax

    # @api.depends('sale_order_id')
    # def _compute_delivery_charges(self):
    #     for move in self:
    #         move.delivery_charges = move.sale_order_id.delivery_charges

    @api.depends('sale_order_id')
    def _compute_other_charges(self):
        for move in self:
            move.other_charges = move.sale_order_id.other_charges

    @api.depends('after_tax_amount', 'delivery_charges', 'other_charges')
    def _compute_net_amount(self):
        for move in self:
            move.net_amount = move.after_tax_amount + move.delivery_charges + move.other_charges

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        res = super(AccountMove, self).action_register_payment()

        return res

    discount_type = fields.Selection(
        [('percent', 'Percentage'), ('amount', 'Amount')],
        string='Discount type',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default='percent')
    discount_rate = fields.Float('Discount Rate', digits=(16, 2),
                                 readonly=True,
                                 states={'draft': [('readonly', False)],
                                         'sent': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True,
                                      compute='_compute_amount', readonly=True,
                                      track_visibility='always')

    # def action_post(self):
    #     res = super(AccountInvoice, self).action_post()
    #     self.payment_state = "not_paid"
    #     return res

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0
            total_to_pay = move.amount_total

            currencies = set()
            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===

                    if line.display_type == 'tax' or (
                            line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            sign = move.direction_sign
            move.amount_untaxed = sign * (total_untaxed_currency if len(
                currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (
                total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(
                total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = abs(
                move.amount_total) if move.move_type == 'entry' else -(
                    sign * move.amount_total)
            currency = len(
                currencies) == 1 and currencies.pop() or move.company_id.currency_id

            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(
                    include_receipts=True) and move.state == 'posted':
                if currency.is_zero(move.amount_residual):
                    if all(payment.is_matched for payment in
                           move._get_reconciled_payments()):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay,
                                              abs(total_residual)) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in (
                    'in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search(
                    [('reversed_entry_id', '=', move.id),
                     ('state', '=', 'posted'),
                     ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in case of 1 to 1 full
                # reconciliation with a reverse entry; otherwise, we use the
                # regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped(
                    'line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped(
                        'reconciled_line_ids.move_id').filtered(
                    lambda x: x not in (
                            reverse_moves + reverse_moves_full_recs.mapped(
                        'exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def _supply_rate(self):
        for inv in self:
            if inv.discount_type == 'percent':
                discount_totals = 0
                for line in inv.invoice_line_ids:
                    line.discount = inv.discount_rate
                    total_price = line.price_unit * line.quantity
                    discount_total = total_price - line.price_subtotal
                    discount_totals = discount_totals + discount_total
                    inv.amount_discount = discount_totals
                    line._compute_totals()
            else:
                total = discount = 0.0
                for line in inv.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                if inv.discount_rate != 0:
                    discount = (inv.discount_rate / total) * 100
                else:
                    discount = inv.discount_rate
                for line in inv.invoice_line_ids:
                    line.discount = discount
                    inv.amount_discount = inv.discount_rate
                    line._compute_totals()

            inv._compute_tax_totals()

    def button_dummy(self):
        self.supply_rate()
        return True


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields):
        defaults = super(AccountPaymentRegister, self).default_get(fields)
        if 'amount' in fields and self._context.get('active_id'):
            invoice = self.env['account.move'].browse(self._context['active_id'])
            defaults['amount'] = invoice.net_amount  # Assuming net_amount is a field in account.move
        return defaults