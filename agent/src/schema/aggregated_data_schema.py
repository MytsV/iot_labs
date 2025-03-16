from marshmallow import Schema, fields
from schema.gyroscope_schema import GyroscopeSchema
from schema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    gyroscope = fields.Nested(GyroscopeSchema)
    gps = fields.Nested(GpsSchema)
    timestamp = fields.DateTime("iso")
    user_id = fields.Int()
