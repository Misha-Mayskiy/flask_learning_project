from flask_restful import reqparse

job_parser = reqparse.RequestParser()
job_parser.add_argument('job', type=str, required=True, help="Job title (job) cannot be blank!")
job_parser.add_argument('team_leader_id', type=int, required=True,
                        help="Team leader ID cannot be blank and must be an integer!")
job_parser.add_argument('work_size', type=int, required=False)
job_parser.add_argument('collaborators', type=str, required=False)
job_parser.add_argument('is_finished', type=bool, required=False, default=False)
job_parser.add_argument('start_date', type=str, required=False,
                        help="Start date in ISO format (YYYY-MM-DDTHH:MM:SS) or None")
job_parser.add_argument('end_date', type=str, required=False,
                        help="End date in ISO format (YYYY-MM-DDTHH:MM:SS) or None")
job_parser.add_argument('category_ids', type=int, action='append', required=False, help="List of category IDs")

job_put_parser = reqparse.RequestParser()
job_put_parser.add_argument('job', type=str)
job_put_parser.add_argument('team_leader_id', type=int)
job_put_parser.add_argument('work_size', type=int)
job_put_parser.add_argument('collaborators', type=str)
job_put_parser.add_argument('is_finished', type=bool)
job_put_parser.add_argument('start_date', type=str, help="Start date in ISO format (YYYY-MM-DDTHH:MM:SS) or None")
job_put_parser.add_argument('end_date', type=str, help="End date in ISO format (YYYY-MM-DDTHH:MM:SS) or None")
job_put_parser.add_argument('category_ids', type=int, action='append',
                            help="List of category IDs (will replace existing)")
