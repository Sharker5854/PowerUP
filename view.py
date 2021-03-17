from flask import render_template, redirect, url_for, flash, request, abort, session, json, current_app

from flask_wtf.csrf import CSRFError

from app import app
from app import db
from app import login_manager
from models import User, Role, Device, DeviceType
from forms import RegistrationForm, LoginForm, MakeOrderForm
from app import user_datastore
from config import Configuration
import os
import random
from collections import Counter
from operator import attrgetter
from cloudipsp import Api, Checkout

from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

'''current app context variables'''
@app.context_processor
def login_context():
    return {
        'register_form' : RegistrationForm(),
        'login_form': LoginForm(),
    }



@app.route('/', methods=['POST', 'GET'])
def index():
	return render_template('index.html')	



@app.before_request
def create_basket():
	if 'basket' not in session:
		session['basket'] = []
	else:
		pass



@app.route('/catalog/<device_type>', methods=['POST', 'GET'])
def catalog(device_type):
	q = request.args.get('q')
	page = request.args.get('page')

	pages = search(device_type, q).paginate(check_page_type(page), Configuration.PRODUCTS_FOR_PAGE)

	return render_template('catalog.html', pages=pages, spec_urls=Configuration.FUNCTIONS_URL)


@app.route('/product/<product_id>')
def product_page(product_id):
	product = Device.query.get(product_id)

	return render_template('product_page.html', 
		page_title=product.name, 
		picture_dir=Configuration.STORAGE_PRODUCT_PIC_FOR_STATIC, 
		product=product,
		product_device_type=DeviceType.query.get(product.dev_type).type_name,
		spec_urls=Configuration.FUNCTIONS_URL)


@app.route('/making_order', methods=["POST", "GET"])
@login_required
def making_order():
	form = MakeOrderForm()

	if session['basket'] == []:
		return redirect(url_for('basket'))
	else:
		#all added devices list
		added_devices = [Device.query.get(product_id) for product_id in session['basket']]

		#unique added device list
		added_devices_unique = set(product for product in added_devices)
		added_devices_unique = sorted([product for product in added_devices_unique], key=attrgetter('price')) #attrgetter - special function to get attribute from objects
		added_devices_unique.reverse() #result: sorting from expensive to cheap

		#quantity of every added device
		counts = Counter(added_devices)
		quantity_product = {}
		for unique_product in added_devices_unique:
			quantity_product[unique_product.id] = counts[unique_product]

		#general price
		general_price = sum([device.price for device in added_devices])


		if request.method == 'POST': 
			if form.validate_on_submit():
				user_order_data = {}

				for field in form:
					if field.name == 'submit' or field.name == 'csrf_token':
						pass
					elif field.name == 'phone_num' and field.data.startswith('+7'):
						user_order_data[field.name] = field.data.replace('+7', '8')
					else:
						user_order_data[field.name] = field.data

				if remember_order_data(user_order_data, current_user.id):
					print('Введенные пользователем данные при заказе сохранены!')
				else: 
					print('Введенные данные при заказе не сохранены!')

				return redirect(url_for('payment', price=general_price))

			else: flash('Введены некорректные данные!', 'danger')


		return render_template('making_order.html', 
			page_title='Оформление заказа',
			form=form, #must send exactly this form, not from context_processor!!!
			picture_dir=Configuration.STORAGE_PRODUCT_PIC_FOR_STATIC, 
			spec_urls=Configuration.FUNCTIONS_URL,
			devices_data={
				'added_devices' : added_devices_unique,
				'device_quantity' : quantity_product,
				'general_quantity' : len(added_devices),
				'general_price' : general_price
			}
		)


@app.route('/payment/<int:price>', methods=["POST", "GET"])
@login_required
def payment(price):
	api = Api(merchant_id=1396424, secret_key='test')
	checkout = Checkout(api=api)
	data = {
		'currency' : 'RUB',
		'amount' : str(price) + '00'
	}
	url = checkout.url(data).get('checkout_url')

	return redirect(url)


@app.route('/about', methods=["POST", "GET"])
def about():
	return render_template('about.html')



'''Used to reload the user object from the user ID stored in the session.
It should return None (not raise an exception) if the ID is not valid 
(in that case, the ID will manually be removed from the session and processing will continue.)'''
@login_manager.user_loader
def get_user(user_id):
	return User.query.get(int(user_id))



