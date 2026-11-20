# Copyright (C) 2017 Creu Blanca
# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import logging

from werkzeug.urls import url_decode

from odoo.http import (
    content_disposition,
    request,
    route,
)
from odoo.http import (
    serialize_exception as _serialize_exception,
)
from werkzeug.urls import url_parse
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time
import werkzeug.exceptions
from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)


class ReportController(ReportController):
    @route()
    def report_download(self, data, context=None, token=None):  # pylint: disable=unused-argument
        """This function is used by 'action_manager_report.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with an attachment header

        """
        requestcontent = json.loads(data)
        url, type_ = requestcontent[0], requestcontent[1]
        reportname = '???'
        try:
            if type_ in ['qweb-pdf', 'qweb-text']:
                converter = 'pdf' if type_ == 'qweb-pdf' else 'text'
                extension = 'pdf' if type_ == 'qweb-pdf' else 'txt'

                pattern = '/report/pdf/' if type_ == 'qweb-pdf' else '/report/text/'
                reportname = url.split(pattern)[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids, converter=converter, context=context)
                else:
                    # Particular report:
                    data = url_parse(url).decode_query(cls=dict)  # decoding the args represented in JSON
                    if 'context' in data:
                        context, data_context = json.loads(context or '{}'), json.loads(data.pop('context'))
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(reportname, converter=converter, context=context, **data)

                report = request.env['ir.actions.report']._get_report_from_name(reportname)
                filename = "%s.%s" % (report.name, extension)
                if not docids:
                    ctx = json.loads(context or '{}')
                    active_ids = ctx.get("active_ids") or []
                    active_model = ctx.get("active_model")
                    if active_ids:
                        if active_model == report.model:
                            docids = ','.join(map(str, active_ids))
                        elif active_model == "product.product" and report.model == "product.template":
                            # active_ids are variant ids: map them to their templates
                            tmpl_ids = request.env["product.product"].browse(active_ids).exists().product_tmpl_id.ids
                            docids = ','.join(map(str, tmpl_ids))

                if docids:
                    ids = [int(x) for x in docids.split(",") if x.isdigit()]
                    obj = request.env[report.model].browse(ids).exists()
                    if report.print_report_name and len(obj) == 1:
                        report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
                        filename = "%s.%s" % (report_name, extension)
                response.headers.add('Content-Disposition', content_disposition(filename))
                return response
            else:
                return super().report_download(data, context=context, token=token)
        except Exception as e:
            _logger.warning("Error while generating report %s", reportname, exc_info=True)
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            res = request.make_response(html_escape(json.dumps(error)))
            raise werkzeug.exceptions.InternalServerError(response=res) from e
