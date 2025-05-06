import flask
from flask import jsonify, make_response, request
from database import db_session
from models.users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates',
    url_prefix='/api'
)


# --- API Helper to convert User object to dictionary (excluding password) ---
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
        'modified_date': user_object.modified_date.isoformat() if user_object.modified_date else None
    }


# --- 1. Получение всех пользователей ---
@blueprint.route('/users', methods=['GET'])
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    if not users:
        return make_response(jsonify({'error': 'No users found'}), 404)
    return jsonify(
        {'users': [user_to_dict(user) for user in users]}
    )


# --- 2. Получение одного пользователя ---
@blueprint.route('/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': f'User with id {user_id} not found'}), 404)
    return jsonify({'user': user_to_dict(user)})


# --- 3. Добавление пользователя ---
@blueprint.route('/users', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request or not JSON'}), 400)

    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in request.json:
            return make_response(jsonify({'error': f'Missing required field: {field}'}), 400)

    db_sess = db_session.create_session()

    if db_sess.query(User).filter(User.email == request.json['email']).first():
        return make_response(jsonify({'error': f'User with email {request.json["email"]} already exists'}),
                             409)  # Conflict

    new_user = User(
        name=request.json['name'],
        surname=request.json.get('surname'),
        age=request.json.get('age'),
        position=request.json.get('position'),
        speciality=request.json.get('speciality'),
        address=request.json.get('address'),
        email=request.json['email']
    )
    new_user.set_password(request.json['password'])

    db_sess.add(new_user)
    db_sess.commit()

    return make_response(jsonify({
        'message': 'User created successfully',
        'user': user_to_dict(new_user)
    }), 201)  # Created


# --- 4. Редактирование пользователя ---
@blueprint.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    user_to_edit = db_sess.query(User).get(user_id)

    if not user_to_edit:
        return make_response(jsonify({'error': f'User with id {user_id} not found'}), 404)

    if not request.json:
        return make_response(jsonify({'error': 'Request must be JSON'}), 400)

    user_to_edit.name = request.json.get('name', user_to_edit.name)
    user_to_edit.surname = request.json.get('surname', user_to_edit.surname)
    user_to_edit.age = request.json.get('age', user_to_edit.age)
    user_to_edit.position = request.json.get('position', user_to_edit.position)
    user_to_edit.speciality = request.json.get('speciality', user_to_edit.speciality)
    user_to_edit.address = request.json.get('address', user_to_edit.address)

    new_email = request.json.get('email')
    if new_email and new_email != user_to_edit.email:
        if db_sess.query(User).filter(User.email == new_email).first():
            return make_response(jsonify({'error': f'Email {new_email} is already taken'}), 409)  # 409 Conflict
        user_to_edit.email = new_email

    new_password = request.json.get('password')
    if new_password:
        user_to_edit.set_password(new_password)

    db_sess.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user': user_to_dict(user_to_edit)
    })


# --- 5. Удаление пользователя ---
@blueprint.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user_to_delete = db_sess.query(User).get(user_id)

    if not user_to_delete:
        return make_response(jsonify({'error': f'User with id {user_id} not found'}), 404)

    try:
        db_sess.delete(user_to_delete)
        db_sess.commit()
    except Exception as e:
        db_sess.rollback()
        return make_response(
            jsonify({'error': 'Failed to delete user. '
                              'Check for associated records (e.g., jobs).', 'details': str(e)}),
            500)

    return make_response('', 204)  # No Content
