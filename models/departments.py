import sqlalchemy
from sqlalchemy import orm
from database.db_session import SqlAlchemyBase


class Department(SqlAlchemyBase):
    __tablename__ = 'departments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chief = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    members = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)

    chief_user = orm.relationship('User')

    def __repr__(self):
        return f'<Department> {self.id} {self.title} chief:{self.chief}'
