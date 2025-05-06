import glob
import json
import os
import random
from sqlalchemy import orm
from api import jobs_api
from api import users_api
from forms.department_form import DepartmentForm
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.job_form import JobForm
from models.departments import Department
from models.users import User
from models.jobs import Jobs
from models.category import Category
from database import db_session
from flask import Flask, url_for, render_template, request, redirect, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(jobs_api.blueprint)
app.register_blueprint(users_api.blueprint)

login_manager = LoginManager()
login_manager.init_app(app)

PROFESSIONS = [
    "инженер-исследователь", "пилот", "строитель", "экзобиолог", "врач",
    "инженер по терраформированию", "климатолог", "специалист по радиационной защите",
    "астрогеолог", "гляциолог", "инженер жизнеобеспечения", "метеоролог",
    "оператор марсохода", "киберинженер", "штурман", "пилот дронов"
]

ASTRONAUTS = [
    "Ридли Скотт", "Энди Уир", "Марк Уотни", "Венката Капур", "Тедди Сандерс", "Шон Бин"
]


@app.route("/")
def works_log():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template("works_log.html", jobs=jobs, title="Works log")


@app.route('/index/<title>')
def index_with_title(title):
    return render_template('base.html', title=title)


@login_manager.user_loader
def load_user(user_id):
    return db_session.create_session().query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            print(f"Пользователь {user.email} успешно вошел.")
            return redirect("/")
        else:
            print(f"Неудачная попытка входа для email: {form.email.data}")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form,
                                   title='Авторизация')

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        print(f"Новый пользователь зарегистрирован: {user.email}")
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    print(f"Пользователь {current_user.email} выходит.")
    logout_user()
    return redirect("/")


@app.route('/departments')
def departments_list():
    """Отображение списка департаментов"""
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).options(orm.joinedload(Department.chief_user)).all()
    return render_template("departments_list.html",
                           departments=departments,
                           title="List of Departments")


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    """Обработчик добавления департамента"""
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if not db_sess.query(User).get(form.chief.data):
            return render_template('add_department.html', title='Adding Department',
                                   form=form, message="Руководитель с таким ID не найден")
        if db_sess.query(Department).filter(Department.email == form.email.data).first():
            return render_template('add_department.html', title='Adding Department',
                                   form=form, message="Департамент с таким email уже существует")

        department = Department(
            title=form.title.data,
            chief=form.chief.data,
            members=form.members.data,
            email=form.email.data
        )
        db_sess.add(department)
        db_sess.commit()
        print(f"Добавлен новый департамент: '{department.title}'")
        return redirect('/departments')
    return render_template('add_department.html', title='Adding Department', form=form)


