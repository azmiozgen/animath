import numpy as np
import matplotlib.pyplot as plt
import cairo
import colorsys
import moviepy.editor as mpy

width, height = 500, 500
nCircles = 2
t = 2.5
duration = 5
length = width / 4

def colorGradient(gradientType, stops_and_colors, xy0, xy1, r01=None):
	if gradientType == "linear":
		grad = cairo.LinearGradient(xy0[0], xy0[1], xy1[0], xy1[1])
	elif gradientType == "radial":
		grad = cairo.RadialGradient(xy0[0], xy0[1], r01[0], xy1[0], xy1[1], r01[1])
	for stop, color in stops_and_colors:
		if len(color) == 4:
			grad.add_color_stop_rgba(stop, *color)
		else:
			grad.add_color_stop_rgb(stop, *color)
	return grad

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
	context.stroke_preserve()
	context.restore()

	context.save()
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
	context.save()
	context.set_source_rgb(1, 1, 1)
	context.rectangle(0, 0, width, height)
	context.fill()
	context.restore()

	context.set_line_width(0.005 * width)
	context.set_source_rgb(0, 0, 0)

	curve_start = (100, 100)
	# curve_end = (200, 400)
	

	context.move_to(curve_start[0], 0)
	context.line_to(*curve_start)

	context.curve_to(curve_start[0], curve_start[1] + (curve_end[1] - curve_start[1]) * 0.6,
					 curve_end[0],   curve_start[1] + (curve_end[1] - curve_start[1]) * 0.4,
					 *curve_end)

	context.line_to(curve_end[0], 500)
	context.stroke_preserve()

	curve_start = (200, 100)
	curve_end = (100, 400)

	context.set_line_width(3)
	context.set_source_rgb(0, 0, 0)
	context.move_to(curve_start[0], 0)
	context.line_to(*curve_start)
	context.curve_to(curve_start[0], curve_start[1] + (curve_end[1] - curve_start[1]) * 0.6,
	curve_end[0],   curve_start[1] + (curve_end[1] - curve_start[1]) * 0.4,
	*curve_end)
	context.line_to(curve_end[0], 500)
	context.stroke_preserve()
	context.save()
	context.translate(x, y)
	context.rotate(angle)
	context.move_to(0, 0)
	context.rectangle(-length / 2, -length / 2, length, length)
	context.stroke_preserve()
	context.set_source_rgb(*color)
	context.fill()
	context.restore()

	return getImage(surface)

# clip = mpy.VideoClip(make_frame=makeFrame, duration=duration).resize(0.5)
# clip.write_gif("ellipse_{}x{}.gif".format(width, height),fps=15, program="ImageMagick", opt="OptimizePlus")



context.set_source_rgb(1, 0, 0)
context.fill()

img = getImage(surface)
surface.finish()
plt.grid()
plt.imshow(img)
plt.show()
