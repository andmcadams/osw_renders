import json
import random
from inspect import signature
from typing import List, Optional

possible_playerkits = [
    [[0, 0, 0, 0, 312, 0, 320, 326, 382, 324, 336, 0], [5, 19, 9, 1, 2]],
    [[0, 0, 0, 0, 312, 0, 351, 326, 310, 324, 336, 0], [1, 22, 24, 1, 4]],
    [[0, 0, 0, 0, 312, 0, 317, 326, 380, 324, 336, 0], [3, 23, 8, 5, 6]],
    [[0, 0, 0, 0, 312, 0, 320, 326, 382, 324, 336, 0], [0, 11, 8, 5, 0]],
    [[0, 0, 0, 0, 312, 0, 355, 326, 304, 324, 336, 0], [12, 6, 4, 5, 1]],
    [[0, 0, 0, 0, 315, 0, 317, 326, 377, 324, 336, 0], [7, 25, 20, 4, 1]],
    [[0, 0, 0, 0, 315, 0, 317, 326, 380, 324, 336, 0], [7, 0, 2, 3, 7]],
    [[0, 0, 0, 0, 315, 0, 351, 326, 376, 324, 336, 0], [3, 13, 6, 3, 5]],
    [[0, 0, 0, 0, 312, 0, 317, 326, 379, 324, 336, 0], [0, 26, 2, 2, 3]],
    [[0, 0, 0, 0, 315, 0, 352, 326, 375, 324, 336, 0], [14, 22, 6, 1, 2]]
]


def get_random_kits() -> List[List[int]]:
    return random.choice(possible_playerkits)


class EquippedRender:

    def __init__(self, item_id: int, is_female: Optional[bool], page_name: str, infobox_version: str, file_name: str,
                 playerkit: List[int], colorkit: List[int], zero_bitmap: Optional[List[int]], equip_slot: int,
                 pose_anim: Optional[int], xan2d: Optional[int], yan2d: Optional[int], zan2d: Optional[int]):
        self.__item_id = item_id
        self.__is_female = is_female
        self.__page_name = page_name.strip()
        self.__infobox_version = infobox_version.strip()
        self.__file_name = file_name.strip()
        self.__playerkit = playerkit
        self.__colorkit = colorkit
        self.__zero_bitmap = zero_bitmap
        self.__equip_slot = equip_slot
        self.__pose_anim = pose_anim
        self.__xan2d = xan2d
        self.__yan2d = yan2d
        self.__zan2d = zan2d

    @property
    def item_id(self) -> int:
        return self.__item_id

    @property
    def page_name(self) -> str:
        return self.__page_name

    @page_name.setter
    def page_name(self, page_name: str):
        self.__page_name = page_name.strip()

    @property
    def is_female(self) -> bool:
        return self.__is_female

    @property
    def infobox_version(self) -> str:
        return self.__infobox_version

    @infobox_version.setter
    def infobox_version(self, infobox_version: str):
        self.__infobox_version = infobox_version

    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str):
        self.__file_name = file_name

    @property
    def playerkit(self) -> List[int]:
        return self.__playerkit

    @playerkit.setter
    def playerkit(self, playerkit: List[int]):
        self.__playerkit = playerkit

    @property
    def colorkit(self) -> List[int]:
        return self.__colorkit

    @colorkit.setter
    def colorkit(self, colorkit: List[int]):
        self.__colorkit = colorkit

    @property
    def zero_bitmap(self) -> List[int]:
        return self.__zero_bitmap

    @zero_bitmap.setter
    def zero_bitmap(self, zero_bitmap: List[int]):
        self.__zero_bitmap = zero_bitmap

    @property
    def equip_slot(self) -> int:
        return self.__equip_slot

    @equip_slot.setter
    def equip_slot(self, equip_slot: int):
        self.__equip_slot = equip_slot

    @property
    def pose_anim(self) -> int:
        return self.__pose_anim

    @pose_anim.setter
    def pose_anim(self, pose_anim: int):
        self.__pose_anim = pose_anim

    def has_pose_anim(self) -> bool:
        return self.__pose_anim != -1

    @property
    def xan2d(self) -> int:
        return self.__xan2d

    @xan2d.setter
    def xan2d(self, xan2d: int):
        self.__xan2d = xan2d

    def has_xan2d(self) -> bool:
        return self.__xan2d != -1

    @property
    def yan2d(self) -> int:
        return self.__yan2d

    @yan2d.setter
    def yan2d(self, yan2d: int):
        self.__yan2d = yan2d

    def has_yan2d(self) -> bool:
        return self.__yan2d != -1

    @property
    def zan2d(self) -> int:
        return self.__zan2d

    @zan2d.setter
    def zan2d(self, zan2d: int):
        self.__zan2d = zan2d

    def has_zan2d(self) -> bool:
        return self.__zan2d != -1

    def to_tsv(self) -> str:
        # Tiny helper to print None as ''
        def s(prop):
            if prop is None:
                return ''
            return str(prop)

        return (f'{self.item_id}\t{self.is_female}\t{s(self.page_name)}\t{s(self.infobox_version)}\t'
                f'{s(self.file_name)}\t{s(self.playerkit)}\t{s(self.colorkit)}\t{s(self.zero_bitmap)}\t'
                f'{s(self.equip_slot)}\t{s(self.pose_anim)}\t{s(self.xan2d)}\t{s(self.yan2d)}\t{s(self.zan2d)}')

    @classmethod
    def from_tsv(cls, tsv_line: str) -> 'EquippedRender':
        values = tsv_line.split('\t')

        # Remove self from count of parameters required
        num_required_params = len(signature(EquippedRender.__init__).parameters) - 1
        if len(values) != num_required_params:
            raise ValueError(f'Given {len(values)} params, {num_required_params} expected')

        # item_id
        values[0] = int(values[0])
        # is_female
        values[1] = values[1].lower() == 'true'

        if values[5]:
            values[5] = json.loads(values[5])
        else:
            values[5] = None
        if values[6]:
            values[6] = json.loads(values[6])
        else:
            values[6] = None
        if values[7]:
            values[7] = json.loads(values[7])
        else:
            values[7] = None
        values[8] = int(values[8]) if values[8] else -1
        values[9] = int(values[9]) if values[9] else -1
        values[10] = int(values[10]) if values[10] else 96
        values[11] = int(values[11]) if values[11] else -1
        values[12] = int(values[12]) if values[12] else 0

        return cls(*values)
