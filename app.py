from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db
from models import CalorieCalculator, User

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'

init_db()

@app.context_processor
def inject_user():
    user = None
    if 'user' in session:
        user = session['user']
    return dict(user=user)


def auth_required_for_history(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Для просмотра истории расчетов необходимо войти в систему', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if not username or not password:
            flash('Имя пользователя и пароль обязательны', 'danger')
            return redirect(url_for('register'))

        user_id = User.register(username, password, email)
        if user_id:
            flash('Регистрация успешна! Теперь войдите в систему.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Имя пользователя уже занято', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.login(username, password)
        if user:
            session['user'] = user
            session['session_token'] = user['session_token']
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'session_token' in session:
        User.logout(session['session_token'])
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@auth_required_for_history
def dashboard():
    user = session['user']
    calculations = CalorieCalculator.get_user_calculations(user['id'])
    return render_template('dashboard.html', calculations=calculations)


@app.route('/calculate', methods=['GET', 'POST'])
def calculate():

    if request.method == 'POST':
        try:
            gender = request.form.get('gender')
            age = int(request.form.get('age'))
            weight = float(request.form.get('weight'))
            height = float(request.form.get('height'))
            activity = request.form.get('activity', 'sedentary')
            goal = request.form.get('goal', 'maintenance')

            if not gender:
                flash('Пожалуйста, укажите пол', 'danger')
                return redirect(url_for('calculate'))

            bmr = CalorieCalculator.calculate_bmr(gender, weight, height, age)
            tdee = CalorieCalculator.calculate_tdee(bmr, activity)
            target_calories = CalorieCalculator.calculate_target_calories(tdee, goal)

            macros = CalorieCalculator.calculate_macronutrients(target_calories, goal, weight)
            recommendations = CalorieCalculator.get_macro_recommendations(goal)

            user = session.get('user')
            if user:
                CalorieCalculator.save_calculation(
                    user['id'], gender, age, weight, height, goal, activity,
                    bmr, tdee, target_calories, macros
                )
                flash('Расчет сохранен в вашей истории', 'success')
            else:
                flash('Расчет не сохранен. Для сохранения истории войдите в систему', 'info')

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

        except ValueError as e:
            flash(f'Ошибка в данных: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Ошибка сервера: {str(e)}', 'danger')

    return render_template('calculate.html')


@app.route('/history')
@auth_required_for_history
def history():
    user = session['user']
    calculations = CalorieCalculator.get_user_calculations(user['id'])
    return render_template('history.html', calculations=calculations)


@app.route('/delete_calculation/<int:calculation_id>', methods=['POST'])
@auth_required_for_history
def delete_calculation(calculation_id):
    user = session['user']
    success = CalorieCalculator.delete_calculation(user['id'], calculation_id)

    if success:
        flash('Расчет успешно удален', 'success')
    else:
        flash('Не удалось удалить расчет', 'danger')

    return redirect(url_for('history'))


# Обработчик ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)