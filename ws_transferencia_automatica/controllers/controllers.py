# -*- coding: utf-8 -*-

import uuid
from odoo import http
from odoo.http import request, Response
import jsonschema
from jsonschema import validate
import json
import datetime


class TransferenciaAutomaticaController(http.Controller):

    @http.route('/tpco/odoo/ws007', auth="public", type="json", method=['POST'], csrf=False)
    def lista_ubicaciones(self, **post):

        post = json.loads(request.httprequest.data)
        res = {}
        as_token = uuid.uuid4().hex
       

        try:
            myapikey = request.httprequest.headers.get("Authorization")
            if not myapikey:
                mensaje_error['RespCode'] = -2
                mensaje_error['RespMessage'] = f"Rechazado: API KEY no existe"
                return mensaje_error

            user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=myapikey)
            request.uid = user_id
            if user_id:
                res['token'] = as_token

                stock_picking = request.env['stock.picking']
                stock_picking_type = request.env['stock.picking.type']
                production_lot = request.env['stock.production.lot']


                stock_picking_type_obj = stock_picking_type.sudo().search([('name', '=', 'Internal Transfers')], limit=1)
                location_parent_id = request.env['stock.location'].search([('name', '=', post['ubicacionPadre'])], limit=1)
                location_id = request.env['stock.location'].sudo().search([('name', '=', post['ubicacion'])], limit=1)
                detalleActivos = []

                for detalle in post['detalleActivos']:
                    production_lot_obj = production_lot.sudo().search([('name', '=', detalle['EPCCode'])], limit=1)
                    producto_id = production_lot_obj.product_id
                    stock_picking_nuevo = stock_picking.sudo().create({
                        'product_id': producto_id.id,
                        'picking_type_id': stock_picking_type_obj.id,
                        'location_id': location_parent_id.id,
                        'location_dest_id': location_id.id,
                    })
                    request.env.cr.commit()
                    detalleActivos.append({
                        "EPCCode": detalle['EPCCode'],
                        "codigo": 0,
                        "mensaje": "Activo transferido"
                    })

                return {
                         "idTransferencia": stock_picking_nuevo.id,
                         "fechaOperacion": datetime.datetime.now(),
                         "ubicacionPadre": location_parent_id.name,
                         "ubicacion": location_id.name,
                         "user": post['user'],
                         "detalleActivos": detalleActivos
                        }




        except Exception as e:
            mensaje_error = {
                "Token": as_token,
                "RespCode": -5,
                "RespMessage": "Rechazado: Autenticación fallida"
            }
            mensaje_error['RespMessage'] = f"Error: {str(e)}"
            return mensaje_error
