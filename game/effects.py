# game/effects.py
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.box import ROUNDED
from typing import Optional, Dict, Any
from enum import Enum
import time

#Разметка цветом
console = Console()


class EffectType(Enum):
    """Типы эффектов"""
    BUFF = "buff"  # Положительный эффект
    DEBUFF = "debuff"  # Отрицательный эффект


class Effect:
    """Базовый класс для эффектов"""

    def __init__(
        self,
        effect_id: int,
        name: str,
        description: str,
        effect_type: EffectType,
        duration: float,
        max_stacks: int = 1,
        is_permanent: bool = False,
        attack_modifier: int = 0,
        defense_modifier: int = 0,
        health_modifier: int = 0,
        speed_modifier: int = 0,
        damage_per_second: int = 0,
        heal_per_second: int = 0,
        heal_percent_per_second: float = 0.0,  # Новый параметр - восстановление в % от макс. здоровья
        tick_interval: float = 1.0,
        is_stunned: bool = False,
        is_poisoned: bool = False,
        is_burning: bool = False,
        is_frozen: bool = False,
        is_silenced: bool = False,
        is_invisible: bool = False,
        is_bleeding: bool = False,
    ):
        """
        Инициализация эффекта

        :param effect_id: Уникальный идентификатор эффекта
        :param name: Название эффекта
        :param description: Описание эффекта
        :param effect_type: Тип эффекта (BUFF/DEBUFF)
        :param duration: Длительность эффекта в секундах (0 для постоянных)
        :param max_stacks: Максимальное количество стаков эффекта
        :param is_permanent: Является ли эффект постоянным
        :param attack_modifier: Изменение атаки
        :param defense_modifier: Изменение защиты
        :param health_modifier: Изменение здоровья
        :param speed_modifier: Изменение скорости
        :param damage_per_second: Урон в секунду
        :param heal_per_second: Лечение в секунду
        :param tick_interval: Интервал между тиками эффекта
        :param is_stunned: Оглушение
        :param is_poisoned: Отравление
        :param is_burning: Горение
        :param is_frozen: Заморозка
        :param is_silenced: Немота
        :param is_invisible: Невидимость
        :param is_bleeding: Кровотечение
        """
        self.id = effect_id
        self.name = name
        self.description = description
        self.type = effect_type
        self.duration = duration
        self.max_stacks = max_stacks
        self.is_permanent = is_permanent
        self.stacks = 1
        self.start_time = time.time()
        self.end_time = self.start_time + duration if not is_permanent else None

        # Модификаторы характеристик
        self.attack_modifier = attack_modifier
        self.defense_modifier = defense_modifier
        self.health_modifier = health_modifier
        self.heal_percent_per_second = heal_percent_per_second
        self.speed_modifier = speed_modifier

        # Флаги особых эффектов
        self.is_stunned = is_stunned
        self.is_poisoned = is_poisoned
        self.is_burning = is_burning
        self.is_frozen = is_frozen
        self.is_silenced = is_silenced
        self.is_invisible = is_invisible
        self.is_bleeding = is_bleeding

        # Дополнительные параметры
        self.damage_per_second = damage_per_second
        self.heal_per_second = heal_per_second
        self.tick_interval = tick_interval
        self.last_tick_time = self.start_time

    def __str__(self):
        return f"{self.name} ({self.stacks}x) - {self.description}"

    def is_expired(self) -> bool:
        """Проверяет, истекло ли время действия эффекта"""
        if self.is_permanent:
            return False
        return time.time() >= self.end_time

    def remaining_time(self) -> float:
        """Возвращает оставшееся время действия эффекта"""
        if self.is_permanent:
            return float('inf')
        return max(0, self.end_time - time.time())

    def can_stack(self) -> bool:
        """Можно ли добавить стак этого эффекта"""
        return self.stacks < self.max_stacks

    def add_stack(self) -> bool:
        """Добавляет стак эффекта (если возможно)"""
        if self.can_stack():
            self.stacks += 1
            # Обновляем время окончания для временных эффектов
            if not self.is_permanent:
                self.end_time = time.time() + self.duration
            return True
        return False

    def update(self, character: Any) -> bool:
        """Обновляет состояние эффекта"""
        current_time = time.time()

        # Проверяем, нужно ли применять эффект
        if current_time - self.last_tick_time >= self.tick_interval:
            self.last_tick_time = current_time

            # Лечение
            if self.heal_per_second > 0:
                heal_amount = self.heal_per_second * self.stacks
                character.health_points = min(
                    character.max_health_points(),
                    character.health_points + heal_amount
                )
                # Выводим сообщение только в бою
                if hasattr(character, 'in_battle') and character.in_battle:
                    console.print(f"[green]{character.name} восстанавливает {heal_amount} HP[/green]")

        return self.is_expired()

    def apply_instant_effect(self, character: Any) -> None:
        """Применяет мгновенный эффект при наложении"""
        # Модификация характеристик
        if self.attack_modifier != 0:
            character.attack_power += self.attack_modifier * self.stacks

        if self.defense_modifier != 0:
            character.defence += self.defense_modifier * self.stacks

        if self.health_modifier != 0:
            max_hp = character.max_health_points()
            character.health_points = min(
                max_hp,
                character.health_points + (self.health_modifier * self.stacks)
            )

    def remove_effect(self, character: Any) -> None:
        """Отменяет эффект при его снятии"""
        # Возвращаем модифицированные характеристики
        if self.attack_modifier != 0:
            character.attack_power -= self.attack_modifier * self.stacks

        if self.defense_modifier != 0:
            character.defence -= self.defense_modifier * self.stacks