@app.route('/register', methods=['POST', 'GET'])
def register():
	form = RegistrationForm()

	if current_user.is_authenticated:
		flash('Вы уже авторизованы!', 'warning')
		return redirect(url_for('profile'))

	if request.method == 'POST' and form.validate_on_submit():
		hash = generate_password_hash(form.password.data)
		new_user_data = User(name=form.name.data, email=form.email.data, password=hash)
		if add_to_database(new_user_data):
			login_user( get_user_by_email(form, form.email.data)[1], remember=True ) #sign-in with new registered data of user in DB
			flash('Вы успешно зарегистрировались!', 'success')
	
			give_role('customer') #give role to new user IMMEDIATELY

			return redirect(url_for('profile'))
		else:
			flash('Аккаунт с такой почтой уже существует!', 'danger')

	return render_template('security/register_user.html', page_title='Регистрация')



@app.route('/auth', methods=['POST', 'GET'])
def login():
	form = LoginForm() #leave, to check data after completion forms

	if current_user.is_authenticated:
		flash('Вы уже авторизованы!', 'warning')
		return redirect(url_for('profile'))

	if form.validate_on_submit():
		
		if check_password_hash( get_user_by_email(form, form.email.data)[0], form.password.data ):
			login_user( get_user_by_email(form, form.email.data)[1], remember=form.remember.data)
			session['basket'] = [item for item in session['basket']] #save current basket
			flash('Вы успешно авторизовались!', 'success')
			return redirect(url_for('profile'))
		else:
			flash('Неверный логин или пароль!', 'danger')
			return render_template('security/login_user.html', page_title='Авторизация')

	return render_template('security/login_user.html', page_title='Авторизация')



@app.route('/logout_user', methods=['POST', 'GET'])
@login_required
def logout():
	if current_user.is_authenticated:
		logout_user()
		session['basket'] = [] #update basket
		flash('Вы вышли из аккаунта!', 'warning')
		return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))



@app.errorhandler(CSRFError)
def csrf_error_handler(e):
	abort(400)



@app.route('/basket', methods=['POST', 'GET'])
def basket():
	if session['basket'] == []:
		return render_template('basket.html', page_title='Козина товаров', devices_data={'added_devices' : None})
	else:
		#all added devices list
		added_devices = [Device.query.get(product_id) for product_id in session['basket']]

		#unique added device list
		added_devices_unique = set(product for product in added_devices)
		added_devices_unique = sorted([product for product in added_devices_unique], key=attrgetter('price')) #attrgetter - special function to get attribute from objects
		added_devices_unique.reverse() #result: sorting from expensive to cheap

		#quantity of every added device
		counts = Counter(added_devices)
		quantity_product = {}
		for unique_product in added_devices_unique:
			quantity_product[unique_product.id] = counts[unique_product]

		#general price
		general_price = sum([device.price for device in added_devices])

		return render_template('basket.html', 
			page_title='Козина товаров',  
			picture_dir=Configuration.STORAGE_PRODUCT_PIC_FOR_STATIC, 
			spec_urls=Configuration.FUNCTIONS_URL,
			devices_data={
				'added_devices' : added_devices_unique,
				'device_quantity' : quantity_product,
				'general_quantity' : len(added_devices),
				'general_price' : general_price
			}
		)



@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
	if request.method == 'POST':
		user_data = ProfileControllers(request.form, request.files, current_user)

		name = user_data.change_name()
		email = user_data.change_email()
		password = user_data.change_password() 
		avatar = user_data.change_avatar()


		if name or email or password or avatar:
			flash('Изменения сохранены!', 'success')


	return render_template('profile.html', page_title='Профиль')



#---------------------------------------------------------------------------------------#

'''Adding string to DB'''
def add_to_database(data):
	try:
		db.session.add(data)
		db.session.commit()
	except BaseException as e:
		print('Ошибка занесения данных в БД - ' + str(e))
		return False
	else:
		return True

'''Get user data from DB by entered email'''
def get_user_by_email(form, entered_email):
	user_account = User.query.filter_by(email=entered_email).first()
	if user_account is None:
		flash('Такого пользователя не существует!', 'danger')
		return render_template('security/login_user.html', page_title='Авторизация')
	else:
		return user_account.password, user_account

'''Give any role to user'''
def give_role(role):
	try:
		giving_role = user_datastore.find_or_create_role(role)
		user_datastore.add_role_to_user(current_user, giving_role) #give role to new user IMMEDIATELY
		db.session.commit()		
		return True
	except: 
		return False

'''Checking if the page that we got from GET-request is int-type'''
def check_page_type(page):
	if page and page.isdigit():
		page = int(page)
		return page
	else:
		page = 1
		return page

