import glob
import os
from flask import Flask, url_for, render_template, request, redirect

app = Flask(__name__)
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PROFESSIONS = [
    "инженер-исследователь", "пилот", "строитель", "экзобиолог", "врач",
    "инженер по терраформированию", "климатолог", "специалист по радиационной защите",
    "астрогеолог", "гляциолог", "инженер жизнеобеспечения", "метеоролог",
    "оператор марсохода", "киберинженер", "штурман", "пилот дронов"
]

ASTRONAUTS = [
    "Ридли Скотт", "Энди Уир", "Марк Уотни", "Венката Капур", "Тедди Сандерс", "Шон Бин"
]


@app.route('/')
def root():
    return redirect('/index/Заготовка')


@app.route('/index/<title>')
def index_with_title(title):
    return render_template('base.html', title=title)


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


@app.route('/login')
def login_form():
    return render_template('login.html', title='Аварийный доступ')


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


# Старые маршруты, из предыдущего урока

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

    app.run(port=8080, host='127.0.0.1', debug=True)