class EffectManager:
    """Менеджер эффектов для управления всеми активными эффектами персонажа"""
    def __init__(self):
        self.active_effects: Dict[int, Effect] = {}  # Словарь активных эффектов
        self.last_update_time = time.time()  # Время последнего обновления

    def add_effect(self, effect: Effect, character: Any) -> bool:
        """
        Добавляет новый эффект или увеличивает стак существующего
        Возвращает True, если эффект был добавлен/увеличен
        """
        # Проверяем, есть ли уже такой эффект
        existing_effect = self.active_effects.get(effect.id)

        if existing_effect:
            if existing_effect.can_stack():
                return existing_effect.add_stack()
            return False
        else:
            self.active_effects[effect.id] = effect
            effect.apply_instant_effect(character)
            return True

    def remove_effect(self, effect_id: int, character: Any) -> bool:
        """Удаляет эффект по его ID"""
        effect = self.active_effects.pop(effect_id, None)
        if effect:
            effect.remove_effect(character)
            return True
        return False

    def update_effects(self, character: Any) -> None:
        """Обновляет все активные эффекты и удаляет истекшие"""
        current_time = time.time()
        time_passed = current_time - self.last_update_time
        self.last_update_time = current_time

        effects_to_remove = []

        for effect_id, effect in self.active_effects.items():
            # Обновляем длительность эффекта
            if not effect.is_permanent:
                effect.end_time -= time_passed

            # Применяем эффекты с учетом прошедшего времени
            self._apply_effect_over_time(effect, character, time_passed)

            if effect.is_expired():
                effects_to_remove.append(effect_id)

        for effect_id in effects_to_remove:
            self.remove_effect(effect_id, character)

    def has_effect(self, effect_id: int) -> bool:
        """Проверяет, есть ли у персонажа указанный эффект"""
        return effect_id in self.active_effects

    def get_effect(self, effect_id: int) -> Optional[Effect]:
        """Возвращает эффект по его ID или None"""
        return self.active_effects.get(effect_id)

    def clear_all_effects(self, character: Any) -> None:
        """Удаляет все эффекты"""
        for effect_id in list(self.active_effects.keys()):
            self.remove_effect(effect_id, character)

    def _apply_effect_over_time(self, effect: Effect, character: Any, time_passed: float) -> None:
        """Применяет эффекты с учетом прошедшего времени"""
        # Для эффектов с периодическим действием
        current_time = time.time()
        if effect.tick_interval > 0:
            ticks = int(time_passed // effect.tick_interval)
            remaining_time = time_passed % effect.tick_interval

            for _ in range(ticks):
                self._apply_single_tick(effect, character)

            # Сохраняем остаток времени для следующего обновления
            effect.last_tick_time = current_time - remaining_time
        else:
            # Для мгновенных эффектов
            effect.update(character)

    def _apply_single_tick(self, effect: Effect, character: Any) -> None:
        """Применяет один тик эффекта"""
        # Лечение
        if effect.heal_per_second > 0:
            heal_amount = effect.heal_per_second * effect.stacks
            character.health_points = min(
                character.max_health_points(),
                character.health_points + heal_amount
            )

        # Урон
        if effect.damage_per_second > 0:
            damage = effect.damage_per_second * effect.stacks
            character.health_points = max(0, character.health_points - damage)

    def calculate_ticks(self, time_passed: float) -> int:
        #Возвращает количество тиков, которые должны произойти за прошедшее время
        if self.tick_interval <= 0:
            return 0
        return int(time_passed // self.tick_interval)



# Примеры эффектов (3 положительных и 3 отрицательных)
# Положительные эффекты
REGENERATION = Effect(
    effect_id=1,
    name="Регенерация",
    description="Восстанавливает здоровье с течением времени",
    effect_type=EffectType.BUFF,
    duration=30,
    max_stacks=3,
    heal_per_second=5
)

STRENGTH_BOOST = Effect(
    effect_id=2,
    name="Усиление силы",
    description="Увеличивает силу атаки",
    effect_type=EffectType.BUFF,
    duration=45,
    max_stacks=1,
    attack_modifier=10  # +10 к атаке
)

PROTECTION_AURA = Effect(
    effect_id=3,
    name="Аура защиты",
    description="Увеличивает защиту",
    effect_type=EffectType.BUFF,
    duration=60,
    max_stacks=1,
    defense_modifier=15  # +15 к защите
)

LONG_REGENERATION = Effect(
    effect_id=4,
    name="Долгая регенерация",
    description="Восстанавливает 5 HP каждые 3 секунд (20 минут)", # ТЕСТ ТЕСТ ТЕСТ
    effect_type=EffectType.BUFF,
    duration=1200,  # 20 минут
    max_stacks=1,
    heal_per_second=5,  # Фиксированное восстановление
    tick_interval=3.0   # Каждые 3 секунд
)


# Отрицательные эффекты
POISON = Effect(
    effect_id=101,
    name="Яд",
    description="Наносит периодический урон",
    effect_type=EffectType.DEBUFF,
    duration=20,
    max_stacks=5,
    damage_per_second=3,
    is_poisoned=True
)

WEAKNESS = Effect(
    effect_id=102,
    name="Слабость",
    description="Уменьшает силу атаки",
    effect_type=EffectType.DEBUFF,
    duration=30,
    max_stacks=1,
    attack_modifier=-8  # -8 к атаке
)

STUN = Effect(
    effect_id=103,
    name="Оглушение",
    description="Персонаж не может действовать",
    effect_type=EffectType.DEBUFF,
    duration=3,
    max_stacks=1,
    is_stunned=True
)