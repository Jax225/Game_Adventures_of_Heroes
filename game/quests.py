# game/quests.py
from datetime import datetime

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