@app.route('/edit_department/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    """Обработчик редактирования департамента"""
    form = DepartmentForm()
    db_sess = db_session.create_session()

    department = db_sess.query(Department).filter(Department.id == dept_id).first()

    if not department:
        abort(404)

    if not (current_user.id == department.chief or current_user.id == 1):
        print(f"Попытка редактирования департамента {dept_id} пользователем {current_user.id} без прав.")
        abort(403)  # Запрещено

    if request.method == "GET":
        form.title.data = department.title
        form.chief.data = department.chief
        form.members.data = department.members
        form.email.data = department.email
    elif form.validate_on_submit():
        if department.chief != form.chief.data and not db_sess.query(User).get(form.chief.data):
            return render_template('add_department.html', title='Editing Department',
                                   form=form, message="Руководитель с таким ID не найден")
        existing_dept_with_email = db_sess.query(Department).filter(Department.email == form.email.data,
                                                                    Department.id != dept_id).first()
        if existing_dept_with_email:
            return render_template('add_department.html', title='Editing Department',
                                   form=form, message="Департамент с таким email уже существует")

        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        db_sess.commit()
        print(f"Департамент {dept_id} успешно отредактирован пользователем {current_user.id}")
        return redirect('/departments')

    return render_template('add_department.html', title='Editing Department', form=form)


@app.route('/delete_department/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def delete_department(dept_id):
    """Обработчик удаления департамента"""
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == dept_id).first()
    if not department:
        abort(404)
    if current_user.id == department.chief or current_user.id == 1:
        db_sess.delete(department)
        db_sess.commit()
        print(f"Департамент {dept_id} успешно удален пользователем {current_user.id}")
    else:
        print(f"Попытка удаления департамента {dept_id} пользователем {current_user.id} без прав.")
        abort(403)

    return redirect('/departments')


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        job.team_leader = current_user.id

        job.categories.clear()
        category_ids_str = form.category_ids.data.split(',')
        for cat_id_str in category_ids_str:
            try:
                cat_id = int(cat_id_str.strip())
                category = db_sess.query(Category).get(cat_id)
                if category:
                    job.categories.append(category)
                else:
                    print(f"Предупреждение: Категория с ID {cat_id} не найдена.")
            except ValueError:
                if cat_id_str.strip():
                    print(f"Предупреждение: Неверный ID категории '{cat_id_str.strip()}'.")

        db_sess.add(job)
        db_sess.commit()
        print(
            f"Добавлена новая работа: '{job.job}' от пользователя ID "
            f"{current_user.id} с категориями ID: {form.category_ids.data}")
        return redirect('/')

    return render_template('add_job.html', title='Добавление работы', form=form)


@app.route('/editjob/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    form = JobForm()
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).options(
        orm.subqueryload(Jobs.categories)).first()

    if not job:
        abort(404)

    if not (current_user.id == job.team_leader or current_user.id == 1):
        print(f"Попытка редактирования работы {job_id} пользователем {current_user.id} без прав.")
        abort(403)

    if request.method == "GET":
        form.job.data = job.job
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished
        form.category_ids.data = ", ".join(str(cat.id) for cat in job.categories)

    elif form.validate_on_submit():
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data

        job.categories.clear()
        category_ids_str = form.category_ids.data.split(',')
        for cat_id_str in category_ids_str:
            try:
                cat_id = int(cat_id_str.strip())
                category = db_sess.query(Category).get(cat_id)
                if category:
                    if category not in job.categories:
                        job.categories.append(category)
                else:
                    print(f"Предупреждение: Категория с ID {cat_id} не найдена при редактировании.")
            except ValueError:
                if cat_id_str.strip():
                    print(f"Предупреждение: Неверный ID категории "
                          f"'{cat_id_str.strip()}' при редактировании.")

        db_sess.commit()
        print(
            f"Работа {job_id} успешно отредактирована пользователем "
            f"{current_user.id} с категориями ID: {form.category_ids.data}")
        return redirect('/')

    return render_template('add_job.html', title='Редактирование работы', form=form)


@app.route('/deletejob/<int:job_id>',
           methods=['GET', 'POST'])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()

    if job:
        if current_user.id == job.team_leader or current_user.id == 1:
            db_sess.delete(job)
            db_sess.commit()
            print(f"Работа {job_id} успешно удалена пользователем {current_user.id}")
        else:
            print(f"Попытка удаления работы {job_id} пользователем {current_user.id} без прав.")
            abort(403)
    else:
        abort(404)

    return redirect('/')


# Старые маршруты, из предыдущего урока

@app.route('/training/<prof>')
def training(prof):
    profession = prof.lower()
    title = f"Тренировка {prof}"

    if 'инженер' in profession or 'строитель' in profession:
        h2_title = "Инженерные тренажеры"
        image_filename = "engineering_ship.png"
    else:
        h2_title = "Научные симуляторы"
        image_filename = "science_lab.png"

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    if not os.path.exists(image_path):
        print(f"Предупреждение: Файл изображения '{image_filename}' не найден.")

    return render_template(
        'training.html',
        title=title,
        h2_title=h2_title,
        image_filename=image_filename
    )


@app.route('/list_prof/<list_type>')
def list_professions(list_type):
    if list_type not in ['ol', 'ul']:
        list_type = 'invalid'

    return render_template(
        'list_prof.html',
        title='Список профессий',
        professions=PROFESSIONS,
        list_type=list_type
    )


@app.route('/answer')
@app.route('/auto_answer')
def show_answer():
    user_data = {
        "title": "Анкета",
        "surname": "Watny",
        "name": "Mark",
        "education": "выше среднего",
        "profession": "штурман марсохода",
        "sex": "male",
        "motivation": "Всегда мечтал застрять на Марсе!",
        "ready": "True"
    }
    return render_template('auto_answer.html', **user_data)


@app.route('/distribution')
def distribution():
    return render_template(
        'distribution.html',
        title='Размещение',
        astronauts=ASTRONAUTS
    )


@app.route('/table_param/<sex>/<int:age>')
def table_param(sex, age):
    sex_lower = sex.lower()

    if sex_lower == 'female':
        if age < 21:
            wall_color = '#ff9966'
            alien_image = 'alien_female.jpg'
        else:
            wall_color = '#ff6633'
            alien_image = 'alien_male.jpg'
    elif sex_lower == 'male':
        if age < 21:
            wall_color = '#99ccff'
            alien_image = 'alien_male.jpg'
        else:
            wall_color = '#3399ff'
            alien_image = 'alien_female.jpg'
    else:
        wall_color = '#cccccc'
        alien_image = None

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], alien_image)
    if not os.path.exists(image_path):
        print(f"Предупреждение: Файл изображения '{alien_image}' не найден.")
        alien_image = None

    return render_template(
        'table_param.html',
        title='Оформление каюты',
        wall_color=wall_color,
        alien_image_filename=alien_image
    )


