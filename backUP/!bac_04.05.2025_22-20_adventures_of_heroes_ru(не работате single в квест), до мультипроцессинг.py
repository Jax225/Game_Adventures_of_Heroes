import time
import random
import json
import os
from copy import deepcopy
from rich.console import Console
from datetime import datetime
# константы
MAX_INVENTORY_SIZE = 999999999 # пока бесконечность
#Разметка цветом
console = Console()

#Основные параметры предметов
class Item:
    def __init__(self, name: str, effect: str, effect_heal: int, chance: float, stock_price: int, id_item: int, mob_chances: dict = None) -> None:
        self.name = name
        self.effect = effect
        self.chance = chance
        self.effect_heal = effect_heal
        self.stock_price = stock_price
        self.id_item = id_item
        self.mob_chances = mob_chances if mob_chances else {}  # Словарь шансов для разных монстров

    def __str__(self):
        return self.name
# Подкласс для стакающихся предметов
class StackableItem(Item):
    def __init__(self, name: str, effect: str, effect_heal: int, chance: float, stock_price: int,
                 id_item: int, quantity: int = 1, max_stack: int = 20, mob_chances: dict = None) -> None:
        super().__init__(name, effect, effect_heal, chance, stock_price, id_item, mob_chances)
        self.quantity = quantity
        self.max_stack = max_stack

    def __str__(self):
        return f"{self.name} (x{self.quantity})"  # Этот метод уже правильный
# Основные параметры экипировки
class Equipment(Item):
    def __init__(self, name: str, slot: str, effect: str, effect_value: int, chance: float, stock_price: int, id_item: int, mob_chances: dict = None) -> None:
        super().__init__(name, effect, 0, chance, stock_price, id_item, mob_chances)
        self.slot = slot
        self.effect_value = effect_value
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

#Основные параметры классов

