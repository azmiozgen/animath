import numpy as np
import cairo
import moviepy.editor as mpy

width, height = 1024, 1024
duration = 4
nCircles = 8

# Draw a circle
def drawCircle(context, x, y, r, fill=None, stroke_width=0.0, stroke_rgb=(0, 0, 0), scaling=None):
	context.save()
	context.set_line_width(stroke_width)
	context.set_source_rgb(*stroke_rgb)

	context.arc(x, y, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	context.stroke_preserve()

	if (type(fill) == tuple) and (len(fill) == 3):
		context.set_source_rgb(*fill)
		context.fill()
	elif (type(fill) == tuple) and (len(fill) == 4):
		context.set_source_rgba(*fill)
		context.fill()
	elif (type(fill) == cairo.LinearGradient) or (type(fill) == cairo.RadialGradient):
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
	for angle in np.linspace(0, 2 * np.pi, nCircles + 1)[:-1]:
		center = np.array([width / 2, height / 2]) + polar2cartesian(0.2 * width, angle)
		for i in [0, 1]:		## One outer, one new inner
			drawCircle(context, x=center[0], y=center[1], r=width * 0.45 * (i + t / duration), fill=(1, 1, 1, 1.0 / 255))	## Circles are almost transparent

	## Intersection points of circles become 1 + 1 = 2
	## So mod operation makes them negative color
	return 255 * ((getImage(surface)) % 2)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration).resize(0.5)
clip.write_gif("roses{}_{}x{}.gif".format(nCircles, width, height),fps=15, program="ImageMagick", opt="OptimizePlus", fuzz=30)
