import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

from equipped_render import EquippedRender, IncompleteDataException

# Move each file of the form "[playerkit]_[colorkit].png" to "File name equipped female.png"
# Print out a warning each time a file is overwritten and is not the same image.

pages = defaultdict(set)


def validate_args(infile: str, renders_dir: str, outdir: str) -> bool:
    # Validate infile
    infile_path = Path(infile)
    if not infile_path.is_file():
        print('Infile given does not exist!')
        return False
    if infile_path.suffix != '.csv':
        print('Infile must be a .csv file!')
        return False
    # Validate renders dir
    if not Path(renders_dir).is_dir():
        print(f'Cannot find dir: {renders_dir}')
        return False
    # Validate outdir (if given)
    if outdir:
        if not Path(outdir).is_dir():
            print(f'Cannot find outdir: {outdir}')
            return False
    return True


def rename_images(infile: str, renders_folder: str, outdir: str):
    num_lines_data = sum(1 for _ in open(infile, 'r'))
    f = open(infile, 'r')
    dict_reader = csv.DictReader(f, dialect='excel')
    for line in tqdm(dict_reader, total=num_lines_data):
        render: EquippedRender = EquippedRender.from_dict(line)
        try:
            for is_female in [True, False]:
                # If this render does not have a file name or an image, ignore
                if not render.get_file_name(is_female):
                    continue
                path = Path(renders_folder).joinpath('female' if is_female else 'male').joinpath('player').joinpath(
                    f'{str(render.get_complete_playerkit(is_female))}_{str(render.get_colorkit(is_female))}.png')
                if not path.is_file():
                    continue
                # Copy file over to new spot
                new_file_name = render.get_file_name(is_female)[7:-2]
                new_path = Path(outdir).joinpath('female' if is_female else 'male').joinpath(
                    new_file_name)
                if new_path.is_file():
                    print(f'{new_path} already exists!')
                outfile = new_path.open(mode='wb+')
                outfile.write(path.open('rb').read())
                outfile.close()
        except IncompleteDataException as e:
            print(f'Id {render.item_id}: Incomplete data...Skipping...')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to rename renders')
    parser.add_argument('--renders-dir', required=True, help='Folder containing player dir with renders')
    parser.add_argument('--outdir', help='Directory to put renamed renders in. Default: {RENDERS_DIR}_renamed')
    args = parser.parse_args()

    infile = args.infile
    renders_dir = args.renders_dir
    outdir = args.outdir

    if not validate_args(infile, renders_dir, outdir):
        exit(1)

    # If outdir is not given, create the dir for renamed
    if not outdir:
        outdir = f'{str(Path(renders_dir))}_renamed'
        if not Path(outdir).exists():
            os.mkdir(Path(outdir))
            os.mkdir(Path(outdir).joinpath('male'))
            os.mkdir(Path(outdir).joinpath('female'))

    rename_images(infile, renders_dir, outdir)


if __name__ == '__main__':
    main()
