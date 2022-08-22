from marshmallow import Schema, fields


class AdminRequestSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class AdminResponseSchema(Schema):
    id = fields.Int(required=True)
    email = fields.String(required=True)
