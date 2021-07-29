import copy
import json
import random
from dataclasses import dataclass
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


class IncompleteDataException(BaseException):
    pass


@dataclass
class EquippedRender:

    # Fields about the item
    item_id: int
    page_name: str
    infobox_version: str

    # Male specific fields
    male_file_name: str = None
    male_playerkit: List[int] = None
    male_colorkit: List[int] = None

    # Female specific fields
    female_file_name: str = None
    female_playerkit: List[int] = None
    female_colorkit: List[int] = None

    # Fields for generating images
    zero_bitmap: List[int] = None
    equip_slot: int = -1
    pose_anim: int = -1
    xan2d: int = -1
    yan2d: int = -1
    zan2d: int = -1

    def file_name(self, is_female: bool) -> str:
        if is_female:
            return self.female_file_name
        return self.male_file_name

    def playerkit(self, is_female: bool) -> List[int]:
        if is_female:
            return self.female_playerkit
        return self.male_playerkit

    def colorkit(self, is_female: bool) -> List[int]:
        if is_female:
            return self.female_colorkit
        return self.male_playerkit

    def has_zero_bitmap(self) -> bool:
        return self.zero_bitmap is None

    def has_equip_slot(self) -> bool:
        return self.equip_slot != -1

    def has_pose_anim(self) -> bool:
        return self.pose_anim != -1

    def has_xan2d(self) -> bool:
        return self.xan2d != -1

    def has_yan2d(self) -> bool:
        return self.yan2d != -1

    def has_zan2d(self) -> bool:
        return self.zan2d != -1

    def get_complete_playerkit(self, is_female: bool) -> Optional[List[int]]:
        # Determine which playerkit we want
        playerkit = self.playerkit(is_female)

        # If we are missing any crucial pieces throw an error
        if not (playerkit and self.equip_slot != -1 and self.zero_bitmap):
            raise IncompleteDataException()

        # Copy the base playerkit
        playerkit_copy = copy.deepcopy(playerkit)

        # Replace equipslot with the item
        playerkit_copy[self.equip_slot] = self.item_id + 512

        # Hide all needed slots from zbm
        for i, val in enumerate(self.zero_bitmap):
            if val == 0:
                playerkit_copy[i] = 0

        return playerkit_copy

    def can_render(self) -> bool:
        return True

    def to_tsv(self) -> str:
        # Tiny helper to print None as ''
        def s(prop):
            if prop is None:
                return ''
            return str(prop)

        return (f'{self.item_id}\t{s(self.page_name)}\t{s(self.infobox_version)}\t{s(self.male_file_name)}\t'
                f'{s(self.female_file_name)}\t{s(self.male_playerkit)}\t{s(self.female_playerkit)}\t{s(self.colorkit)}\t'
                f'{s(self.zero_bitmap)}\t{s(self.equip_slot)}\t{s(self.pose_anim)}\t{s(self.xan2d)}\t{s(self.yan2d)}\t'
                f'{s(self.zan2d)}')

    @classmethod
    def from_tsv(cls, tsv_line: str) -> 'EquippedRender':
        values = tsv_line.split('\t')

        # Remove self from count of parameters required
        num_required_params = len(signature(EquippedRender.__init__).parameters) - 1
        if len(values) != num_required_params:
            print(values)
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
