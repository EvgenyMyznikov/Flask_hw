from flask import Blueprint, jsonify
from announcements.app import logger, docs
from announcements.schemas import AnnouncementSchema
from flask_apispec import use_kwargs, marshal_with
from announcements.models import Announcement
from flask_jwt_extended import jwt_required, get_jwt_identity
from announcements.base_view import BaseView

ads = Blueprint('ads', __name__)


class ListView(BaseView):
    @marshal_with(AnnouncementSchema(many=True))
    def get(self):
        try:
            ads = Announcement.get_list()
        except Exception as e:
            logger.warning(f'announcements - read action failed with errors: {e}')
            return {'message': str(e)}, 400
        return ads


@ads.route('/announcements', methods=['GET'])
@jwt_required()
@marshal_with(AnnouncementSchema(many=True))
def get_list_ads():
    try:
        user_id = get_jwt_identity()
        ads = Announcement.get_user_list(user_id=user_id)
    except Exception as e:
        logger.warning(f'user:{user_id} announcements - read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return ads


@ads.route('/announcements', methods=['POST'])
@jwt_required()
@use_kwargs(AnnouncementSchema)
@marshal_with(AnnouncementSchema)
def update_list_ads(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_ad = Announcement(user_id=user_id, **kwargs)
        new_ad.save()
    except Exception as e:
        logger.warning(f'user:{user_id} announcements - create action failed with errors: {e}')
        return {'message': str(e)}, 400
    return new_ad


@ads.route('/announcements/<int:ad_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(AnnouncementSchema)
@marshal_with(AnnouncementSchema)
def update_ad(ad_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        item = Announcement.get(ad_id, user_id)
        item.update(**kwargs)
    except Exception as e:
        logger.warning(f'user:{user_id} announcement:{ad_id} - update action failed with errors: {e}')
        return {'message': str(e)}, 400
    return item


@ads.route('/announcements/<int:ad_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(AnnouncementSchema)
def delete_ad(ad_id):
    try:
        user_id = get_jwt_identity()
        item = Announcement.get(ad_id, user_id)
        item.delete()
    except Exception as e:
        logger.warning(f'user:{user_id} announcement:{ad_id} - delete action failed with errors: {e}')
        return {'message': str(e)}, 400
    return '', 204


@ads.errorhandler(422)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['invalid request!'])
    logger.warning(f'invalid input params {messages}')
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


docs.register(get_list_ads, blueprint='ads')
docs.register(update_list_ads, blueprint='ads')
docs.register(update_ad, blueprint='ads')
docs.register(delete_ad, blueprint='ads')
ListView.register(ads, docs, '/main', 'listview')