@app.route('/galery', methods=['POST', 'GET'])
def galery():
    if request.method == 'POST':
        if 'galery_file' not in request.files:
            print('Нет файла в запросе')
            return redirect(request.url)

        file = request.files['galery_file']
        if file.filename == '':
            print('Файл не выбран')
            return redirect(request.url)

        if file:
            existing_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'galery_*.jpg')) \
                             + glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'galery_*.png')) \
                             + glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], 'galery_*.jpeg'))

            new_index = len(existing_files) + 1
            ext = os.path.splitext(file.filename)[1].lower()

            filename = f"galery_{new_index}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                print(f'Файл сохранен как {filepath}')
            except Exception as e:
                print(f"Ошибка при сохранении файла: {e}")
            return redirect(url_for('galery'))

    image_files = []
    patterns = ['*.jpg', '*.png', '*.jpeg', '*.gif']
    for pattern in patterns:
        full_paths = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], pattern))
        image_files.extend([os.path.basename(f) for f in full_paths])
    gallery_images = sorted(image_files)

    print(f"Найдены изображения для галереи: {gallery_images}")

    return render_template('galery.html', title='Красная планета', images=gallery_images)


@app.route('/member')
def show_random_member():
    try:
        json_file_path = os.path.join('templates', 'crew.json')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            crew_data = json.load(f)

        if not crew_data:
            print("Ошибка: Список экипажа в crew.json пуст.")
            selected_member = None
        else:
            selected_member = random.choice(crew_data)
            if 'specialties' in selected_member and isinstance(selected_member['specialties'], list):
                selected_member['specialties'] = sorted(selected_member['specialties'])
            else:
                selected_member['specialties'] = []

    except FileNotFoundError:
        print("Ошибка: Файл 'templates/crew.json' не найден.")
        selected_member = None
    except json.JSONDecodeError:
        print("Ошибка: Не удалось декодировать JSON из файла 'templates/crew.json'.")
        selected_member = None
    except Exception as e:
        print(f"Непредвиденная ошибка при обработке данных экипажа: {e}")
        selected_member = None

    return render_template(
        'member.html',
        title='Случайный член экипажа',
        member=selected_member
    )


@app.route('/promotion_image')
def promotion_image():
    promotion_lines = [
        "Человечество вырастает из детства.",
        "Человечеству мала одна планета.",
        "Мы сделаем обитаемыми безжизненные пока планеты.",
        "И начнем с Марса!",
        "Присоединяйся!"
    ]
    return render_template(
        'promotion_image.html',
        title='Колонизация',
        promotion_lines=promotion_lines
    )


@app.route('/astronaut_selection')
def astronaut_form():
    return render_template('astronaut_form.html', title='Отбор астронавтов')


@app.route('/choice/<planet_name>')
def choice_planet(planet_name):
    reasons = [
        f"Эта планета близка к Земле;",
        "На ней много необходимых ресурсов;",
        "На ней есть вода и атмосфера;",
        "На ней есть небольшое магнитное поле;",
        "Наконец, она просто красива!"
    ]
    return render_template(
        'choice.html',
        title='Варианты выбора',
        planet_name=planet_name,
        reasons=reasons
    )


@app.route('/results/<nickname>/<int:level>/<float:rating>')
def show_results(nickname, level, rating):
    return render_template(
        'results.html',
        title='Результаты',
        nickname=nickname,
        level=level,
        rating=rating
    )


@app.route('/load_photo', methods=['POST', 'GET'])
def load_photo():
    image_url = None
    if request.method == 'POST':
        if 'photo_file' not in request.files:
            print('Нет файла в запросе')
            return render_template('load_photo.html', title='Отбор астронавтов', image_url=None)
        file = request.files['photo_file']
        if file.filename == '':
            print('Файл не выбран')
            return render_template('load_photo.html', title='Отбор астронавтов', image_url=None)
        if file:
            filename = 'uploaded_photo.jpg'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                print(f'Файл сохранен как {filepath}')
                image_url = url_for('static', filename=f'img/{filename}')
            except Exception as e:
                print(f"Ошибка при сохранении файла: {e}")
                return render_template('load_photo.html', title='Отбор астронавтов', image_url=None,
                                       error="Ошибка сохранения файла")

    return render_template('load_photo.html', title='Отбор астронавтов', image_url=image_url)


@app.route('/carousel')
def carousel():
    image_files = [
        'mars1.jpg',
        'mars2.jpg',
        'mars3.jpg',
        'mars4.jpg',
        'mars5.jpg',
        'mars6.jpg'
    ]
    existing_images = []
    for filename in image_files:
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            existing_images.append(filename)
        else:
            print(f"Предупреждение: Файл {filename} не найден в {app.config['UPLOAD_FOLDER']}")

    return render_template('carousel.html', title='Пейзажи Обои 4K без СМС и регистрации', images=existing_images)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Создана папка {UPLOAD_FOLDER}")

    css_folder = os.path.join('static', 'css')
    if not os.path.exists(css_folder):
        os.makedirs(css_folder)
        print(f"Создана папка {css_folder}")

    css_file = os.path.join(css_folder, 'style.css')
    if not os.path.exists(css_file):
        with open(css_file, 'w') as f:
            pass
        print(f"Создан файл {css_file}")

    db_session.global_init("database/mars_explorer.db")

    app.run(port=8080, host='127.0.0.1', debug=True)
