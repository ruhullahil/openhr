# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.http import request
import json


class DtJwtLogin(Home):
    @http.route('/jwt/login', auth='none',type='http',csrf=False,cors='*')
    def index(self):
        # parms = request.par
        data = request.params
        if request.httprequest.content_length:
            data = json.loads(request.httprequest.data)
        data['type'] = 'password'
        print('results',data)
        request.params = data
        parms = request.params
        request.httprequest.method = 'POST'
        print('parms', parms)
        return self.web_login(redirect='/odoo?',login=data.get('login'),password=data.get('password'),type='password')
        # return self.web_login(,redirect=None)




