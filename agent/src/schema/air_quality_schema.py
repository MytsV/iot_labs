from marshmallow import Schema, fields
from schema.gps_schema import GpsSchema


class AirQualitySchema(Schema):
    pm25 = fields.Float(required=True)
    pm10 = fields.Float(required=True)
    aqi = fields.Integer(required=True)
    gps = fields.Nested(GpsSchema, required=True)
    humidity = fields.Float(required=True)
    temperature = fields.Float(required=True)
    timestamp = fields.DateTime("iso", required=True)
