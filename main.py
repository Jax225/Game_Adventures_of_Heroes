#main.py
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.box import ROUNDED
from copy import deepcopy
from datetime import datetime
import random
import json
import os
import sys
import time
try:
    import msvcrt  # Для Windows
except ImportError:
    import select  # Для Unix-систем
# импорты из соседних файлов
# main.py
from game.character import Character, Human, Warrior, Mage, Mob
from game.items import Item, Equipment, StackableItem
from game.quests import Quest
from game.quests import quest_database
from game.locations import Location, location_database

# константы
MAX_INVENTORY_SIZE = 999999999 # инвентарь - пока бесконечность
TURN_TIME = 3  # Время на ход в секундах

#Разметка цветом
console = Console()
# Настраиваемая Панель действий
class ActionBindingsManager:
    def __init__(self, config_path="save\\action_bindings.json"):
        self.config_path = config_path
        self.bindings = {
            "1": "attack",
            "2": "escape",
            "3": "heal",
            "4": "strong_attack",
            "5": None,
            "6": None,
            "7": None,
            "8": None,
            "9": None,
            "0": None
        }
        self.available_actions = [
            "attack",
            "escape",
            "heal",
            "strong_attack"
        ]
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bindings.update(data.get("bindings", {}))
                    self.available_actions = data.get("available_actions", self.available_actions)
        except Exception as e:
            print(f"Error loading action bindings: {e}")

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "bindings": self.bindings,
                    "available_actions": self.available_actions
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving action bindings: {e}")

    def get_action(self, key):
        return self.bindings.get(key)

    def set_binding(self, key, action):
        if key in self.bindings and action in self.available_actions:
            self.bindings[key] = action
            return True
        return False

    def get_available_actions(self):
        return self.available_actions

    def add_new_action(self, action_name):
        if action_name not in self.available_actions:
            self.available_actions.append(action_name)
            return True
        return False
action_manager = ActionBindingsManager() #Инициализация в начале игры


def configure_action_panel(action_manager):
    """Меню настройки панели действий"""
    while True:
        clear_screen()

        # Показываем текущие настройки
        bindings_text = Text()
        bindings_text.append("Текущие настройки панели действий:\n", style="bold underline")

        for key in sorted(action_manager.bindings.keys()):
            action = action_manager.bindings[key]
            bindings_text.append(f"{key}: {action if action else 'Не назначено'}\n")

        console.print(Panel(bindings_text, title="Настройки панели действий", border_style="blue"))

        # Показываем доступные действия
        actions_text = Text()
        actions_text.append("Доступные действия:\n", style="bold underline")
        for i, action in enumerate(action_manager.get_available_actions(), 1):
            actions_text.append(f"{i}. {action}\n")

        console.print(Panel(actions_text, title="Доступные действия", border_style="green"))

        # Меню управления
        menu_text = Text()
        menu_text.append("Команды:\n", style="bold underline")
        menu_text.append("[Н] - Назначить действие на клавишу\n")
        menu_text.append("[С] - Сбросить настройки по умолчанию\n")
        menu_text.append("[В] - Выйти из настроек\n")
        console.print(Panel(menu_text, title="Управление", border_style="yellow"))

        choice = input("Выберите действие: ").strip().lower()

        if choice in ["н", "назначить"]:
            key = input("Введите цифру (1-9, 0) для настройки: ").strip()
            if key not in action_manager.bindings:
                console.print("[red]Неверная клавиша![/red]")
                input("Нажмите Enter чтобы продолжить...")
                continue

            action_num = input("Введите номер действия для назначения: ").strip()
            try:
                action_num = int(action_num)
                if 1 <= action_num <= len(action_manager.available_actions):
                    action = action_manager.available_actions[action_num - 1]
                    action_manager.set_binding(key, action)
                    action_manager.save_config()
                    console.print(f"[green]Действие '{action}' назначено на клавишу '{key}'[/green]")
                else:
                    console.print("[red]Неверный номер действия![/red]")
            except ValueError:
                console.print("[red]Введите число![/red]")

            input("Нажмите Enter чтобы продолжить...")

        elif choice in ["с", "сбросить"]:
            action_manager.bindings = {
                "1": "attack",
                "2": "escape",
                "3": "heal",
                "4": "strong_attack",
                "5": None,
                "6": None,
                "7": None,
                "8": None,
                "9": None,
                "0": None
            }
            action_manager.save_config()
            console.print("[green]Настройки сброшены к значениям по умолчанию[/green]")
            input("Нажмите Enter чтобы продолжить...")

        elif choice in ["в", "выход"]:
            break

        else:
            console.print("[red]Неверная команда![/red]")
            input("Нажмите Enter чтобы продолжить...")

#класс панель
class GameUI:
    def __init__(self, hero):
        self.hero = hero
        self.layout = Layout()

        # Разделяем экран на части
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=7)
        )

        # Делим основную часть на две колонки
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )

        self.message_log = []

    def update_ui(self):
        # Обновляем заголовок
        self.layout["header"].update(
            Panel(f"Adventures of Heroes - {self.hero.name} (Уровень: {self.hero.level})", style="bold blue")
        )

        # Левая панель - основная информация
        #a_round = '%.1f' % round((self.experience / (self.exp_base * 2) * 100), 2)
        stats = (
            f"Здоровье: {self.hero.health_points}/{self.hero.max_health_points()}\n"
            f"Атака: {self.hero.attack_power}\n"
            f"Защита: {self.hero.defence}\n"
            f"Опыт: {self.hero.experience}/{self.hero.exp_base * 2}\n"
            f"Деньги: {self.hero.money} монет\n"
            f"Локация: {self.hero.location.name}\n"
            f"Убито врагов: {self.hero.count_kill}"
        )
        self.layout["left"].update(
            Panel(stats, title="Характеристики", border_style="green")
        )

        # Правая панель - снаряжение
        equipment = "\n".join(
            f"{slot}: {item.name if item else 'Пусто'}"
            for slot, item in self.hero.equipment.items()
        )
        self.layout["right"].update(
            Panel(equipment, title="Снаряжение", border_style="blue")
        )

        # Нижняя панель - сообщения и ввод
        messages = "\n".join(self.message_log[-5:]) if self.message_log else "Добро пожаловать в игру!"
        self.layout["footer"].update(
            Panel(messages, title="Сообщения", border_style="yellow")
        )

    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 100:  # Ограничиваем количество сообщений
            self.message_log.pop(0)

    def get_input(self, prompt):
        # Временное решение для ввода - можно улучшить с помощью curses
        self.update_ui()
        console.print(Panel(prompt, style="bold"))
        return input("> ")

# все функции для баров (красявости и читательность удобство)

