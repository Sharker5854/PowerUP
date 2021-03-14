from flask_login import UserMixin
from flask_security import RoleMixin

from app import db


''' One-To-Many '''
#MANY
class Device(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(200), nullable=False)
	price = db.Column(db.Integer(), nullable=False)
	description = db.Column(db.Text())
	picture = db.Column(db.String(255), nullable=True)
	dev_type = db.Column(db.Integer(), db.ForeignKey('device_type.id'), nullable=False)

	def __init__(self, *args, **kwargs):
		super(Device, self).__init__(*args, **kwargs)

	def __repr__(self):
		return '<DEVICE - id: {}, name: {}, type: {}, price: {}>'.format(self.id, self.name, self.dev_type, self.price) 

#ONE
class DeviceType(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	type_name = db.Column(db.String(50), unique=True, nullable=False)
	devices = db.relationship('Device', backref='type', lazy=True)

	def __init__(self, *args, **kwargs):
		super(Device_type, self).__init__(*args, **kwargs)

	def __repr__(self):
		return '{}'.format(self.type_name)



'''ManyToMany'''
class RolesUsers(db.Model):
	#id = db.Column(db.Integer(), primary_key=True)
	__table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'role_id'),
    )
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
	user = db.relationship('User', backref=db.backref('user_email', lazy='dynamic'))
	role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))
	role = db.relationship('Role', backref=db.backref('role_name', lazy='dynamic'))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.Text(), nullable=False)
	avatar = db.Column(db.Text(), nullable=False, default='anon.jpg')
	phone_num = db.Column(db.String(100), nullable=True)
	city = db.Column(db.String(255), nullable=True)
	adress = db.Column(db.Text(), nullable=True)
	roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)

	def __repr__(self):
		return '{}'.format(self.email)


class Role(db.Model, RoleMixin):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(255), nullable=False, unique=True)
	description = db.Column(db.String(500))

	def __init__(self, *args, **kwargs):
		super(Role, self).__init__(*args, **kwargs)

	def __repr__(self):
		return '{}'.format(self.name)