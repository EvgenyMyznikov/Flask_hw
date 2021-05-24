from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from announcements.app import db, session, Base
from flask_jwt_extended import create_access_token
from passlib.hash import bcrypt


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    announcements = relationship('Announcement', backref='user', lazy=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = bcrypt.hash(kwargs.get('password'))

    def get_token(self, expire_time=24):
        expire_delta = timedelta(expire_time)
        token = create_access_token(identity=self.id, expires_delta=expire_delta)
        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email == email).one()
        if not bcrypt.verify(password, user.password):
            raise Exception('User with this password not found!')
        return user


class Announcement(Base):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def get_user_list(cls, user_id):
        try:
            announcements = cls.query.filter(cls.user_id == user_id).all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return announcements

    @classmethod
    def get_list(cls):
        try:
            announcements = cls.query.all()
            session.commit()
        except Exception:
            session.rollback()
            raise
        return announcements

    def save(self):
        try:
            session.add(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    @classmethod
    def get(cls, ad_id, user_id):
        try:
            announcement = Announcement.query.filter(
                Announcement.id == ad_id,
                Announcement.user_id == user_id
            ).first()
            if not announcement:
                raise Exception('No announcement with this id')
        except Exception:
            session.rollback()
            raise
        return announcement

    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def delete(self):
        try:
            session.delete(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