class Character:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level
        self.health_points = self.base_health_points * level
        self.attack_power = self.base_attack_power * level
        self.defence = self.base_defence * level
        self.experience = 0
        self.exp_base = 100
        self.count_kill = 0
        self.location = None  # Устанавливаем начальную локацию
        self.class_character = None
        self.inventory = []
        self.equipment = {
            "Голова": None,
            "Тело": None,
            "Руки": None,
            "Ноги": None,
            "Оружие": None,
            "Плащ": None,
        }
        self.money = 0  # Новое поле для хранения денег

    def __str__(self):
        return f"Class: {self.get_class_hero()}. Name:'{self.name}', level: {self.level} HP: {self.health_points}, Money: {self.money}"

    def hero_inventory(self) -> None:
        print(f"---------------------\n"
              f"Содержимое инвентаря:\n"
              f"---------------------"
              )
        i = 1
        for inventory_item in self.inventory:
            print(f"Ячейка № {i}: '{inventory_item}'")
            i += 1

    def show_character_and_inventory(self) -> None:
        # Вывод характеристик героя
        stats = (
            f"Имя Вашего героя: '{self.name}', [yellow3]Уровень:[/yellow3][yellow3] {self.level}[/yellow3]\n"
            f"Здоровье: {self.health_points}/{self.max_health_points()}\n"
            f"Защита героя: {self.defence}\n"
            f"Атака героя: {self.attack_power}\n"
            f"Уровень: {self.level}\n"
            f"Опыт героя: {self.experience} из {self.exp_base * 2} до следующего уровня\n"
            f"Количество убитых врагов: {self.count_kill}\n"
            f"Локация: {self.location.name}\n"
            f"Деньги: {self.money} монет\n"  # Отображение денег
        )

        # Вывод снаряжения в формате ячеек
        equipment = (
            f"Снаряжение Вашего героя:\n"
            f"1. Голова: {self.equipment.get('Голова', 'None')}\n"
            f"2. Тело: {self.equipment.get('Тело', 'None')}\n"
            f"3. Руки: {self.equipment.get('Руки', 'None')}\n"
            f"4. Ноги: {self.equipment.get('Ноги', 'None')}\n"
            f"5. Оружие: {self.equipment.get('Оружие', 'None')}\n"
            f"6. Плащ: {self.equipment.get('Плащ', 'None')}\n"
        )

        # Вывод инвентаря с учетом количества стакающихся предметов
        inventory_items = []
        for i, item in enumerate(self.inventory, 1):
            if isinstance(item, StackableItem):
                inventory_items.append(f"{i}. {item.name} (x{item.quantity})")
            else:
                inventory_items.append(f"{i}. {item.name}")

        inventory_str = "\n".join(inventory_items) if inventory_items else "Инвентарь пуст."

        console.print(f"[green]{stats}[/green]\n[blue]{equipment}[/blue]\n[blue]Инвентарь:\n{inventory_str}[/blue]")

    def get_class_hero(self) -> str:
        return self.__class__.__name__
    def get_class_hero_rus(self) -> str:
        class_hero = ""
        if self.get_class_hero() == "Human":
            class_hero = "Человек"
        elif self.get_class_hero() == "Warrior":
            class_hero = "Воин"
        elif self.get_class_hero() == "Mage":
            class_hero = "Маг"
        return class_hero

    def is_alive(self) -> bool:
        return self.health_points > 0

    def got_damage(self, *, damage: int) -> None:
        damage = damage * (100 - self.defence) / 100
        damage = round(damage)
        self.health_points -= damage

    def gain_experience(self, *, target: "Character") -> None:
        if not (target.is_alive()):
            self.experience += target.max_health_points() * 4


    def level_up(self, exp_base: int):
        exp_base = exp_base * 2
        if self.experience >= exp_base:
            self.level += 1
            self.health_points = self.base_health_points * self.level
            self.attack_power = self.base_attack_power * self.level
            self.defence = self.base_defence * self.level
            self.exp_base = exp_base
            self.experience = self.experience - exp_base
            console.print(f"[bright_cyan]{self.name} получает опыт и повышает уровень до {self.level}[/bright_cyan]")

    def attack(self, *, target: "Character") -> None:
        print(f"{self.name} атакует {target.name}")
        target.got_damage(damage=self.attack_power)
        if target.is_alive():
            print(f"{self.name}, HP={self.health_points} | {target.name}, HP={target.health_points}")
        else:
            print(f"{target.name} погибает!")
            self.gain_experience(target=target)
            self.count_kill += 1
            self.level_up(exp_base=self.exp_base)

            # Добавление денег к персонажу
            if isinstance(target, Mob):
                self.money += target.money  # Добавляем деньги монстра к персонажу
                console.print(f"[yellow3]{self.name} получает: {target.money} монет![/yellow3]")

            if target.get_class_hero() == "Mob":
                for loot in target.inventory:
                    if isinstance(loot, StackableItem):  # Проверяем, что это стакуемый предмет
                        self.add_item(item=loot)
                        console.print(f"[yellow3]{self.name} получает: '{loot.name}'[/yellow3]")
                    else:
                        # Если это не стакуемый предмет, добавляем его напрямую
                        self.inventory.append(loot)
                        console.print(f"[yellow3]{self.name} получает: '{loot}'[/yellow3]")
            else:
                if len(target.inventory) != 0:
                    target.inventory.pop(int(random.uniform(0, len(target.inventory))))


    def max_health_points(self):
        return self.base_health_points * self.level

    def add_item(self, item: Item) -> bool:
        # Проверка на нулевое количество
        if isinstance(item, StackableItem) and item.quantity <= 0:
            return False
        # Для нестакающихся предметов
        if not isinstance(item, StackableItem):
            if len(self.inventory) < MAX_INVENTORY_SIZE:  # Максимальный размер инвентаря константа в нчале
                self.inventory.append(item)
                return True
            return False

        # Для стакающихся предметов
        for existing_item in self.inventory:
            if (isinstance(existing_item, StackableItem) and
                    existing_item.id_item == item.id_item and
                    existing_item.quantity < existing_item.max_stack):

                # Сколько можно добавить в этот стак
                space_left = existing_item.max_stack - existing_item.quantity
                add_amount = min(item.quantity, space_left)

                existing_item.quantity += add_amount
                item.quantity -= add_amount

                if item.quantity <= 0:
                    return True

        # Если остались предметы или нет подходящего стака
        while item.quantity > 0 and len(self.inventory) < MAX_INVENTORY_SIZE:
            new_stack = deepcopy(item)
            new_stack.quantity = min(item.quantity, item.max_stack)
            self.inventory.append(new_stack)
            item.quantity -= new_stack.quantity

        return item.quantity == 0

    def use_item(self, *, number_item: int) -> None:
        """
        Использует предмет из инвентаря по указанному номеру.
        Для стакающихся предметов уменьшает количество, а не удаляет сразу.
        Аргументы: number_item (int): Номер предмета в инвентаре (начиная с 0)
        Возможные исключения:IndexError: если номер предмета выходит за границы инвентаря
        """
        try:
            # Проверка корректности номера предмета
            if number_item < 0 or number_item >= len(self.inventory):
                raise IndexError("Номер предмета выходит за границы инвентаря")

            item = self.inventory[number_item]

            # Обработка экипировки
            if isinstance(item, Equipment):
                self._use_equipment(item, number_item)

            # Обработка стакающихся предметов (зелий и т.д.)
            elif isinstance(item, StackableItem):
                self._use_stackable_item(item, number_item)

            # Обработка обычных предметов
            else:
                self._use_regular_item(item, number_item)

        except IndexError as e:
            console.print(f"[red]Ошибка: {str(e)}[/red]")
        except Exception as e:
            console.print(f"[red]Неизвестная ошибка при использовании предмета: {str(e)}[/red]")

    def _use_equipment(self, item: Equipment, slot_index: int) -> None:
        """Вспомогательный метод для использования экипировки"""
        slot = item.slot

        # Если в слоте уже есть предмет - возвращаем его в инвентарь
        if self.equipment[slot] is not None:
            old_item = self.equipment[slot]
            self.inventory.append(old_item)
            console.print(f"[yellow3]Сняли: {old_item.name}[/yellow3]")

        # Экипируем новый предмет
        self.equipment[slot] = item
        self.inventory.pop(slot_index)
        self.update_stats()

        console.print(
            f"------------------------------------\n"
            f"Экипировано: {item.name} ({slot})\n"
            f"------------------------------------"
        )

    def _use_stackable_item(self, item: StackableItem, item_index: int) -> None:
        """Вспомогательный метод для использования стакающихся предметов"""
        # Применяем эффект
        if item.effect == "heal":
            self.health_points = min(
                self.health_points + item.effect_heal,
                self.max_health_points()
            )
            console.print(
                f"------------------------------------\n"
                f"Здоровье +{item.effect_heal} (осталось: {item.quantity - 1})\n"
                f"------------------------------------"
            )

        # Уменьшаем количество
        item.quantity -= 1

        # Если предмет закончился - удаляем из инвентаря
        if item.quantity <= 0:
            self.inventory.pop(item_index)

    def _use_regular_item(self, item: Item, item_index: int) -> None:
        """Вспомогательный метод для обычных предметов"""
        if item.effect == "heal":
            self.health_points = min(
                self.health_points + item.effect_heal,
                self.max_health_points()
            )
            console.print(
                f"------------------------------------\n"
                f"Здоровье +{item.effect_heal}\n"
                f"------------------------------------"
            )

        # Удаляем предмет после использования
        self.inventory.pop(item_index)

    def remove_item(self, slot: str) -> None:
        if slot in self.equipment and self.equipment[slot] is not None:
            removed_item = self.equipment[slot]
            self.equipment[slot] = None  # Снимаем предмет
            self.inventory.append(removed_item)  # Добавляем предмет обратно в инвентарь
            self.update_stats()  # Обновляем характеристики
            console.print(
                f"[yellow3]Вы сняли '{removed_item.name}' из слота '{slot}' и добавили в инвентарь.[/yellow3]")
        else:
            console.print(f"[red]Ошибка: В слоте '{slot}' нет экипированного предмета.[/red]")

    def discard_item(self, number_item: int) -> None:
        if 0 <= number_item < len(self.inventory):
            discarded_item = self.inventory.pop(number_item)
            console.print(f"[yellow3]Вы выбросили '{discarded_item}' из инвентаря.[/yellow3]")
        else:
            console.print("[red]Ошибка: Неверный номер предмета.[/red]")

    def get_all_params_for_save(self) -> dict:
        save_hero = {
            'version': 4,  # Обновляем версию на 4
            'name': self.name,
            'level': self.level,
            'health_points': self.health_points,
            'attack_power': self.attack_power,
            'defence': self.defence,
            'experience': self.experience,
            'exp_base': self.exp_base,
            'count_kill': self.count_kill,
            'location': self.location.name if isinstance(self.location, Location) else "Город",
            'class_character': self.class_character,
            'inventory': self._get_inventory_for_save(),
            'equipment': self._get_equipment_for_save(),  # Используем новый метод
            'money': self.money,  # Сохраняем количество денег
            'active_quests': [{
                'id': q.id,
                'current_amount': q.current_amount,
                'is_completed': q.is_completed,
                'completion_date': q.completion_date.timestamp() if q.completion_date else None
            } for q in self.active_quests],
            'completed_quests': [q.id for q in self.completed_quests],
            'now_time': round(time.time())
        }
        return save_hero

    def get_list_id_item_from_save(self, items) -> list:
        i = 0
        inventory_from_save = []
        for _ in self.inventory:
            inventory_from_save.append(self.inventory[i].id_item)
            i += 1
        return [item.id_item if item else None for item in items]

    def _get_inventory_for_save(self) -> list:
        inventory_data = []
        for item in self.inventory:
            if isinstance(item, StackableItem):
                inventory_data.append({
                    'id': item.id_item,
                    'quantity': item.quantity
                })
            else:
                inventory_data.append({
                    'id': item.id_item,
                    'quantity': 1
                })
        return inventory_data

    def _get_equipment_for_save(self) -> list:
        """Возвращает список ID предметов экипировки для сохранения"""
        equipment_data = []
        for slot in ["Голова", "Тело", "Руки", "Ноги", "Оружие", "Плащ"]:
            item = self.equipment.get(slot)
            if item:
                equipment_data.append(item.id_item)
            else:
                equipment_data.append(None)
        return equipment_data

    def update_stats(self):
        self.attack_power = self.base_attack_power * self.level
        self.defence = self.base_defence * self.level
        for item in self.equipment.values():
            if item:
                if item.effect == "attack":
                    self.attack_power += item.effect_value
                elif item.effect == "defence":
                    self.defence += item.effect_value

    def set_location(self, location) -> None:
        self.location = location

    def move_to_location(self, new_location) -> None:
        if self.location.name == "Город":
            # Если текущая локация - Город, можно перемещаться в любую локацию
            self.set_location(new_location)
            console.print(f"[green]Вы переместились в '{self.location.name}'![/green]")
        elif new_location.name == "Город":
            # Если перемещение в Город, разрешаем
            self.set_location(new_location)
            console.print(f"[green]Вы вернулись в 'Город'![/green]")
        else:
            # Если пытаемся переместиться из другой локации в другую, запрещаем
            console.print(f"[red]Вы можете перемещаться только в 'Город' из '{self.location.name}'![/red]")

    def get_location(self) -> str:
        return str(self.location) if isinstance(self.location, Location) else "Неизвестно"

    def add_quest(self, quest_data: dict) -> bool:
        """Добавляет квест из базы данных"""
        # Проверяем, можно ли получить квест
        if self.level < quest_data["required_level"]:
            console.print(
                f"[red]Ваш уровень слишком низок для этого квеста (требуется: {quest_data['required_level']})[/red]")
            return False

        # Проверяем выполнены ли требуемые квесты
        for req_quest_id in quest_data["required_quests"]:
            if not any(q.id == req_quest_id and q.is_completed for q in self.completed_quests):
                console.print(f"[red]Вы не выполнили необходимые предварительные квесты[/red]")
                return False

        # Проверяем ограничение по локации
        if quest_data["location_restriction"] and self.location.id_loc != quest_data["location_restriction"]:
            console.print(f"[red]Этот квест можно получить только в определённой локации[/red]")
            return False

        # Проверяем, есть ли уже такой квест
        existing_quest = next((q for q in self.active_quests if q.id == quest_data["id"]), None)
        if existing_quest:
            if existing_quest.quest_type == "single":
                console.print("[red]Этот квест можно выполнить только один раз[/red]")
                return False
            elif not existing_quest.can_be_repeated():
                console.print("[red]Вы уже выполнили этот квест сегодня[/red]")
                return False

        # Создаем экземпляр квеста
        new_quest = Quest(
            quest_id=quest_data["id"],
            name=quest_data["name"],
            description=quest_data["description"],
            target_item_id=quest_data["target_item_id"],
            target_amount=quest_data["target_amount"],
            reward_exp=quest_data["reward_exp"],
            reward_money=quest_data["reward_money"],
            quest_type=quest_data["quest_type"],
            giver=quest_data["giver"]
        )

        self.active_quests.append(new_quest)
        console.print(f"[yellow3]Получен новый квест: '{new_quest.name}'[/yellow3]")
        console.print(f"[yellow3]Описание: {new_quest.description}[/yellow3]")
        return True

    def complete_quest(self, quest: Quest) -> None:
        """Завершает квест и выдает награду"""
        # Удаляем требуемые предметы из инвентаря
        if quest.target_item_id:
            target_amount = quest.target_amount
            # Проходим по инвентарю в обратном порядке для безопасного удаления
            for i in range(len(self.inventory) - 1, -1, -1):
                item = self.inventory[i]
                if item.id_item == quest.target_item_id:
                    if item.quantity <= target_amount:
                        target_amount -= item.quantity
                        self.inventory.pop(i)
                    else:
                        item.quantity -= target_amount
                        target_amount = 0
                    if target_amount == 0:
                        break

        # Выдаем награду
        self.experience += quest.reward_exp
        self.money += quest.reward_money
        quest.is_completed = True
        quest.completion_date = datetime.now()

        # Перемещаем квест в завершенные (для одноразовых)
        if quest.quest_type == "single":
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
        else:
            quest.current_amount = 0
            quest.is_completed = False

        console.print(f"[bright_green]====================================[/bright_green]")
        console.print(f"[bright_green]Квест '{quest.name}' завершен![/bright_green]")
        console.print(f"[bright_green]Награда: {quest.reward_exp} опыта и {quest.reward_money} монет[/bright_green]")
        console.print(f"[bright_green]====================================[/bright_green]")

    def show_quests(self) -> None:
        for i, quest in enumerate(self.active_quests, 1):
            status = "[green]Готово к сдаче![/green]" if self.is_quest_ready_to_complete(
                quest.id) else f"{quest.current_amount}/{quest.target_amount}"
            console.print(f"{i}. {quest.name} - {status}")
        """Показывает активные и завершенные квесты"""
        console.print("[bold underline]Активные квесты:[/bold underline]")
        if not self.active_quests:
            console.print("[italic]Нет активных квестов[/italic]")
        else:
            for i, quest in enumerate(self.active_quests, 1):
                console.print(f"{i}. {quest}")
                console.print(f"   [italic]Дает: {quest.giver}[/italic]")
                console.print(f"   [yellow3]Чтобы сдать квест, введите у {quest.giver} 'сдать {quest.id}'[/yellow3]")
                console.print(f"   Награда: {quest.reward_exp} опыта и {quest.reward_money} монет")
                console.print("")

        console.print("[bold underline]Завершенные квесты:[/bold underline]")
        if not self.completed_quests:
            console.print("[italic]Нет завершенных квестов[/italic]")
        else:
            for i, quest in enumerate(self.completed_quests, 1):
                console.print(f"{i}. [green]{quest.name} (завершён)[/green]")

    def is_quest_ready_to_complete(self, quest_id: int) -> bool:
        """Проверяет, можно ли завершить квест"""
        quest = next((q for q in self.active_quests if q.id == quest_id), None)
        if not quest:
            return False

        # Проверяем, есть ли нужные предметы в инвентаре
        if quest.target_item_id:
            total = sum(item.quantity for item in self.inventory
                        if item.id_item == quest.target_item_id)
            return total >= quest.target_amount
        return True

    def check_quest_progress(self, item_id: int, amount: int = 1) -> None:
        """Проверяет прогресс по квестам при получении предмета"""
        for quest in self.active_quests:
            if quest.target_item_id == item_id and not quest.is_completed:
                quest.current_amount += amount

                # Проверяем, нужно ли автоматическое завершение
                quest_data = next((q for q in quest_database if q["id"] == quest.id), None)
                if quest_data and quest_data.get("auto_complete", False):
                    if quest.current_amount >= quest.target_amount:
                        self.complete_quest(quest)
