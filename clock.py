import numpy as np
from itertools import product
import cairo
import moviepy.editor as mpy
from objects import Arrow

WIDTH = 500
HEIGHT = 500
BACKGROUND = np.array((207, 207, 18)) / 255.
DURATION = 10

def getImage(surface):
	image = np.frombuffer(surface.get_data(), np.uint8)
	image = image.reshape((surface.get_height(), surface.get_width(), 4))
	image = image[:, :, [2, 1, 0, 3]]
	return image[:, :, :3]

def makeFrame(t):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
	context = cairo.Context(surface)
	context.save()
	context.set_source_rgb(*BACKGROUND)
	context.rectangle(0, 0, WIDTH, HEIGHT)
	context.fill()
	context.restore()

	## Hour-hand
	l = WIDTH * 0.2
	a = 0.25 * np.pi - 2.0 * np.pi * t / DURATION
	xx = WIDTH / 2
	yy = HEIGHT / 2
	hour = Arrow(context=context, x=xx, y=yy, length=l, angle=a, fill_rgb=(0, 0, 0), stroke=False, line_width=5.0, stroke_rgb=(0, 0, 0), gradient=None, scaling=None)
	hour.draw()

	## Minute-hand
	l = WIDTH * 0.3
	a = 0.25 * np.pi - 12.0 * 2.0 * np.pi * t / DURATION
	xx = WIDTH / 2
	yy = HEIGHT / 2
	minute = Arrow(context=context, x=xx, y=yy, length=l, angle=a, fill_rgb=(0, 0, 0), stroke=False, line_width=5.0, stroke_rgb=(0, 0, 0), gradient=None, scaling=None)
	minute.draw()

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=DURATION)
clip.write_gif("clock.gif",fps=25, program="ImageMagick", opt="OptimizePlus")
