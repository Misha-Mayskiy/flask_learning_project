from flask_restful import Resource, abort
from flask import jsonify
import datetime
from database import db_session
from models.jobs import Jobs
from models.users import User
from models.category import Category
from .job_parsers import job_parser, job_put_parser


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")
    return job


def job_to_dict(job_object):
    if not job_object:
        return None
    return {
        'id': job_object.id,
        'team_leader_id': job_object.team_leader,
        'job': job_object.job,
        'work_size': job_object.work_size,
        'collaborators': job_object.collaborators,
        'start_date': job_object.start_date.isoformat() if job_object.start_date else None,
        'end_date': job_object.end_date.isoformat() if job_object.end_date else None,
        'is_finished': job_object.is_finished,
        'categories': [{'id': cat.id, 'name': cat.name} for cat in job_object.categories] if hasattr(job_object,
                                                                                                     'categories') else []
    }


def parse_datetime_from_iso(iso_string):
    if not iso_string:
        return None
    try:
        return datetime.datetime.fromisoformat(iso_string)
    except ValueError:
        return None


class JobsResource(Resource):
    def get(self, job_id):
        job = abort_if_job_not_found(job_id)
        return jsonify({'job': job_to_dict(job)})

    def delete(self, job_id):
        job = abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job_to_delete = session.query(Jobs).get(job_id)
        session.delete(job_to_delete)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, job_id):
        job_to_edit = abort_if_job_not_found(job_id)
        args = job_put_parser.parse_args()
        session = db_session.create_session()

        current_job_in_session = session.query(Jobs).get(job_id)

        if args['job'] is not None:
            current_job_in_session.job = args['job']
        if args['team_leader_id'] is not None:
            leader = session.query(User).get(args['team_leader_id'])
            if not leader:
                abort(400, message=f"Team leader with id {args['team_leader_id']} not found.")
            current_job_in_session.team_leader = args['team_leader_id']
        if args['work_size'] is not None:
            current_job_in_session.work_size = args['work_size']
        if args['collaborators'] is not None:
            current_job_in_session.collaborators = args['collaborators']
        if args['is_finished'] is not None:
            current_job_in_session.is_finished = args['is_finished']

        if args['start_date'] is not None:
            parsed_start_date = parse_datetime_from_iso(args['start_date'])
            if args['start_date'] and not parsed_start_date:
                abort(400, message=f"Invalid start_date format for '{args['start_date']}'. Use YYYY-MM-DDTHH:MM:SS.")
            current_job_in_session.start_date = parsed_start_date

        if args['end_date'] is not None:
            parsed_end_date = parse_datetime_from_iso(args['end_date'])
            if args['end_date'] and not parsed_end_date:
                abort(400, message=f"Invalid end_date format for '{args['end_date']}'. Use YYYY-MM-DDTHH:MM:SS.")
            current_job_in_session.end_date = parsed_end_date

        if args.get('category_ids') is not None:
            new_categories = []
            if args['category_ids']:
                for cat_id in args['category_ids']:
                    category = session.query(Category).get(cat_id)
                    if not category:
                        abort(400, message=f"Category with id {cat_id} not found.")
                    new_categories.append(category)
            current_job_in_session.categories = new_categories

        session.commit()
        return jsonify({'job': job_to_dict(current_job_in_session)})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [job_to_dict(job) for job in jobs]})

    def post(self):
        args = job_parser.parse_args()
        session = db_session.create_session()

        leader = session.query(User).get(args['team_leader_id'])
        if not leader:
            abort(400, message=f"Team leader with id {args['team_leader_id']} not found.")

        job = Jobs(
            job=args['job'],
            team_leader=args['team_leader_id'],
            work_size=args.get('work_size'),
            collaborators=args.get('collaborators'),
            is_finished=args.get('is_finished', False)
        )

        if args['start_date']:
            parsed_start_date = parse_datetime_from_iso(args['start_date'])
            if not parsed_start_date:
                abort(400, message=f"Invalid start_date format for '{args['start_date']}'. Use YYYY-MM-DDTHH:MM:SS.")
            job.start_date = parsed_start_date
        else:
            job.start_date = datetime.datetime.now()

        if args['end_date']:
            parsed_end_date = parse_datetime_from_iso(args['end_date'])
            if not parsed_end_date:
                abort(400, message=f"Invalid end_date format for '{args['end_date']}'. Use YYYY-MM-DDTHH:MM:SS.")
            job.end_date = parsed_end_date

        if args.get('category_ids'):
            for cat_id in args['category_ids']:
                category = session.query(Category).get(cat_id)
                if not category:
                    session.rollback()
                    abort(400, message=f"Category with id {cat_id} not found.")
                job.categories.append(category)

        session.add(job)
        session.commit()
        return {'id': job.id, 'job': job_to_dict(job)}, 201