# Класс торговец
class Merchant:
    def __init__(self, name: str, items: list) -> None:
        self.name = name
        self.items = items  # Список предметов, которые продает торговец

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




class Location:
    def __init__(self, name: str, description: str, danger_level: int, zone_type: str, id_loc: int) -> None:
        self.name = name
        self.description = description
        self.danger_level = danger_level
        self.zone_type = zone_type  # Новый параметр для типа зоны
        self.id_loc = id_loc

    def __str__(self):
        return f"{self.name}: {self.description} (Уровень опасности: {self.danger_level}, Тип зоны: {self.zone_type})"

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

#База данных локаций
location_database = [
    Location(name="Город", description="Место, полное жизни и возможностей.", danger_level=1, zone_type="peaceful", id_loc="1"),
    Location(name="Зачарованный лес", description="Лес, полный магии и тайн. Уровни монстров: (5-7)", danger_level=3, zone_type="combat", id_loc="2"),
    Location(name="Безлюдная пустыня", description="Широкие песчаные дюны и отсутствие жизни.Уровни монстров: (10-13)", danger_level=4, zone_type="combat", id_loc="3"),
    Location(name="Храм", description="Древний храм, хранящий множество секретов.Уровни монстров: (1)", danger_level=2, zone_type="combat", id_loc="4"),

]
# База данных квестов
quest_database = [
    {
        "id": 1,
        "name": "Жемчужный сбор",
        "description": "Принесите 10 жемчужин, которые падают с монстра 'Внизуда'",
        "target_item_id": 12,  # ID жемчужины
        "target_amount": 10,
        "reward_exp": 200,
        "reward_money": 500,
        "giver": "Торговец",
        "quest_type": "single",  # Типы: single (одноразовый), daily (ежедневный), repeatable (повторяемый)
        "required_level": 1,
        "required_quests": [],  # ID квестов, которые нужно выполнить перед этим
        "location_restriction": None,  # Можно указать ID локации, где можно получить квест
        "auto_complete": False,  # False - нужно сдавать вручную, True - завершается автоматически
    },
    # Здесь можно добавлять другие квесты по аналогии
]

