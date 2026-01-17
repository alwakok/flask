class CalorieCalculator:
    @staticmethod
    def calculate_bmr(gender, weight, height, age):
        """Рассчитывает базовый метаболизм (BMR)"""
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return round(bmr, 2)

    @staticmethod
    def calculate_tdee(bmr, activity_level='sedentary'):
        """Рассчитывает общий дневной расход энергии (TDEE)"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }

        multiplier = activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 2)

    @staticmethod
    def calculate_target_calories(tdee, goal):
        """Рассчитывает целевое количество калорий в зависимости от цели"""
        if goal == 'loss':
            return round(tdee - 500, 2)
        elif goal == 'gain':
            return round(tdee + 500, 2)
        else:  # maintenance
            return round(tdee, 2)

    @staticmethod
    def calculate_macronutrients(calories, goal, weight):
        """
        Рассчитывает норму БЖУ в граммах
        Формулы:
        - Белки: 1.5-2.2 г/кг для похудения, 1.2-1.8 г/кг для поддержания, 1.8-2.5 г/кг для набора
        - Жиры: 20-35% от калорий (0.8-1 г/кг)
        - Углеводы: остаток калорий
        """
        # Расчет белков
        if goal == 'loss':
            protein_per_kg = 2.0  # г/кг для похудения (сохранение мышц)
        elif goal == 'gain':
            protein_per_kg = 2.2  # г/кг для набора массы
        else:  # maintenance
            protein_per_kg = 1.6  # г/кг для поддержания

        protein_grams = round(weight * protein_per_kg, 1)
        protein_calories = protein_grams * 4  # 1 г белка = 4 ккал

        # Расчет жиров (25% от калорий или 0.9 г/кг, что больше)
        fat_percentage = 0.25
        fat_calories = calories * fat_percentage
        fat_grams_from_percentage = round(fat_calories / 9, 1)  # 1 г жира = 9 ккал

        fat_per_kg = 0.9
        fat_grams_from_weight = round(weight * fat_per_kg, 1)

        # Выбираем большее значение для жиров
        fat_grams = max(fat_grams_from_percentage, fat_grams_from_weight)
        fat_calories = fat_grams * 9

        # Остаток калорий на углеводы
        carb_calories = calories - protein_calories - fat_calories
        carb_grams = round(carb_calories / 4, 1)  # 1 г углеводов = 4 ккал

        # Пересчитываем точные калории после округления
        protein_calories = protein_grams * 4
        fat_calories = fat_grams * 9
        carb_calories = carb_grams * 4
        total_calories_recalc = protein_calories + fat_calories + carb_calories

        # Процентное распределение
        protein_percent = round((protein_calories / total_calories_recalc) * 100, 1)
        fat_percent = round((fat_calories / total_calories_recalc) * 100, 1)
        carb_percent = round((carb_calories / total_calories_recalc) * 100, 1)

        return {
            'protein': {
                'grams': protein_grams,
                'calories': protein_calories,
                'percent': protein_percent
            },
            'fat': {
                'grams': fat_grams,
                'calories': fat_calories,
                'percent': fat_percent
            },
            'carbs': {
                'grams': carb_grams,
                'calories': carb_calories,
                'percent': carb_percent
            },
            'total_calories': total_calories_recalc
        }

    @staticmethod
    def get_macro_recommendations(goal):
        """Рекомендации по БЖУ в зависимости от цели"""
        recommendations = {
            'loss': {
                'protein': '1.8-2.2 г/кг - помогает сохранить мышцы при дефиците калорий',
                'fat': '0.8-1 г/кг (20-30% от калорий) - важны для гормонов',
                'carbs': 'Остаток калорий - снижаем для создания дефицита'
            },
            'maintenance': {
                'protein': '1.2-1.6 г/кг - для поддержания мышечной массы',
                'fat': '0.8-1 г/кг (25-35% от калорий)',
                'carbs': '45-55% от калорий - основной источник энергии'
            },
            'gain': {
                'protein': '1.8-2.5 г/кг - для роста мышц',
                'fat': '0.8-1 г/кг (20-30% от калорий)',
                'carbs': '50-60% от калорий - энергия для тренировок и восстановления'
            }
        }
        return recommendations.get(goal, recommendations['maintenance'])

    @staticmethod
    def save_calculation(gender, age, weight, height, goal, activity, bmr, tdee, target_calories, macros):
        """Сохраняет расчет в базу данных"""
        from database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO calculations 
            (gender, age, weight, height, goal, activity, bmr, tdee, target_calories,
             protein_g, fat_g, carbs_g, protein_percent, fat_percent, carbs_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            gender, age, weight, height, goal, activity, bmr, tdee, target_calories,
            macros['protein']['grams'], macros['fat']['grams'], macros['carbs']['grams'],
            macros['protein']['percent'], macros['fat']['percent'], macros['carbs']['percent']
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_calculation_history():
        """Получает историю расчетов"""
        from database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM calculations 
            ORDER BY timestamp DESC
        ''')

        calculations = cursor.fetchall()
        conn.close()

        return calculations