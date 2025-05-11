# game/utils.py
import random
import os
from copy import deepcopy
from rich.console import Console


#импорты из соседних файлов
from .items import Item, StackableItem

console = Console()

def generate_inventory(item_database: list, allowed_item_ids: list, max_item=5, mob_name: str = None):
    inventory = []
    filtered_items = [item for item in item_database if item.id_item in allowed_item_ids]

    for _ in range(max_item):
        item_template = random.choice(filtered_items)
        chance = item_template.mob_chances.get(mob_name, item_template.chance)

        if random.uniform(0, 100) < chance:
            if isinstance(item_template, StackableItem):
                # Создаем новый экземпляр с quantity=1
                new_item = deepcopy(item_template)
                new_item.quantity = 1
                inventory.append(new_item)
            else:
                inventory.append(deepcopy(item_template))

    return inventory

def clear_screen():
    """
    Универсальная очистка экрана с многоуровневой обработкой ошибок.
    Пробует методы в порядке приоритета:
    1. Через rich.console (самый надежный)
    2. Стандартный os.system
    3. Резервный вывод пустых строк
    """
    try:
        # Пытаемся очистить через rich (предпочтительный способ)
        console.clear()
    except Exception as rich_error:
        try:
            # Если rich не сработал, пробуем стандартный способ
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as os_error:
            try:
                # Для Jupyter/особых случаев
                from IPython.display import clear_output
                clear_output(wait=True)
            except:
                # Последний резерв - выводим много пустых строк
                print('\n' * 100)
                # Логируем ошибки, если нужно
                if 'rich_error' in locals():
                    console.print(f"[yellow]Rich clear error: {rich_error}[/yellow]")
                if 'os_error' in locals():
                    console.print(f"[yellow]OS clear error: {os_error}[/yellow]")

