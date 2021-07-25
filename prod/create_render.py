import argparse
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


def render_images(images_queue: Queue, cache: str, outdir: str):
    while not images_queue.empty():
        render: EquippedRender = images_queue.get()
        if render.page_name and render.file_name and render.playerkit and render.pose_anim != -1 and render.yan2d != -1:
            playerkit = [str(k) for k in render.get_complete_playerkit()]
            colorkit = [str(k) for k in render.colorkit]
            os.system(
                f'java -jar renderer-all.jar --cache {cache} --out {outdir} --playerkit "{COMMA.join(playerkit)}" '
                f'--poseanim {render.pose_anim} --yan2d {render.yan2d} --playerfemale --playercolors "{COMMA.join(colorkit)}"')
        images_queue.task_done()


def run_jobs(infile: str, cache_arg: str, outdir_arg: str):
    num_lines_data = sum(1 for _ in open(infile, 'r'))
    f = open(infile, 'r')

    jobs = Queue()
    for line in tqdm(f, total=num_lines_data):
        render = EquippedRender.from_tsv(line)
        jobs.put(render)

    for i in range(MAX_THREADS):
        t = threading.Thread(target=render_images, args=(jobs, cache_arg, outdir_arg))
        t.start()
    jobs.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to generate renders')
    parser.add_argument('--cache', required=True, help='Path to the cache to use')
    parser.add_argument('--outdir', help='Folder to use for the renderer output')
    args = parser.parse_args()

    infile = args.infile
    cache = args.cache
    outdir = args.outdir if args.outdir else 'renders'

    if not validate_args(infile, cache, outdir):
        exit(1)

    run_jobs(infile, cache, outdir)

if __name__ == '__main__':
    main()