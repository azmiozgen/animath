import numpy as np
import cairo
import moviepy.editor as mpy

width, height = 512, 512
duration = 2.0
nDisksPerCycle = 8
speed = 0.05

delay = (1.0 * duration) / (2 * nDisksPerCycle)
nDisks = int(nDisksPerCycle / speed)
t0 = 1.0 / speed

# Draw a circle
def drawCircle(context, x, y, r, fill=None, stroke_width=0.0, stroke_rgb=(0, 0, 0), scaling=None):
	context.save()
	context.set_line_width(stroke_width)
	context.set_source_rgb(*stroke_rgb)

	context.translate(x, y)
	if scaling is not None:
		context.scale(scaling[0], scaling[1])
		context.arc(0, 0, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	else:
		context.arc(0, 0, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	context.stroke_preserve()

	if (type(fill) == tuple) and (len(fill) == 3):
		context.set_source_rgb(*fill)
		context.fill()
	elif (type(fill) == tuple) and (len(fill) == 4):
		context.set_source_rgba(*fill)
		context.fill()
	elif type(fill) == cairo.LinearGradient or type(fill) == cairo.RadialGradient:
		context.set_source(fill)	## Fill gradient
		context.fill()

	context.restore()

def polar2cartesian(r, theta):
	return  r * np.array([np.cos(theta), np.sin(theta)])

def getImage(surface):
	image = np.frombuffer(surface.get_data(), np.uint8)
	image = image.reshape((surface.get_height(), surface.get_width(), 4))
	image = image[:, :, [2, 1, 0, 3]]
	return image[:, :, :3]


def makeFrame(t):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)

	for i in xrange(1, nDisks):
		a = (np.pi / nDisksPerCycle) * (nDisks - i -1)
		r = np.maximum(0, speed * (t + t0 - delay * (nDisks - i - 1)))
		center = width * (0.5 + polar2cartesian(r, a))
		color = 3 * ((1.0 * i / nDisksPerCycle) % 1.0,)
		drawCircle(context, x=center[0], y=center[1], r=0.3 * width, fill=color, stroke_width=0.01 * width)

	drawCircle(context, x=width / 2, y=height / 2, r=0.72 * width, stroke_width=0.5 * width)								## Wider black bound
	drawCircle(context, x=width / 2, y=height / 2, r=0.49 * width, stroke_width=0.02 * width, stroke_rgb=(1, 1, 1))			## Thinner white bound

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("black_white_spiral_{}x{}.gif".format(width, height),fps=30, program="ImageMagick", opt="OptimizePlus", fuzz=10)
