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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