#Все подклассы
class Human(Character):
    base_health_points = 100
    base_attack_power = 10
    base_defence = 5
    base_inventory = []
class Warrior(Human):
    base_health_points = 200
    base_attack_power = 20
    base_defence = 10
class Mage(Human):
    base_health_points = 100
    base_attack_power = 40
    base_defence = 6
class Mob(Character):
    base_health_points = 100  # test
    base_attack_power = 8
    base_defence = 3

    def __init__(self, *, name: str, level: int, item_database: list, allowed_item_ids: list) -> None:
        super().__init__(name, level)
        self.inventory = generate_inventory(item_database, allowed_item_ids, mob_name=name)  # Передаем имя монстра
        self.money = random.randint(5, 20)  # Генерация случайного количества денег для монстра

#class Mob_mini(Mob)
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


def fight(*, charcter1: Character, charcter2: Character):
    while charcter1.is_alive() and charcter2.is_alive():
        charcter1.attack(target=charcter2)
        if charcter2.is_alive():
            charcter2.attack(target=charcter1)
        time.sleep(0.1)  # время задержки


def fight_wiht_mob():
    new_mob = spawn_mob(hero_user.location)  # Передаем текущую локацию героя
    if new_mob:
        print(f"Начинается бой с '{new_mob.name}', {new_mob.level} уровня\n"
              f"Количество здоровья '{new_mob.name}' = {new_mob.health_points}"
              )
        fight(charcter1=hero_user, charcter2=new_mob)
    else:
        console.print("[red]Не удалось создать монстра.[/red]")


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

