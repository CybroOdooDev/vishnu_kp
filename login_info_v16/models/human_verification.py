from odoo import models, fields, api,_

class Userlog(models.Model):
    _name = 'user.log'
    _description = 'user log infomation'
    _rec_name = 'user'

    user = fields.Many2one('res.users', string='User')
    image = fields.Binary()
    date = fields.Datetime('login Date')