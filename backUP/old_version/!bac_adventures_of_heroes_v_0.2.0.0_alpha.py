import time
import random
from rich.console import Console

"""Разметка цветом"""
console = Console()

"""Основные параметры классов"""


class Character:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level
        self.health_points = self.base_health_points * level
        self.attack_power = self.base_attack_power * level
        self.defence = self.base_defence * level
        self.experience = 0
        self.inventory = []
        self.exp_base = 100
        self.count_kill = 0

    def __str__(self):
        return f"Class: {self.get_class_hero()}. Name:'{self.name}', level: {self.level} HP: {self.health_points}"

    def hero_stats(self) -> str:
        massage_hero_stats = (
            f"------Характеристики игрока----------\n"
            f"Имя Вашего героя: '{hero_user.name}', [yellow3]Уровень: {hero_user.level}[/yellow3]\n"
            f"Количество здоровья: {hero_user.health_points} из {hero_user.max_health_points()}\n"
            f"Защита героя: {hero_user.defence}\n"
            f"Атака героя: {hero_user.attack_power}\n"
            f"Опыт героя: {hero_user.experience} из {hero_user.exp_base * 2} до следующего уровня\n"
            f"Класс вашего героя: '{hero_user.get_class_hero_rus()}'\n"
            f"Количество убитых врагов: {hero_user.count_kill}"
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
            if target.get_class_hero() == "Mob":  # переделать систему получения exp
                self.experience += 100
            else:
                self.experience += 200

    def level_up(self, exp_base: int):
        exp_base = exp_base * 2
        if self.experience >= exp_base:
            self.level += 1
            self.health_points = self.base_health_points * self.level
            self.attack_power = self.base_attack_power * self.level
            self.defence = self.base_defence * self.level
            self.exp_base = exp_base
            self.experience = self.experience - exp_base
            print(f"{self.name} получает опыт и повышает уровень до {self.level}")

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
            for loot in target.inventory:
                self.add_item(item=loot)
                console.print(f"Герой получает '{loot}'")
    def max_health_points(self):
        return self.base_health_points * self.level
    def add_item(self, item: str) -> None:
        self.inventory.append(item)

    def use_item(self, *, number_item: int):
        console.print(
            f"------------------------------------\n"
            f"Ваше здоровье восполнено на {self.inventory[number_item].effect_heal} единиц!\n"
            f"------------------------------------"
        )
        self.health_points += self.inventory[number_item].effect_heal
        hero_user.inventory.pop(number_item)
        if self.health_points > self.max_health_points():
            self.health_points = self.max_health_points()

"""Основные параметры предметов"""


class Item:
    def __init__(self, name: str, effect: str, effect_heal: int, chance: float,stock_price: int) -> None:
        self.name = name
        self.effect = effect
        self.chance = chance
        self.effect_heal = effect_heal
        self.stock_price = stock_price

    def __str__(self):
        return self.name


"""Базы данных"""
"""База данных врагов"""
list_name_orcs = [
    'Азог', 'Балкмег', 'Болдог', 'Больг', 'Верховный Гоблин', 'Гольфимбул', 'Горбаг', 'Готмог', 'Гришнак',
    'Лагдуф', 'Луг', 'Лугдуш', 'Лурц', 'Маухур', 'Музгаш', 'Нарзуг', 'Оркобал', 'Отрод', 'Радбуг',
    'Снага', 'Углук', 'Уфтак', 'Фимбул', 'Шаграт', 'Шарку', 'Язнег'
]
item_database = [
    Item(name="Малое зелье лечения", effect="heal", effect_heal= 50, chance=33.3, stock_price=10), #33.3
    Item(name="Среднее зелье лечения", effect="heal", effect_heal=100, chance=10.0, stock_price=20),#10
    Item(name="Большое зелье лечения", effect="heal", effect_heal=200, chance=5.0, stock_price=50)#5
]
"""Все подклассы"""


class Human(Character):
    base_health_points = 100
    base_attack_power = 10
    base_defence = 5
    base_inventory = []


class Warrior(Character):
    base_health_points = 200
    base_attack_power = 20
    base_defence = 10
    base_inventory = []


class Mage(Character):
    base_health_points = 100
    base_attack_power = 40
    base_defence = 6
    base_inventory = []


class Mob(Character):
    base_health_points = 70  # test
    base_attack_power = 8
    base_defence = 3

    def __init__(self, *,  name: str, level: int, item_database: list) -> None:
        super().__init__(name, level)
        self.inventory = generate_inventory(item_database)



def spawn_mob():
    name = list_name_orcs[int(random.uniform(0, len(list_name_orcs)))]
    new_spawn_mob = Mob(name=name, level=1,item_database=item_database)
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
        if random.uniform(0,100) < item.chance:
            inventory.append(item)
    return inventory

"""Основной блок игры"""

console.print(f"Добро пожаловать в игру\n\n[red]--- Adventures of Heroes ---\n[/red]")

menu = ""
while menu != "выход" or menu != "в":
    menu = input(
        f"-----------Меню------------\n"
        f"Введите команду\n"
        f"'СТАРТ' или 'C' чтобы начать новую игру\n"
        f"'ВЫХОД' или 'В' для выхода\n"
        f"Поле ввода: "
    )
    menu = menu.strip().lower()
    if menu == "старт" or menu == "с":

        hero_user = Human(level=1, name=input(
            f"Начало новой игры!\n"
            f"Создание персонажа\n"
            f"Введите 'ВЫХОД'или 'В' если хотите выйти\n"
            f"Введите имя своего героя: "
        )
                          )

        quickly_check = hero_user.name.lower().strip()
        if quickly_check == "выход" or quickly_check == "в":
            print("Выход из игры.")
            break
        if quickly_check == "":
            print(
                f"--------------------------------\n"
                "Поле не может быть пустым")
            continue
        print(
            f"Вы только что создали своего героя.\n"
            f"Попробуйте атаковать кого-нибудь"
        )
        command = ""
        while hero_user.is_alive():
            command = input(
                f"-----------Действия игрока----------\n"
                f"'БОЙ' или 'Б' для перехода к новому бою\n"
                f"'ГЕРОЙ' или 'Г' чтобы посмотреть характеристики героя\n"
                f"'ИНВЕНТАРЬ' или 'И' чтобы посмотреть содержимое инвентаря героя\n"
                f"'ВЫХОД' или 'В' для выхода\n"
                f"Введите слуедущую команду: \n"
            )
            command = command.strip().lower()
            if command == "бой" or command == "б":
                fight_wiht_mob()
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
                                               f"Или нажмите 'Enter' чтобы продолжить..\n"
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

            elif command == "выход" or command == "в":
                print("Выход из игры.")
                break
            else:
                print(
                    f"----------------------------------\n"
                    f"Неверная команда. Попробуйте другую.\n"
                    f"----------------------------------"
                )
                continue
        print(f"Ваш резултат:\n"
              f"Имя Вашего героя: '{hero_user.name}', Уровень: {hero_user.level}\n"
              f"Количество убитых врагов: {hero_user.count_kill}"
              )
    elif menu == "выход" or menu == "в":
        print(
            f"-----------------\n"
            f"---Конец игры----\n"
            f"-----------------"
        )
        break
    else:
        print(
            f"----------------------------------\n"
            f"Неверная команда. Попробуйте другую\n"
            f"----------------------------------"
        )
        continue


