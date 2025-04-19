from flask import Flask, render_template

app = Flask(__name__)


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
    # Example: http://127.0.0.1:8080/results/Scott/1/75.1
    return render_template(
        'results.html',
        title='Результаты',
        nickname=nickname,
        level=level,
        rating=rating
    )


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
