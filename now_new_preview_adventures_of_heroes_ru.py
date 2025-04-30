import time
import random
import json
import os
from copy import deepcopy
from rich.console import Console
from datetime import datetime

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

        # Вывод инвентаря
        inventory_items = "\n".join(
            [f"{i + 1}. {item.name}" for i, item in enumerate(self.inventory)]) if self.inventory else "Инвентарь пуст."

        console.print(f"[green]{stats}[/green]\n[blue]{equipment}[/blue]\n[blue]Инвентарь:\n{inventory_items}[/blue]")

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
                    self.add_item(item=loot)
                    console.print(f"[yellow3]{self.name} получает: '{loot}'[/yellow3]")
            else:
                if len(target.inventory) != 0:
                    target.inventory.pop(int(random.uniform(0, len(target.inventory))))


    def max_health_points(self):
        return self.base_health_points * self.level
    def add_item(self, item: str) -> None:
        self.inventory.append(item)

    def use_item(self, *, number_item: int):
        item = self.inventory[number_item]
        if isinstance(item, Equipment):
            slot = item.slot

            # Проверяем, есть ли уже предмет в этом слоте
            if self.equipment[slot] is not None:
                # Если есть, перемещаем старый предмет в инвентарь
                old_item = self.equipment[slot]
                self.inventory.append(old_item)  # Добавляем старый предмет в инвентарь
                console.print(
                    f"[yellow3]Старый предмет '{old_item.name}' перемещен в инвентарь.[/yellow3]"
                )

            # Экипируем новый предмет
            self.equipment[slot] = item
            self.update_stats()  # Обновляем характеристики
            console.print(
                f"------------------------------------\n"
                f"Вы экипировали {item.name} в слот '{slot}'\n"
                f"------------------------------------"
            )
        else:
            self.health_points += item.effect_heal
            console.print(
                f"------------------------------------\n"
                f"Ваше здоровье восполнено на {item.effect_heal} единиц!\n"
                f"------------------------------------"
            )

        self.inventory.pop(number_item)  # Удаляем предмет из инвентаря
        if self.health_points > self.max_health_points():
            self.health_points = self.max_health_points()

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
            'version': 3,  # Обновляем версию на 3
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
            'inventory': self.get_list_id_item_from_save(self.inventory),
            'equipment': self.get_list_id_item_from_save(self.equipment.values()),
            'money': self.money,  # Сохраняем количество денег
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
#Основные параметры экипировки
class Equipment(Item):
    def __init__(self, name: str, slot: str, effect: str, effect_value: int, chance: float, stock_price: int, id_item: int, mob_chances: dict = None) -> None:
        super().__init__(name, effect, 0, chance, stock_price, id_item, mob_chances)
        self.slot = slot
        self.effect_value = effect_value



#Базы данных
#База данных врагов
list_name_orcs = [
    'Внизуда','Азог', 'Балкмег', 'Болдог', 'Больг', 'Верховный Гоблин', 'Гольфимбул', 'Горбаг', 'Готмог', 'Гришнак',
    'Лагдуф', 'Луг', 'Лугдуш', 'Лурц', 'Маухур', 'Музгаш', 'Нарзуг', 'Оркобал', 'Отрод', 'Радбуг',
    'Снага', 'Углук', 'Уфтак', 'Фимбул', 'Шаграт', 'Шарку', 'Язнег'
]
#База данных предметов
item_database = [
    Item(name="Малое зелье лечения", effect="heal", effect_heal=50, chance=33.3, stock_price=10, id_item=1,mob_chances={"Азог":50}),  # 33.3
    Item(name="Среднее зелье лечения", effect="heal", effect_heal=100, chance=10.0, stock_price=20, id_item=2, mob_chances={"Азог":20,"Балкмег":30}),# 10
    Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3, mob_chances={"Азог":10,"Балкмег":18}),
    Equipment(name="Шлем рыцаря", slot="Голова", effect="defence", effect_value=5, chance=5.0, stock_price=100, id_item=4),
    Equipment(name="Кираса рыцаря", slot="Тело", effect="defence", effect_value=10, chance=5.0, stock_price=200, id_item=5,mob_chances={"Балкмег":7}),
    Equipment(name="Перчатки силы", slot="Руки", effect="attack", effect_value=3, chance=5.0, stock_price=75, id_item=6),
    Equipment(name="Сапоги ловкости", slot="Ноги", effect="defence", effect_value=3, chance=5.0, stock_price=75, id_item=7),
    Equipment(name="Меч воина", slot="Оружие", effect="attack", effect_value=10, chance=5.0, stock_price=150, id_item=8),
    Equipment(name="Плащ теней", slot="Плащ", effect="defence", effect_value=7, chance=5.0, stock_price=100, id_item=9,mob_chances={"Балкмег":7}),# 5
    Equipment(name="Старые перчатки", slot="Руки", effect="defence", effect_value=1, chance=20.0, stock_price=8, id_item=10),
    Equipment(name="Старые сапоги", slot="Ноги", effect="defence", effect_value=2, chance=2.0, stock_price=8, id_item=11,mob_chances={"Внизуда":0}),
    # Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3)  # 5
]


