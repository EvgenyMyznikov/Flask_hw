from marshmallow import Schema, validate, fields


class AnnouncementSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=[validate.Length(max=300)])
    description = fields.String(required=True, validate=[validate.Length(max=1000)])
    created = fields.DateTime(dump_only=True)
    message = fields.String(dump_only=True)


class UserRegistrationSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(max=250)])
    email = fields.String(required=True, validate=[validate.Length(max=250)])
    password = fields.String(required=True, validate=[validate.Length(max=100)], load_only=True)
    announcements = fields.Nested(AnnouncementSchema, many=True, dump_only=True)


class UserLoginSchema(Schema):
    email = fields.String(required=True, validate=[validate.Length(max=250)])
    password = fields.String(required=True, validate=[validate.Length(max=100)], load_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
