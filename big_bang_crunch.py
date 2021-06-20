import os
import sys

import cairo
import moviepy.editor as mpe
import numpy as np

from lib import PI
from lib import polar2cartesian
from objects import Circle

WIDTH = 400

CIRCLE_RADIUS = WIDTH / 400
BG_COLOR = np.array((0, 0, 0))
DURATION = 8
PHASE_TIME = DURATION / 4
FPS = 30

OUTPUT_FILENAME = 'horde.gif'

def get_image(surface):
    image = np.frombuffer(surface.get_data(), np.uint8)
    image = image.reshape((surface.get_height(), surface.get_width(), 4))
    image = image[:, :, [2, 1, 0, 3]]
    return image[:, :, :3]

def set_circle_locations(context):
    rs = np.arange(-WIDTH * 0.70, WIDTH * 0.70, WIDTH // 10)
    angles = np.arange(0, 2 * np.pi + 1, PI / 16)
    rs, angles = np.meshgrid(rs, angles)
    return rs.flatten(), angles.flatten()

def make_frame(t):
    context.save()
    context.set_source_rgb(*BG_COLOR)
    context.rectangle(0, 0, WIDTH, WIDTH)
    context.fill()
    context.restore()

    for r, angle in zip(rs, angles):
        # shifted_angle = angle + angle * np.sin(2 * PI * t / DURATION)
        shifted_angle = angle + 2 * PI * t / DURATION
        shifted_r = max(0, r + WIDTH / 3 - WIDTH * np.sin(2 * PI * (t + PHASE_TIME) / DURATION))

        x, y = np.round(polar2cartesian(shifted_r, shifted_angle), 2) + WIDTH / 2
        # x, y = np.round(polar2cartesian(r, angle), 2) + WIDTH / 2

        circle = Circle(context, x=x, y=y, r=CIRCLE_RADIUS, fill_rgb=(1, 1, 1), stroke=True, gradient=None)
        circle.draw()

    return get_image(surface)

if __name__ == "__main__":
    output_file = os.path.join('output', OUTPUT_FILENAME)
    if os.path.isfile(output_file):
        print(output_file, 'exists. Exiting.')
        sys.exit()

    ## Set context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, WIDTH)
    context = cairo.Context(surface)

    rs, angles = set_circle_locations(context)

    clip = mpe.VideoClip(make_frame=make_frame, duration=DURATION)
    clip.write_gif(output_file, fps=FPS, program='imageio', opt='wu')
    # clip.write_gif(output_file, fps=FPS, program='ImageMagick', opt='OptimizePlus')