#База данных локаций
location_database = [
    Location(name="Город", description="Место, полное жизни и возможностей.", danger_level=1, zone_type="peaceful", id_loc="1"),
    Location(name="Зачарованный лес", description="Лес, полный магии и тайн. Уровни монстров: (5-7)", danger_level=3, zone_type="combat", id_loc="2"),
    Location(name="Безлюдная пустыня", description="Широкие песчаные дюны и отсутствие жизни.Уровни монстров: (10-13)", danger_level=4, zone_type="combat", id_loc="3"),
    Location(name="Храм", description="Древний храм, хранящий множество секретов.Уровни монстров: (1)", danger_level=2, zone_type="combat", id_loc="4"),

]

# Создаем экземпляр локации "Храм"
# temple_location = Location(name="Храм", description="Древний храм, хранящий множество секретов.", danger_level=4, zone_type="combat")

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
        allowed_item_ids = [1, 2, 6, 7, 10, 11]  # Предметы, которые могут выпадать от монстров в храме [1, 2, 6, 7, 10, 11]
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

    # Фильтруем предметы из базы данных по allowed_item_ids
    filtered_items = [item for item in item_database if item.id_item in allowed_item_ids]

    # Генерируем инвентарь
    for _ in range(max_item):
        item = random.choice(filtered_items)  # Выбираем случайный предмет из отфильтрованных

        # Получаем шанс на выпадение предмета для данного монстра
        chance = item.mob_chances.get(mob_name, item.chance)  # Если шанса нет, используем стандартный шанс

        # Проверяем шанс на выпадение предмета
        if random.uniform(0, 100) < chance:
            inventory.append(item)

    return inventory

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
    list_error = []

    # Проверка версии
    if 'version' not in dict_character or dict_character['version'] != 3:
        list_error.append("Неверная версия сохранения. Сохранения, созданные до обновления версии, не будут совместимы с этой версией игры.")

    # Проверка основных атрибутов
    if not isinstance(dict_character.get('name'), str):
        list_error.append("Параметр 'Имя героя' не является строкой")
    if not isinstance(dict_character.get('level'), int):
        list_error.append("Параметр 'уровень героя' не является целым числом")
    if not isinstance(dict_character.get('health_points'), int):
        list_error.append("Параметр количество жизней не является целым числом")
    if not isinstance(dict_character.get('attack_power'), int):
        list_error.append("Параметр 'атака' не является целым числом")
    if not isinstance(dict_character.get('defence'), int):
        list_error.append("Параметр 'защита' не является целым числом")
    if not isinstance(dict_character.get('experience'), int):
        list_error.append("Параметр 'опыт' не является целым числом")
    if not isinstance(dict_character.get('exp_base'), int):
        list_error.append("Параметр 'базовый опыт' не является целым числом")
    if not isinstance(dict_character.get('count_kill'), int):
        list_error.append("Параметр 'количество убийств' не является целым числом")
    if not isinstance(dict_character.get('location'), str):
        list_error.append("Параметр 'локация' не является строкой")
    if not isinstance(dict_character.get('class_character'), str):
        list_error.append("Параметр 'класс героя' не является строкой")
    if not isinstance(dict_character.get('money'), int):  # Проверка на наличие денег
        list_error.append("Параметр 'деньги' не является целым числом")
    if not isinstance(dict_character.get('now_time'), int):
        list_error.append("Параметр 'время сохранения' не является целым числом")

    # Проверка инвентаря
    if not isinstance(dict_character.get('inventory'), list):
        list_error.append("Параметр 'инвентарь' не является списком")
    else:
        for item_id in dict_character['inventory']:
            if not isinstance(item_id, int):
                list_error.append(f"Элемент инвентаря '{item_id}' не является целым числом")

    # Проверка снаряжения
    if not isinstance(dict_character.get('equipment'), list):
        list_error.append("Параметр 'снаряжение' не является списком")
    else:
        for item_id in dict_character['equipment']:
            if item_id is not None and not isinstance(item_id, int):
                list_error.append(f"Элемент снаряжения '{item_id}' не является целым числом или None")

    # Вывод ошибок
    if list_error:
        for error in list_error:
            print("Ошибка в файле сохранения:", error)
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
        with open('save/save.json', 'r', encoding='utf-8') as file:
            content = file.read()
            saves = content.split("₽")  # Разбиваем по разделителю
            for save in saves:
                if save.strip():  # Игнорируем пустые строки
                    try:
                        dict_character_in_download = json.loads(save)
                        if check_file_save(dict_character_in_download):
                            list_saves.append((dict_character_in_download, "OK"))  # Добавляем корректное сохранение
                        else:
                            list_saves.append((dict_character_in_download, "Ошибка"))  # Добавляем поврежденное сохранение
                    except json.JSONDecodeError as e:
                        print("Ошибка при декодировании JSON:", e)
                        list_saves.append((save, "Ошибка"))  # Добавляем строку с ошибкой
    except FileNotFoundError:
        print("Файл сохранения не найден.")
    return list_saves


