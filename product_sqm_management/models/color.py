from odoo import models, fields, api

class ColorColor(models.Model):
    _name = 'color.color'
    _rec_name = 'name'


    name = fields.Char(string='Name')


class SizeSize(models.Model):
    _name = 'size.size'
    _rec_name = 'name'


    name = fields.Char(string='Name')


class OriginOrigin(models.Model):
    _name = 'origin.origin'
    _rec_name = 'name'


    name = fields.Char(string='Name')


class Thickness(models.Model):
    _name = 'thickness.thickness'
    _rec_name = 'name'


    name = fields.Char(string='Name')

class GroupGroup(models.Model):
    _name = 'group.group'
    _rec_name = 'name'


    name = fields.Char(string='Name')