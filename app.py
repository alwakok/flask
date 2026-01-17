from flask import Flask, render_template, request, redirect, url_for
from database import init_db
from models import CalorieCalculator

app = Flask(__name__)

# Инициализация базы данных
init_db()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        gender = request.form.get('gender')
        age = int(request.form.get('age'))
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        activity = request.form.get('activity', 'sedentary')
        goal = request.form.get('goal', 'maintenance')

        # Основные расчеты
        bmr = CalorieCalculator.calculate_bmr(gender, weight, height, age)
        tdee = CalorieCalculator.calculate_tdee(bmr, activity)
        target_calories = CalorieCalculator.calculate_target_calories(tdee, goal)

        # Расчет БЖУ
        macros = CalorieCalculator.calculate_macronutrients(target_calories, goal, weight)
        recommendations = CalorieCalculator.get_macro_recommendations(goal)

        # Сохранение в базу данных
        CalorieCalculator.save_calculation(
            gender, age, weight, height, goal, activity,
            bmr, tdee, target_calories, macros
        )

        # Определение названий
        goal_names = {
            'loss': 'Похудение',
            'maintenance': 'Поддержание веса',
            'gain': 'Набор массы'
        }

        activity_names = {
            'sedentary': 'Сидячий образ жизни',
            'light': 'Легкая активность',
            'moderate': 'Умеренная активность',
            'active': 'Высокая активность',
            'very_active': 'Очень высокая активность'
        }

        return render_template('calculate.html',
                               gender=gender,
                               age=age,
                               weight=weight,
                               height=height,
                               activity=activity_names.get(activity),
                               activity_key=activity,
                               goal=goal_names.get(goal),
                               goal_key=goal,
                               bmr=bmr,
                               tdee=tdee,
                               target_calories=target_calories,
                               macros=macros,
                               recommendations=recommendations)

    return render_template('calculate.html')


@app.route('/history')
def history():
    calculations = CalorieCalculator.get_calculation_history()
    return render_template('history.html', calculations=calculations)


if __name__ == '__main__':
    app.run(debug=True)