'''Search according to typing of products'''
def search(device_type, q):
	if device_type == 'all' and not q:
		products = Device.query
	elif device_type == 'all' and q:
		products = Device.query.filter(Device.name.contains(q))
	elif device_type != 'all' and not q:
		products = Device.query.filter(Device.dev_type == DeviceType.id).filter(DeviceType.type_name == device_type) #get devices whose   dev_type == DeviceType.id   and type_name of this DeviceType == "device_type"(that we've got in query)
	elif device_type != 'all' and q:
		products = Device.query.filter(Device.name.contains(q))
	else:
		products = Device.query

	return products

'''Secretly remember phone_num, city and adress after ordering'''
def remember_order_data(user_order_data, cur_id):
	try: 
		user_data = User.query.get(cur_id)
		user_data.phone_num = user_order_data['phone_num']
		user_data.city = user_order_data['city']
		user_data.adress = user_order_data['adress']
		db.session.commit()
	except Exception:
		print('Ошибка сохранения данных пользователя при заказе!')
		return False
	return True
	

'''Add item to basket'''
@app.route('/adding_basket/<device_id>', methods=["POST", "GET"])
def add_basket(device_id):
	session['basket'].insert(0, device_id) #add to the start of the list
	session.modified = True # necessary!!!
	#session['basket'] = [] #use it when you need to clear the basket ^_^
	return json.dumps({'f_message' : 'Добавлено &#10003;'}) #f-message: send json-text to js function (specially to show this message on button with AJAX)
	
'''Delete item from basket'''
@app.route('/deleting_basket/<device_id>', methods=["POST", "GET"])
def delete_basket(device_id):
	session['basket'].remove(device_id)
	session.modified = True
	return json.dumps({'status':'Successfully deleted - ' + str(device_id)})




class ProfileControllers:
	def __init__(self, form, file, current_user):
		self.form = form
		self.file = file
		self.cur_user = current_user
		self.user = User.query.get(self.cur_user.id)

	def change_name(self):
		if self.form['profile_name']!=self.cur_user.name:
			if (2 <= len(self.form['profile_name']) <= 50):
				self.user.name = self.form['profile_name']
				db.session.commit()
				return True
			else:
				flash('Новое имя должно быть от 2 до 50 символов', 'danger')
		return False


	def change_email(self):
		if self.form['profile_mail']!=self.cur_user.email: 
			if self.__validate_email(self.form['profile_mail']):
				self.user.email = self.form['profile_mail']
				db.session.commit()
				return True
			else:
				flash('Введена некорректная почта!', 'danger')
		return False


	def change_password(self):
		if self.form['profile_psw_old']!='' and self.form['profile_psw_new']!='':
			if (4 <= len(self.form['profile_psw_new']) <= 50):
				if check_password_hash(self.cur_user.password, self.form['profile_psw_old']):
					if self.form['profile_psw_old'] != self.form['profile_psw_new']:
						self.user.password = generate_password_hash(self.form['profile_psw_new'])
						db.session.commit()
						return True
					else:
						flash('Старый пароль должен отличаться от нового!', 'danger')
				else:
					flash('Неверный пароль!', 'danger')
			else:
				flash('Новый пароль должен быть от 4 до 50 символов', 'danger')
		return False


	def change_avatar(self):		
		if self.file['profile_avatar']:
			file = self.file['profile_avatar']
			saving = self.__save_file(file)
			if saving[0] is True:
				self.__del_prev_ava()
				self.user.avatar = saving[1]
				db.session.commit()
				return True
			else:
				flash('Ошибка изменения аватара!', 'danger')
		return False


	def __validate_email(self, email_data):
		if ('@' in email_data) and ('.' in email_data.split('@')[1]) and (1 < len( email_data.split('.')[1] )):
			return True
		else:
			return False


	def __save_file(self, file):
		try:
			new_filename = str(random.getrandbits(32))
			file_ext = '.' + str(file.filename.split('.')[1])
			final_name = Configuration.STORAGE_USER_AVA + new_filename + file_ext
			picture = open(final_name, 'wb')
			picture.write(file.read())
			return True, new_filename + file_ext
		except BaseException as e:
			print('ОШИБКА СОХРАНЕНИЯ АВАТАРА - ' + e)
			return False


	def __del_prev_ava(self):
		try:
			if self.user.avatar == 'anon.jpg':
				pass
			else:
				prev_ava = Configuration.STORAGE_USER_AVA + self.user.avatar
				os.remove(prev_ava)
		except BaseException as e:
			print('ОШИБКА УДАЛЕНИЯ АВАТАРА - ' + e)