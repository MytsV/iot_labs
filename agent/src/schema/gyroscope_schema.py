from marshmallow import Schema, fields


class GyroscopeSchema(Schema):
    x = fields.Int()
    y = fields.Int()
    z = fields.Int()
