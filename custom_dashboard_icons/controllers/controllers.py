# -*- coding: utf-8 -*-
# from odoo import http


# class TestIcon(http.Controller):
#     @http.route('/custom_dashboard_icons/custom_dashboard_icons', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_dashboard_icons/custom_dashboard_icons/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_dashboard_icons.listing', {
#             'root': '/custom_dashboard_icons/custom_dashboard_icons',
#             'objects': http.request.env['custom_dashboard_icons.custom_dashboard_icons'].search([]),
#         })

#     @http.route('/custom_dashboard_icons/custom_dashboard_icons/objects/<model("custom_dashboard_icons.custom_dashboard_icons"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_dashboard_icons.object', {
#             'object': obj
#         })

