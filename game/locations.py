# game/locations.py

class Location:
    def __init__(self, name: str, description: str, danger_level: int, zone_type: str, id_loc: int) -> None:
        self.name = name
        self.description = description
        self.danger_level = danger_level
        self.zone_type = zone_type  # Новый параметр для типа зоны
        self.id_loc = id_loc

    def __str__(self):
        return f"{self.name}: {self.description} (Уровень опасности: {self.danger_level}, Тип зоны: {self.zone_type})"



#База данных локаций
location_database = [
    Location(name="Город", description="Место, полное жизни и возможностей.", danger_level=1, zone_type="peaceful", id_loc="1"),
    Location(name="Зачарованный лес", description="Лес, полный магии и тайн. Уровни монстров: (5-7)", danger_level=3, zone_type="combat", id_loc="2"),
    Location(name="Безлюдная пустыня", description="Широкие песчаные дюны и отсутствие жизни.Уровни монстров: (10-13)", danger_level=4, zone_type="combat", id_loc="3"),
    Location(name="Храм", description="Древний храм, хранящий множество секретов.Уровни монстров: (1)", danger_level=2, zone_type="combat", id_loc="4"),

]