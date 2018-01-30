import numpy as np
from itertools import product
import cairo
import moviepy.editor as mpy
from objects import Circle

WIDTH = 500
HEIGHT = 500
INTERVAL = 25
Xs = np.arange(INTERVAL, WIDTH, INTERVAL)
Ys = np.arange(INTERVAL, HEIGHT, INTERVAL)
coords = list(product(Ys, Xs))

R = WIDTH / 100
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

	element = 2 * int((t / DURATION) * len(coords))
	if element <= len(coords):
		for coord in coords[:element]:
			circle = Circle(context, x=coord[0], y=coord[1], r=R, fill_rgb=(0, 0, 0), stroke=True, gradient=None)
			circle.draw()
	else:
		element = element - len(coords)
		for coord in coords[element:]:
			circle = Circle(context, x=coord[0], y=coord[1], r=R, fill_rgb=(0, 0, 0), stroke=True, gradient=None)
			circle.draw()

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=DURATION)
clip.write_gif("ball_test.gif",fps=25, program="ImageMagick", opt="OptimizePlus")
