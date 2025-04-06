import os
import sys

import cairo
from moviepy import VideoClip
import numpy as np

from objects import Circle

WIDTH = 800
HEIGHT = 800
CIRCLE_COUNT = 20
CIRCLE_RADIUS_MEAN = WIDTH / 50
CIRCLE_COLOR = np.array((1, 1, 1, 1))
CIRCLE_BUFFER_Y = 0.4 * HEIGHT
N_GROUPS = 8

DURATION = 10
FPS = 30

def get_image(surface):
    image = np.frombuffer(surface.get_data(), np.uint8)
    image = image.reshape((surface.get_height(), surface.get_width(), 4))
    image = image[:, :, [2, 1, 0, 3]]
    return image[:, :, :3]

def set_circle_locations():
    groups = []
    for i in range(N_GROUPS):
        xs = np.arange(5, WIDTH, WIDTH / CIRCLE_COUNT)
        rs = np.random.normal(loc=CIRCLE_RADIUS_MEAN,
                              scale=CIRCLE_RADIUS_MEAN / 4,
                              size=CIRCLE_COUNT)
        if i % 2 == 0:
            ys = np.zeros_like(xs) - CIRCLE_BUFFER_Y
        else:
            ys = np.ones_like(xs) * HEIGHT + CIRCLE_BUFFER_Y
        groups.append((xs.flatten(), ys, rs.flatten()))
    return groups

def make_frame(t):
    context.save()
    bg_color = np.array([0, 0, 0])
    context.set_source_rgb(*bg_color)
    context.rectangle(0, 0, WIDTH, HEIGHT)
    context.fill()
    context.restore()

    drawn_circles = []
    for i, group in enumerate(groups):
        xs, ys, rs = group
        for (x, y, r) in zip(xs, ys, rs):
            speed_as_power = 2 * r / CIRCLE_RADIUS_MEAN
            if i % 2 == 0:
                y_ = y + (HEIGHT + 2 * CIRCLE_BUFFER_Y) * (t / DURATION) ** speed_as_power
            else:
                y_ = y - (HEIGHT + 2 * CIRCLE_BUFFER_Y) * (t / DURATION) ** speed_as_power
            circle = Circle(context,
                            x=x, y=y_,
                            r=r,
                            fill_rgba=CIRCLE_COLOR,
                            stroke=True,
                            gradient=None)
            context.save()
            circle.draw()

            # Check for intersections with previously drawn circles
            for cx, cy, cr in drawn_circles:
                distance = np.sqrt((x - cx) ** 2 + (y_ - cy) ** 2)
                if distance < r + cr:  # Intersection detected
                    # Clip the intersection area and fill it with black
                    context.save()
                    context.arc(x, y_, r, 0, 2 * np.pi)
                    context.clip()
                    context.arc(cx, cy, cr, 0, 2 * np.pi)
                    context.clip()
                    context.set_source_rgb(0, 0, 0)  # Black color
                    context.paint()
                    context.restore()

            # Add the current circle to the list of drawn circles
            drawn_circles.append((x, y_, r))

    return get_image(surface)

if __name__ == '__main__':

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

    groups = set_circle_locations()

    clip = VideoClip(frame_function=make_frame, duration=DURATION)
    clip.write_gif(filename=output_file, fps=FPS, loop=0, logger='bar')
