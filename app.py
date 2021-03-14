from flask import Flask, flash, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import FileUploadField

from flask_login import LoginManager

from flask_security import current_user
from flask_security import SQLAlchemyUserDatastore, Security 

from config import Configuration
import random
import os


app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)


### MIGRATE ###
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно авторизоваться'
login_manager.login_message_category = 'warning'


### ADMIN-PANEL ###
from models import *

class AdminMixin():
	def is_accessible(self):
		return 'admin' in current_user.roles

	def inaccessible_callback(self, name, **kwargs):
		flash('У вас нет доступа к этой странице!', 'danger')
		return redirect(url_for('index'))


class HomeAdminView(AdminMixin, AdminIndexView):
	pass



class DeviceAdminView(AdminMixin, ModelView):
	column_searchable_list = ['name']

	#column_exclude_list = ['pictures'] #exclude just from model view
	form_overrides = {
		'picture' : FileUploadField
	}
	form_args = {
        'picture': {
            'label': 'Picture',
            'base_path': Configuration.STORAGE_PRODUCT_PIC,
            'allow_overwrite': True,
            'allowed_extensions' : ['jpg', 'png', 'svg', 'jpeg']
        }
    }



class DeviceTypeAdminView(AdminMixin, ModelView):
	form_columns = ['type_name']

class UserAdminView(AdminMixin, ModelView):
	column_exclude_list = ['id', 'password']
	can_create = False
	can_edit = False
	column_searchable_list = ['email']

class RoleAdminView(AdminMixin, ModelView):
	form_columns = ['name', 'description']

class RolesUsersAdminView(AdminMixin, ModelView):
	can_delete = False
	can_create = False
	can_edit = True


admin = Admin(app, 'Main page', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(DeviceAdminView(Device, db.session))
admin.add_view(DeviceTypeAdminView(DeviceType, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RoleAdminView(Role, db.session))
admin.add_view(RolesUsersAdminView(RolesUsers, db.session))


### SECURITY ###
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)