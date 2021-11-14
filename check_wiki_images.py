# Check images to see which ones need to be updated
import argparse
import csv
import filecmp
import hashlib
import os
import random
import string
import threading
from pathlib import Path
from queue import Queue
from typing import Optional

import requests

from equipped_render import EquippedRender

RENDERER_PATH = os.environ.get('RENDERER_PATH', './renderer-all.jar')
diff_files = set()
non_uploaded_files = set()
failed_to_generate_files = set()
COMMA = ','
MAX_THREADS = 5
try:
    USER_AGENT = os.environ['USER_AGENT']
except KeyError:
    print('Set a user agent environment variable! (Or change the code)')
    exit(-1)


def validate_args(infile: str, cache: str, outdir: str, idfile: str) -> bool:
    # Validate infile
    infile_path = Path(infile)
    if not infile_path.is_file():
        print('Infile given does not exist!')
        return False
    if infile_path.suffix != '.csv':
        print('Infile must be a .csv file!')
        return False
    # Validate cache
    cache_path = Path(cache)
    if not cache_path.is_dir():
        print('Cache given is not a dir!')
        return False
    # Validate outdir
    if not isinstance(outdir, str):
        print('Outdir given is not a string!')
        return False
    # Validate idfile
    if idfile:
        idfile_path = Path(idfile)
        if not idfile_path.is_file():
            print('Idfile given does not exist!')
            return False

    return True


def download_image(file_name: str, outdir: str) -> Optional[str]:
    if not file_name:
        return None
    md5_val = hashlib.md5(file_name.encode('utf-8')).hexdigest()
    url_encoded_file_name = file_name.replace("(", "%28").replace(")", "%29")
    cache_buster = ''.join([random.choice(string.hexdigits) for _ in range(5)])

    file_url = f'https://oldschool.runescape.wiki/images/{md5_val[:1]}/{md5_val[:2]}/{url_encoded_file_name}?{cache_buster}'
    download_path = Path(outdir).joinpath(file_name)
    resp = requests.get(file_url, headers={'User-agent': USER_AGENT})
    if resp.status_code == 200:
        out_file = open(download_path, 'wb+')
        out_file.write(resp.content)
        out_file.close()
        return download_path
    else:
        # print(f'{file_name}: Error code {resp.status_code}')
        return None


def check_image(render: EquippedRender, is_female: bool, cache: str, renders_outdir: str, wiki_path: str,
                force_rerender: bool):
    download_path = Path(wiki_path).joinpath(render.get_file_name(is_female)[7:-2])
    if not download_path.exists():
        downloaded_name = download_image(render.get_file_name(is_female)[7:-2], wiki_path)
    else:
        downloaded_name = str(download_path)
    render_file_name = Path(renders_outdir).joinpath('female' if is_female else 'male').joinpath('player').joinpath(
        f'{render.get_complete_playerkit(is_female)}_{render.get_colorkit(is_female)}.png')
    # Check if we have the image already generated. If not, generate it
    if downloaded_name:
        if not render_file_name.is_file() or force_rerender:
            print(f'Rendering a file for {render.page_name}')
            playerkit = [str(k) for k in render.get_complete_playerkit(is_female)]
            colorkit = [str(k) for k in render.get_colorkit(is_female)]
            complete_outdir = Path(renders_outdir).joinpath('female' if is_female else 'male')
            os.system(
                f'java -jar {RENDERER_PATH} --cache {cache} --out {complete_outdir} '
                f'{"--playerfemale" if is_female else ""} '
                f'--playerkit "{COMMA.join(playerkit)}" --playercolors "{COMMA.join(colorkit)}" '
                f'--poseanim {render.pose_anim} --xan2d {render.xan2d} --yan2d {render.yan2d} --zan2d {render.zan2d}')
        # Compare the two files
        if render_file_name.is_file():
            is_same_image = filecmp.cmp(render_file_name, downloaded_name, shallow=False)
            if not is_same_image:
                diff_files.add(render)
        else:
            failed_to_generate_files.add(render)
    else:
        non_uploaded_files.add(render)


def check_images(images_queue: Queue, cache: str, renders_outdir: str, wiki_path: str, force_rerender: bool):
    while not images_queue.empty():
        render: EquippedRender = images_queue.get()
        # Get the file from the wiki, if it exists
        if render.can_render(is_female=False):
            check_image(render=render, is_female=False, cache=cache, renders_outdir=renders_outdir, wiki_path=wiki_path,
                        force_rerender=force_rerender)

        images_queue.task_done()


def run_jobs(infile: str, cache_arg: str, outdir_arg: str, idfile_arg: str, force_rerender: bool):
    should_use_whitelist = False
    id_whitelist = set()
    if idfile_arg:
        should_use_whitelist = True
        with open(idfile_arg, 'r') as idfile:
            for line in idfile:
                id_whitelist.add(int(line))

    f = open(infile, 'r')
    dict_reader = csv.DictReader(f, dialect='excel')
    jobs = Queue()
    for line in dict_reader:
        render = EquippedRender.from_dict(line)
        # If we are using the whitelist and the item id is in there, render it
        # If not using the whitelist, render all equipped images
        if should_use_whitelist and render.item_id in id_whitelist:
            jobs.put(render)
        elif not should_use_whitelist:
            jobs.put(render)

    wiki_path = Path(f'{str(Path(outdir_arg))}_wiki')
    if not wiki_path.exists():
        os.mkdir(wiki_path)
    for i in range(MAX_THREADS):
        t = threading.Thread(target=check_images, args=(jobs, cache_arg, outdir_arg, wiki_path, force_rerender))
        t.start()
    jobs.join()
    print('DIFF FILES:')
    for render in diff_files:
        print(f'{render.item_id}: {render.file_name}')
    print('MISSING FILES:')
    for render in non_uploaded_files:
        print(f'{render.item_id}: {render.file_name}')
    print('FAILED FILES:')
    for render in failed_to_generate_files:
        print(f'{render.item_id}: {render.file_name}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', required=True, help='Path to a csv to use to generate renders')
    parser.add_argument('--cache', required=True, help='Path to the cache to use')
    parser.add_argument('--outdir', help='Folder to use for the renderer output')
    parser.add_argument('--idfile', help='File containing ids to check')
    parser.add_argument('--rerender', action='store_true', help='Force rerender images')
    args = parser.parse_args()

    infile = args.infile
    cache = args.cache
    outdir = args.outdir if args.outdir else 'renders'
    idfile = args.idfile
    force_rerender = args.rerender

    if not validate_args(infile, cache, outdir, idfile):
        exit(1)

    run_jobs(infile, cache, outdir, idfile, force_rerender)


if __name__ == '__main__':
    main()
