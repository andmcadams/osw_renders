import copy
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class IncompleteDataException(BaseException):
    pass


@dataclass
class EquippedRender:
    # Fields about the item
    item_id: int
    page_name: str
    infobox_version: str

    # Male specific fields
    male_file_name: Optional[str] = ''
    male_playerkit: Optional[List[int]] = None
    male_colorkit: Optional[List[int]] = None

    # Female specific fields
    female_file_name: Optional[str] = ''
    female_playerkit: Optional[List[int]] = None
    female_colorkit: Optional[List[int]] = None

    # Fields for generating images
    zero_bitmap: Optional[List[int]] = None
    equip_slot: int = -1
    pose_anim: int = -1
    xan2d: int = -1
    yan2d: int = -1
    zan2d: int = -1

    def get_file_name(self, is_female: bool) -> str:
        if is_female:
            return self.female_file_name
        return self.male_file_name

    def get_playerkit(self, is_female: bool) -> List[int]:
        if is_female:
            return self.female_playerkit
        return self.male_playerkit

    def get_colorkit(self, is_female: bool) -> List[int]:
        # Colorkit order: hair, shirt, pants, boots, skin
        if is_female:
            return self.female_colorkit
        return self.male_colorkit

    def has_zero_bitmap(self) -> bool:
        return bool(self.zero_bitmap)

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
        playerkit = self.get_playerkit(is_female)

        # If we are missing any crucial pieces throw an error
        if not (playerkit and self.has_equip_slot() and self.has_zero_bitmap()):
            raise IncompleteDataException()

        # Copy the base playerkit
        playerkit_copy = copy.deepcopy(playerkit)

        # Replace equip slot with the item
        playerkit_copy[self.equip_slot] = self.item_id + 2048

        # Hide all needed slots from zbm
        for i, val in enumerate(self.zero_bitmap):
            if val == 0:
                playerkit_copy[i] = 0

        return playerkit_copy

    def can_render(self, is_female: bool) -> bool:
        if not self.get_playerkit(is_female):
            return False
        if not self.get_colorkit(is_female):
            return False
        if not self.has_zero_bitmap():
            return False
        if not self.has_equip_slot():
            return False
        if not self.has_pose_anim():
            return False
        if not self.has_xan2d():
            return False
        if not self.has_yan2d():
            return False
        if not self.has_zan2d():
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquippedRender':
        # item_id
        data['item_id'] = int(data['item_id'])
        # page name, infobox version
        # Male specific fields
        data['male_playerkit'] = json.loads(data['male_playerkit']) if data['male_playerkit'] else None
        data['male_colorkit'] = json.loads(data['male_colorkit']) if data['male_colorkit'] else None
        # Female specific fields
        data['female_playerkit'] = json.loads(data['female_playerkit']) if data['female_playerkit'] else None
        data['female_colorkit'] = json.loads(data['female_colorkit']) if data['female_colorkit'] else None
        # Fields for generating images
        data['zero_bitmap'] = json.loads(data['zero_bitmap']) if data['zero_bitmap'] else None

        data['equip_slot'] = int(data['equip_slot']) if data['equip_slot'] else -1
        data['pose_anim'] = int(data['pose_anim']) if data['pose_anim'] else -1
        data['xan2d'] = int(data['xan2d']) if data['xan2d'] else -1
        data['yan2d'] = int(data['yan2d']) if data['yan2d'] else -1
        data['zan2d'] = int(data['zan2d']) if data['zan2d'] else -1

        return cls(**data)

    @staticmethod
    def get_csv_headers() -> List[str]:
        return list(EquippedRender.__dict__['__dataclass_fields__'].keys())


class ItemSet:

    def __init__(self, items: List[EquippedRender]):
        self.items = items

    def get_complete_playerkit(self, is_female: bool) -> Optional[List[int]]:
        # Note we should get each item's playerkit, then create a full one with zero'd out values
        # Use the regular kit for first item
        playerkit = self.items[0].get_complete_playerkit(is_female)

        # Determine which playerkit we want for each item
        for item in self.items:
            # Hide all needed slots from zbm
            for i, val in enumerate(item.zero_bitmap):
                if val == 0:
                    playerkit[i] = 0
        for item in self.items:
            # Replace equip slot with the item
            playerkit[item.equip_slot] = item.item_id + 2048


        return playerkit

    def get_colorkit(self, is_female: bool) -> List[int]:
        return self.items[0].get_colorkit(is_female)
