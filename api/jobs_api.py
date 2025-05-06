import flask
from flask import jsonify, make_response
from database import db_session
from models.jobs import Jobs

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
