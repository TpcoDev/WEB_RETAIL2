# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo import http
from odoo.http import request
from datetime import datetime
from bs4 import BeautifulSoup
import json
import sys
import uuid
from odoo import http
from odoo.http import request, Response
import jsonschema
from jsonschema import validate
import json
import yaml
import requests, json
import logging

_logger = logging.getLogger(__name__)
from datetime import timedelta, datetime, date

MESSAGES = {
    '0': 'Activo existe',
    '1': 'Activo faltante en inventario',
    '2': 'Activo sobrante en inventario',
    '9': 'Activo no esta en el sistema',
}


class OdooController(http.Controller):

    @http.route('/tpco/odoo/ws005', auth="public", type="json", method=['POST'], csrf=False)
    def activo_query(self, **post):

        post = json.loads(request.httprequest.data)
        res = {}
        as_token = uuid.uuid4().hex
        mensaje_error = {
            "Token": as_token,
            "RespCode": -1,
            "RespMessage": "Error de conexión"
        }
        mensaje_correcto = {
            "Token": as_token,
            "RespCode": 0,
            "RespMessage": "Activo existe"
        }
        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if not myapikey:
                mensaje_error['RespCode'] = -2
                mensaje_error['RespMessage'] = f"Rechazado: API KEY no existe"
                return mensaje_error

            user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=myapikey)
            request.uid = user_id

            if post['params']:
                post = post['params']
                vals = {
                    'idConciliacion': '',
                    'fechaOperacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ubicacion': post['ubicacion'],
                    'ubicacionPadre': post['ubicacionPadre'],
                    'user': post['user'],
                    'detalleActivos': []
                }

                domain = []
                location_parent_id = None
                location_id = None
                if not post['ubicacion'] == 'todos':
                    location_parent_id = request.env['stock.location'].sudo().search(
                        [('name', '=', post['ubicacionPadre'])], limit=1)
                    location_id = request.env['stock.location'].sudo().search([('name', '=', post['ubicacion'])],
                                                                              limit=1)
                    if location_parent_id:
                        location_id = request.env['stock.location'].sudo().search(
                            [('name', '=', post['ubicacion']), ('location_id', '=', location_parent_id.id)],
                            limit=1)
                    domain.append(('location_id', '=', location_id.id))

                quants = request.env['stock.quant'].sudo().search(domain)

                for quant in quants:
                    product_id = quant.product_id
                    lot = quant.lot_id

                    vals['detalleActivos'].append({
                        'EPCCode': lot.name if lot else '',
                        'codigo': MESSAGES.keys(),
                        'mensaje': MESSAGES.keys(),

                    })

                return vals

        except Exception as e:
            mensaje_error = {
                "Token": as_token,
                "RespCode": -5,
                "RespMessage": "Rechazado: Autenticación fallida"
            }
            mensaje_error['RespMessage'] = f"Error: {str(e)}"
            return mensaje_error
