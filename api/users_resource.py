from flask import jsonify
from flask_restful import Resource, abort
from database import db_session
from models.users import User
from .user_parsers import user_parser, user_put_parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")
    return user


def user_to_dict(user_object):
    if not user_object:
        return None
    return {
        'id': user_object.id,
        'surname': user_object.surname,
        'name': user_object.name,
        'age': user_object.age,
        'position': user_object.position,
        'speciality': user_object.speciality,
        'address': user_object.address,
        'email': user_object.email,
        'city_from': user_object.city_from,
        'modified_date': user_object.modified_date.isoformat() if user_object.modified_date else None
    }


class UsersResource(Resource):
    def get(self, user_id):
        user = abort_if_user_not_found(user_id)
        return jsonify({'user': user_to_dict(user)})

    def delete(self, user_id):
        user = abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user_to_delete = session.query(User).get(user_id)
        try:
            session.delete(user_to_delete)
            session.commit()
        except Exception as e:
            session.rollback()
            abort(500, message=f"Error deleting user: {str(e)}. Check for associated records.")
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        user = abort_if_user_not_found(user_id)
        args = user_put_parser.parse_args()
        session = db_session.create_session()
        user_to_edit = session.query(User).get(user_id)

        if args['name'] is not None:
            user_to_edit.name = args['name']
        if args['surname'] is not None:
            user_to_edit.surname = args['surname']
        if args['age'] is not None:
            user_to_edit.age = args['age']
        if args['position'] is not None:
            user_to_edit.position = args['position']
        if args['speciality'] is not None:
            user_to_edit.speciality = args['speciality']
        if args['address'] is not None:
            user_to_edit.address = args['address']
        if args['city_from'] is not None:
            user_to_edit.city_from = args['city_from']

        if args['email'] is not None and args['email'] != user_to_edit.email:
            if session.query(User).filter(User.email == args['email']).first():
                session.rollback()
                abort(409, message=f"Email {args['email']} already exists")
            user_to_edit.email = args['email']

        if args['password'] is not None:
            user_to_edit.set_password(args['password'])

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            abort(500, message=f"Error committing user changes: {str(e)}")

        return jsonify({'user': user_to_dict(user_to_edit)})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user_to_dict(user) for user in users]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()

        if session.query(User).filter(User.email == args['email']).first():
            abort(409, message=f"User with email {args['email']} already exists")

        user = User(
            name=args['name'],
            surname=args.get('surname'),
            age=args.get('age'),
            position=args.get('position'),
            speciality=args.get('speciality'),
            address=args.get('address'),
            city_from=args.get('city_from'),
            email=args['email']
        )
        user.set_password(args['password'])

        try:
            session.add(user)
            session.commit()
        except Exception as e:
            session.rollback()
            abort(500, message=f"Error creating user: {str(e)}")

        return {'id': user.id, 'user': user_to_dict(user)}, 201
