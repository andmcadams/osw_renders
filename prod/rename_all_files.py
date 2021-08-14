import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path
from typing import Optional, List

from tqdm import tqdm

from equipped_render import EquippedRender, IncompleteDataException

# Move each file of the form "[playerkit]_[colorkit].png" to "File name equipped female.png"
# Print out a warning each time a file is overwritten and is not the same image.

pages = defaultdict(set)


def validate_args(infile: str, renders_dir: str, only_ids_file: str, check_renders_dir: bool = True) -> bool:
    # Validate infile
    infile_path = Path(infile)
    if not infile_path.is_file():
        print('Infile given does not exist!')
        return False
    if infile_path.suffix != '.csv':
        print('Infile must be a .csv file!')
        return False

    # Validate renders dir
    if check_renders_dir:
        if not Path(renders_dir).is_dir():
            print(f'Cannot find dir: {renders_dir}')
            return False

    # Validate ids file
    if only_ids_file:
        only_ids_file_path = Path(only_ids_file)
        if not only_ids_file_path.is_file():
            print('Only-ids file does not exist!')
            return False
        try:
            _ = [int(item_id) for item_id in open(only_ids_file).read().split(',')]
        except ValueError:
            print('id-list file is not a comma separated list of integers!')
            return False

    return True


def rename_chathead_image(render: EquippedRender, renders_folder: str, outdir: str, is_female: bool):
    path = Path(renders_folder).joinpath('female' if is_female else 'male').joinpath('playerchathead').joinpath(
        f'{str(render.get_complete_playerkit(is_female))}_{str(render.get_colorkit(is_female))}.png')
    if path.is_file():
        # Copy file over to new spot
        new_file_name = render.get_file_name(is_female)[7:-2].replace('equipped', 'chathead')
        new_path = Path(outdir).joinpath('female' if is_female else 'male').joinpath('playerchathead').joinpath(
            new_file_name)
        if new_path.is_file():
            print(f'{new_path} already exists!')
        outfile = new_path.open(mode='wb+')
        outfile.write(path.open('rb').read())
        outfile.close()


def rename_equipped_image(render: EquippedRender, renders_folder: str, outdir: str, is_female: bool):
    path = Path(renders_folder).joinpath('female' if is_female else 'male').joinpath('player').joinpath(
        f'{str(render.get_complete_playerkit(is_female))}_{str(render.get_colorkit(is_female))}.png')
    if path.is_file():
        # Copy file over to new spot
        new_file_name = render.get_file_name(is_female)[7:-2]
        new_path = Path(outdir).joinpath('female' if is_female else 'male').joinpath('player').joinpath(
            new_file_name)
        if new_path.is_file():
            print(f'{new_path} already exists!')
        outfile = new_path.open(mode='wb+')
        outfile.write(path.open('rb').read())
        outfile.close()


def rename_images(infile: str, renders_folder: str, outdir: str, only_gender: Optional[str], only_render: Optional[str],
                  only_ids: Optional[List[int]]):
    num_lines_data = sum(1 for _ in open(infile, 'r'))
    f = open(infile, 'r')
    dict_reader = csv.DictReader(f, dialect='excel')
    for line in tqdm(dict_reader, total=num_lines_data):
        render: EquippedRender = EquippedRender.from_dict(line)
        # Only rename the ones we specify, if we specify any
        if only_ids is not None and render.item_id not in only_ids:
            continue

        try:
            # Only render the gender we specify, if we specify any
            if only_gender is None:
                genders_to_render = [False, True]
            elif only_gender == 'female':
                genders_to_render = [True]
            else:
                genders_to_render = [False]

            for is_female in genders_to_render:
                # If this render does not have a file name or an image, ignore
                if not render.get_file_name(is_female):
                    continue
                # Only render the type of image we specify, if we specify any
                if only_render is None or only_render == 'player':
                    rename_equipped_image(render, renders_folder, outdir, is_female)
                if only_render is None or only_render == 'chathead':
                    rename_chathead_image(render, renders_folder, outdir, is_female)
        except IncompleteDataException as e:
            print(f'Id {render.item_id}: Incomplete data...Skipping...')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to rename renders')
    parser.add_argument('--renders-dir', required=True, help='Folder containing player dir with renders')
    parser.add_argument('--outdir', help='Directory to put renamed renders in. Default: {RENDERS_DIR}_renamed')
    parser.add_argument('--only-gender', choices=['male', 'female'],
                        help='Only generate renders for the given gender. Defaults to generating both.')
    parser.add_argument('--render-type', choices=['player', 'chathead'],
                        help='Only generate renders for the given type. Defaults to generating both.')
    parser.add_argument('--id-list', help='Only generate renders for the ids in this file (comma separated list)')
    args = parser.parse_args()

    infile = args.infile
    renders_dir = args.renders_dir
    outdir = args.outdir
    only_gender = args.only_gender
    only_render = args.render_type
    only_ids_file = args.id_list

    if not validate_args(infile, renders_dir, only_ids_file):
        exit(1)

    start_up(infile, renders_dir, outdir, only_gender, only_render, only_ids_file)


def start_up(infile: str, renders_dir: str, outdir: Optional[str], only_gender: Optional[str],
             only_render: Optional[str], only_ids_file: Optional[str]):
    # If outdir is not given, create the dir for renamed
    if not outdir:
        outdir = f'{str(Path(renders_dir))}_renamed'

    paths = [Path(outdir), Path(outdir).joinpath('male'), Path(outdir).joinpath('female'),
             Path(outdir).joinpath('male').joinpath('playerchathead'),
             Path(outdir).joinpath('female').joinpath('playerchathead'),
             Path(outdir).joinpath('male').joinpath('player'),
             Path(outdir).joinpath('female').joinpath('player')]
    for path in paths:
        if not path.exists():
            os.mkdir(path)

    only_ids = None
    if only_ids_file is not None:
        only_ids = [int(item_id) for item_id in open(only_ids_file).read().split(',')]

    rename_images(infile, renders_dir, outdir, only_gender, only_render, only_ids)


if __name__ == '__main__':
    main()
