import numpy as np
import cairo
import moviepy.editor as mpy

## TODO
## GRADIENT IN POLYGONS IS BROKEN !!

width, height = 500, 500
duration = 2
R = 20 ## Font size
word = "yeah"
distance = width / (len(word) + 1)
xy = np.array(zip(np.arange(distance, width, distance), np.array(len(word) * [height / 2,])))		## Coordinates of letters

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


def makeFrame(t):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)
	context.save()
	context.set_source_rgb(1, 1, 1)
	context.rectangle(0, 0, width, height)
	context.fill()
	context.restore()

	context.select_font_face("Lato", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	context.set_font_size(3 * R / 2)
	points = [polar2cartesian(R, a) for a in np.linspace(0, 2 * np.pi, 6)[:-1]]

	for i, letter in enumerate(word):
		angle = 2 * np.pi * max(0, min(1, 2 * t / duration - 1.0 * i / 5))
		x_ex, y_ex, w_ex, h_ex = context.text_extents(letter)[:4]
		nx = -w_ex / 2.0
		ny = h_ex / 2
		grad = colorGradient(gradientType="linear", stops_and_colors=[(0, (1, 0, 0)), (1, (1, 1, 1))],
							 xy0=[xy[i][0], xy[i][1] - R], xy1=[xy[i][0], xy[i][1] + R])

		context.save()
		context.translate(*xy[i])
		context.rotate(angle)
		context.move_to(0, 0)
		drawPolygon(context, points, close_path=True, fill=grad, stroke_width=3, stroke_rgb=(0, 0, 0))
		context.restore()

		context.save()
		context.translate(*xy[i])
		context.rotate(angle)
		context.translate(nx, ny)
		context.move_to(0, 0)
		context.show_text(letter)
		context.restore()

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("text_in_polygon2_{}x{}.gif".format(width, height), fps=15, program="ImageMagick", opt="OptimizePlus", fuzz=10)