# Метод торговли
def trade_with_merchant(character: Character, merchant: Merchant):
    pearl_quest_data = next((q for q in quest_database if q["id"] == 1), None)

    while True:
        console.print("\n[bold]Меню торговли:[/bold]")
        console.print(f"Ваши деньги: {character.money} монет")

        # Показываем активные квесты от этого торговца
        merchant_quests = [q for q in character.active_quests if q.giver == "Торговец"]
        for quest in merchant_quests:
            console.print(f"\n[bold]Активный квест:[/bold] {quest}")

        merchant.show_items()
        character.show_character_and_inventory()

        action = input("\nВведите 'купить [номер]' или 'к [номер]' для покупки\n"
                       "Введите 'продать [номер]' или 'п [номер]' для продажи\n"
                       "Введите 'квест' чтобы получить квест от торговца\n"
                       "Введите 'сдать [номер]' чтобы сдать квест\n"
                       "Для выхода 'выйти' или 'в': ").strip().lower()

        if action.startswith(('купить ', 'к ')):
            try:
                parts = action.split()
                item_index = int(parts[1]) - 1
                merchant.buy_item(character, item_index)
            except (ValueError, IndexError):
                console.print("[red]Неверный формат команды. Используйте 'купить [номер]'[/red]")
        elif action.startswith('сдать '):
            try:
                quest_num = int(action.split()[1]) - 1
                if 0 <= quest_num < len(merchant_quests):
                    quest = merchant_quests[quest_num]
                    if character.is_quest_ready_to_complete(quest.id):
                        character.complete_quest(quest)
                    else:
                        console.print("[red]У вас недостаточно предметов для сдачи этого квеста![/red]")
                else:
                    console.print("[red]Неверный номер квеста[/red]")
            except (ValueError, IndexError):
                console.print("[red]Используйте: 'сдать [номер]'[/red]")
        elif action.startswith(('продать ', 'п ')):
            try:
                parts = action.split()
                item_index = int(parts[1]) - 1
                merchant.sell_item(character, item_index)
            except (ValueError, IndexError):
                console.print("[red]Неверный формат команды. Используйте 'продать [номер]'[/red]")
        elif action == "квест":
            if pearl_quest_data:
                character.add_quest(pearl_quest_data)
            else:
                console.print("[red]Торговец сейчас не предлагает квестов[/red]")
        elif action.startswith('сдать'):
            try:
                quest_num = int(action.split()[1]) - 1
                if 0 <= quest_num < len(merchant_quests):
                    quest = merchant_quests[quest_num]
                    quest_data = next((q for q in quest_database if q["id"] == quest.id), None)

                    if quest_data and quest_data.get("auto_complete", False):
                        console.print("[yellow]Этот квест завершается автоматически при выполнении условий[/yellow]")
                    else:
                        if character.is_quest_ready_to_complete(quest.id):
                            character.complete_quest(quest)
                        else:
                            console.print(
                                f"[red]Не выполнены условия квеста! ({quest.current_amount}/{quest.target_amount})[/red]")
                else:
                    console.print("[red]Неверный номер квеста[/red]")
            except (ValueError, IndexError):
                console.print("[red]Используйте: 'сдать [номер]'[/red]")

        elif action in ["выйти", "в"]:
            break
        else:
            console.print("[red]Неверная команда.[/red]")


