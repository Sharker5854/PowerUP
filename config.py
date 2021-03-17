import uuid

class Configuration(object):
	DEBUG = True
	SECRET_KEY = uuid.uuid4().hex
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:1379@localhost/flsite_database'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	PRODUCTS_FOR_PAGE = 6


	'''PROJECT DIRS'''
	STORAGE_USER_AVA = 'static/image_storage/user_avatar/'
	STORAGE_USER_AVA_FOR_STATIC = 'image_storage/user_avatar/'
	STORAGE_PRODUCT_PIC = 'static/image_storage/product_pic/'
	STORAGE_PRODUCT_PIC_FOR_STATIC = 'image_storage/product_pic/'


	'''URLS FOR JavaScript FUNCTIONS'''
	FUNCTIONS_URL = {
		'ADDING_BASKET' : 'http://localhost:5000/adding_basket/',
		'DELETING_FROM_BASKET' : 'http://localhost:5000/deleting_basket/'
	}


	'''FLASK-SECURITY'''
	SECURITY_MSG_LOGIN = ('Для доступа к этой странице нужно авторизоваться!', 'warning')