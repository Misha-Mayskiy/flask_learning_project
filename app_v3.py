from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def mission_name():
    return "Миссия Колонизация Марса"


@app.route('/index')
def mission_motto():
    return "И на Марсе будут яблони цвести!"


@app.route('/promotion')
def promotion_page():
    promotion_lines = [
        "Человечество вырастает из детства.",
        "Человечеству мала одна планета.",
        "Мы сделаем обитаемыми безжизненные пока планеты.",
        "И начнем с Марса!",
        "Присоединяйся!"
    ]
    return "<br>".join(promotion_lines)


@app.route('/image_mars')
def image_mars_page():
    """Отображает страницу с картинкой Марса, используя шаблон."""
    return render_template(
        'image_mars.html',
        title='Привет, Марс!',
        h1_text='Жди нас, Марс!',
        paragraph_text='Вот она какая, красная планета.'
    )


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