#Функция перемещения персонажа
def move_character():
    console.print("Выберите локацию для перемещения:")
    for index, loc in enumerate(location_database):
        if loc.name != "Город" and hero_user.location.name != "Город":
            continue  # Если не в Городе, не показываем другие локации
        console.print(f"{index + 1}. {loc.name} - {loc.description}")

    choice = input("Введите номер локации для перемещения: ").strip()
    if choice.isdigit():
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(location_database):
            selected_location = location_database[choice_index]
            hero_user.move_to_location(selected_location)
        else:
            console.print("[red]Ошибка: Неверный номер локации.[/red]")
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
    if not os.path.isdir("save"):
        os.mkdir("save")
    with open(file="save/save.json", mode="a", encoding="utf-8") as file:
        new_dict_for_save = hero_user.get_all_params_for_save()
        json.dump(new_dict_for_save, file, indent=4)
        file.write("₽")  # Добавляем разделитель перед новым сохранением


def get_list_all_saves():
    list_saves = []
    try:
        if not os.path.exists('save/save.json'):
            return list_saves

        with open('save/save.json', 'r', encoding='utf-8') as file:
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
            with open('save/save.json', 'r+', encoding='utf-8') as file:
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
        with open('save/save.json', 'w', encoding='utf-8') as file:
            file.write("")  # Очищаем файл
        console.print("[yellow3]Все сохранения успешно удалены.[/yellow3]")
    else:
        console.print("[yellow3]Удаление всех сохранений отменено.[/yellow3]")

