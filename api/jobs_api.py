import flask
from flask import jsonify, make_response, request
from database import db_session
from models.jobs import Jobs
from models.category import Category

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates',
    url_prefix='/api'
)


@blueprint.route('/jobs', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    if not jobs:
        return make_response(jsonify({'error': 'No jobs found in the system'}), 404)
    return jsonify(
        {
            'jobs': [
                {
                    'id': job.id,
                    'team_leader_id': job.team_leader,
                    'job': job.job,
                    'work_size': job.work_size,
                    'collaborators': job.collaborators,
                    'start_date': job.start_date.isoformat() if job.start_date else None,
                    'end_date': job.end_date.isoformat() if job.end_date else None,
                    'is_finished': job.is_finished,
                    'categories': [
                        {'id': category.id, 'name': category.name}
                        for category in job.categories
                    ],
                }
                for job in jobs
            ]
        }
    )


@blueprint.route('/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': f'Job with id {job_id} not found'}), 404)
    return jsonify(
        {
            'job': {
                'id': job.id,
                'team_leader_id': job.team_leader,
                'job': job.job,
                'work_size': job.work_size,
                'collaborators': job.collaborators,
                'start_date': job.start_date.isoformat() if job.start_date else None,
                'end_date': job.end_date.isoformat() if job.end_date else None,
                'is_finished': job.is_finished,
                'categories': [
                    {'id': category.id, 'name': category.name}
                    for category in job.categories
                ],
            }
        }
    )


@blueprint.route('/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request or not JSON'}), 400)

    required_fields = ['job', 'team_leader_id', 'work_size']
    for field in required_fields:
        if field not in request.json:
            return make_response(jsonify({'error': f'Missing required field: {field}'}), 400)

    db_sess = db_session.create_session()

    new_job = Jobs(
        job=request.json['job'],
        team_leader=request.json['team_leader_id'],
        work_size=request.json['work_size'],
        collaborators=request.json.get('collaborators'),
        is_finished=request.json.get('is_finished', False)
    )

    if 'category_ids' in request.json and isinstance(request.json['category_ids'], list):
        for cat_id in request.json['category_ids']:
            if not isinstance(cat_id, int):
                return make_response(jsonify({'error': f'Invalid category_id: {cat_id}. Must be an integer.'}), 400)
            category = db_sess.query(Category).get(cat_id)
            if category:
                new_job.categories.append(category)
            else:
                return make_response(jsonify({'error': f'Category with id {cat_id} not found'}), 400)

    db_sess.add(new_job)
    db_sess.commit()

    return make_response(jsonify({
        'message': 'Job created successfully',
        'job': {
            'id': new_job.id,
            'team_leader_id': new_job.team_leader,
            'job': new_job.job,
            'work_size': new_job.work_size,
            'collaborators': new_job.collaborators,
            'start_date': new_job.start_date.isoformat() if new_job.start_date else None,
            'end_date': new_job.end_date.isoformat() if new_job.end_date else None,
            'is_finished': new_job.is_finished,
            'categories': [{'id': cat.id, 'name': cat.name} for cat in new_job.categories]
        }
    }), 201)


@blueprint.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """
    Deletes a job by its ID.
    """
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)

    if not job:
        return make_response(jsonify({'error': f'Job with id {job_id} not found'}), 404)

    db_sess.delete(job)
    db_sess.commit()

    return make_response('', 204)


@blueprint.route('/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    """
    Edits an existing job by its ID.
    """
    db_sess = db_session.create_session()
    job_to_edit = db_sess.query(Jobs).get(job_id)

    if not job_to_edit:
        return make_response(jsonify({'error': f'Job with id {job_id} not found'}), 404)

    if not request.json:
        return make_response(jsonify({'error': 'Request must be JSON'}), 400)

    job_to_edit.job = request.json.get('job', job_to_edit.job)
    job_to_edit.team_leader = request.json.get('team_leader_id',
                                               job_to_edit.team_leader)
    job_to_edit.work_size = request.json.get('work_size', job_to_edit.work_size)
    job_to_edit.collaborators = request.json.get('collaborators', job_to_edit.collaborators)
    job_to_edit.is_finished = request.json.get('is_finished', job_to_edit.is_finished)

    if 'category_ids' in request.json:
        if not isinstance(request.json['category_ids'], list):
            return make_response(jsonify({'error': 'category_ids must be a list'}), 400)

        new_categories = []
        for cat_id in request.json['category_ids']:
            if not isinstance(cat_id, int):
                return make_response(jsonify({'error': f'Invalid category_id: {cat_id}. Must be an integer.'}), 400)
            category = db_sess.query(Category).get(cat_id)
            if category:
                new_categories.append(category)
            else:
                db_sess.rollback()
                return make_response(jsonify({'error': f'Category with id {cat_id} not found'}), 400)
        job_to_edit.categories = new_categories

    db_sess.commit()

    return jsonify({
        'message': 'Job updated successfully',
        'job': {
            'id': job_to_edit.id,
            'team_leader_id': job_to_edit.team_leader,
            'job': job_to_edit.job,
            'work_size': job_to_edit.work_size,
            'collaborators': job_to_edit.collaborators,
            'start_date': job_to_edit.start_date.isoformat() if job_to_edit.start_date else None,
            'end_date': job_to_edit.end_date.isoformat() if job_to_edit.end_date else None,
            'is_finished': job_to_edit.is_finished,
            'categories': [{'id': cat.id, 'name': cat.name} for cat in job_to_edit.categories]
        }
    })