def download(database: list):
    list_saves = get_list_all_saves()
    if not list_saves:
        print("Нет доступных сохранений.")
        return None

    # Отображаем все сохранения с их статусами
    for index, (save, status) in enumerate(list_saves, start=1):
        if isinstance(save, dict):  # Проверяем, что это словарь
            name = save.get('name', 'Unknown')
            level = save.get('level', 'Unknown')
            time_saved = save.get('now_time', 0)
            time_formatted = datetime.fromtimestamp(time_saved).strftime('%d-%m-%Y %H:%M:%S') # strftime('%d-%m-%Y %H:%M:%S')
            print(
                f"Ячейка сохранения № {index}: Имя: {name} Уровень: {level} Дата: {time_formatted}: Статус: {status}")
        else:
            print(f"Ячейка сохранения № {index}: Статус: {status} (не удалось загрузить данные)")

    # Получаем выбор пользователя
    while True:
        try:
            choice_user = int(input("Введите номер ячейки для загрузки: "))  # Получаем выбор пользователя
            selected_save, status = list_saves[choice_user - 1]

            if status == "OK":
                if check_file_save(dict_character=selected_save):
                    hero_after_load = load_hero_user(dict_param=selected_save, database=database)
                    if hero_after_load is not None:  # Проверяем, что загрузка прошла успешно
                        return hero_after_load
                    else:
                        print("Ошибка: не удалось загрузить героя.")
                        return None
                else:
                    print("Сохранение сломано...")
                    return None
            else:
                print("Ошибка: сохранение повреждено.")
                return None
        except (IndexError, ValueError) as e:
            print("Неверный выбор сохранения. Пожалуйста, введите корректный номер ячейки.")


def load_hero_user(*, dict_param: dict, database: list):
    loading_character_from_file = Human(name=dict_param['name'], level=dict_param['level'])
    loading_character_from_file.health_points = dict_param['health_points']
    loading_character_from_file.attack_power = dict_param['attack_power']
    loading_character_from_file.defence = dict_param['defence']
    loading_character_from_file.experience = dict_param['experience']
    loading_character_from_file.exp_base = dict_param['exp_base']
    loading_character_from_file.count_kill = dict_param['count_kill']
    loading_character_from_file.money = dict_param['money']  # Загружаем количество денег

    # Загрузка локации
    location_name = dict_param['location']
    loading_character_from_file.location = next(
        (loc for loc in location_database if loc.name == location_name),
        None
    )

    # Если локация не найдена или пустая, устанавливаем "Город"
    if loading_character_from_file.location is None or loading_character_from_file.location.name == "":
        loading_character_from_file.location = next(loc for loc in location_database if loc.name == "Город")

    loading_character_from_file.class_character = dict_param['class_character']

    # Load equipment
    for slot, item_id in zip(loading_character_from_file.equipment.keys(), dict_param['equipment']):
        if item_id is not None:
            item = next((item for item in database if item.id_item == item_id), None)
            loading_character_from_file.equipment[slot] = item

    # Load inventory
    loading_character_from_file.inventory = [
        next((item for item in database if item.id_item == item_id), None)
        for item_id in dict_param['inventory']
    ]

    loading_character_from_file.update_stats()
    return loading_character_from_file

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
            command_hero_inventory = input(f"--------------------------------------------------\n"
                                           f"Введите 'ПРЕДМЕТ' или 'П' чтобы взаимодействовать:\n"
                                           f"Введите 'СНЯТЬ' или 'С' для снятия предмета:\n"
                                           f"Введите 'ВЫБРОСИТЬ' или 'В' чтобы выбросить предмет:\n"
                                           f"Или нажмите 'Enter' чтобы продолжить...\n"
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

            elif command_hero_inventory in ['выбросить', 'в']:
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
        try:
            hero_user = download(database=item_database)
            if hero_user is None:
                print("Не удалось загрузить героя. Пожалуйста, попробуйте снова.")
            else:
                hero_user.class_character = hero_user.get_class_hero()

            console.print(f"[yellow3]--------------------------------------------------\n"
                          f"Успешно загружено\n"
                          f"--------------------------------------------------[/yellow3]\n")
            game()
        except Exception as e:  # Ловим все исключения
            console.print(f"[red]-----------   КАКАЯ-ТО ОШИБКА   ------------------\n"
                          "--------------------------------------------------\n"
                          "Откройте папку с игрой.\n"
                          "Рядом с файлом 'adventures_of_heroes._._.exe'\n"
                          "должна быть папка 'save'\n"
                          "В папке 'save' должен быть файл 'save.json' \n"
                          "Или файл с сохранением был испорчен\n"
                          f"Ошибка: {str(e)}\n"  # Выводим текст ошибки для отладки
                          "--------------------------------------------------[/red]"
            )

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
