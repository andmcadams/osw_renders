import os

import render_images
import json
from collections import defaultdict, Counter
from typing import List

from tqdm import tqdm

# Vals to use for knowledge
UNKNOWN = 0
ZERO_OUT = 1
LEAVE_ALONE = 2
OCCUPIES_SLOT = 3

JAW_SLOT_ZEROS = [10556, 10557, 10558, 10559, 12659, 25212, 25228]


def preprocess(playerkit: List[int], item_id: int):
    new_arr = [UNKNOWN] * 12
    count = 0
    for index, v in enumerate(playerkit):
        v = int(v)
        if v - 512 == item_id:
            new_arr[index] = OCCUPIES_SLOT
        elif v > 0:
            new_arr[index] = LEAVE_ALONE
        elif v == 0 or v in JAW_SLOT_ZEROS:
            new_arr[index] = ZERO_OUT

        if v >= 512:
            count += 1
    return new_arr, count


def combine_arrs(old_arr, new_arr, item_count):
    # If we see non-zero vals, we know these are LEAVE_ALONE
    # If we see zero vals and the item is the only thing equipped, we know these are ZERO_OUT
    # Otherwise, they are UNKNOWN
    combined_arr = old_arr
    for i in range(len(old_arr)):

        if old_arr[i] != UNKNOWN:
            continue

        if new_arr[i] == OCCUPIES_SLOT:
            combined_arr[i] = OCCUPIES_SLOT

        elif new_arr[i] == LEAVE_ALONE:
            combined_arr[i] = LEAVE_ALONE

        elif new_arr[i] == ZERO_OUT and item_count == 1 and i != 11:
            combined_arr[i] = ZERO_OUT

        elif i in [0, 1, 2, 3, 5]:
            combined_arr[i] = LEAVE_ALONE

    return combined_arr


def default_value():
    return [[UNKNOWN] * 12, Counter()]


# Keys are item_ids, values are bools
playerkit_dict = defaultdict(default_value)


def update_from_playerkit(playerkit, pose_anim):
    for index, v in enumerate(playerkit):
        v = int(v)
        if v < 512:
            continue

        # Can move this out if I do something smarter, depends on runtime
        item_id = v - 512
        new_arr, count = preprocess(playerkit, item_id)

        old_arr = playerkit_dict[item_id][0]
        playerkit_dict[item_id][1][pose_anim] += 1

        # If looking at an item, apply the rest of the vals to the dict
        playerkit_dict[item_id][0] = combine_arrs(old_arr, new_arr, count)


def main():
    num_lines_data = sum(1 for line in open('./prod_playerkit_formatted.json'))
    num_lines_data2 = sum(1 for line in open('./staging_playerkits.json'))

    data = open('./prod_playerkit_formatted.json')
    data2 = open('./staging_playerkits.json')

    for line in tqdm(data, total=num_lines_data):
        line = line.replace("'", '"')
        l = json.loads(line)
        update_from_playerkit(l['playerkit'], int(l['poseAnim']))
    for line in tqdm(data2, total=num_lines_data2):
        l = json.loads(line)
        update_from_playerkit(l['playerkit'], int(l['poseAnim']))


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
       if isinstance(obj, Counter):
          return obj.most_common(1)
       return json.JSONEncoder.default(self, obj)

main()

sorted_dict = {}
count = 0
print('Starting to render...')
for key, value in sorted(playerkit_dict.items(), key=lambda x: int(x[0])):
    sorted_dict[key] = value

for key in tqdm(sorted_dict, total=len(sorted_dict)):
    value = sorted_dict[key]
    if UNKNOWN in value[0]:
        continue
    count += 1
    if value[0][3] == 3:
        pose_anim = str(value[1].most_common(1)[0][0])
    else:
        pose_anim = 808
    playerkit, colorkit = render_images.generate_playerkit(int(key), value[0])
    comma = ','

    for rot in [0, 512, 1024, 1536]:
        os.system(f'java -jar renderer-all.jar --cache newcache --out renders{(rot+128) % 2048} --playerkit "{comma.join(playerkit)}" --poseanim {pose_anim} --yan2d {(rot+128) % 2048} --playerfemale --playercolors "{comma.join(colorkit)}"')
        os.system(f'java -jar renderer-all.jar --cache newcache --out renders{(rot-128) % 2048} --playerkit "{comma.join(playerkit)}" --poseanim {pose_anim} --yan2d {(rot-128) % 2048} --playerfemale --playercolors "{comma.join(colorkit)}"')
