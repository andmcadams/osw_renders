import argparse
import csv
import os
import threading
from pathlib import Path
from queue import Queue

from tqdm import tqdm

from equipped_render import EquippedRender

COMMA = ','
MAX_THREADS = 5


def validate_args(infile_arg: str, cache_arg: str, outdir_arg: str) -> bool:
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

    return True


def render_image(render: EquippedRender, is_female: bool, cache: str, outdir: str):
    playerkit = [str(k) for k in render.get_complete_playerkit(is_female)]
    colorkit = [str(k) for k in render.get_colorkit(is_female)]
    complete_outdir = Path(outdir).joinpath('female' if is_female else 'male')
    os.system(
        f'java -jar renderer-all.jar --cache {cache} --out {complete_outdir} '
        f'--playerkit "{COMMA.join(playerkit)}" --playercolors "{COMMA.join(colorkit)}" '
        f'--poseanim {render.pose_anim} --xan2d {render.xan2d} --yan2d {render.yan2d} --zan2d {render.zan2d} '
        f'{"--playerfemale" if is_female else ""}'
    )


def render_images(images_queue: Queue, cache: str, outdir: str, only: str):
    while not images_queue.empty():
        render: EquippedRender = images_queue.get()
        if render.can_render(is_female=False) and only != 'female':
            render_image(render=render, is_female=False, cache=cache, outdir=outdir)
        if render.can_render(is_female=True) and only != 'male':
            render_image(render=render, is_female=True, cache=cache, outdir=outdir)
        images_queue.task_done()


def run_jobs(infile: str, cache_arg: str, outdir_arg: str, only: str):
    num_lines_data = sum(1 for _ in open(infile, 'r'))
    f = open(infile, 'r')
    dict_reader = csv.DictReader(f, dialect='excel')

    jobs = Queue()
    for line in tqdm(dict_reader, total=num_lines_data):
        render = EquippedRender.from_dict(line)
        jobs.put(render)

    for i in range(MAX_THREADS):
        t = threading.Thread(target=render_images, args=(jobs, cache_arg, outdir_arg, only))
        t.start()
    jobs.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to generate renders')
    parser.add_argument('--cache', required=True, help='Path to the cache to use')
    parser.add_argument('--outdir', help='Folder to use for the renderer output')
    parser.add_argument('--only', choices=['male', 'female'], help='Only generate renders for the given gender')
    args = parser.parse_args()

    infile = args.infile
    cache = args.cache
    outdir = args.outdir if args.outdir else 'renders'
    only = args.only

    if not validate_args(infile, cache, outdir):
        exit(1)

    run_jobs(infile, cache, outdir, only)


if __name__ == '__main__':
    main()
