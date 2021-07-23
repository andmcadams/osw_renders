import os
import threading
from collections import defaultdict
from queue import Queue

from tqdm import tqdm

from equipped_render import EquippedRender

jobs = Queue()
num_lines_data = sum(1 for line in open('./collapsed_pages.csv', 'r'))
f = open('./collapsed_pages.csv', 'r')
pages = defaultdict(set)

comma = ','
def render_images(images_queue: Queue):
    while not images_queue.empty():
        render = images_queue.get()
        if render.page_name and render.file_name and render.playerkit and render.pose_anim != -1 and render.yan2d != -1:
            playerkit = [str(k) for k in render.playerkit]
            colorkit = [str(k) for k in render.colorkit]
            os.system(
                f'java -jar renderer-all.jar --cache 2021july7 --out renderscollapsed --playerkit "{comma.join(playerkit)}" --poseanim {render.pose_anim} --yan2d {render.yan2d} --playerfemale --playercolors "{comma.join(colorkit)}"')
        images_queue.task_done()

for line in tqdm(f, total=num_lines_data):
    render = EquippedRender.from_tsv(line)
    jobs.put(render)

MAX_THREADS = 5
for i in range(MAX_THREADS):
    t = threading.Thread(target=render_images, args=(jobs,))
    t.start()

jobs.join()