def get_player_command():
    # Формируем строку с командами
    command_options = (
        f"-----------Действия игрока----------\t\t\t\t Имя Вашего героя: {hero_user.name}\t Уровень: {hero_user.level}\n"
        f"'ГЕРОЙ' или 'Г' характеристики героя и инвентарь \t Здоровье: {hero_user.health_points}/{hero_user.max_health_points()}\t\t\t Локация: {hero_user.location.name} \n"
        f"'СОХРАНИТЬ' или 'С' для сохранения прогресса \t\t Опыт: {hero_user.experience}/{hero_user.exp_base * 2}\n"  
        f"'ВЫХОД' или 'В' для выход  \n"
        f"'ПЕРЕМЕЩЕНИЕ' или 'П' для перемещения \n"
        f"'квесты' или 'кв' для просмотра активных квестов\n"

    )

    # Добавляем опцию торговли, если мирной зоне
    if hero_user.location.zone_type == "peaceful":
        command_options += (
            f"'ТОРГОВЕЦ' или 'Т' для торговли \n"
        )

    # Добавляем опцию боя, если зона боевое
    if hero_user.location.zone_type == "combat":
        command_options += (
            f"'БОЙ' или 'Б' для перехода к новому бою \n"
        )

    command = input(command_options + "Введите следующую команду: \n").strip().lower()
    return command

#Здесь функция игры
def game() -> None:
    while hero_user.is_alive():
        command = get_player_command()  # Получаем команду от игрока

        if command in ["бой", "б"] and hero_user.location.zone_type == "combat":
            fight_wiht_mob()  # Вызываем бой только если зона боевое
        elif command in ["бой", "б"] and hero_user.location.zone_type == "peaceful":
            console.print("[red]Вы не можете вступить в бой в мирной зоне![/red]")
        elif command in ["квесты", "кв"]:
            hero_user.show_quests()
        elif command in ["торговец", "т"] and hero_user.location.zone_type == "peaceful":
            # Создание торговца
            merchant_items = [item_database[0], item_database[1], item_database[3]]  # Пример товаров
            merchant = Merchant(name="Торговец", items=merchant_items)
            trade_with_merchant(hero_user, merchant)  # Вызов торговли





        elif command in ["перемещение", "п"]:
            move_character()  # Вызов функции перемещения

        elif command in ["сохранить", "с"]:
            save_in_file()
            console.print(f"[yellow3]--------------------------------------------------\n"
                          f"Успешно сохранено\n"
                          f"--------------------------------------------------[/yellow3]\n")
        elif command in ["выход", "в"]:
            confirmation = input(
                "Вы уверены, что хотите выйти? Весь несохраненный прогресс будет утерян! (да/нет):").strip().lower()
            if confirmation in ["да", "д"]:
                print("Выход из игры.")
                break
            else:
                console.print("[yellow3]Вы остаетесь в игре.[/yellow3]")
                continue

        elif command in ["герой", "г"]:
            hero_user.show_character_and_inventory()  # Вызов функции для показа характеристик и инвентаря
            while True:  # Цикл для работы с инвентарем
                hero_user.show_character_and_inventory()  # Вызов функции для показа характеристик и инвентаря
                command_hero_inventory = input(f"--------------------------------------------------\n"
                                               f"Введите 'ПРЕДМЕТ' или 'П' чтобы взаимодействовать\n"
                                               f"Введите 'СНЯТЬ' или 'С' для снятия предмета\n"
                                               f"Введите 'кинуть' или 'к' чтобы выбросить предмет\n"
                                               f"Введите 'выход' или 'в' чтобы закрыть инвентарь\n"
                                               f"--------------------------------------------------\n"
                                               )
                command_hero_inventory = command_hero_inventory.strip().lower()
                if command_hero_inventory in ['предмет', 'п']:
                    input_number_item = input(f"Введите номер ячейки чтобы использовать предмет: ")
                    if input_number_item == "0":
                        print("Введите корректное значение\nИли инвентарь пуст")
                        continue
                    try:
                        hero_user.use_item(number_item=int(input_number_item) - 1)
                    except IndexError:
                        print('Ячейка инвентаря пуста!')
                    except Exception as e:
                        print(f"Ошибка: {str(e)}")
                elif command_hero_inventory in ['снять', 'с']:
                    slot_number = input("Введите номер ячейки (1-6) для снятия предмета: ")
                    try:
                        slot_index = int(slot_number) - 1
                        slot_names = list(hero_user.equipment.keys())
                        if 0 <= slot_index < len(slot_names):
                            slot_name = slot_names[slot_index]
                            hero_user.remove_item(slot=slot_name)
                        else:
                            console.print("[red]Ошибка: Неверный номер слота.[/red]")
                    except ValueError:
                        console.print("[red]Ошибка: Пожалуйста, введите корректный номер.[/red]")

                elif command_hero_inventory in ['кинуть', 'к']:
                    input_number_item = input(f"Введите номер ячейки чтобы выбросить предмет: ")
                    if input_number_item == "0":
                        print("Введите корректное значение\nИли инвентарь пуст")
                        continue
                    try:
                        hero_user.discard_item(number_item=int(input_number_item) - 1)
                    except IndexError:
                        print('Ячейка инвентаря пуста!')
                    except Exception as e:
                        print(f"Ошибка: {str(e)}")
                elif command_hero_inventory in ['выход', 'в']:
                    print("Вы вышли из инвентаря.")
                    break  # Выход из цикла инвентаря
                else:
                    massage_invalid_command()  # Обработка неверной команды

    print(f"Имя Вашего героя: '{hero_user.name}', Уровень: {hero_user.level}\n"
          f"Ждем Вашего возвращения!!!"
          )
