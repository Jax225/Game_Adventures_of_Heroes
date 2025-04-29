import time
import random
"""Основные параметры классов персонажей"""
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
    def get_class_hero(self) -> str:
        return self.__class__.__name__
    def is_alive(self) -> bool:
        return self.health_points > 0
    def got_damage(self, *, damage: int) -> None:
        damage = damage * (100 - self.defence) / 100
        damage = round(damage)
        self.health_points -= damage
    def gain_experience(self, *, target: "Character") -> None:
        if not (target.is_alive()):
            if target.get_class_hero() == "Mob":
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
            print(f"{target.name} is Die!")
            self.gain_experience(target=target)
            self.count_kill += 1
            self.level_up(exp_base=self.exp_base)
    def add_item(self, item: str) -> None:
        self.inventory.append(item)
"""Основные параметры предметов"""
class Item:
    def __init__(self, *, name: str, effect: str) -> None:
        self.name = name
        self.effect = effect
    def __str__(self):
        return f"Имя предмета '{self.name}', свойство предмета '{self.effect}'"
"""Базы данных"""
"""База данных врагов"""
list_name_orcs = ['Азог', 'Балкмег', 'Болдог', 'Больг', 'Верховный Гоблин', 'Гольфимбул', 'Горбаг', 'Готмог', 'Гришнак',
                  'Лагдуф', 'Луг', 'Лугдуш', 'Лурц', 'Маухур', 'Музгаш', 'Нарзуг', 'Оркобал', 'Отрод', 'Радбуг',
                  'Снага', 'Углук', 'Уфтак', 'Фимбул', 'Шаграт', 'Шарку', 'Язнег']
"""Все подклассы"""
class Human(Character):
    base_health_points = 100
    base_attack_power = 10
    base_defence = 5
class Warrior(Character):
    base_health_points = 200
    base_attack_power = 20
    base_defence = 10
class Mage(Character):
    base_health_points = 100
    base_attack_power = 40
    base_defence = 6
class Mob(Character):
    base_health_points = 70 #test
    base_attack_power = 8
    base_defence = 3

def spawn_mob():
    name = list_name_orcs[int(random.uniform(0, len(list_name_orcs)))]
    new_spawn_mob = Mob(name=name, level=1)
    return new_spawn_mob
def fight(*, charcter1: Character, charcter2: Character, ):
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
"""Основной блок игры"""
menu = ""
while menu != "quit":
    menu = input(
        f"-----------Меню------------\n"
        f"Введите команду в теримнал\n"
        f"'NEW' чтобы начать новую игру\n"
        f"'QUIT' для выхода\n"
        f"Поле ввода:"
    )
    menu = menu.strip().lower()
    if menu == "new":
        hero_user = Human(level=1, name=input (
            f"Начало новой игры!\n"
            f"Создание персонажа\n"
            f"'QUIT' для выхода\n"
            f"Введите имя своего героя: "
                                                )
                            )
        check_quit = hero_user.name.lower().strip()
        if check_quit == "quit":
            print("User has left!")
            continue
        command = ""
        while hero_user.is_alive():
            command = input(
                f"-----------Действия игрока----------\n"
                f"'HIT' для перехода к новому бою\n"
                f"'HERO' чтобы посмотреть характеристики героя\n"
                f"'QUIT' для выхода\n"
                f"Введите слуедущую команду:\n"
            )
            command = command.strip().lower()
            if command == "hit":
                fight_wiht_mob()
            elif command == "hero":
                print(
                    f"------Характеристики игрока----------\n"
                    f"Имя Вашего героя: '{hero_user.name}', Уровень: {hero_user.level}\n"
                    f"Количество здоровья: {hero_user.health_points}\n"
                    f"Защита героя: {hero_user.defence}\n"
                    f"Атака героя: {hero_user.attack_power}\n"
                    f"Опыт героя: {hero_user.experience} из {hero_user.exp_base * 2} до следующего уровня\n"
                    f"Класс вашего героя: '{hero_user.get_class_hero()}'\n"
                    f"Количество убитых вравов: {hero_user.count_kill}"
                )
            elif command == "quit":
                print("User has left!")
                break
            else:
                print(
                    f"----------------------------------\n"
                    f"Неверная команда. Попробуйте другую\n"
                    f"----------------------------------"
                )
                continue
        print(f"Ваш резултат:\n"
              f"Имя Вашего героя: '{hero_user.name}', Уровень: {hero_user.level}\n"
              f"Количество убитых вравов: {hero_user.count_kill}"
              )
    elif menu == "quit":
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