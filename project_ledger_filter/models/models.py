# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResProject(models.Model):
    _name = 'res.project'
    _description = 'Project'
    name = fields.Char(required=True,translate=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    project_id = fields.Many2one('res.project', string="project")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    project_id = fields.Many2one('res.project', string="project",related="partner_id.project_id",store=True)


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_project = fields.Boolean(
        string="project",
        compute=lambda x: x._compute_report_option_filter('filter_project'), readonly=False, store=True,
        depends=['root_report_id'],
    )

    def _init_options_project(self, options, previous_options=None):
        # if not self.filter_project:
        #     return
        options['project'] = True

        options['project_ids'] = previous_options and previous_options.get('project_ids') or []
        selected_project_ids = [int(project) for project in options['project_ids']] or []
        selected_projects = selected_project_ids and self.env['res.project'].browse(selected_project_ids) or self.env['res.project']
        options['selected_project_ids'] = selected_projects.mapped('name')

        print("OOO", options)

    @api.model
    def _get_options_project_domain(self, options):
        domain = []
        if options.get('project_ids'):
            project_ids = [int(project) for project in options['project_ids']] or []
            domain.append(('project_id', 'in', project_ids))

        return domain

    def _get_options_domain(self, options, date_scope):
        domain = super(AccountReport, self)._get_options_domain(options, date_scope)

        domain += self._get_options_project_domain(options)

        return domain





class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountPartnerLedger, self)._get_options_domain(options)
        domain += self._get_options_project_domain()
        return domain

    @api.model
    def _get_options_project_domain(self, options):
        domain = []
        if options.get('project_ids'):
            project_ids = [int(project) for project in options['project_ids']]
            domain.append(('project_id', 'in', project_ids))
        return domain

    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        rslt = {partner_id: [] for partner_id in partner_ids}

        partner_ids_wo_none = [x for x in partner_ids if x]
        directly_linked_aml_partner_clauses = []
        directly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IS NOT NULL'
        if None in partner_ids:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IS NULL')
        if partner_ids_wo_none:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IN %s')
            directly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
            indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IN %s'
            indirectly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
        directly_linked_aml_partner_clause = '(' + ' OR '.join(directly_linked_aml_partner_clauses) + ')'

        ct_query = self.env['account.report']._get_query_currency_table(options)
        queries = []
        all_params = []
        lang = self.env.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        report = self.env.ref('account_reports.partner_ledger_report')
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            tables, where_clause, where_params = report._query_get(group_options, 'strict_range')

            all_params += [
                column_group_key,
                *where_params,
                *directly_linked_aml_partner_params,
                column_group_key,
                *indirectly_linked_aml_partner_params,
                *where_params,
                group_options['date']['date_from'],
                group_options['date']['date_to'],
            ]

            # For the move lines directly linked to this partner
            queries.append(f'''
                SELECT
                    account_move_line.id,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    COALESCE(account_move_line.invoice_date, account_move_line.date)                 AS invoice_date,
                    ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                    ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                    ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                    account_move.name                                                                AS move_name,
                    account_move.move_type                                                           AS move_type,
                    account.code                                                                     AS account_code,
                    {account_name}                                                                   AS account_name,
                    journal.code                                                                     AS journal_code,
                    {journal_name}                                                                   AS journal_name,
                    project.name                                                                      AS project_name,                    
                    %s                                                                               AS column_group_key,
                    'directly_linked_aml'                                                            AS key
                FROM {tables}
                JOIN account_move ON account_move.id = account_move_line.move_id
                LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                LEFT JOIN res_project project                 ON project.id = account_move_line.project_id                
                WHERE {where_clause} AND {directly_linked_aml_partner_clause}
                ORDER BY account_move_line.date, account_move_line.id
            ''')

            # For the move lines linked to no partner, but reconciled with this partner. They will appear in grey in the report
            queries.append(f'''
                SELECT
                    account_move_line.id,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    aml_with_partner.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    COALESCE(account_move_line.invoice_date, account_move_line.date)                    AS invoice_date,
                    CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    ) END                                                                               AS debit,
                    CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    ) END                                                                               AS credit,
                    - sign(aml_with_partner.balance) * ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    )                                                                                   AS balance,
                    account_move.name                                                                   AS move_name,
                    account_move.move_type                                                              AS move_type,
                    account.code                                                                        AS account_code,
                    {account_name}                                                                      AS account_name,
                    journal.code                                                                        AS journal_code,
                    {journal_name}                                                                      AS journal_name,
                    project.name                                                                         AS project_name,
                    %s                                                                                  AS column_group_key,
                    'indirectly_linked_aml'                                                             AS key
                FROM {tables}
                    LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id,
                    account_partial_reconcile partial,
                    account_move,
                    account_move_line aml_with_partner,
                    account_journal journal,
                    account_account account,
                    res_project project
                WHERE
                    (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
                    AND account_move_line.partner_id IS NULL
                    AND account_move.id = account_move_line.move_id
                    AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                    AND {indirectly_linked_aml_partner_clause}
                    AND journal.id = account_move_line.journal_id
                    AND account.id = account_move_line.account_id
                    AND {where_clause}
                    AND partial.max_date BETWEEN %s AND %s
                    AND project.id = account_move_line.project_id
                ORDER BY account_move_line.date, account_move_line.id
            ''')

        query = '(' + ') UNION ALL ('.join(queries) + ')'

        if offset:
            query += ' OFFSET %s '
            all_params.append(offset)

        if limit:
            query += ' LIMIT %s '
            all_params.append(limit)

        self._cr.execute(query, all_params)
        for aml_result in self._cr.dictfetchall():
            if aml_result['key'] == 'indirectly_linked_aml':

                # Append the line to the partner found through the reconciliation.
                if aml_result['partner_id'] in rslt:
                    rslt[aml_result['partner_id']].append(aml_result)

                # Balance it with an additional line in the Unknown Partner section but having reversed amounts.
                if None in rslt:
                    rslt[None].append({
                        **aml_result,
                        'debit': aml_result['credit'],
                        'credit': aml_result['debit'],
                        'balance': -aml_result['balance'],
                    })
            else:
                rslt[aml_result['partner_id']].append(aml_result)

        return rslt