#Здесь конец функции игры




#Основной блок игры

console.print(f"Добро пожаловать в игру\n\n[red]--- Adventures of Heroes ---\n[/red]")

menu = ""
while menu not in ["выход", "в"]:
    menu = input(
        f"-----------Меню------------\n"
        f"Введите команду\n"
        f"'СТАРТ' или 'C' чтобы начать новую игру\n"
        f"'ЗАГРУЗИТЬ' или 'З' чтобы загрузить игру\n"
        f"'УДАЛИТЬ' или 'У' чтобы удалить сохранение\n"  
        f"'УДАЛИТЬ ВСЕ' или 'УВ' чтобы удалить все сохранения\n"
        f"'ВЫХОД' или 'В' для выхода\n"
        f"Поле ввода: "
    ).strip().lower()  # Приводим ввод к нижнему регистру и убираем пробелы

    if menu in ["старт", "с"]:


        hero_user = Human(level=1, name=input(
            f"Начало новой игры!\n"
            f"Создание персонажа\n"
            f"Введите 'ВЫХОД' или 'В' если хотите выйти\n"
            f"Введите имя героя: "
        ).strip())  # Убираем пробелы из имени героя
        """Определения квестов"""
        if not hasattr(hero_user, 'active_quests'):
            hero_user.active_quests = []
        if not hasattr(hero_user, 'completed_quests'):
            hero_user.completed_quests = []

        if hero_user.name.lower() in ["выход", "в"]:
            print("Выход из игры.")
            break
        elif hero_user.name == "":
            print(f"--------------------------------\nПоле не может быть пустым")
            continue
        # Создаем экземпляр локации "Храм"
        temple_location = Location(name="Храм", description="Древний храм, хранящий множество секретов.", danger_level=4, zone_type="combat", id_loc=4)
        # Устанавливаем локацию героя на "Храм"
        hero_user.set_location(temple_location)

        console.print(f"Имя Вашего героя: {hero_user.name}\nПродолжить?")
        answer_user = input(f"'ДА','Д' или нажмите 'Enter' чтобы продолжить с этим именем.\n"
                            f"'НЕТ','Н' чтобы изменить.\n"
                            f"Поле ввода: ").strip().lower()  # Убираем пробелы и приводим к нижнему регистру

        if answer_user in ["", "да", "д"]:
            print(
                f"Вы только что создали героя. \nВы находитесь в локации {hero_user.location.name} \nПопробуйте атаковать кого-нибудь")
            hero_user.class_character = hero_user.get_class_hero()
            # Функция игры | новая игра
            game()

        elif answer_user in ["нет", "н"]:
            print(f"----------------------------------\nПопробуйте заново...\n----------------------------------")
            continue
        else:
            massage_invalid_command()
            continue

    elif menu in ["загрузить", "з"]:
        #try:
            hero_user = download(database=item_database)
            if hero_user is None:
                print("Не удалось загрузить героя. Пожалуйста, попробуйте снова.")
            else:
                hero_user.class_character = hero_user.get_class_hero()

            console.print(f"[yellow3]--------------------------------------------------\n"
                          f"Успешно загружено\n"
                          f"--------------------------------------------------[/yellow3]\n")
            game()
        #except Exception as e:  # Ловим все исключения
        #    console.print(f"[red]-----------   КАКАЯ-ТО ОШИБКА   ------------------\n""--------------------------------------------------\n""Откройте папку с игрой.\n""Рядом с файлом 'adventures_of_heroes._._.exe'\n""должна быть папка 'save'\n""В папке 'save' должен быть файл 'save.json' \n""Или файл с сохранением был испорчен\n"f"Ошибка: {str(e)}\n""--------------------------------------------------[/red]") # Выводим текст ошибки для отладки


    elif menu in ["удалить", "у"]:  # Обработка новой команды
        prompt_for_save_deletion()  # Запрос на удаление сохранения

    elif menu in ["удалить все", "ув"]:  # Обработка команды для удаления всех сохранений
        delete_all_saves()

    elif menu in ["выход", "в"]:
        print(f"-----------------\n---Конец игры----\n-----------------")
        break
    else:
        massage_invalid_command()
        continue
