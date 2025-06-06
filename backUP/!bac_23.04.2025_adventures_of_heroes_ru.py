import time
import random
import json
import os
from copy import deepcopy
from rich.console import Console

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
        self.location = "start_location"
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

    def __str__(self):
        return f"Class: {self.get_class_hero()}. Name:'{self.name}', level: {self.level} HP: {self.health_points}"

    def hero_stats(self) -> str:
        equipment_str = "\n".join(f"{slot}: {item or '[]'}" for slot, item in self.equipment.items())
        massage_hero_stats = (
            f"------Характеристики игрока----------\n"
            f"Имя Вашего героя: '{self.name}', [yellow3]Уровень:[/yellow3][yellow3] {self.level}[/yellow3]\n"
            f"Количество здоровья: {self.health_points} из {self.max_health_points()}\n"
            f"Защита героя: {self.defence}\n"
            f"Атака героя: {self.attack_power}\n"
            f"Опыт героя: {self.experience} из {self.exp_base * 2} до следующего уровня\n"
            f"Класс вашего героя: '{self.class_character}'\n"
            f"Количество убитых врагов: {self.count_kill}\n"
            f"Снаряжение Вашего героя:\n{equipment_str}"
        )
        return massage_hero_stats

    def hero_inventory(self) -> None:
        print(f"---------------------\n"
              f"Содержимое инвентаря:\n"
              f"---------------------"
              )
        i = 1
        for inventory_item in self.inventory:
            print(f"Ячейка № {i}: '{inventory_item}'")
            i += 1



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
            if target.get_class_hero() == "Mob":
                for loot in target.inventory:
                    self.add_item(item=loot)
                    console.print(f"[yellow3]'{self.name}' получает: '{loot}'[/yellow3]")
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
            self.equipment[slot] = item
            self.update_stats()
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
        self.inventory.pop(number_item)
        if self.health_points > self.max_health_points():
            self.health_points = self.max_health_points()

    def get_all_params_for_save(self) -> dict:
        save_hero = {
            'name': self.name,
            'level': self.level,
            'health_points': self.health_points,
            'attack_power': self.attack_power,
            'defence': self.defence,
            'experience': self.experience,
            'exp_base': self.exp_base,
            'count_kill': self.count_kill,
            'location': self.location,
            'class_character': self.class_character,
            'inventory': self.get_list_id_item_from_save(self.inventory),  # Передаем self.inventory
            'equipment': self.get_list_id_item_from_save(self.equipment.values()),  # Передаем self.equipment.values()
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




#Принты для избавления от повторов
def massage_invalid_command() -> str:
    massage = (f"[dark_olive_green1]---------------------------------------------\n" + f"Неверная команда. Попробуйте ввести другую...\n" + f"---------------------------------------------[/dark_olive_green1]")
    return console.print(massage)



#Основные параметры предметов
class Item:
    def __init__(self, name: str, effect: str, effect_heal: int, chance: float, stock_price: int, id_item: int) -> None:
        self.name = name
        self.effect = effect
        self.chance = chance
        self.effect_heal = effect_heal
        self.stock_price = stock_price
        self.id_item = id_item

    def __str__(self):
        return self.name
#Основные параметры экипировки
class Equipment(Item):
    def __init__(self, name: str, slot: str, effect: str, effect_value: int, chance: float, stock_price: int, id_item: int) -> None:
        super().__init__(name, effect, 0, chance, stock_price, id_item)
        self.slot = slot
        self.effect_value = effect_value



#Базы данных
#База данных врагов
list_name_orcs = [
    'Азог', 'Балкмег', 'Болдог', 'Больг', 'Верховный Гоблин', 'Гольфимбул', 'Горбаг', 'Готмог', 'Гришнак',
    'Лагдуф', 'Луг', 'Лугдуш', 'Лурц', 'Маухур', 'Музгаш', 'Нарзуг', 'Оркобал', 'Отрод', 'Радбуг',
    'Снага', 'Углук', 'Уфтак', 'Фимбул', 'Шаграт', 'Шарку', 'Язнег'
]
item_database = [
    Item(name="Малое зелье лечения", effect="heal", effect_heal=50, chance=33.3, stock_price=10, id_item=1),  # 33.3
    Item(name="Среднее зелье лечения", effect="heal", effect_heal=100, chance=10.0, stock_price=20, id_item=2),
    # 10
    Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3),
    Equipment(name="Шлем рыцаря", slot="Голова", effect="defence", effect_value=5, chance=5.0, stock_price=100, id_item=4),
    Equipment(name="Кираса рыцаря", slot="Тело", effect="defence", effect_value=10, chance=5.0, stock_price=200, id_item=5),
    Equipment(name="Перчатки силы", slot="Руки", effect="attack", effect_value=3, chance=5.0, stock_price=75, id_item=6),
    Equipment(name="Сапоги ловкости", slot="Ноги", effect="defence", effect_value=3, chance=5.0, stock_price=75, id_item=7),
    Equipment(name="Меч воина", slot="Оружие", effect="attack", effect_value=10, chance=5.0, stock_price=150, id_item=8),
    Equipment(name="Плащ теней", slot="Плащ", effect="defence", effect_value=7, chance=5.0, stock_price=100, id_item=9),
    # 5
    # Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50, id_item=3)  # 5
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
    base_health_points = 50  # test
    base_attack_power = 8
    base_defence = 3

    def __init__(self, *, name: str, level: int, item_database: list) -> None:
        super().__init__(name, level)
        self.inventory = generate_inventory(item_database)
#class Mob_mini(Mob)
#Отдельные функции

def spawn_mob():
    name = list_name_orcs[int(random.uniform(0, len(list_name_orcs)))]
    new_spawn_mob = Mob(name=name, level=1, item_database=item_database)
    return new_spawn_mob


def fight(*, charcter1: Character, charcter2: Character):
    while charcter1.is_alive() and charcter2.is_alive():
        charcter1.attack(target=charcter2)
        if charcter2.is_alive():
            charcter2.attack(target=charcter1)
        time.sleep(0.1)  # время задержки


def fight_wiht_mob():
    new_mob = spawn_mob()
    print(f"Начинается бой с '{new_mob.name}', {new_mob.level} уровня\n"
          f"Количство здоровья '{new_mob.name}' = {new_mob.health_points}"

          )
    fight(charcter1=hero_user, charcter2=new_mob)
def generate_inventory(item_database: list, max_item=2):
    inventory = []
    for i in range(max_item):
        item = random.choice(item_database)
        # Добавляем шанс выпадения перчаток и сапог
        if isinstance(item, Equipment) and (item.slot == "Руки" or item.slot == "Ноги"):
            if random.uniform(0, 100) < 80:  # 5% шанс выпадения
                inventory.append(item)
        elif random.uniform(0, 100) < item.chance:
            inventory.append(item)
    return inventory

#Функции сохранения и загрузки
def check_file_save(dict_character: dict) -> bool:
    list_error = []

    # Проверка основных атрибутов
    if not isinstance(dict_character['name'], str):
        list_error.append("Параметр 'Имя героя' не является строкой")
    if not isinstance(dict_character['level'], int):
        list_error.append("Параметр 'уровень героя' не является целым числом")
    if not isinstance(dict_character['health_points'], int):
        list_error.append("Параметр количество жизней не является целым числом")
    if not isinstance(dict_character['attack_power'], int):
        list_error.append("Параметр 'атака' не является целым числом")
    if not isinstance(dict_character['defence'], int):
        list_error.append("Параметр 'защита' не является целым числом")
    if not isinstance(dict_character['experience'], int):
        list_error.append("Параметр 'опыт' не является целым числом")
    if not isinstance(dict_character['exp_base'], int):
        list_error.append("Параметр 'базовый опыт' не является целым числом")
    if not isinstance(dict_character['count_kill'], int):
        list_error.append("Параметр 'количество убийств' не является целым числом")
    if not isinstance(dict_character['location'], str):
        list_error.append("Параметр 'локация' не является строкой")
    if not isinstance(dict_character['class_character'], str):
        list_error.append("Параметр 'класс героя' не является строкой")
    if not isinstance(dict_character['now_time'], int):
        list_error.append("Параметр 'время сохранения' не является целым числом")

    # Проверка инвентаря
    if not isinstance(dict_character['inventory'], list):
        list_error.append("Параметр 'инвентарь' не является списком")
    else:
        for item_id in dict_character['inventory']:
            if not isinstance(item_id, int):
                list_error.append(f"Элемент инвентаря '{item_id}' не является целым числом")

    # Проверка снаряжения
    if not isinstance(dict_character['equipment'], list):
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


def save_in_file():
    if not os.path.isdir("save"):
        os.mkdir("save")
    with open(file="save/save.json", mode="w") as file:
        dist_for_save = hero_user.get_all_params_for_save()
        json.dump(dist_for_save, file, indent=4)


def download(*, database: list):
    try:
        with open(file="save/save.json", mode="r") as file:
            dict_character = json.load(file)
            if check_file_save(dict_character=dict_character):
                hero_after_load = load_hero_user(dict_param=dict_character, database=database)
            else:
                console.print(f"[red]--------------------------------------------------\n"
                              f"Сохранение сломано...\n"
                              f"--------------------------------------------------[/red]\n")
                hero_after_load = ''
        return hero_after_load
    except FileNotFoundError:
        print("Не найден файл с сохранениями")

def load_hero_user(*, dict_param: dict, database: list):

    loading_character_from_file = Human(name=dict_param['name'], level=dict_param['level'])
    loading_character_from_file.health_points = dict_param['health_points']
    loading_character_from_file.attack_power = dict_param['attack_power']
    loading_character_from_file.defence = dict_param['defence']
    loading_character_from_file.experience = dict_param['experience']
    loading_character_from_file.exp_base = dict_param['exp_base']
    loading_character_from_file.count_kill = dict_param['count_kill']
    loading_character_from_file.location = dict_param['location']
    loading_character_from_file.class_character = loading_character_from_file.get_class_hero()
    list_for_download_inventory = []
    for slot, item_id in zip(loading_character_from_file.equipment.keys(), dict_param['equipment']):
        for item_in_database in database:
            if item_id == item_in_database.id_item:
                loading_character_from_file.equipment[slot] = item_in_database
    for item_in_inventory in dict_param['inventory']:
        for item_in_database in database:
            if item_in_inventory == item_in_database.id_item:
                list_for_download_inventory.append(item_in_database)
    loading_character_from_file.inventory = deepcopy(list_for_download_inventory)
    loading_character_from_file.update_stats()
    return loading_character_from_file


#Здесь функция игры
def game() -> None:
    while hero_user.is_alive():
        command = input(
            f"-----------Действия игрока----------\n"
            f"'БОЙ' или 'Б' для перехода к новому бою\n"
            f"'ГЕРОЙ' или 'Г' чтобы посмотреть характеристики героя\n"
            f"'ИНВЕНТАРЬ' или 'И' чтобы посмотреть содержимое инвентаря героя\n"
            f"'СОХРАНИТЬ' или 'С' для сохранения прогресса\n"
            f"'ВЫХОД' или 'В' для выхода\n"
            f"Введите слуедущую команду: \n"
        )
        command = command.strip().lower()
        if command == "бой" or command == "б":
            fight_wiht_mob()
        elif command == "сохранить" or command == "с":
            save_in_file()
            console.print(  f"[yellow3]--------------------------------------------------\n"
                            f"Успешно сохранено\n"
                            f"--------------------------------------------------[/yellow3]\n")

        elif command == "герой" or command == "г":
            console.print(hero_user.hero_stats())
            input(
                f"--------------------------------\n"
                f"нажмите 'Enter' чтобы продолжить..\n"
            )
        elif command == "инвентарь" or command == "и":
            hero_user.hero_inventory()
            command_hero_inventory = input(f"--------------------------------------------------\n"
                                           f"Введите 'ПРЕДМЕТ' или 'П' чтобы взаимодействовать:\n"
                                           f"Или нажмите 'Enter' чтобы продолжить...\n"
                                           f"--------------------------------------------------\n"
                                           )

            command_hero_inventory = command_hero_inventory.strip().lower()
            if command_hero_inventory == 'предмет' or command_hero_inventory == "п":
                input_number_item = input(f"Введите номер ячейки чтобы использовать предмет: ")
                if input_number_item == "0":
                    print("Введите корректное значение\n"
                          "Или инвентарь пуст")
                    continue
                try:
                    hero_user.use_item(number_item=int(input_number_item) - 1)
                except IndexError:
                    print('Ячейка инвентаря пуста!')
                except:
                    print("Введите корректное значение\n"
                          "Или инвентарь пуст")
            else:
                massage_invalid_command()

        elif command == "выход" or command == "в":
            print("Выход из игры.")
            break
        else:
            massage_invalid_command()
            # print("Появление 2")
            continue
    print(f"Ваш резултат:\n"
          f"Имя Вашего героя: '{hero_user.name}', Уровень: {hero_user.level}\n"
          f"Количество убитых врагов: {hero_user.count_kill}"
          )
#Здесь конец функции игры




#Основной блок игры

console.print(f"Добро пожаловать в игру\n\n[red]--- Adventures of Heroes ---\n[/red]")

menu = ""
while menu != "выход" or menu != "в":
    menu = input(
        f"-----------Меню------------\n"
        f"Введите команду\n"
        f"'СТАРТ' или 'C' чтобы начать новую игру\n"
        f"'ЗАГРУЗИТЬ' или 'З' чтобы загрузить игру\n"
        f"'ВЫХОД' или 'В' для выхода\n"
        f"Поле ввода: "
    )
    menu = menu.strip().lower()
    if menu == "старт" or menu == "с":

        hero_user = Human(level=1, name=input(
            f"Начало новой игры!\n"
            f"Создание персонажа\n"
            f"Введите 'ВЫХОД' или 'В' если хотите выйти\n"
            f"Введите имя героя: "
        )
                          )
        quickly_check = hero_user.name.lower().strip()
        if quickly_check == "выход" or quickly_check == "в":
            print("Выход из игры.")
            break
        elif quickly_check == "":
            print(
                f"--------------------------------\n"
                "Поле не может быть пустым")
            continue

        console.print(f"Имя Ващего героя: {hero_user.name}\n"
                      f"Продолжить?")
        answer_user = input(f"'ДА','Д' или нажмите 'Enter' чтобы продолжить с этим именем.\n"
                            f"НЕТ','Н' чтобы изменить.\n"
                            f"Поле ввода: ")
        answer_user = answer_user.lower().strip()

        if answer_user == "" or answer_user == "да" or answer_user == "д":
            print(
                f"Вы только что создали героя.\n"
                f"Попробуйте атаковать кого-нибудь"
            )
            hero_user.class_character = hero_user.get_class_hero()
            #Фнкция игры| новая игра
            game()


        elif answer_user == "нет" or answer_user == "н":
            print(
                f"----------------------------------\n"
                f"Попробуйте заново...\n"
                f"----------------------------------"
            )
            continue
        else:
            massage_invalid_command()
            continue


    elif menu == "загрузить" or menu == "з":
        try:
            hero_user = download(database=item_database)
            hero_user.class_character = hero_user.get_class_hero()

            console.print(f"[yellow3]--------------------------------------------------\n"
                          f"Успешно загружено\n"
                          f"--------------------------------------------------[/yellow3]\n")
            game()
        except:
            console.print(  "[red]-----------   КАКАЯ-ТО ОШИБКА   ------------------\n"
                            "--------------------------------------------------\n"
                            "Откройте папку с игрой.\n"
                            "Рядом с файлом 'adventures_of_heroes._._.exe'\n"
                            "должна быть папка 'save'\n"
                            "В папке 'save' должен быть файл 'save.json' \n"
                            "Или файл с сохранением был испочен\n"
                            "--------------------------------------------------[/red]"
                    )

    elif menu == "выход" or menu == "в":
        print(
            f"-----------------\n"
            f"---Конец игры----\n"
            f"-----------------"
        )
        break
    else:
        massage_invalid_command()
        continue


