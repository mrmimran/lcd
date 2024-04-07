# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Nimisha Muralidhar (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    automate_print_invoices = fields.Boolean(
        'Print Invoices',
        help="Print invoices for corresponding purchase orders")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """
    #         Super the method create to confirm quotation, create and validate
    #         invoice
    #     """
    #     res = super(SaleOrder, self).create(vals_list)
    #     automate_purchase = self.env['ir.config_parameter'].sudo().get_param(
    #         'automate_sale')
    #     automate_invoice = self.env['ir.config_parameter'].sudo().get_param(
    #         'automate_invoice')
    #     automate_print_invoices = self.env[
    #         'ir.config_parameter'].sudo().get_param('automate_print_invoices')
    #     automate_validate_invoice = self.env[
    #         'ir.config_parameter'].sudo().get_param('automate_validate_invoice')
    #     automate_confirm_delivery = self.env[
    #         'ir.config_parameter'].sudo().get_param('automate_confirm_delivery')
    #     if automate_print_invoices:
    #         res.automate_print_invoices = True
    #     if automate_purchase:
    #         res.action_confirm()
    #         if automate_invoice:
    #             res._create_invoices()
    #             if automate_validate_invoice:
    #                 res.invoice_ids.action_post()
    #         if automate_confirm_delivery:
    #             # Check if the sale order has a delivery order
    #             if res.picking_ids:
    #                 for picking in res.picking_ids.filtered(lambda p: p.state in ['confirmed', 'assigned']):
    #                     for move in picking.move_ids_without_package:
    #                         move.quantity_done = move.product_uom_qty
    #                     picking.action_assign()
    #                     picking.action_confirm()
    #                     picking.button_validate()
    #                     picking.write({'state': 'done'})
    #                     # picking.write({'state': 'done'})
    #                     if picking.move_ids:
    #                         for move in picking.move_ids:
    #                              move.quantity_done = move.product_uom_qty
    #                     else:
    #                         picking.write({'state': 'assigned'})
    #
    #                 # pickings_to_validate = res.picking_ids.filtered(
    #                 #     lambda picking: picking.state in ['confirmed', 'assigned'])
    #                 #
    #                 # for picking in pickings_to_validate:
    #                 #     picking.write({'state': 'done'})
    #
    #     return res

    def _automate_sale(self):
        automate_purchase = self.env['ir.config_parameter'].sudo().get_param('automate_sale')
        automate_invoice = self.env['ir.config_parameter'].sudo().get_param('automate_invoice')
        automate_print_invoices = self.env['ir.config_parameter'].sudo().get_param('automate_print_invoices')
        automate_validate_invoice = self.env['ir.config_parameter'].sudo().get_param('automate_validate_invoice')
        automate_confirm_delivery = self.env['ir.config_parameter'].sudo().get_param('automate_confirm_delivery')

        if automate_print_invoices:
            self.automate_print_invoices = True

        if automate_purchase:
            if not self._context.get('bypass_automate_sale'):
                self.action_confirm()

            if automate_invoice:
                self._create_invoices()

                if automate_validate_invoice:
                    self.invoice_ids.action_post()

            if automate_confirm_delivery:
                if self.picking_ids:
                    for picking in self.picking_ids.filtered(lambda p: p.state in ['confirmed', 'assigned']):
                        for move in picking.move_ids_without_package:
                            move.quantity_done = move.product_uom_qty

                        picking.action_assign()
                        picking.action_confirm()
                        picking.button_validate()
                        picking.write({'state': 'done'})

                        if picking.move_ids:
                            for move in picking.move_ids:
                                move.quantity_done = move.product_uom_qty
                        else:
                            picking.write({'state': 'assigned'})

    def action_confirm(self):
        # Your custom logic before calling super().action_confirm() if needed

        # Set context to bypass calling _automate_sale from here
        self = self.with_context(bypass_automate_sale=True)
        res = super(SaleOrder, self).action_confirm()

        # Your custom logic after calling super().action_confirm()
        self._automate_sale()

        return res

    def action_print_invoice(self):
        """Method to print invoice"""
        data = self.invoice_ids
        return self.env.ref('account.account_invoices').report_action(data)