def show_hero_creation_panel(hero_name, location_name):
    clear_screen()
    """Отображает красивую панель создания героя"""
    PANEL_WIDTH = 42  # Ширина панели (должна соответствовать количеству символов в рамке)

    creation_text = Text()
    creation_text.append("\n\n", style="bold")

    # Верхняя граница
    creation_text.append("╔" + "═" * (PANEL_WIDTH - 2) + "╗\n", style="bright_cyan")
    creation_text.append("║" + " " * (PANEL_WIDTH - 2) + "║\n", style="bright_cyan")

    # Заголовок
    creation_text.append("║", style="bright_cyan")
    creation_text.append(" " * ((PANEL_WIDTH - len("НОВЫЙ ГЕРОЙ СОЗДАН!")) // 2), style="bright_cyan")
    creation_text.append("НОВЫЙ ГЕРОЙ СОЗДАН!", style="bright_cyan bold blink")
    creation_text.append(" " * ((PANEL_WIDTH - len("НОВЫЙ ГЕРОЙ СОЗДАН!")-2) // 2), style="bright_cyan")
    creation_text.append("║\n", style="bright_cyan")

    creation_text.append("║" + " " * (PANEL_WIDTH - 2) + "║\n", style="bright_cyan")
    creation_text.append("╠" + "═" * (PANEL_WIDTH - 2) + "╣\n", style="bright_cyan")

    # Имя героя
    name_line = f"Имя: {hero_name}"
    creation_text.append("║ ", style="bright_cyan")
    creation_text.append(name_line, style="bright_yellow bold")
    creation_text.append(" " * (PANEL_WIDTH - len(name_line) - 3) + "║\n", style="bright_cyan")

    # Класс героя
    class_line = "Класс: Человек (Странник)"
    creation_text.append("║ ", style="bright_cyan")
    creation_text.append(class_line, style="bright_yellow")
    creation_text.append(" " * (PANEL_WIDTH - len(class_line) - 3) + "║\n", style="bright_cyan")

    # Локация
    location_line = f"Стартовая локация: {location_name}"
    creation_text.append("║ ", style="bright_cyan")
    creation_text.append(location_line, style="bright_yellow")
    creation_text.append(" " * (PANEL_WIDTH - len(location_line) - 3) + "║\n", style="bright_cyan")

    # Пустая строка
    creation_text.append("║" + " " * (PANEL_WIDTH - 2) + "║\n", style="bright_cyan")

    # Совет 1
    advice_line1 = "Совет: Начните с исследования Храма"
    creation_text.append("║ ", style="bright_cyan")
    creation_text.append(advice_line1, style="italic")
    creation_text.append(" " * (PANEL_WIDTH - len(advice_line1) - 3) + "║\n", style="bright_cyan")

    # Совет 2
    advice_line2 = "и попробуйте сразиться с монстрами"
    creation_text.append("║ ", style="bright_cyan")
    creation_text.append(advice_line2, style="italic")
    creation_text.append(" " * (PANEL_WIDTH - len(advice_line2) - 3) + "║\n", style="bright_cyan")

    # Нижняя граница
    creation_text.append("╚" + "═" * (PANEL_WIDTH - 2) + "╝\n", style="bright_cyan")

    console.print(creation_text)
    input("\nНажмите Enter чтобы начать свое приключение...")


def show_name_confirmation(name):
    """Отображает панель подтверждения имени"""
    clear_screen()

    # Создаем текст для панели
    panel_content = Text()
    name_text = Text(f"Вы выбрали имя: {name}\n\n", style="bright_yellow")
    name_text.append(name, style="bold bright_green")
    panel_content.append(name_text)

    question = Text("Это имя вам нравится?\n\n", style="bright_yellow")
    panel_content.append(question)

    options = Text()
    options.append("1. Да, начать игру!\n", style="green")
    options.append("2. Нет, изменить имя", style="red")
    panel_content.append(options)

    # Создаем панель
    panel = Panel(
        panel_content,
        border_style="bright_yellow",
        width=50,
        padding=(1, 2)
    )

    console.print(panel)
    return input("> Ваш выбор (1/2): ").strip().lower()


def show_name_input_panel():
    """Отображает красивую панель ввода имени"""
    clear_screen()

    # Создаем текст для панели
    panel_content = Text()
    title = Text("СОЗДАНИЕ ПЕРСОНАЖА\n", style="bold bright_cyan")
    title.justify = "center"  # Выравнивание по центру
    panel_content.append(title)
    panel_content.append("\nДайте имя вашему герою\n", style="bright_yellow")
    panel_content.append("(или введите 'выход' для отмены)", style="italic")

    # Создаем панель
    panel = Panel(
        panel_content,
        border_style="bright_blue",
        width=50,
        padding=(1, 2)
    )

    console.print(panel)
    return input("\n> Введите имя героя: ").strip()

def character_creation_flow():
    """Управляет процессом создания персонажа"""
    while True:
        # Шаг 1: Ввод имени
        hero_name = show_name_input_panel()

        if hero_name.lower() in ["выход", "в"]:
            console.print("[bright_red]Создание персонажа отменено[/bright_red]")
            time.sleep(1)
            return None

        if not hero_name:
            console.print("[red]Имя не может быть пустым![/red]")
            time.sleep(1)
            continue

        # Шаг 2: Подтверждение имени
        choice = show_name_confirmation(hero_name)

        if choice in ["1", "да", "д", ""]:
            # Создаем героя
            hero = Human(level=1, name=hero_name)
            hero.active_quests = []
            hero.completed_quests = []
            hero.set_location(Location(
                name="Храм",
                description="Древний храм",
                danger_level=4,
                zone_type="combat",
                id_loc=4
            ))

            # Показываем финальный экран
            show_hero_creation_panel(hero.name, hero.location.name)
            return hero

        elif choice in ["2", "нет", "н"]:
            console.print("[yellow]Попробуем другое имя...[/yellow]")
            time.sleep(1)
            continue

        else:
            console.print("[red]Неверный выбор![/red]")
            time.sleep(1)

def show_trade_interface(hero, merchant):
    """Отображает интерфейс торговли с панелями"""
    clear_screen()

    # 1. Панель предложений торговца (левая)
    merchant_text = Text()
    merchant_text.append(f"Торговец: {merchant.name}\n", style="bold underline")
    #merchant_text.append(f"Ваши деньги: {hero.money} монет\n", style="gold1")
    merchant_text.append("\nПредлагаемые товары:\n", style="bold")

    for i, item in enumerate(merchant.items, 1):
        merchant_text.append(f"{i}. {item.name} - {item.stock_price} монет\n")

    merchant_panel = Panel(
        merchant_text,
        title="Торговец",
        border_style="blue",
        width=40
    )

    # 2. Панель инвентаря героя (правая)
    inventory_text = Text()
    inventory_text.append("Ваш инвентарь:\n", style="bold underline")
    inventory_text.append(f"Ваши деньги: {hero.money} монет\n", style="gold1")

    if not hero.inventory:
        inventory_text.append("Инвентарь пуст\n", style="dim")
    else:
        for i, item in enumerate(hero.inventory, 1):
            if isinstance(item, StackableItem):
                inventory_text.append(f"{i}. {item.name} (x{item.quantity}) - {item.stock_price // 2} монет\n")
            else:
                inventory_text.append(f"{i}. {item.name} - {item.stock_price // 2} монет\n")

    inventory_panel = Panel(
        inventory_text,
        title="Инвентарь",
        border_style="green",
        width=40
    )

    # 3. Панель диалога (середина)
    dialog_text = Text()
    dialog_text.append("Диалог с торговцем:\n", style="bold underline")

    # Проверяем активные квесты от этого торговца
    merchant_quests = [q for q in hero.active_quests if q.giver == "Торговец"]
    if merchant_quests:
        dialog_text.append("\nАктивные квесты:\n", style="bold")
        for quest in merchant_quests:
            status = "Готово к сдаче!" if hero.is_quest_ready_to_complete(
                quest.id) else f"{quest.current_amount}/{quest.target_amount}"
            color = "green" if hero.is_quest_ready_to_complete(quest.id) else None
            dialog_text.append(f"- {quest.name}: ")
            dialog_text.append(status + "\n", style=color)

    dialog_panel = Panel(
        dialog_text,
        title="Диалог",
        border_style="yellow",
        width=40
    )

    # 4. Панель действий (нижняя)
    actions_text = Text()
    actions_text.append("Доступные действия:\n", style="bold underline")
    actions_text.append("[К]упить [номер] - купить предмет у торговца\n")
    actions_text.append("[П]родать [номер] - продать предмет из инвентаря\n")
    actions_text.append("[У]слуга [номер] - приобрести услугу\n")  # Новая строка
    actions_text.append("[КВ]ест - получить квест от торговца\n")
    actions_text.append("[С]дать [номер] - сдать квест\n")
    actions_text.append("[В]ыход - закончить торговлю\n")

    actions_panel = Panel(
        actions_text,
        title="Действия",
        border_style="red",
        width=120
    )

    # Вывод всех панелей
    console.print(Columns([merchant_panel, dialog_panel, inventory_panel], expand=False))
    console.print(actions_panel)


def get_exp_bar(current, max_exp, width=20):
    """Создает текстовую полоску опыта"""
    current = max(0, int(current))
    max_exp = max(1, int(max_exp))
    percent = min(1.0, current / max_exp)

    filled = int(percent * width)
    empty = width - filled

    exp_bar = (
            f"[cyan]{'█' * filled}[/cyan]" +
            f"[white]{'░' * empty}[/white] " +
            #f"{current}/{max_exp}"
            f"\n"
            f"[blue] {round(current / (max_exp) * 100, 2)} %[/blue]"
    )
    return exp_bar


def get_health_bar(current, max_hp, width=20):
    """Создает текстовую полоску здоровья с правильным применением цветов"""
    # Защита от некорректных значений
    current = max(0, int(current))
    max_hp = max(1, int(max_hp))
    percent = min(1.0, current / max_hp)

    # Определение цвета
    if percent < 0.33:
        color = "red"
    elif percent < 0.66:
        color = "yellow"
    else:
        color = "green"

    # Создаем полоску здоровья
    filled = int(percent * width)
    empty = width - filled

    # Собираем все в одну строку без переносов
    health_bar = (
            f"[{color}]" +
            '█' * filled +
            "[/]" +
            "[white]" +
            '░' * empty +
            "[/] " +
            "\n" +
            f"{current}/{max_hp}"
    )
    return health_bar


def show_character_interface(hero):
    """Отображает интерфейс характеристик героя с 4 панелями"""
    clear_screen()

    # 1. Панель статуса (левая)
    status_text = Text()
    status_text.append(f"Имя: {hero.name}\n", style="bold")
    status_text.append(f"Класс: {hero.get_class_hero_rus()}\n")
    status_text.append(f"Уровень: {hero.level}\n", style="cyan")

    # Здоровье с использованием Text.from_markup
    health_line = Text("Здоровье: ")
    health_line.append(Text.from_markup(get_health_bar(hero.health_points, hero.max_health_points())))
    status_text.append(health_line)
    status_text.append("\n\n")

    # Опыт с использованием Text.from_markup
    exp_line = Text("Опыт: ")
    exp_line.append(Text.from_markup(get_exp_bar(hero.experience, hero.exp_base * 2)))
    status_text.append(exp_line)
    status_text.append("\n\n")



    status_text.append(f"Атака: {hero.attack_power}\n")
    status_text.append(f"Защита: {hero.defence}\n")
    status_text.append(f"Убито врагов: {hero.count_kill}\n")
    status_text.append(f"\nДеньги: {hero.money} монет\n", style="gold1")
    status_text.append(f"Локация: {hero.location.name}\n", style="magenta")

    status_panel = Panel(
        status_text,
        title="Статус героя",
        border_style="blue",
        width=40
    )

    # 2. Панель снаряжения (середина)
    equipment_text = Text()
    equipment_text.append("Снаряжение героя:\n", style="bold underline cyan")

    slot_colors = {
        "Голова": "bright_cyan",
        "Тело": "bright_blue",
        "Руки": "bright_yellow",
        "Ноги": "bright_magenta",
        "Оружие": "bright_red",
        "Плащ": "bright_green"
    }

    # Создаем список слотов с сохранением порядка
    slots = list(hero.equipment.items())

    for index, (slot, item) in enumerate(slots, start=1):
        # Нумерация и название слота
        equipment_text.append(f"{index}. {slot}: ", style=slot_colors.get(slot, "bold"))

        # Предмет или "Пусто"
        if item:
            equipment_text.append(item.name, style="bright_white")
            if isinstance(item, Equipment):
                # Добавляем бонусы для экипировки
                equipment_text.append(f" (+{item.effect_value} {item.effect})", style="bright_green")
        else:
            equipment_text.append("Пусто", style="dim italic")

        equipment_text.append("\n")  # Перенос строки

    equipment_panel = Panel(
        equipment_text,
        title="[gold1]Снаряжение[/gold1]",
        border_style="yellow",
        width=45,
        padding=(1, 2)
    )

    # 3. Панель инвентаря (правая)
    inventory_text = Text()
    inventory_text.append("Инвентарь:\n", style="bold underline")
    if not hero.inventory:
        inventory_text.append("Инвентарь пуст\n", style="dim")
    else:
        for i, item in enumerate(hero.inventory, 1):
            if isinstance(item, StackableItem):
                inventory_text.append(f"{i}. {item.name} (x{item.quantity})\n")
            else:
                inventory_text.append(f"{i}. {item.name}\n")

    inventory_panel = Panel(
        inventory_text,
        title="Инвентарь",
        border_style="green",
        width=40
    )

    # 4. Панель действий (нижняя)
    actions_text = Text()
    actions_text.append("Управление инвентарем:\n", style="bold underline")
    actions_text.append("1. Использовать предмет:\n", style="bold")
    actions_text.append("   • Введите 'п [номер]' или 'предмет [номер]'\n")
    #actions_text.append("   • Пример: 'п 1' - использовать первый предмет\n")
    actions_text.append("2. Снять экипировку:\n", style="bold")
    actions_text.append("   • Введите 'с [номер]' или 'снять [номер]'\n")
    actions_text.append("   • Номера слотов: 1-Голова, 2-Тело, 3-Руки, 4-Ноги, 5-Оружие, 6-Плащ\n")
    actions_text.append("   • Пример: 'с 3' - снять перчатки\n")
    actions_text.append("3. Выход:\n", style="bold")
    actions_text.append("   • Введите 'в' или 'выход' для возврата в игру\n")
    actions_text.append("Подсказка: Номера предметов соответствуют их позициям в инвентаре", style="italic")

    actions_panel = Panel(
        actions_text,
        title="Действия",
        border_style="red",
        width=120
    )

    # Вывод всех панелей
    console.print(Columns([status_panel, equipment_panel, inventory_panel], expand=False))
    console.print(actions_panel)


def display_battle_interface(player, enemy, ui=None, action_manager=None):
    """Отображает интерфейс боя с гарантированным применением цветов"""
    clear_screen()

    # Левая панель - статус игрока
    player_stats = Text()
    player_stats.append(f"Имя: {player.name}\n", style="bold")
    player_stats.append(f"Уровень: {player.level}\n", style="cyan")

    # Полоска здоровья как единый текст
    health_text = Text.from_markup(get_health_bar(player.health_points, player.max_health_points()))
    player_stats.append("Здоровье: ")
    player_stats.append(health_text)
    player_stats.append("\n")

    player_stats.append(f"Атака: {player.attack_power}\n")
    player_stats.append(f"Защита: {player.defence}\n")
    player_stats.append(f"Деньги: {player.money} монет\n", style="gold1")
    player_panel = Panel(player_stats, title="Ваш герой", border_style="yellow", width=40)

    # Правая панель - статус врага
    enemy_stats = Text()
    enemy_stats.append(f"Имя: {enemy.name}\n", style="bold red")
    enemy_stats.append(f"Уровень: {enemy.level}\n", style="cyan")

    # Полоска здоровья врага
    enemy_health_text = Text.from_markup(get_health_bar(enemy.health_points, enemy.max_health_points()))
    enemy_stats.append("Здоровье: ")
    enemy_stats.append(enemy_health_text)
    enemy_stats.append("\n")

    enemy_stats.append(f"Атака: {enemy.attack_power}\n")
    enemy_stats.append(f"Защита: {enemy.defence}\n")
    enemy_panel = Panel(enemy_stats, title="Противник", border_style="red", width=40)

    # Выводим панели
    console.print(Columns([player_panel, enemy_panel], expand=False, equal=False))

    # Панель действий
    actions = Text()
    actions.append("Доступные действия:\n", style="bold underline")

    if action_manager:
        # Группируем действия по типам для лучшего отображения
        attack_actions = []
        other_actions = []

        for key in sorted(action_manager.bindings.keys()):
            action = action_manager.bindings[key]
            if action:
                action_name = {
                    "attack": "Обычная атака",
                    "escape": "Попытаться убежать",
                    "heal": "Использовать зелье лечения",
                    "strong_attack": "Сильная атака",
                    "skill_1": "Умение 1",
                    "skill_2": "Умение 2"
                }.get(action, action)

                if "атака" in action_name.lower() or "attack" in action.lower():
                    attack_actions.append(f"{key} - {action_name}")
                else:
                    other_actions.append(f"{key} - {action_name}")

        # Выводим атаки первой группой
        if attack_actions:
            actions.append("Атаки:\n", style="bold yellow")
            for action in attack_actions:
                actions.append(f"{action}\n")

        # Затем остальные действия
        if other_actions:
            actions.append("\nДругие действия:\n", style="bold green")
            for action in other_actions:
                actions.append(f"{action}\n")
    else:
        # Стандартные действия (для обратной совместимости)
        actions.append("1 - Обычная атака\n")
        actions.append("2 - Попытаться убежать\n")
        actions.append("3 - Использовать зелье лечения\n")
        actions.append("4 - Сильная атака\n")

    console.print(Panel(actions, title="Действия", border_style="blue"))


def show_main_menu():
    """Отображает главное меню в стиле игрового интерфейса"""
    clear_screen()

    # Создаем панель с командами
    commands_text = Text()
    commands_text.append("Доступные команды:\n", style="bold underline")
    commands_text.append("[С]тарт - начать новую игру\n")
    commands_text.append("[З]агрузить - загрузить игру\n")
    commands_text.append("[У]далить - удалить сохранение\n")
    commands_text.append("[УВ] - удалить все сохранения\n")
    commands_text.append("[В]ыход - выйти из игры\n")
    commands_panel = Panel(commands_text, title="Главное меню", border_style="green", width=38)

    # Создаем панель статуса (пустую, так как нет героя)
    status_text = Text()
    status_text.append("Adventures of Heroes\n", style="bold")
    status_text.append("Версия: 0.5.2.2\n")
    #status_text.append("Автор: Ваше имя\n")
    status_panel = Panel(status_text, title="Статус", border_style="blue", width=38)

    # Выводим панели рядом
    console.print(Columns([commands_panel, status_panel], expand=True))


def character_menu(hero):
    """Цикл меню характеристик героя"""
    while True:
        show_character_interface(hero)
        command = input("\nВведите команду: ").strip().lower()

        if command.startswith(('предмет ', 'п ')):
            # Обработка команды использования предмета
            try:
                item_num = int(command.split()[1]) - 1  # Получаем номер предмета из команды
                hero.use_item(number_item=item_num)
            except (ValueError, IndexError):
                console.print("[red]Ошибка: Неверный номер предмета[/red]")
                input("\nНажмите Enter чтобы продолжить...")

        elif command.startswith(('снять ', 'с ')):
            # Обработка команды снятия предмета
            try:
                slot_num = int(command.split()[1])
                if 1 <= slot_num <= 6:
                    slot_names = list(hero.equipment.keys())
                    hero.remove_item(slot=slot_names[slot_num - 1])
                else:
                    console.print("[red]Ошибка: Номер слота должен быть от 1 до 6[/red]")
                    input("\nНажмите Enter чтобы продолжить...")
            except (ValueError, IndexError):
                console.print("[red]Ошибка: Неверный номер слота[/red]")
                input("\nНажмите Enter чтобы продолжить...")

        elif command in ["выход", "в"]:
            break

        else:
            console.print("[red]Неверная команда![/red]")
            input("\nНажмите Enter чтобы продолжить...")



def get_main_menu_command():
    """Получает команду в главном меню"""
    while True:
        show_main_menu()
        command = input("\nВведите команду: ").strip().lower()

        if command in ["старт", "с"]:
            return "start"
        elif command in ["загрузить", "з"]:
            return "load"
        elif command in ["удалить", "у"]:
            return "delete"
        elif command in ["удалить все", "ув"]:
            return "delete_all"
        elif command in ["выход", "в"]:
            return "exit"
        else:
            console.print("[red]Неверная команда. Попробуйте снова.[/red]")
            time.sleep(1)  # Задержка для чтения сообщения об ошибке

def get_commands_panel():
    """Создает панель с доступными командами"""
    commands = Text()
    commands.append("Доступные команды:\n", style="bold underline")
    commands.append("[Г]ерой - характеристики и инвентарь\n")
    commands.append("[С]охр - сохранить игру\n")
    commands.append("[П]еремещ - сменить локацию\n")
    commands.append("[Б]ой - начать бой (в боевой зоне)\n")
    commands.append("[Т]орговец - торговля (в мирной зоне)\n")
    commands.append("[КВ]есты - просмотр квестов\n")
    commands.append("[НП]/[Н] - настройка панели действий\n")  # Новая команда
    commands.append("[В]ыход - выйти из игры")
    return Panel(commands, title="Команды", border_style="green")

def clear_screen():
    """Очищает экран консоли"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_player_command(hero):
    """Отображает интерфейс и получает команду от игрока с детализированной обработкой ошибок"""
    clear_screen()
    status_bar = get_status_bar(hero)
    commands_panel = get_commands_panel()

    try:
        # Пытаемся использовать стандартный вывод с Columns
        console.print(Columns([status_bar, commands_panel], width=80))
    except ZeroDivisionError:
        # Специальная обработка для ZeroDivisionError
        console.print("\n[red]ОШИБКА РЕНДЕРИНГА:[/red] [yellow]Проблема с разметкой колонок (деление на ноль)[/yellow]")
        console.print("[yellow]Используется упрощенный интерфейс...[/yellow]\n")
        console.print(status_bar)
        console.print(commands_panel)
    except Exception as e:
        # Общая обработка всех других исключений
        console.print(f"\n[red]КРИТИЧЕСКАЯ ОШИБКА:[/red] [yellow]{str(e)}[/yellow]")
        console.print("[yellow]Тип ошибки:[/yellow]", type(e).__name__)
        console.print("[yellow]Используется аварийный режим интерфейса...[/yellow]\n")
        console.print(status_bar)
        console.print(commands_panel)
    finally:
        # Этот блок выполнится в любом случае
        console.print("\n[dim]Для продолжения введите команду:[/dim]", end=" ")

    return input().strip().lower()

def get_health_color(hero):
    """Возвращает цвет для здоровья в зависимости от процента"""
    percent = hero.health_points / hero.max_health_points()
    if percent < 0.2: return "red"
    if percent < 0.5: return "yellow"
    return "green"

def get_status_bar(hero):
    """Улучшенная версия с цветовыми индикаторами"""
    status_text = Text()
    status_text.append(f"Имя: {hero.name}\n", style="bold")
    status_text.append(f"Уровень: {hero.level}\n", style="cyan")

    # Добавляем строку с активными эффектами
    if hero.effect_manager.active_effects:
        effects_str = ", ".join([f"{e.name}" for e in hero.effect_manager.active_effects.values()])
        status_text.append(f"Эффекты: {effects_str}\n", style="magenta")

    status_text.append("Здоровье: ", style="bold")
    status_text.append(f"{hero.health_points}/{hero.max_health_points()}\n",
                      style=get_health_color(hero))
    status_text.append("Опыт: ", style="bold")
    status_text.append(f"{round(hero.experience / (hero.exp_base * 2) * 100, 2)} % \n", style="blue")
    status_text.append("Локация: ", style="bold")
    status_text.append(f"{hero.location.name}\n", style="magenta")
    status_text.append("Деньги: ", style="bold")
    status_text.append(f"{hero.money} монет", style="gold1")
    return Panel(status_text, title="Статус героя", border_style="blue")

#Основные параметры предметов

# Класс Квесты
class Quest:
    def __init__(self, quest_id: int, name: str, description: str, target_item_id: int,
                 target_amount: int, reward_exp: int, reward_money: int,
                 quest_type: str, giver: str, is_completed: bool = False,
                 current_amount: int = 0):
        self.id = quest_id
        self.name = name
        self.description = description
        self.target_item_id = target_item_id
        self.target_amount = target_amount
        self.reward_exp = reward_exp
        self.reward_money = reward_money
        self.quest_type = quest_type  # single, daily, repeatable
        self.giver = giver
        self.is_completed = is_completed
        self.current_amount = current_amount
        self.completion_date = None  # Для ежедневных квестов

    def __str__(self):
        status = "[green]Завершён[/green]" if self.is_completed else f"[yellow]{self.current_amount}/{self.target_amount}[/yellow]"
        return f"{self.name} {status} - {self.description}"

    def can_be_repeated(self) -> bool:
        """Можно ли повторно получить этот квест"""
        if self.quest_type == "single":
            return False
        elif self.quest_type == "daily":
            # Проверяем, был ли квест завершен сегодня
            if self.completion_date and self.completion_date.date() == datetime.now().date():
                return False
            return True
        elif self.quest_type == "repeatable":
            return True
        return False

# Класс торговец
class Merchant:
    def __init__(self, name: str, items: list) -> None:
        self.name = name
        self.items = items  # Список предметов, которые продает торговец
        self.services = {  # Новый словарь услуг
            1: ("Долгая регенерация", 5)  # Название и цена
        }

    def show_services(self):
        """Показывает доступные услуги"""
        console.print("\nДоступные услуги:")
        for idx, (name, price) in self.services.items():
            console.print(f"{idx}. {name} - {price} монет")

    def buy_service(self, character: Character, service_id: int):
        """Покупка услуги"""
        if service_id in self.services:
            name, price = self.services[service_id]
            if character.money >= price:
                character.money -= price

                # Применяем соответствующий эффект
                if service_id == 1:  # Долгая регенерация
                    from game.effects import LONG_REGENERATION
                    character.apply_effect(LONG_REGENERATION)
                    console.print(f"[green]Вы получили эффект '{name}' на 20 минут![/green]")
            else:
                console.print("[red]Недостаточно денег![/red]")
        else:
            console.print("[red]Неверный номер услуги.[/red]")

    def show_items(self):
        console.print(f"{self.name} предлагает следующие товары:")
        for index, item in enumerate(self.items):
            console.print(f"{index + 1}. {item.name} - Цена: {item.stock_price} монет")

    def buy_item(self, character: Character, item_index: int):
        if 0 <= item_index < len(self.items):
            item = deepcopy(self.items[item_index])  # Создаем копию предмета
            if character.money >= item.stock_price:
                character.money -= item.stock_price
                if character.add_item(item):
                    console.print(f"{character.name} купил {item.name} у {self.name}.")
                else:
                    console.print("[red]Не удалось добавить предмет в инвентарь![/red]")
                    character.money += item.stock_price  # Возвращаем деньги
            else:
                console.print("[red]Недостаточно денег![/red]")
        else:
            console.print("[red]Неверный индекс товара.[/red]")

    def sell_item(self, character: Character, item_index: int):
        if 0 <= item_index < len(character.inventory):
            item = character.inventory[item_index]

            # Для стакающихся предметов спрашиваем количество
            if isinstance(item, StackableItem):
                max_sell = item.quantity
                console.print(f"У вас есть {max_sell} шт. {item.name}")
                try:
                    sell_count = int(input(f"Сколько хотите продать? (1-{max_sell}): "))
                    if sell_count < 1 or sell_count > max_sell:
                        console.print("[red]Неверное количество![/red]")
                        return
                except ValueError:
                    console.print("[red]Введите число![/red]")
                    return

                # Продаем указанное количество
                sell_price = (item.stock_price // 2) * sell_count
                character.money += sell_price

                if sell_count == max_sell:
                    character.inventory.pop(item_index)  # Удаляем весь стак
                else:
                    item.quantity -= sell_count  # Уменьшаем количество

                console.print(f"{character.name} продал {sell_count} шт. {item.name} за {sell_price} монет.")
            else:
                # Для нестакающихся предметов
                sell_price = item.stock_price // 2
                character.money += sell_price
                character.inventory.pop(item_index)
                console.print(f"{character.name} продал {item.name} за {sell_price} монет.")
        else:
            console.print("[red]Неверный индекс товара.[/red]")






#Принты для избавления от повторов
def massage_invalid_command() -> str:
    massage = (f"[dark_olive_green1]---------------------------------------------\n" + f"Неверная команда. Попробуйте ввести другую...\n" + f"---------------------------------------------[/dark_olive_green1]")
    return console.print(massage)

#Базы данных
#База данных врагов
list_name_orcs = [
    'Внизуда','Азог', 'Балкмег', 'Болдог', 'Больг', 'Верховный Гоблин', 'Гольфимбул', 'Горбаг', 'Готмог', 'Гришнак',
    'Лагдуф', 'Луг', 'Лугдуш', 'Лурц', 'Маухур', 'Музгаш', 'Нарзуг', 'Оркобал', 'Отрод', 'Радбуг',
    'Снага', 'Углук', 'Уфтак', 'Фимбул', 'Шаграт', 'Шарку', 'Язнег'
]
#База данных предметов
item_database = [
    StackableItem(name="Малое зелье лечения", effect="heal", effect_heal=50, chance=33.3, stock_price=10, id_item=1,mob_chances={"Азог":50, "Внизуда":33}),  # 33.3
    StackableItem(name="Среднее зелье лечения", effect="heal", effect_heal=100, chance=10.0, stock_price=20, id_item=2, mob_chances={"Азог":20,"Балкмег":30}),# 10
    StackableItem(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3, mob_chances={"Азог":10,"Балкмег":18}),
    StackableItem(name="Жемчужина", effect="quest", effect_heal=0, chance=50.0, stock_price=25, id_item=12, mob_chances={"Внизуда": 50}),
    Equipment(name="Шлем рыцаря", slot="Голова", effect="defence", effect_value=5, chance=5.0, stock_price=100, id_item=4),
    Equipment(name="Кираса рыцаря", slot="Тело", effect="defence", effect_value=10, chance=5.0, stock_price=200, id_item=5,mob_chances={"Балкмег":7}),
    Equipment(name="Перчатки силы", slot="Руки", effect="attack", effect_value=3, chance=5.0, stock_price=75, id_item=6),
    Equipment(name="Сапоги ловкости", slot="Ноги", effect="defence", effect_value=3, chance=5.0, stock_price=75, id_item=7),
    Equipment(name="Меч воина", slot="Оружие", effect="attack", effect_value=10, chance=5.0, stock_price=150, id_item=8),
    Equipment(name="Плащ теней", slot="Плащ", effect="defence", effect_value=7, chance=5.0, stock_price=100, id_item=9,mob_chances={"Балкмег":7}),# 5
    Equipment(name="Старые перчатки", slot="Руки", effect="defence", effect_value=1, chance=20.0, stock_price=8, id_item=10, mob_chances={"Внизуда":10}),
    Equipment(name="Старые сапоги", slot="Ноги", effect="defence", effect_value=2, chance=2.0, stock_price=8, id_item=11, mob_chances={"Внизуда":0}),
    # Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3)  # 5
]



#Отдельные функции

def spawn_mob(location: Location):
    if location.name == "Храм":
        level = 1  # Константа! Монстры только первого уровня
        name = list_name_orcs[0]  # Имя орка из храма (Внизуда)
        allowed_item_ids = [1, 2, 6, 7, 10, 11, 12]  # Предметы, которые могут выпадать от монстров в храме [1, 2, 6, 7, 10, 11]
        money = random.randint(5, 10)  # Генерация денег для монстра в храме
    elif location.name == "Зачарованный лес":
        level = random.randint(5, 7) # уровни монстров для "Зачарованный лес"
        name = list_name_orcs[2]  # Имя орка из зачарованного леса (Балкмег)
        allowed_item_ids = [1, 2, 3, 9, 4]  # Предметы, которые могут выпадать от монстров в лесу [1, 2, 3, 9, 4]
        money = random.randint(10, 20)  # Генерация денег для монстра в лесу
    elif location.name == "Безлюдная пустыня":
        level = random.randint(10, 13) # уровни монстров для "Безлюдная пустыня"
        name = list_name_orcs[1]  # Имя орка из пустыни (Азог)
        allowed_item_ids = [2, 3, 5, 8, 9]  # Предметы, которые могут выпадать от монстров в пустыне [2, 3, 5, 8, 9]
        money = random.randint(50, 90)  # Генерация денег для монстра в пустыне
    else:
        return None  # Если локация не распознана

    # Создаем нового монстра с учетом уровня и денег
    new_spawn_mob = Mob(name=name, level=level, item_database=item_database, allowed_item_ids=allowed_item_ids)
    new_spawn_mob.money = money  # Устанавливаем сгенерированное количество денег

    return new_spawn_mob

# Функции алаки и спелов
def try_escape(character: Character, enemy: Character) -> bool:
    """Попытка убежать из боя с 30% шансом, если здоровье меньше половины"""
    if character.health_points < character.max_health_points() / 2:
        return random.random() < 0.3
    return False


def use_healing(character: Character) -> bool:
    """Попытка использовать зелье лечения"""
    for i, item in enumerate(character.inventory):
        if isinstance(item, StackableItem) and item.effect == "heal":
            character.use_item(number_item=i)
            return True
    return False


def strong_attack(character: Character, enemy: Character) -> int:
    """Сильная атака с увеличенным уроном"""
    damage = character.attack_power * 1.5  # Увеличенный урон
    damage = damage * (100 - enemy.defence) / 100
    return round(damage)


def get_input_with_timeout(prompt, timeout):
    """Получаем ввод с таймаутом, работает в Windows и Unix"""
    print(prompt, end='', flush=True)

    if 'msvcrt' in sys.modules:
        # Реализация для Windows
        start_time = time.time()
        input_text = []
        while (time.time() - start_time) < timeout:
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if char == '\r':  # Enter
                    print()
                    return ''.join(input_text)
                elif char == '\x08':  # Backspace
                    if input_text:
                        input_text.pop()
                        print('\b \b', end='', flush=True)
                else:
                    input_text.append(char)
                    print(char, end='', flush=True)
            time.sleep(0.05)
        print()
        return None
    else:
        # Реализация для Unix
        import select
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        return None


def fight_turn(player, enemy, ui=None, action_manager=None):
    # Обновляем эффекты перед ходом
    player.effect_manager.update_effects(player)
    enemy.effect_manager.update_effects(enemy)

    # Проверяем, оглушен ли игрок
    if any(effect.is_stunned for effect in player.effect_manager.active_effects.values()):
        console.print("[yellow]Вы оглушены и пропускаете ход![/yellow]")
        time.sleep(1)
        return Fals
    """Один ход боя с новым интерфейсом"""
    display_battle_interface(player, enemy, ui, action_manager)

    # Получаем действие игрока с таймером
    action = get_input_with_timeout("Выберите действие: ", TURN_TIME)

    # Если ввод пустой или None - считаем это обычной атакой
    if action is None or action.strip() == "":
        action = "1"  # Дефолтное действие
        console.print("[yellow]Автоматическая атака.[/yellow]")
        time.sleep(0.3)
    else:
        action = action.strip()  # Удаляем лишние пробелы

    enemy_killed = False

    # Определяем тип действия
    if action_manager:
        action_type = action_manager.get_action(action)
    else:
        # Стандартные действия для обратной совместимости
        action_type = {
            "1": "attack",
            "2": "escape",
            "3": "heal",
            "4": "strong_attack"
        }.get(action)

    # Обработка действий
    if action_type == "attack":
        player.attack(target=enemy)
        if not enemy.is_alive():
            enemy_killed = True
            player.gain_experience(target=enemy)  # Добавляем опыт
            #player.count_kill += 1  # Увеличиваем количество убитых монстров
    elif action_type == "escape":
        if try_escape(player, enemy):
            console.print("[green]Вам удалось сбежать![/green]")
            time.sleep(2)
            return True
        else:
            console.print("[red]Не удалось сбежать![/red]")
            time.sleep(1)
    elif action_type == "heal":
        if use_healing(player):
            console.print("[green]Вы использовали зелье лечения![/green]")
            time.sleep(1)
        else:
            console.print("[red]У вас нет зелий лечения![/red]")
            time.sleep(1)
    elif action_type == "strong_attack":
        damage = strong_attack(player, enemy)
        enemy.got_damage(damage=damage)
        console.print(f"[yellow]Вы наносите сильный удар на {damage} урона![/yellow]")
        time.sleep(1)
        if not enemy.is_alive():
            enemy_killed = True
            player.gain_experience(target=enemy)  # Добавляем опыт
            #player.count_kill += 1  # Увеличиваем количество убитых монстров
    else:
        console.print("[red]Неизвестное действие![/red]")
        time.sleep(1)

    # Если враг жив и игрок не лечился - враг атакует
    if enemy.is_alive() and action_type != "heal" and not enemy_killed:
        enemy.attack(target=player)
        time.sleep(1)

    return False


def fight(*, player, enemy, ui=None, action_manager=None):
    """Модифицированная функция боя с обработкой ошибок"""
    player.in_battle = True
    enemy.in_battle = True

    try:
        while True:
            try:
                display_battle_interface(player, enemy, ui, action_manager)
                console.print(f"[bold red]Начинается бой с {enemy.name}![/bold red]")
                time.sleep(1.5)

                while player.is_alive() and enemy.is_alive():
                    try:
                        escaped = fight_turn(player, enemy, ui, action_manager)
                        if escaped:
                            return True
                    except Exception as turn_error:
                        console.print(f"[red]Ошибка в ходе боя: {str(turn_error)}[/red]")
                        import traceback
                        traceback.print_exc()
                        # Продолжаем бой несмотря на ошибку
                        time.sleep(2)
                        continue

                # Обработка результатов боя
                if not enemy.is_alive():
                    try:
                        process_mob_defeat(player, enemy, ui)
                    except Exception as defeat_error:
                        console.print(f"[red]Ошибка при обработке победы: {str(defeat_error)}[/red]")
                        # Все равно даем награду, но упрощенную
                        player.money += enemy.money
                        player.count_kill += 1

                # Панель действий после боя
                actions_text = Text()
                actions_text.append("Действия после боя:\n", style="bold underline")
                actions_text.append("[Enter] или [Б] - Начать новый бой\n")
                actions_text.append("[В] - Выйти из режима боя\n")
                console.print(Panel(actions_text, title="Выберите действие", border_style="blue"))

                # Ожидаем ввода пользователя с обработкой ошибок
                while True:
                    try:
                        if 'msvcrt' in sys.modules:  # Windows
                            if msvcrt.kbhit():
                                key = msvcrt.getch()
                                try:
                                    key = key.decode('cp866').lower()
                                except UnicodeDecodeError:
                                    continue

                                if key in ('\r', 'б'):
                                    return False  # Начать новый бой
                                elif key == 'в':
                                    return True  # Выйти из боя
                        else:  # Unix
                            import select
                            if select.select([sys.stdin], [], [], 0)[0]:
                                key = sys.stdin.readline().strip().lower()
                                if key in ('', 'б'):
                                    return False
                                elif key == 'в':
                                    return True
                        time.sleep(0.1)
                    except Exception as input_error:
                        console.print(f"[yellow]Ошибка ввода: {str(input_error)}[/yellow]")
                        time.sleep(0.5)
                        continue

            except Exception as battle_error:
                console.print(f"[red]Критическая ошибка в бою: {str(battle_error)}[/red]")
                import traceback
                traceback.print_exc()
                # Пытаемся восстановить игру
                player.health_points = max(1, player.health_points)  # Гарантируем, что игрок не умрет от бага
                time.sleep(3)
                return True  # Выходим из боя при критической ошибке

    finally:
        try:
            player.in_battle = False
            enemy.in_battle = False
        except Exception as attr_error:
            console.print(f"[yellow]Ошибка сброса флага боя: {str(attr_error)}[/yellow]")
            # Игнорируем, так как это не критично

def process_mob_defeat(hero: Character, mob: Character, ui=None):
    """Обрабатывает победу над монстром: добавляет лут, опыт и деньги"""
    try:
        # Добавляем деньги
        hero.money += mob.money
        message = f"[yellow3]{hero.name} получает: {mob.money} монет![/yellow3]"

        # Добавляем опыт
        gained_exp = mob.max_health_points() * 4
        hero.experience += gained_exp
        message += f"\n[cyan]Получено опыта: {gained_exp}[/cyan]"

        # Проверяем повышение уровня
        if hero.experience >= hero.exp_base:
            hero.level_up()
            message += f"\n[bold green]Повышен уровень до {hero.level}![/bold green]"

        # Добавляем предметы из инвентаря монстра
        loot_messages = []
        for loot in mob.inventory:
            if isinstance(loot, StackableItem):
                added = hero.add_item(deepcopy(loot))
                if added:
                    loot_messages.append(f"- {loot.name} (x{loot.quantity})")
            else:
                hero.inventory.append(deepcopy(loot))
                loot_messages.append(f"- {loot.name}")

        # Формируем сообщение о луте
        if loot_messages:
            message += "\n\n[green]Полученные предметы:[/green]\n" + "\n".join(loot_messages)

        # Увеличиваем счетчик убитых монстров
        hero.count_kill += 1

        # Обновляем квесты
        for quest in hero.active_quests:
            if not quest.is_completed and quest.target_item_id:
                for item in mob.inventory:
                    if item.id_item == quest.target_item_id:
                        quest.current_amount += item.quantity if isinstance(item, StackableItem) else 1

        # Выводим сообщение
        if ui:
            ui.add_message(message)
        else:
            console.print(Panel(Text.from_markup(message), title="Победа!", border_style="green"))

        return True
    except Exception as e:
        error_msg = f"[red]Ошибка при обработке победы: {str(e)}[/red]"
        if ui:
            ui.add_message(error_msg)
        else:
            console.print(error_msg)
        return False


def fight_with_mob(ui=None, action_manager=None):
    """Функция боя с мобом с поддержкой настраиваемой панели"""
    while True:
        new_mob = spawn_mob(hero_user.location)
        if new_mob:
            if ui:
                ui.add_message(f"\n[bright_red]Начинается бой с '{new_mob.name}', {new_mob.level} уровня[/bright_red]")
                ui.add_message(f"[bright_red]Здоровье врага: {new_mob.health_points}[/bright_red]")
                ui.update_ui()
            else:
                console.print(f"\n[bright_red]Начинается бой с '{new_mob.name}', {new_mob.level} уровня[/bright_red]")
                console.print(f"[bright_red]Здоровье врага: {new_mob.health_points}[/bright_red]")

            should_exit = fight(player=hero_user, enemy=new_mob, ui=ui, action_manager=action_manager)
            if should_exit:
                break
        else:
            if ui:
                ui.add_message("[red]Не удалось создать монстра.[/red]")
            else:
                console.print("[red]Не удалось создать монстра.[/red]")
            break



# Метод торговли
def trade_with_merchant(hero, merchant):
    """Основной цикл торговли с новым интерфейсом"""
    pearl_quest_data = next((q for q in quest_database if q["id"] == 1), None)
    last_message = ""

    while True:
        show_trade_interface(hero, merchant)

        if last_message:
            console.print(f"\n[bold]{last_message}[/bold]")
            last_message = ""
            input("Нажмите Enter чтобы продолжить...")
            continue

        action = input("\nВведите команду: ").strip().lower()

        if action.startswith(('купить ', 'к ')):
            try:
                item_index = int(action.split()[1]) - 1
                if 0 <= item_index < len(merchant.items):
                    item = merchant.items[item_index]
                    if hero.money >= item.stock_price:
                        hero.money -= item.stock_price
                        new_item = deepcopy(item)
                        if hero.add_item(new_item):
                            last_message = f"Вы купили: {item.name} за {item.stock_price} монет"
                        else:
                            hero.money += item.stock_price
                            last_message = "Не удалось добавить предмет в инвентарь!"
                    else:
                        last_message = "Недостаточно денег!"
                else:
                    last_message = "Неверный номер товара!"
            except (ValueError, IndexError):
                last_message = "Используйте: 'купить [номер]'"

        elif action.startswith(('продать ', 'п ')):
            try:
                item_index = int(action.split()[1]) - 1
                if 0 <= item_index < len(hero.inventory):
                    item = hero.inventory[item_index]
                    sell_price = item.stock_price // 2

                    if isinstance(item, StackableItem):
                        max_sell = item.quantity
                        console.print(f"У вас есть {max_sell} шт. {item.name}")
                        try:
                            sell_count = int(input(f"Сколько хотите продать? (1-{max_sell}): "))
                            if 1 <= sell_count <= max_sell:
                                hero.money += sell_price * sell_count
                                if sell_count == max_sell:
                                    hero.inventory.pop(item_index)
                                else:
                                    item.quantity -= sell_count
                                last_message = f"Продано {sell_count} шт. {item.name} за {sell_price * sell_count} монет"
                            else:
                                last_message = "Неверное количество!"
                        except ValueError:
                            last_message = "Введите число!"
                    else:
                        hero.money += sell_price
                        hero.inventory.pop(item_index)
                        last_message = f"Вы продали: {item.name} за {sell_price} монет"
                else:
                    last_message = "Неверный номер предмета!"
            except (ValueError, IndexError):
                last_message = "Используйте: 'продать [номер]'"

        elif action.startswith(('сдать ', 'с ')):
            try:
                merchant_quests = [q for q in hero.active_quests if q.giver == "Торговец"]
                quest_num = int(action.split()[1]) - 1
                if 0 <= quest_num < len(merchant_quests):
                    quest = merchant_quests[quest_num]
                    if hero.is_quest_ready_to_complete(quest.id):
                        hero.complete_quest(quest)
                        last_message = f"Квест '{quest.name}' завершен!"
                    else:
                        last_message = f"Не выполнены условия квеста! ({quest.current_amount}/{quest.target_amount})"
                else:
                    last_message = "Неверный номер квеста!"
            except (ValueError, IndexError):
                last_message = "Используйте: 'сдать [номер]'"

        elif action.startswith(('услуга ', 'у ')):
            try:
                service_id = int(action.split()[1])
                merchant.buy_service(hero, service_id)
                input("\nНажмите Enter чтобы продолжить...")
            except (ValueError, IndexError):
                last_message = "Используйте: 'услуга [номер]'"

        elif action in ["квест", "кв"]:
            if pearl_quest_data:
                if hero.add_quest(pearl_quest_data):
                    last_message = f"Получен квест: '{pearl_quest_data['name']}'"
                else:
                    last_message = "Не удалось получить квест"
            else:
                last_message = "Торговец сейчас не предлагает квестов"

        elif action in ["выход", "в"]:
            break

        else:
            last_message = "Неверная команда!"

#Функция перемещения персонажа
def move_character(ui=None):
    """Функция перемещения персонажа с поддержкой нового интерфейса"""
    if ui:
        ui.add_message("Выберите локацию для перемещения:")
        for index, loc in enumerate(location_database):
            if loc.name != "Город" and hero_user.location.name != "Город":
                continue
            ui.add_message(f"{index + 1}. {loc.name} - {loc.description}")
        ui.update_ui()

        choice = ui.get_input("Введите номер локации для перемещения: ").strip()
    else:
        console.print("Выберите локацию для перемещения:")
        for index, loc in enumerate(location_database):
            if loc.name != "Город" and hero_user.location.name != "Город":
                continue
            console.print(f"{index + 1}. {loc.name} - {loc.description}")

        choice = input("Введите номер локации для перемещения: ").strip()

    if choice.isdigit():
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(location_database):
            selected_location = location_database[choice_index]
            hero_user.move_to_location(selected_location)
            if ui:
                ui.add_message(f"[green]Вы переместились в '{hero_user.location.name}'![/green]")
            else:
                console.print(f"[green]Вы переместились в '{hero_user.location.name}'![/green]")
        else:
            if ui:
                ui.add_message("[red]Ошибка: Неверный номер локации.[/red]")
            else:
                console.print("[red]Ошибка: Неверный номер локации.[/red]")
    else:
        if ui:
            ui.add_message("[red]Ошибка: Пожалуйста, введите корректный номер.[/red]")
        else:
            console.print("[red]Ошибка: Пожалуйста, введите корректный номер.[/red]")


#Функции сохранения и загрузки
def check_file_save(dict_character: dict) -> bool:
    if not isinstance(dict_character, dict):
        return False

    # Проверка версии
    version = dict_character.get('version', 0)
    if version != 4:
        return False

    # Проверка обязательных полей
    required_fields = {
        'name': str,
        'level': int,
        'health_points': int,
        'attack_power': int,
        'defence': int,
        'experience': int,
        'exp_base': int,
        'count_kill': int,
        'location': str,
        'money': int,
        'now_time': int
    }

    for field, field_type in required_fields.items():
        if field not in dict_character or not isinstance(dict_character[field], field_type):
            return False

    # Проверка инвентаря
    if not isinstance(dict_character.get('inventory'), list):
        return False

    for item in dict_character['inventory']:
        if not isinstance(item, dict) or 'id' not in item or 'quantity' not in item:
            return False

    # Проверка экипировки
    if not isinstance(dict_character.get('equipment'), list) or len(dict_character['equipment']) != 6:
        return False

    return True

def display_saves(saves):
    print("Список сохранений:")
    for index, (save, status) in enumerate(saves, start=1):
        if isinstance(save, dict):  # Проверяем, что это словарь
            name = save.get('name', 'Неизвестно')
            level = save.get('level', 'Неизвестно')
            time_saved = save.get('now_time', 0)
            time_formatted = datetime.fromtimestamp(time_saved).strftime('%d-%m-%Y %H:%M:%S')
            location = save.get('location', 'Неизвестно')
            print(f"Ячейка сохранения № {index}: Имя: {name}, Уровень: {level}, Локация: {location}, Дата: {time_formatted}, Статус: {status}")
        else:
            print(f"Ячейка сохранения № {index}: Статус: {status} (не удалось загрузить данные)")


def convert_old_save(old_save: dict) -> dict:
    """Конвертирует старые сохранения (версии 3 и ниже) в новый формат (версия 4)"""
    if not isinstance(old_save, dict):
        return old_save

    new_save = old_save.copy()
    new_save['version'] = 4  # Устанавливаем новую версию

    # Конвертируем инвентарь
    if 'inventory' in new_save and isinstance(new_save['inventory'], list):
        new_inventory = []
        for item in new_save['inventory']:
            if isinstance(item, int):  # Старый формат - только ID
                new_inventory.append({'id': item, 'quantity': 1})
            elif isinstance(item, dict):  # Уже новый формат
                new_inventory.append(item)
            else:  # Неизвестный формат
                continue
        new_save['inventory'] = new_inventory

    # Конвертируем экипировку (если нужно)
    if 'equipment' not in new_save:
        new_save['equipment'] = [None] * 6  # 6 слотов экипировки

    return new_save


def save_in_file():
    """Сохраняет игру с красивым уведомлением"""
    try:
        if not os.path.isdir("save"):
            os.mkdir("save")

        with open(file="save\\save.json", mode="a", encoding="utf-8") as file:
            new_dict_for_save = hero_user.get_all_params_for_save()
            json.dump(new_dict_for_save, file, indent=4)
            file.write("₽")  # Разделитель сохранений

        # Создаем красивую панель уведомления
        success_panel = Panel(
            Text("Сохранение успешно завершено!\n", justify="center" ) + #style="white"
            Text(f"Герой: {hero_user.name}\n") +
            Text(f"Уровень: {hero_user.level}\n") +
            Text(f"Локация: {hero_user.location.name}\n") +
            Text(f"Время сохранения: {datetime.now().strftime('%d.%m.%Y %H:%M')}"),
            title="✓ Сохранение игры",
            border_style="gold1",
            width=60
        )

        clear_screen()
        console.print(success_panel)
        console.print("\n[dim]Нажмите Enter чтобы продолжить...[/dim]")
        input()  # Ждём нажатия Enter

    except Exception as e:
        error_panel = Panel(
            Text(f"Ошибка сохранения!\n{str(e)}", style="bold red"),
            title="Ошибка",
            border_style="red",
            width=60
        )
        console.print(error_panel)
        console.print("\n[dim]Нажмите Enter чтобы продолжить...[/dim]")
        input()  # Ждём нажатия Enter


def get_list_all_saves():
    list_saves = []
    try:
        if not os.path.exists('save\\save.json'):
            return list_saves

        with open('save\\save.json', 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return list_saves

            saves = content.split("₽")
            for save_str in saves:
                if not save_str.strip():
                    continue

                try:
                    save_data = json.loads(save_str)
                    # Конвертируем старые сохранения в новый формат
                    if save_data.get('version', 0) < 4:
                        save_data = convert_old_save(save_data)

                    # Проверяем сохранение
                    if check_file_save(save_data):
                        list_saves.append((save_data, "OK"))
                    else:
                        list_saves.append((save_data, "Ошибка проверки"))
                except json.JSONDecodeError:
                    list_saves.append((save_str, "Ошибка формата JSON"))
                except Exception as e:
                    list_saves.append((save_str, f"Ошибка обработки: {str(e)}"))

    except Exception as e:
        console.print(f"[red]Ошибка при чтении файла сохранения: {str(e)}[/red]")

    return list_saves


def download(database: list):
    list_saves = get_list_all_saves()
    if not list_saves:
        console.print("[yellow]Нет доступных сохранений.[/yellow]")
        return None

    # Показываем все сохранения с статусом
    console.print("Доступные сохранения:")
    valid_count = 0
    for index, (save, status) in enumerate(list_saves, 1):
        if isinstance(save, dict):
            name = save.get('name', 'Неизвестно')
            level = save.get('level', 0)
            time_str = datetime.fromtimestamp(save.get('now_time', 0)).strftime('%d.%m.%Y %H:%M')
            console.print(f"{index}. {name} (ур. {level}), {time_str} - {status}")
            if status == "OK":
                valid_count += 1

    if valid_count == 0:
        console.print("[red]Нет корректных сохранений для загрузки.[/red]")
        return None

    while True:
        try:
            choice = input("Введите номер сохранения для загрузки (0 - отмена): ").strip()
            if choice == '0':
                return None

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(list_saves):
                save_data, status = list_saves[choice_idx]
                if status == "OK":
                    hero = load_hero_user(dict_param=save_data, database=database)
                    if hero:
                        console.print("[green]Сохранение успешно загружено![/green]")
                        return hero
                    else:
                        console.print("[red]Не удалось загрузить героя.[/red]")
                else:
                    console.print(f"[red]Нельзя загрузить это сохранение: {status}[/red]")
            else:
                console.print("[red]Неверный номер сохранения.[/red]")
        except ValueError:
            console.print("[red]Пожалуйста, введите число.[/red]")

def load_hero_user(*, dict_param: dict, database: list):
    # Проверяем версию сохранения
    if dict_param.get('version') != 4:
        console.print("[red]Неверная версия сохранения[/red]")
        return None

    try:
        # Создаем нового персонажа
        hero = Human(name=dict_param['name'], level=dict_param['level'])
        hero.health_points = dict_param['health_points']
        hero.attack_power = dict_param['attack_power']
        hero.defence = dict_param['defence']
        hero.experience = dict_param['experience']
        hero.exp_base = dict_param['exp_base']
        hero.count_kill = dict_param['count_kill']
        hero.money = dict_param['money']
        hero.class_character = dict_param['class_character']

        # Загружаем локацию
        location_name = dict_param.get('location', 'Город')
        hero.location = next(
            (loc for loc in location_database if loc.name == location_name),
            next(loc for loc in location_database if loc.name == "Город")  # fallback
        )

        # Загружаем инвентарь (новый формат)
        hero.inventory = []
        for item_data in dict_param.get('inventory', []):
            item = next((i for i in database if i.id_item == item_data['id']), None)
            if item:
                if isinstance(item, StackableItem):
                    new_item = deepcopy(item)
                    new_item.quantity = item_data.get('quantity', 1)
                    hero.inventory.append(new_item)
                else:
                    hero.inventory.append(deepcopy(item))

        # Загружаем экипировку
        equipment_ids = dict_param.get('equipment', [])
        slot_names = ["Голова", "Тело", "Руки", "Ноги", "Оружие", "Плащ"]
        for i, item_id in enumerate(equipment_ids):
            if item_id is not None:
                item = next((item for item in database if item.id_item == item_id), None)
                if item:
                    hero.equipment[slot_names[i]] = item
        # Загружаем активные квесты
        hero.active_quests = []
        for quest_data in dict_param.get('active_quests', []):
            # Находим квест в базе данных
            quest_template = next((q for q in quest_database if q["id"] == quest_data["id"]), None)
            if quest_template:
                quest = Quest(
                    quest_id=quest_template["id"],
                    name=quest_template["name"],
                    description=quest_template["description"],
                    target_item_id=quest_template["target_item_id"],
                    target_amount=quest_template["target_amount"],
                    reward_exp=quest_template["reward_exp"],
                    reward_money=quest_template["reward_money"],
                    quest_type=quest_template["quest_type"],
                    giver=quest_template["giver"],
                    is_completed=quest_data.get("is_completed", False),
                    current_amount=quest_data.get("current_amount", 0)
                )
                # Восстанавливаем дату завершения
                if quest_data.get("completion_date"):
                    quest.completion_date = datetime.fromtimestamp(quest_data["completion_date"])
                hero.active_quests.append(quest)

        # Загружаем завершенные квесты (только ID)
        hero.completed_quests = []
        for quest_id in dict_param.get('completed_quests', []):
            quest_template = next((q for q in quest_database if q["id"] == quest_id), None)
            if quest_template:
                quest = Quest(
                    quest_id=quest_template["id"],
                    name=quest_template["name"],
                    description=quest_template["description"],
                    target_item_id=quest_template["target_item_id"],
                    target_amount=quest_template["target_amount"],
                    reward_exp=quest_template["reward_exp"],
                    reward_money=quest_template["reward_money"],
                    quest_type=quest_template["quest_type"],
                    giver=quest_template["giver"],
                    is_completed=True
                )
                hero.completed_quests.append(quest)
        hero.update_stats()
        return hero

    except Exception as e:
        console.print(f"[red]Ошибка при загрузке персонажа: {str(e)}[/red]")
        return None

def delete_specific_save(save_index: int):
    saves = get_list_all_saves()
    if 0 <= save_index < len(saves):
        confirmation = input("Вы уверены, что хотите удалить это сохранение? (да/нет): ")
        if confirmation.lower() == 'да':
            with open('save\\save.json', 'r+', encoding='utf-8') as file:
                content = file.read()
                saves = content.split("₽")  # Разбиваем по разделителю
                del saves[save_index]  # Удаляем выбранное сохранение
                file.seek(0)
                file.truncate()  # Очищаем файл
                file.write("₽".join(saves))  # Записываем оставшиеся сохранения
                console.print("[yellow3]Сохранение успешно удалено.[/yellow3]")
        else:
            console.print("[yellow3]Удаление сохранения отменено.[/yellow3]")
    else:
        console.print("[red]Ошибка: Неверный номер ячейки.[/red]")

def prompt_for_save_deletion():
    display_saves(get_list_all_saves())  # Показываем сохранения
    save_index_input = input("Введите номер ячейки для удаления: ").strip()  # Убираем пробелы

    if not save_index_input.isdigit():  # Проверяем, является ли ввод числом
        console.print("[red]Ошибка: Пожалуйста, введите корректный номер ячейки.[/red]")
        return  # Возвращаемся в основное меню

    save_index = int(save_index_input) - 1  # Преобразуем ввод в индекс
    delete_specific_save(save_index)  # Удаляем сохранение

def delete_all_saves():
    confirmation = input("Вы уверены, что хотите удалить все сохранения? Это действие нельзя отменить! (да/нет): ")
    if confirmation.lower() == 'да':
        with open('save\\save.json', 'w', encoding='utf-8') as file:
            file.write("")  # Очищаем файл
        console.print("[yellow3]Все сохранения успешно удалены.[/yellow3]")
    else:
        console.print("[yellow3]Удаление всех сохранений отменено.[/yellow3]")

#Здесь функция игры
def game() -> None:
    global action_manager  # Используем глобальный менеджер действий

    try:
        while hero_user.is_alive():
            # Обновляем эффекты вне боя
            hero_user.effect_manager.update_effects(hero_user)
            command = get_player_command(hero_user)
            # Бой
            if command in ["бой", "б"] and hero_user.location.zone_type == "combat":
                fight_with_mob(action_manager=action_manager)

            # Квесты
            elif command in ["квесты", "кв"]:
                hero_user.show_quests()

            # Торговец
            elif command in ["торговец", "т"] and hero_user.location.zone_type == "peaceful":
                merchant_items = [item_database[0], item_database[1], item_database[4]]
                merchant = Merchant(name="Торговец", items=merchant_items)
                trade_with_merchant(hero_user, merchant)

            # Перемещение
            elif command in ["перемещение", "п"]:
                move_character()

            # Сохранение игры
            elif command in ["сохранить", "с"]:
                save_in_file()

            # Настройка панели действий
            elif command in ["настройка панели", "нп", "н"]:
                configure_action_panel(action_manager)

            # Выход из игры
            elif command in ["выход", "в"]:
                confirmation = input(
                    "Вы уверены, что хотите выйти? Весь несохраненный прогресс будет утерян! (да/нет):"
                ).strip().lower()
                if confirmation in ["да", "д"]:
                    print("Выход из игры.")
                    break
                else:
                    console.print("[yellow3]Вы остаетесь в игре.[/yellow3]")
                    continue

            # Характеристики героя
            elif command in ["герой", "г"]:
                character_menu(hero_user)

            # Неизвестная команда
            else:
                console.print("[red]Неверная команда![/red]")
                input("\nНажмите Enter чтобы продолжить...")

    except Exception as e:
        console.print(f"[red]Произошла ошибка в игре: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter чтобы продолжить...")

    finally:
        # Сохраняем настройки панели действий при выходе
        try:
            action_manager.save_config()
            console.print("[green]Настройки панели действий сохранены.[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка при сохранении настроек панели: {str(e)}[/red]")

        # Финальное сообщение
        console.print(
            f"\n[bright_cyan]────────────────────────────────────────────[/bright_cyan]"
            f"\n[bright_cyan] Имя героя: '{hero_user.name}', Уровень: {hero_user.level} "
            f"\n[bright_cyan] Ждем Вашего возвращения!"
            f"\n[bright_cyan]────────────────────────────────────────────[/bright_cyan]"
        )
        input("\nНажмите Enter чтобы продолжить...")

#Здесь конец функции игры

# Основной блок игры
console.print(f"Добро пожаловать в игру\n\n[red]--- Adventures of Heroes ---\n[/red]")

while True:
    menu_command = get_main_menu_command()

    # В основном игровом цикле:
    if menu_command == "start":
        hero_user = character_creation_flow()
        game()  # Запускаем игру с созданным персонажем

    elif menu_command == "load":
        # Код загрузки игры
        hero_user = download(database=item_database)
        if hero_user:
            hero_user.class_character = hero_user.get_class_hero()
            console.print(f"[yellow3]--------------------------------------------------\n"
                          f"Успешно загружено\n"
                          f"--------------------------------------------------[/yellow3]\n")
            game()
        #except Exception as e:  # Ловим все исключения
        #    console.print(f"[red]-----------   КАКАЯ-ТО ОШИБКА   ------------------\n""--------------------------------------------------\n""Откройте папку с игрой.\n""Рядом с файлом 'adventures_of_heroes._._.exe'\n""должна быть папка 'save'\n""В папке 'save' должен быть файл 'save.json' \n""Или файл с сохранением был испорчен\n"f"Ошибка: {str(e)}\n""--------------------------------------------------[/red]") # Выводим текст ошибки для отладки

    elif menu_command == "delete":
        prompt_for_save_deletion()
    elif menu_command == "delete_all":
        delete_all_saves()
    elif menu_command == "exit":
        console.print(f"[bright_cyan]-----------------\n---Конец игры----\n-----------------[/bright_cyan]")
        break