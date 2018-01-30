import numpy as np
from scipy.ndimage import rotate
import cairo
import colorsys
import moviepy.editor as mpy

width = height = 400
duration = 2
nPoly = 30
rStart = int(50.0 * (width / 2.0) / 100)
rEnd = int(0.1 * (width / 2.0) / 100)
interval = (rStart - rEnd) / float(nPoly)
BEAT = False
FPS = 15

# Draw a polygon
def drawPolygon(context, points, close_path=False, fill=None, stroke_width=0.0, stroke_rgb=(0, 0, 0), scaling=None):
	context.save()
	context.set_line_width(stroke_width)
	context.set_source_rgb(*stroke_rgb)

	context.move_to(*points[0])
	for point in points[1:]:
		context.line_to(*point)
	if close_path:
		context.close_path()
		context.move_to(0, 0)
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

angs = np.linspace(0, 2 * np.pi, 13)[:-1]
def getPoints(R, C):
	ps = np.array([R, R * np.sqrt(3)] * 6)
	points = C + np.array([polar2cartesian(p, ang) for p, ang in zip(ps, angs)])
	return points

def makeFrame(t):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)
	context.save()
	context.set_source_rgb(0, 0, 0)
	context.rectangle(0, 0, width, height)
	context.fill()
	context.restore()

	colors = np.linspace(1, 0, num=nPoly)
	colors = np.array([[i]*3 for i in colors])
	colors[:,1] = 0.0
	colors[:,2] = 0.0
	for n in xrange(nPoly):
		angle = 2 * np.pi * (1.0 * n / nPoly + t / duration)
		center = width * (0.5 + polar2cartesian(0.01, angle))
		if BEAT:
			distance = (rStart * np.sqrt(3)- rStart) * np.fabs(np.sin(np.pi * nPoly * t / duration + np.pi / 2)) + rStart
		else:
			distance = rStart
		points = getPoints(distance - n * interval, center)
		drawPolygon(context, points, close_path=True, fill=tuple(colors[n]),
					stroke_width=0.1, stroke_rgb=(0, 0, 0), scaling=None)

		## Black-white stars
		# drawPolygon(context, points, close_path=True, fill=tuple([(n + 1) % 2] * 3),
		# 			stroke_width=0.1, stroke_rgb=(0, 0, 0), scaling=None)

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("red_star_pyramid_beat_{}x{}.gif".format(width, height), fps=FPS, program="ImageMagick", opt="OptimizePlus", fuzz=10)