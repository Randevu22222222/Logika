from flask import Flask, request, jsonify, render_template
import random
import string
from math import sqrt, factorial
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Логирование
import logging

logging.basicConfig(level=logging.INFO)


# Utility Functions

def generate_password(length, use_uppercase, use_digits, use_special):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    if not characters:
        return "Error: No character set selected"

    return ''.join(random.choice(characters) for _ in range(length))


def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def calculate_pi(iterations):
    pi = 0
    for k in range(iterations):
        pi += (1 / (16 ** k)) * (
                (4 / (8 * k + 1)) -
                (2 / (8 * k + 4)) -
                (1 / (8 * k + 5)) -
                (1 / (8 * k + 6))
        )
    return pi


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


# New Functions

def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i - 1] + fib[i - 2])
    return fib


def convert_temperature(value, to_unit):
    if not isinstance(value, (int, float)):
        return "Invalid temperature value"

    if to_unit == "Celsius":
        return (value - 32) * 5.0 / 9.0
    elif to_unit == "Fahrenheit":
        return (value * 9.0 / 5.0) + 32
    else:
        return "Invalid unit"


def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Additional Functions

def calculate_days_between_dates(date1, date2):
    try:
        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")
        return abs((date2 - date1).days)
    except ValueError:
        return "Invalid date format, use YYYY-MM-DD"


def statistics_operations(numbers):
    if not all(isinstance(x, (int, float)) for x in numbers):
        return "Invalid input, all elements must be numbers"

    mean = sum(numbers) / len(numbers)
    minimum = min(numbers)
    maximum = max(numbers)
    return {"mean": mean, "min": minimum, "max": maximum}


# Task Management

tasks = []


def add_task(description):
    task_id = len(tasks) + 1
    tasks.append({"id": task_id, "description": description, "completed": False})
    return task_id


def update_task(task_id, description=None, completed=None):
    for task in tasks:
        if task["id"] == task_id:
            if description is not None:
                task["description"] = description
            if completed is not None:
                task["completed"] = completed
            return task
    return None


def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]


# CSV Report Generation

def generate_csv_report(filename):
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w", newline="") as csvfile:
        fieldnames = ["Task ID", "Description", "Completed"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for task in tasks:
            writer.writerow({
                "Task ID": task["id"],
                "Description": task["description"],
                "Completed": task["completed"]
            })
    return filepath


# Routes

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate-password', methods=['POST'])
def password():
    data = request.json
    length = data.get('length', 12)
    use_uppercase = data.get('uppercase', False)
    use_digits = data.get('digits', False)
    use_special = data.get('special', False)

    password = generate_password(length, use_uppercase, use_digits, use_special)
    logging.info(f"Generated password: {password}")  # Логируем событие
    return jsonify({'password': password})


@app.route('/prime-factors', methods=['POST'])
def factors():
    data = request.json
    number = data.get('number')
    if not isinstance(number, int):
        return jsonify({'error': 'Number must be an integer'}), 400

    factors = prime_factors(number)
    logging.info(f"Prime factors of {number}: {factors}")
    return jsonify({'factors': factors})


@app.route('/calculate-pi', methods=['POST'])
def pi():
    data = request.json
    iterations = data.get('iterations', 1000)

    if not isinstance(iterations, int) or iterations <= 0:
        return jsonify({'error': 'Iterations must be a positive integer'}), 400

    pi_value = calculate_pi(iterations)
    logging.info(f"Calculated Pi with {iterations} iterations: {pi_value}")
    return jsonify({'pi': pi_value})


@app.route('/is-prime', methods=['POST'])
def check_prime():
    data = request.json
    number = data.get('number')

    if not isinstance(number, int):
        return jsonify({'error': 'Number must be an integer'}), 400

    result = is_prime(number)
    logging.info(f"Checked if {number} is prime: {result}")
    return jsonify({'is_prime': result})


@app.route('/fibonacci', methods=['POST'])
def fibonacci_route():
    data = request.json
    n = data.get('n')

    if not isinstance(n, int) or n <= 0:
        return jsonify({'error': 'n must be a positive integer'}), 400

    fib_sequence = fibonacci(n)
    logging.info(f"Fibonacci sequence for n={n}: {fib_sequence}")
    return jsonify({'fibonacci': fib_sequence})


@app.route('/convert-temperature', methods=['POST'])
def convert_temperature_route():
    data = request.json
    value = data.get('value')
    to_unit = data.get('to_unit')

    if not isinstance(value, (int, float)) or not to_unit:
        return jsonify({'error': 'Invalid input parameters'}), 400

    converted_temp = convert_temperature(value, to_unit)
    logging.info(f"Converted {value} to {to_unit}: {converted_temp}")
    return jsonify({'converted_temperature': converted_temp})


@app.route('/random-string', methods=['POST'])
def random_string():
    data = request.json
    length = data.get('length', 8)

    random_str = generate_random_string(length)
    logging.info(f"Generated random string: {random_str}")
    return jsonify({'random_string': random_str})


@app.route('/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def task_management():
    if request.method == 'GET':
        return jsonify(tasks)

    if request.method == 'POST':
        data = request.json
        description = data.get('description')
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        task_id = add_task(description)
        logging.info(f"Added task with ID {task_id}: {description}")
        return jsonify({'message': 'Task added', 'task_id': task_id})

    if request.method == 'PUT':
        data = request.json
        task_id = data.get('id')
        description = data.get('description')
        completed = data.get('completed')

        task = update_task(task_id, description, completed)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        logging.info(f"Updated task ID {task_id}: {task}")
        return jsonify({'message': 'Task updated', 'task': task})

    if request.method == 'DELETE':
        data = request.json
        task_id = data.get('id')
        if not any(task["id"] == task_id for task in tasks):
            return jsonify({'error': 'Task not found'}), 404
        delete_task(task_id)
        logging.info(f"Deleted task ID {task_id}")
        return jsonify({'message': 'Task deleted'})


@app.route('/generate-csv-report', methods=['POST'])
def generate_csv():
    data = request.json
    filename = data.get('filename', 'tasks_report.csv')
    file_path = generate_csv_report(filename)
    logging.info(f"Generated CSV report at {file_path}")
    return jsonify({'message': 'Report generated', 'file_path': file_path})


if __name__ == '__main__':
    app.run(debug=True)
