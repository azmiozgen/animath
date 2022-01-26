import os
import sys

import cairo
import moviepy.editor as mpe
import numpy as np

from lib import PI
from objects import Rectangle

WIDTH = 800
HEIGHT = 800
SQUARE_W = 64

ROT_F = 2
DURATION = 8
PHASE = 5
FPS = 30

def get_image(surface):
    image = np.frombuffer(surface.get_data(), np.uint8)
    image = image.reshape((surface.get_height(), surface.get_width(), 4))
    image = image[:, :, [2, 1, 0, 3]]
    return image[:, :, :3]

def set_square_locations():
    xs = np.arange(WIDTH * 0.0,
                   WIDTH * 1.09,
                   WIDTH * 0.10)
    ys = np.arange(HEIGHT * 0.0,
                   HEIGHT * 1.09,
                   HEIGHT * 0.10)
    xs, ys = np.meshgrid(xs, ys)
    return xs.flatten(), ys.flatten()

def make_frame(t):
    context.save()
    bg_color = np.array([1.0, 0, 0]) if t < DURATION * 0.5 else np.array([0, 0, 1.0])
    context.set_source_rgb(*bg_color)
    context.rectangle(0, 0, WIDTH, HEIGHT)
    context.fill()
    context.restore()

    for i, (x, y) in enumerate(zip(xs, ys)):
        angle = PI * (x + y) + 2 * PI * ((t + PHASE) / DURATION)  ## Rotational angle of the small squares
        angle = -1 * angle if i % 2 == 0 else angle
        color = (0, 0, 0, 1) if i % 2 == 0 else (1, 1, 1, 1)

        # square_w = SQUARE_W * (1.0 + 0.5 * (np.sin(2 * PI * ROT_F * ((t + PHASE) / DURATION))))
        square_w = SQUARE_W * np.exp(0.5 * (np.sin(2 * PI * ROT_F * ((t + PHASE) / DURATION))))
        x1, y1 = [x - square_w / 2, y - square_w / 2]
        square = Rectangle(context, x=x1, y=y1, w=square_w, h=square_w,
                           fill_rgb=color,
                           stroke=True,
                           gradient=None,
                           rot_angle=angle)

        context.save()
        square.draw()

    return get_image(surface)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print('Usage: python {} <output_file>'.format(__file__))
        sys.exit()
    output_file = sys.argv[1]
    if os.path.isfile(output_file):
        print(output_file, 'exists. Exiting.')
        sys.exit()

    ## Set context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    context = cairo.Context(surface)

    xs, ys = set_square_locations()

    clip = mpe.VideoClip(make_frame=make_frame, duration=DURATION)
    # clip.write_gif(output_file, fps=FPS, program='ffmpeg')
    clip.write_gif(output_file, fps=FPS, program='imageio', opt='wu')
