from peewee import *
from models.task import Task
from playhouse.shortcuts import model_to_dict
from math import ceil
from services.task_activity_service import getTaskActivity, bindTaskWithUser

def createTask(subject, topic, difficulty, description, hint, answer, explanation):
    return Task.create(subject = subject, topic = topic, difficulty = difficulty, description = description, hint = hint, answer = answer, explanation = explanation)
    

def deleteTask(taskId):
    task: Task = Task.get(taskId)
    task.delete_instance()

def editTask(taskId, taskDescription, taskSubject, taskDifficulty, taskHint, taskAnswer, taskExplanation, taskTopic):
    task: Task = Task.get(taskId)
    task.description = taskDescription
    task.subject = taskSubject
    task.difficulty = taskDifficulty
    task.hint = taskHint
    task.answer = taskAnswer
    task.explanation = taskExplanation
    task.topic = taskTopic
    task.save()


def getTasks(page, selectedTopics, selectedDifficulties, userId=None) -> list[map]:
    tasks = []
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    query = Task.select().where(*filters).paginate(page, 10) if len(filters) > 0 else Task.select().paginate(page, 10)
    for task in query:
        d = model_to_dict(task)
        if userId:
            taskActivity = getTaskActivity(task.id, userId)
            if taskActivity != None:
                if taskActivity.status == "correct":
                    d["status"] = "Решено правильно"
                else:
                    d["status"] = "Решено неправильно"
            else:
                d["status"] = "Не решено"
        else:
            d["status"] = "Не решено"
        tasks.append(d)
    return tasks


def getTopics():
    subjects = Task.select(Task.subject).distinct().scalars()
    data = {}
    for subject in subjects:
        data[subject] = list(Task.select(Task.topic).where(Task.subject == subject).distinct().scalars())
    return data


def countTasksPages(selectedTopics, selectedDifficulties):
    filters = []
    if selectedTopics and len(selectedTopics) > 0:
        filters.append(Task.topic << selectedTopics)
    if selectedDifficulties and len(selectedDifficulties) > 0:
        filters.append(Task.difficulty << selectedDifficulties)
    return ceil(len(Task.select().where(*filters)) if len(filters) > 0 else len(Task.select()) / 10)



