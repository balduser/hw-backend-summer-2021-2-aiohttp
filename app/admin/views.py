from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import new_session

from app.admin.schemes import AdminRequestSchema, AdminResponseSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=['admin'], summary='Entry point for the admin to log in')
    @request_schema(AdminRequestSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        """Выполнение логина"""
        email = self.data['email']
        password = self.data['password']
        admin = await self.request.app.store.admins.get_by_email(email)
        if not admin or not admin.password_is_correct(password):
            raise HTTPForbidden
        admin_serialized = AdminResponseSchema().dump(admin)
        session = await new_session(request=self.request)
        session['admin'] = admin_serialized
        return json_response(data=admin_serialized)


class AdminCurrentView(View):
    @docs(tags=['admin'], summary='Information about current user')
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        """Получение данных о себе"""
        if self.request.admin:
            admin_serialized = AdminResponseSchema().dump(self.request.admin)
            return json_response(data=admin_serialized)
        else:  # if 'Request' object has no attribute 'admin' <class 'AttributeError'>
            raise HTTPUnauthorized
