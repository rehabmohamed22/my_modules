# -- coding: utf-8 --
import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import requests, json
# logger = logging.getLogger(name_)
from odoo.tools import format_datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_out_str = fields.Char(
        string='',
        required=False)
    check_date = fields.Date(string="Date", compute="_compute_check_date", store=True)
    is_put_by_system = fields.Boolean()
    @api.depends('check_in')
    def _compute_check_date(self):
        for rec in self:
            rec.check_date = False
            if rec.check_in:
                rec.check_date = rec.check_in.date()

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            # if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
            #     raise ValidationError(
            #         _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s",
            #           empl_name=attendance.employee_id.name,
            #           datetime=format_datetime(self.env, attendance.check_in, dt_format=False)))

            # if not attendance.check_out:
            #     # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
            #     no_check_out_attendances = self.env['hr.attendance'].search([
            #         ('employee_id', '=', attendance.employee_id.id),
            #         ('check_out', '=', False),
            #         ('id', '!=', attendance.id),
            #     ], order='check_in desc', limit=1)
            #     if no_check_out_attendances:
            #         raise ValidationError(
            #             _("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s",
            #               empl_name=attendance.employee_id.name,
            #               datetime=format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False)))
            # else:
            #     # we verify that the latest attendance with check_in time before our check_out time
            #     # is the same as the one before our check_in time computed before, otherwise it overlaps
            #     last_attendance_before_check_out = self.env['hr.attendance'].search([
            #         ('employee_id', '=', attendance.employee_id.id),
            #         ('check_in', '<', attendance.check_out),
            #         ('id', '!=', attendance.id),
            #     ], order='check_in desc', limit=1)
            #     if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
            #         raise ValidationError(
            #             _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s",
            #               empl_name=attendance.employee_id.name,
            #               datetime=format_datetime(self.env, last_attendance_before_check_out.check_in,
            #                                        dt_format=False)))