if not Task.table_exists():
    Task.create_table()
    print("Table 'Task' created")
    createTask(
        subject = "Математика",
        topic = "Теория чисел",
        difficulty = "Средний",
        description = "Сколько нулей стоит в конце десятичной записи числа 100! (факториал 100)?",
        hint = "Количество нулей определяется количеством пар множителей 2 и 5 в разложении числа. Пятерок всегда меньше, чем двоек.",
        answer = "24",
        explanation = "Нули образуются при умножении 2 на 5. В разложении 100! двоек заведомо больше, чем пятерок, поэтому считаем количество множителей 5. Целая часть [100/5] = 20, плюс целая часть [100/25] = 4. Итого 20 + 4 = 24."
    )
    createTask(
        subject = "Физика",
        topic = "Кинематика",
        difficulty = "Простой",
        description = "Автомобиль проехал первую половину пути со скоростью 40 км/ч, а вторую — со скоростью 60 км/ч. Какова средняя скорость (в км/ч) на всем пути?",
        hint = "Средняя скорость — это весь путь, деленный на все время. Не используйте среднее арифметическое.",
        answer = "48",
        explanation = "Пусть половина пути S. Время t1 = S/40, t2 = S/60. Общее время t = S(1/40 + 1/60) = S(5/120) = S/24. Весь путь 2S. Vср = 2S / (S/24) = 48 км/ч."
    )
    createTask(
        subject = "Информатика",
        topic = "Системы счисления",
        difficulty = "Простой",
        description = "Чему равно значение шестнадцатеричного числа 1A в десятичной системе счисления?",
        hint = "В 16-ричной системе A = 10. Формула перевода: 1*16^1 + A*16^0.",
        answer = "26",
        explanation = "Число 1A(16) расписывается как 1 * 16^1 + 10 * 16^0 = 16 + 10 = 26."
    )
    createTask(
        subject = "Математика",
        topic = "Комбинаторика",
        difficulty = "Средний",
        description = "В турнире участвуют 10 шахматистов. Каждый сыграл с каждым по одной партии. Сколько всего партий было сыграно?",
        hint = "Каждая партия объединяет двух игроков. Порядок выбора не важен (сочетания из 10 по 2).",
        answer = "45",
        explanation = "Число сочетаний из 10 по 2 вычисляется по формуле: n*(n-1)/2. 10 * 9 / 2 = 90 / 2 = 45."
    )
    createTask(
        subject = "Химия",
        topic = "Строение вещества",
        difficulty = "Простой",
        description = "Сколько всего атомов содержится в одной молекуле глюкозы (C6H12O6)?",
        hint = "Сложите индексы всех элементов в формуле.",
        answer = "24",
        explanation = "Формула глюкозы C6H12O6. Сумма атомов: 6 (углерод) + 12 (водород) + 6 (кислород) = 24."
    )
    createTask(
        subject = "Физика",
        topic = "Электричество",
        difficulty = "Средний",
        description = "Два резистора сопротивлением 3 Ом и 6 Ом соединены параллельно. Чему равно их общее сопротивление (в Ом)?",
        hint = "При параллельном соединении складываются проводимости: 1/R = 1/R1 + 1/R2.",
        answer = "2",
        explanation = "Формула общего сопротивления для двух параллельных резисторов: R = (R1 * R2) / (R1 + R2). R = (3 * 6) / (3 + 6) = 18 / 9 = 2 Ом."
    )
    createTask(
        subject = "Математика",
        topic = "Алгебра",
        difficulty = "Сложный",
        description = "Известно, что x + 1/x = 3. Найдите значение выражения x^2 + 1/x^2.",
        hint = "Возведите исходное равенство в квадрат.",
        answer = "7",
        explanation = "Возведем (x + 1/x) в квадрат: x^2 + 2*x*(1/x) + 1/x^2 = 3^2. Получаем x^2 + 2 + 1/x^2 = 9. Отсюда x^2 + 1/x^2 = 9 - 2 = 7."
    )
    createTask(
        subject = "Информатика",
        topic = "Алгоритмы",
        difficulty = "Средний",
        description = "Какое максимальное количество шагов потребуется бинарному поиску, чтобы найти элемент в отсортированном массиве из 1000 элементов?",
        hint = "Количество шагов равно логарифму от N по основанию 2, округленному вверх.",
        answer = "10",
        explanation = "2 в 10 степени равно 1024, что покрывает массив из 1000 элементов. Значит, достаточно 10 сравнений."
    )
    createTask(
        subject = "Биология",
        topic = "Цитология",
        difficulty = "Простой",
        description = "Сколько хромосом содержится в нормальной половой клетке (гамете) человека?",
        hint = "Половые клетки содержат гаплоидный (одинарный) набор хромосом, в отличие от диплоидного набора соматических клеток (46).",
        answer = "23",
        explanation = "Соматические клетки человека содержат 46 хромосом (23 пары). Половые клетки образуются в результате мейоза и содержат половину набора, то есть 23 хромосомы."
    )
    createTask(
        subject = "Математика",
        topic = "Геометрия",
        difficulty = "Средний",
        description = "В прямоугольном треугольнике гипотенуза равна 13, а один из катетов равен 5. Чему равна площадь этого треугольника?",
        hint = "Сначала найдите второй катет по теореме Пифагора, затем площадь как половину произведения катетов.",
        answer = "30",
        explanation = "Второй катет b = sqrt(13^2 - 5^2) = sqrt(169 - 25) = sqrt(144) = 12. Площадь S = (a * b) / 2 = (5 * 12) / 2 = 30."
    )
    createTask(
        subject = "Физика",
        topic = "Динамика",
        difficulty = "Простой",
        description = "Какую силу (в Ньютонах) нужно приложить к телу массой 2 кг, чтобы оно двигалось с ускорением 5 м/с²?",
        hint = "Используйте второй закон Ньютона: F = ma.",
        answer = "10",
        explanation = "Согласно второму закону Ньютона F = m * a. F = 2 кг * 5 м/с² = 10 Н."
    )
    createTask(
        subject = "Информатика",
        topic = "Кодирование информации",
        difficulty = "Простой",
        description = "Сколько различных символов можно закодировать, используя 8 бит?",
        hint = "Количество комбинаций равно 2 в степени количества бит.",
        answer = "256",
        explanation = "1 байт = 8 бит. Количество возможных состояний вычисляется как 2^8 = 256."
    )
    createTask(
        subject = "Математика",
        topic = "Последовательности",
        difficulty = "Средний",
        description = "Найдите 10-й член последовательности Фибоначчи, если первые два члена равны 1 и 1 (1, 1, 2, 3...).",
        hint = "Каждое следующее число равно сумме двух предыдущих.",
        answer = "55",
        explanation = "Ряд: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55. Десятый элемент равен 55."
    )
    createTask(
        subject = "Химия",
        topic = "Молярная масса",
        difficulty = "Простой",
        description = "Чему равна молярная масса серной кислоты (H2SO4) в г/моль? (Атомные массы: H=1, S=32, O=16).",
        hint = "Сложите атомные массы всех элементов с учетом их индексов.",
        answer = "98",
        explanation = "M(H2SO4) = 2*1 + 32 + 4*16 = 2 + 32 + 64 = 98 г/моль."
    )
    createTask(
        subject = "Математика",
        topic = "Логика",
        difficulty = "Средний",
        description = "В ящике лежат 10 черных и 10 белых носков. Какое минимальное количество носков нужно достать не глядя, чтобы гарантированно получить пару одного цвета?",
        hint = "Используйте принцип Дирихле. Цветов всего два.",
        answer = "3",
        explanation = "В худшем случае мы достанем один черный и один белый носок (2 шт). Третий носок обязательно совпадет по цвету с одним из уже вытянутых."
    )