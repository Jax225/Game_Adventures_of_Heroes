# app.py
from main import main, game, Character, Human, download, item_database
from flask import Flask, render_template, jsonify, request
import threading
import io
import sys
import queue

app = Flask(__name__)

game_output = io.StringIO()
command_queue = queue.Queue()

def run_game():
    sys.stdout = game_output  # Перенаправляем stdout

    # Заглушка для main, чтобы использовать очередь для ввода
    def custom_input(prompt=''):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        return command_queue.get()  # Получаем команду из очереди

    # Подменяем стандартный input на custom_input
    original_input = __builtins__.input
    __builtins__.input = custom_input

    try:
        main()  # ваша функция main из main.py
    finally:
        __builtins__.input = original_input  # Восстанавливаем input
        sys.stdout = sys.__stdout__  # Восстанавливаем stdout

@app.route("/game_output")
def get_game_output():
    return jsonify(game_output=game_output.getvalue())

@app.route("/send_command", methods=["POST"])
def send_command():
    command = request.json.get('command')
    command_queue.put(command)  # Добавляем команду в очередь
    return '', 204

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    threading.Thread(target=run_game, daemon=True).start()
    app.run(debug=True)
