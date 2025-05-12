# game/character.py
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.box import ROUNDED
import time
from datetime import datetime
from copy import deepcopy
from datetime import datetime
import random
from rich.panel import Panel
from rich.text import Text
#импорты из соседних файлов
from .items import Item, Equipment, StackableItem
from .utils import generate_inventory, clear_screen
from .quests import Quest
from .quests import quest_database
from .locations import Location

MAX_INVENTORY_SIZE = 999999999 # инвентарь - пока бесконечность
TURN_TIME = 3  # Время на ход в секундах

#Разметка цветом
console = Console()


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
            f"Деньги: {self.money} монет"  # Отображение денег
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
        if not target.is_alive():
            gained_exp = target.max_health_points() * 4
            self.experience += gained_exp
            console.print(f"[bright_cyan]{self.name} получает {gained_exp} опыта![/bright_cyan]")
            self.level_up()  # Убрали передачу параметра

    def level_up(self):  # Убрали параметр exp_base
        if self.experience >= self.exp_base:
            self.level += 1
            self.health_points = self.base_health_points * self.level
            self.attack_power = self.base_attack_power * self.level
            self.defence = self.base_defence * self.level
            self.experience -= self.exp_base  # Вычитаем только после повышения уровня
            self.exp_base = int(self.exp_base * 2)  # Увеличиваем exp_base для следующего уровня
            console.print(f"[bright_cyan]{self.name} повышает уровень до {self.level}![/bright_cyan]")
            console.print(f"[bright_cyan]Требуется опыта для следующего уровня: {self.exp_base}[/bright_cyan]")

    def attack(self, *, target: "Character") -> None:
        print(f"{self.name} атакует {target.name}")
        target.got_damage(damage=self.attack_power)
        if target.is_alive():
            print(f"{self.name}, HP={self.health_points} | {target.name}, HP={target.health_points}")
        else:
            print(f"{target.name} погибает!")
            self.gain_experience(target=target)  # Теперь gain_experience сам вызывает level_up
            self.count_kill += 1
            if isinstance(target, Mob):
                self.money += target.money

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
        """Использует предмет из инвентаря с удобным интерфейсом"""
        try:
            # Проверка корректности номера предмета
            if number_item < 0 or number_item >= len(self.inventory):
                raise IndexError("Номер предмета выходит за границы инвентаря")

            item = self.inventory[number_item]

            # Обработка экипировки
            if isinstance(item, Equipment):
                slot = item.slot

                # Если в слоте уже есть предмет - сообщаем о снятии
                if self.equipment[slot] is not None:
                    old_item = self.equipment[slot]
                    self.inventory.append(old_item)
                    console.print(f"\n[yellow3]Снят предмет: {old_item.name}[/yellow3]")

                # Экипируем новый предмет
                self.equipment[slot] = item
                self.inventory.pop(number_item)
                self.update_stats()

                console.print(
                    f"\n[green]====================================[/green]"
                    f"\n[green]Экипирован предмет: {item.name} ({slot})[/green]"
                    f"\n[green]====================================[/green]"
                )

            # Обработка стакающихся предметов (зелий и т.д.)
            elif isinstance(item, StackableItem):
                # Применяем эффект
                if item.effect == "heal":
                    heal_amount = min(item.effect_heal, self.max_health_points() - self.health_points)
                    self.health_points += heal_amount

                    console.print(
                        f"\n[green]====================================[/green]"
                        f"\n[green]Использовано: {item.name}[/green]"
                        f"\n[green]Восстановлено: {heal_amount} здоровья[/green]"
                        f"\n[green]Осталось: {item.quantity - 1} шт.[/green]"
                        f"\n[green]====================================[/green]"
                    )

                # Уменьшаем количество
                item.quantity -= 1

                # Если предмет закончился - удаляем из инвентаря
                if item.quantity <= 0:
                    self.inventory.pop(number_item)

            # Обработка обычных предметов
            else:
                if item.effect == "heal":
                    heal_amount = min(item.effect_heal, self.max_health_points() - self.health_points)
                    self.health_points += heal_amount

                    console.print(
                        f"\n[green]====================================[/green]"
                        f"\n[green]Использовано: {item.name}[/green]"
                        f"\n[green]Восстановлено: {heal_amount} здоровья[/green]"
                        f"\n[green]====================================[/green]"
                    )

                # Удаляем предмет после использования
                self.inventory.pop(number_item)

            # Ждем подтверждения от игрока
            input("\nНажмите Enter чтобы продолжить...")

        except IndexError as e:
            console.print(f"[red]Ошибка: {str(e)}[/red]")
            input("\nНажмите Enter чтобы продолжить...")
        except Exception as e:
            console.print(f"[red]Неизвестная ошибка при использовании предмета: {str(e)}[/red]")
            input("\nНажмите Enter чтобы продолжить...")

    def _use_equipment(self, item: Equipment, slot_index: int) -> None:
        """Вспомогательный метод для использования экипировки"""
        slot = item.slot

        # Если в слоте уже есть предмет - сообщаем о снятии
        if self.equipment[slot] is not None:
            old_item = self.equipment[slot]
            self.inventory.append(old_item)
            console.print(f"\n[yellow3]Снят предмет: {old_item.name}[/yellow3]")

        # Экипируем новый предмет
        self.equipment[slot] = item
        self.inventory.pop(slot_index)
        self.update_stats()

        console.print(
            f"\n[green]====================================[/green]"
            f"\n[green]Экипирован предмет: {item.name} ({slot})[/green]"
            f"\n[green]====================================[/green]"
        )

    def _use_stackable_item(self, item: StackableItem, item_index: int) -> None:
        """Вспомогательный метод для использования стакающихся предметов"""
        # Применяем эффект
        if item.effect == "heal":
            heal_amount = min(item.effect_heal, self.max_health_points() - self.health_points)
            self.health_points += heal_amount

            console.print(
                f"\n[green]====================================[/green]"
                f"\n[green]Использовано: {item.name}[/green]"
                f"\n[green]Восстановлено: {heal_amount} здоровья[/green]"
                f"\n[green]Осталось: {item.quantity - 1} шт.[/green]"
                f"\n[green]====================================[/green]"
            )

        # Уменьшаем количество
        item.quantity -= 1

        # Если предмет закончился - удаляем из инвентаря
        if item.quantity <= 0:
            self.inventory.pop(item_index)

    def _use_regular_item(self, item: Item, item_index: int) -> None:
        """Вспомогательный метод для обычных предметов"""
        if item.effect == "heal":
            heal_amount = min(item.effect_heal, self.max_health_points() - self.health_points)
            self.health_points += heal_amount

            console.print(
                f"\n[green]====================================[/green]"
                f"\n[green]Использовано: {item.name}[/green]"
                f"\n[green]Восстановлено: {heal_amount} здоровья[/green]"
                f"\n[green]====================================[/green]"
            )

        # Удаляем предмет после использования
        self.inventory.pop(item_index)

    def remove_item(self, slot: str) -> None:
        """Снимает предмет экипировки с выводом информации"""
        if slot in self.equipment and self.equipment[slot] is not None:
            removed_item = self.equipment[slot]
            self.equipment[slot] = None
            self.inventory.append(removed_item)
            self.update_stats()

            console.print(
                f"\n[yellow3]====================================[/yellow3]"
                f"\n[yellow3]Снят предмет: {removed_item.name}[/yellow3]"
                f"\n[yellow3]Из слота: {slot}[/yellow3]"
                f"\n[yellow3]====================================[/yellow3]"
            )

            # Ждем подтверждения от игрока
            input("\nНажмите Enter чтобы продолжить...")
        else:
            console.print(f"[red]Ошибка: В слоте '{slot}' нет экипированного предмета.[/red]")
            input("\nНажмите Enter чтобы продолжить...")

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

    def move_to_location(self, new_location, ui=None):
        if self.location.name == "Город":
            self.set_location(new_location)
            if ui:
                ui.add_message(f"[green]Вы переместились в '{self.location.name}'![/green]")
            else:
                console.print(f"[green]Вы переместились в '{self.location.name}'![/green]")
        elif new_location.name == "Город":
            self.set_location(new_location)
            if ui:
                ui.add_message(f"[green]Вы вернулись в 'Город'![/green]")
            else:
                console.print(f"[green]Вы вернулись в 'Город'![/green]")
        else:
            if ui:
                ui.add_message(f"[red]Вы можете перемещаться только в 'Город' из '{self.location.name}'![/red]")
            else:
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

        # Проверяем, есть ли уже такой квест в активных или завершенных
        existing_active = next((q for q in self.active_quests if q.id == quest_data["id"]), None)
        existing_completed = next((q for q in self.completed_quests if q.id == quest_data["id"]), None)

        # Для одноразовых квестов проверяем, был ли он уже выполнен
        if quest_data["quest_type"] == "single" and existing_completed:
            console.print("[red]Этот квест уже был выполнен и больше недоступен[/red]")
            return False

        # Если квест уже активен, проверяем можно ли его повторить
        if existing_active:
            if existing_active.quest_type == "single":
                console.print("[red]Этот квест уже активен[/red]")
                return False
            elif not existing_active.can_be_repeated():
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

        if quest.quest_type == "single":
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
        else:
            quest.current_amount = 0
            quest.is_completed = False

    def show_quests(self) -> None:
        """Показывает активные и завершенные квесты"""
        try:
            clear_screen()
            active_quests_panel = self._create_quests_panel(self.active_quests, "Активные квесты", "yellow")
            completed_quests_panel = self._create_quests_panel(self.completed_quests, "Завершенные квесты", "green")

            console.print(Columns([active_quests_panel, completed_quests_panel], expand=True))
            input("\nНажмите Enter чтобы вернуться в меню...")
        except Exception as e:
            console.print(f"[red]Ошибка при показе квестов: {str(e)}[/red]")
            input("Нажмите Enter чтобы продолжить...")

    def _create_quests_panel(self, quests: list, title: str, color: str) -> Panel:
        """Создает панель с квестами"""
        quests_text = Text()

        if not quests:
            quests_text.append("Нет квестов", style="italic")
        else:
            for i, quest in enumerate(quests, 1):
                # Для активных квестов показываем прогресс
                if title == "Активные квесты":
                    status = Text("Готово к сдаче!", style="green") if self.is_quest_ready_to_complete(
                        quest.id) else f"{quest.current_amount}/{quest.target_amount}"
                    quests_text.append(f"{i}. {quest.name} - ")
                    quests_text.append(status)
                    quests_text.append("\n")
                    quests_text.append(f"   Описание: {quest.description}\n")
                    quests_text.append(f"   Награда: {quest.reward_exp} опыта и {quest.reward_money} монет\n"
                                       f"   Для сдачи квеста введите у {quest.giver} '[с]дать {i}'")
                # Для завершенных - просто список
                else:
                    quests_text.append(f"{i}. {quest.name}\n", style=color)

        return Panel(quests_text, title=title, border_style=color)

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