import os
from flask import Flask, url_for, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def mission_name():
    return "Миссия Колонизация Марса"


@app.route('/index')
def mission_motto():
    return "И на Марсе будут яблони цвести!"


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
                return render_template('load_photo.html', title='Отбор астронавтов', image_url=None, error="Ошибка сохранения файла")

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
        # Добавьте сюда имена других файлов из static/img
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
    app.run(port=8080, host='127.0.0.1', debug=True)