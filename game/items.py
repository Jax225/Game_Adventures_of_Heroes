# game/items.py
from copy import deepcopy
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