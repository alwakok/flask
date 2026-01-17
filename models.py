class CalorieCalculator:
    @staticmethod
    def calculate_bmr(gender, weight, height, age):
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return round(bmr, 2)

    @staticmethod
    def calculate_tdee(bmr, activity_level='sedentary'):
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
        if goal == 'loss':
            return round(tdee - 500, 2)
        elif goal == 'gain':
            return round(tdee + 500, 2)
        else: 
            return round(tdee, 2)

    @staticmethod
    def calculate_macronutrients(calories, goal, weight):

        if goal == 'loss':
            protein_per_kg = 2.0  
        elif goal == 'gain':
            protein_per_kg = 2.2  
        else:  
            protein_per_kg = 1.6 

        protein_grams = round(weight * protein_per_kg, 1)
        protein_calories = protein_grams * 4

        fat_percentage = 0.25
        fat_calories = calories * fat_percentage
        fat_grams_from_percentage = round(fat_calories / 9, 1) 

        fat_per_kg = 0.9
        fat_grams_from_weight = round(weight * fat_per_kg, 1)

        fat_grams = max(fat_grams_from_percentage, fat_grams_from_weight)
        fat_calories = fat_grams * 9

        carb_calories = calories - protein_calories - fat_calories
        carb_grams = round(carb_calories / 4, 1)

        protein_calories = protein_grams * 4
        fat_calories = fat_grams * 9
        carb_calories = carb_grams * 4
        total_calories_recalc = protein_calories + fat_calories + carb_calories

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
