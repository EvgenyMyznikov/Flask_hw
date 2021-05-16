from flask import Flask, jsonify, request
from config import POSTGRE_URI, Config
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine(POSTGRE_URI)

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/')
@app.route('/announcements', methods=['GET'])
@jwt_required()
def get_list_ads():
    user_id = get_jwt_identity()
    ads = Announcement.query.filter(Announcement.user_id == user_id)
    serialized = []
    for ad in ads:
        serialized.append({
            "id": ad.id,
            "user_id": ad.user_id,
            "title": ad.title,
            "description": ad.description
        })
    return jsonify(serialized)


@app.route('/announcements', methods=['POST'])
@jwt_required()
def update_list_ads():
    user_id = get_jwt_identity()
    new_ad = Announcement(user_id=user_id, **request.json)
    session.add(new_ad)
    session.commit()
    serialized = {
        "id": new_ad.id,
        "user_id": new_ad.user_id,
        "title": new_ad.title,
        "description": new_ad.description
    }
    return jsonify(serialized)


@app.route('/announcements/<int:ad_id>', methods=['PUT'])
@jwt_required()
def update_ad(ad_id):
    user_id = get_jwt_identity()
    item = Announcement.query.filter(
        Announcement.id == ad_id,
        Announcement.user_id == user_id
    ).first()
    params = request.json
    if not item:
        return {"message": "Ads with this ID not found!"}, 400
    for key, value in params.items():
        setattr(item, key, value)
    session.commit()
    serialized = {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "description": item.description
    }
    return serialized


@app.route('/announcements/<int:ad_id>', methods=['DELETE'])
@jwt_required()
def delete_ad(ad_id):
    user_id = get_jwt_identity()
    item = Announcement.query.filter(
        Announcement.id == ad_id,
        Announcement.user_id == user_id
    ).first()
    if not item:
        return {"message": "Ads with this ID not found!"}, 400
    session.delete(item)
    session.commit()
    return '', 204


@app.route('/register', methods=['POST'])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {"access_token": token}


@app.route('/login', methods=['POST'])
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return {"access_token": token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == '__main__':
    app.run(debug=True)
