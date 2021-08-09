import argparse
import csv
import random
from csv import DictWriter

from equipped_render import EquippedRender

pks = [
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

parser = argparse.ArgumentParser()
parser.add_argument('--infile', help='Path to a tsv file to use for input')
parser.add_argument('--item-id', help='Item id (numeric)', type=int, metavar='ITEM_ID')
parser.add_argument('--equip-slot', help='Equip slot (numeric)', type=int, metavar='EQUIP_SLOT', choices=range(12))
parser.add_argument('--outfile', default='outfile.csv', help='The file to write to (will overwrite)')
args = parser.parse_args()

if not args.infile and not(args.item_id and args.equip_slot):
    print('Need to specify either an input file or an item id + equip slot')
    exit(1)

outfile = open(args.outfile, 'w+')
dict_writer = DictWriter(outfile, fieldnames=EquippedRender.get_csv_headers(), dialect='excel')
dict_writer.writeheader()
if args.infile:
    print(f'Using infile at {args.infile}')
    infile = open(args.infile, 'r')
    for line in infile:
        line = line.strip()
        item_id, equip_slot = line.split('\t')
        playerkit, colorkit = random.choice(pks)

        render = EquippedRender(item_id=int(item_id), page_name='', infobox_version='',
                                male_file_name='', male_playerkit=playerkit, male_colorkit=colorkit,
                                female_file_name='', female_playerkit=playerkit, female_colorkit=colorkit,
                                equip_slot=int(equip_slot))
        dict_writer.writerow(render.to_dict())
else:
    playerkit, colorkit = random.choice(pks)
    render = EquippedRender(item_id=int(args.item_id), page_name='', infobox_version='',
                            male_file_name='', male_playerkit=playerkit, male_colorkit=colorkit,
                            female_file_name='', female_playerkit=playerkit, female_colorkit=colorkit,
                            equip_slot=int(args.equip_slot))
    dict_writer.writerow(render.to_dict())
outfile.close()