import argparse
import csv
import os
import threading
from pathlib import Path
from queue import Queue
from typing import List, Optional

from tqdm import tqdm

from equipped_render import EquippedRender, ItemSet

RENDERER_PATH = os.environ.get('RENDERER_PATH', './renderer-all.jar')
COMMA = ','
MAX_THREADS = 1


def validate_args(infile_arg: str, cache_arg: str, outdir_arg: str, only_ids_file: Optional[str]) -> bool:
    # Validate infile
    infile_path = Path(infile_arg)
    if not infile_path.is_file():
        print('Infile given does not exist!')
        return False
    if infile_path.suffix != '.csv':
        print('Infile must be a .csv file!')
        return False
    # Validate cache
    cache_path = Path(cache_arg)
    if not cache_path.is_dir():
        print('Cache given is not a dir!')
        return False
    # Validate outdir
    if not isinstance(outdir_arg, str):
        print('Outdir given is not a string!')
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


def render_chathead_images(images_queue: Queue, cache: str, outdir: str, only_gender: Optional[str]):
    def render_image(render_: EquippedRender, is_female: bool, cache_: str, outdir_: str):
        playerkit = [str(k) for k in render_.get_complete_playerkit(is_female)]
        colorkit = [str(k) for k in render_.get_colorkit(is_female)]
        complete_outdir = Path(outdir_).joinpath('female' if is_female else 'male')
        os.system(
            f'java -jar {RENDERER_PATH} --cache {cache_} --out {complete_outdir} '
            f'--playerkit "{COMMA.join(playerkit)}" --playercolors "{COMMA.join(colorkit)}" '
            f'{"--playerfemale" if is_female else ""} --playerchathead --anim 589 --lowres --crophead --yan2d 128'
        )

    while not images_queue.empty():
        render: EquippedRender = images_queue.get()
        if render.can_render(is_female=False) and only_gender != 'female' and render.equip_slot == 0:
            render_image(render_=render, is_female=False, cache_=cache, outdir_=outdir)
        if render.can_render(is_female=True) and only_gender != 'male' and render.equip_slot == 0:
            render_image(render_=render, is_female=True, cache_=cache, outdir_=outdir)
        images_queue.task_done()


def render_equip_images(images_queue: Queue, cache: str, outdir: str, only_gender: Optional[str]):
    def render_image(render_: EquippedRender, is_female: bool, cache_: str, outdir_: str):
        playerkit = [str(k) for k in render_.get_complete_playerkit(is_female)]
        colorkit = [str(k) for k in render_.get_colorkit(is_female)]

        complete_outdir = Path(outdir_).joinpath('female' if is_female else 'male')
        os.system(
            f'java -jar {RENDERER_PATH} --cache {cache_} --out {complete_outdir} '
            f'--playerkit "{COMMA.join(playerkit)}" --playercolors "{COMMA.join(colorkit)}" '
            f'--poseanim {render_.pose_anim} --xan2d {render_.xan2d} --yan2d {render_.yan2d} --zan2d {render_.zan2d} '
            f'{"--playerfemale" if is_female else ""}'
        )

    while not images_queue.empty():
        render: EquippedRender = images_queue.get()
        if render.can_render(is_female=False) and only_gender != 'female':
            render_image(render_=render, is_female=False, cache_=cache, outdir_=outdir)
        if render.can_render(is_female=True) and only_gender != 'male':
            render_image(render_=render, is_female=True, cache_=cache, outdir_=outdir)
        images_queue.task_done()


def run_jobs(infile: str, cache_arg: str, outdir_arg: str, only_gender: Optional[str], only_render: Optional[str],
             only_ids: Optional[List[int]], set_list: Optional[str]):
    num_lines_data = sum(1 for _ in open(infile, 'r'))
    f = open(infile, 'r')
    dict_reader = csv.DictReader(f, dialect='excel')

    equip_jobs = Queue()
    chathead_jobs = Queue()
    renders = {}
    for line in tqdm(dict_reader, total=num_lines_data):
        render = EquippedRender.from_dict(line)
        renders[render.item_id] = render
        if only_ids is None or render.item_id in only_ids:
            if only_render is None or only_render == 'equip':
                equip_jobs.put(render)
            if only_render is None or only_render == 'chathead':
                chathead_jobs.put(render)

    # Hacked in set support, pass in set list and it will only render sets
    if set_list:
        f2 = open(set_list)
        d_r = csv.DictReader(f2, dialect='excel')
        is_female = True
        for line in d_r:
            ids = line['item_ids'].split(',')
            rotation = line['yan2d']
            l = [renders[int(i)] for i in ids]
            s = ItemSet(l)
            playerkit = [str(k) for k in s.get_complete_playerkit(is_female)]
            colorkit = [str(k) for k in s.get_colorkit(is_female)]
            complete_outdir = Path(outdir_arg).joinpath('female' if is_female else 'male')
            comm = (f'java -jar {RENDERER_PATH} --cache {cache_arg} --out {complete_outdir} '
                    f'--playerkit "{COMMA.join(playerkit)}" --playercolors "{COMMA.join(colorkit)}" '
                    f'--poseanim {808} --xan2d {96} --yan2d {rotation} --zan2d {0} '
                    f'{"--playerfemale" if is_female else ""}')
            os.system(comm)

        exit(0)

    for i in range(MAX_THREADS):
        t = threading.Thread(target=render_equip_images, args=(equip_jobs, cache_arg, outdir_arg, only_gender))
        t.start()
    equip_jobs.join()
    for i in range(MAX_THREADS):
        t = threading.Thread(target=render_chathead_images, args=(chathead_jobs, cache_arg, outdir_arg, only_gender))
        t.start()
    chathead_jobs.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to generate renders')
    parser.add_argument('--cache', required=True, help='Path to the cache to use')
    parser.add_argument('--outdir', default='renders', help='Folder to use for the renderer output')
    parser.add_argument('--only-gender', choices=['male', 'female'],
                        help='Only generate renders for the given gender. Defaults to generating both.')
    parser.add_argument('--render-type', choices=['player', 'chathead'],
                        help='Only generate renders for the given type. Defaults to generating both.')
    parser.add_argument('--id-list', help='Only generate renders for the ids in this file (comma separated list)')
    parser.add_argument('--set-list', help='Only generate sets, might break things')
    args = parser.parse_args()

    if not validate_args(args.infile, args.cache, args.outdir, args.only_ids_file):
        exit(1)

    start_up(args.infile, args.cache, args.outdir, args.only_gender, args.only_render, args.only_ids_file, args.set_list)


def start_up(infile: str, cache: str, outdir: str, only_gender: Optional[str], only_render: Optional[str],
             only_ids_file: Optional[str], set_list: Optional[str]):
    only_ids = None
    if only_ids_file is not None:
        only_ids = [int(item_id) for item_id in open(only_ids_file).read().split(',')]
    run_jobs(infile, cache, outdir, only_gender, only_render, only_ids, set_list)


if __name__ == '__main__':
    main()
