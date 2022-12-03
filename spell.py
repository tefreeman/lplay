from enum import Enum


class SpellTargetType(Enum):
    NONE = 1
    AUTO = 2
    LOC = 3
    SELF = 4


class Spell:
    def __init__(self, slot: str, target_type: SpellTargetType) -> None:
        self.slot = slot
        self.target_type = target_type
