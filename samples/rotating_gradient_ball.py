import numpy as np
import cairo
import moviepy.editor as mpy

width, height = 512, 512
duration = 2
R = 128		## Radius of ball
color = np.array([1, 0, 0])

def colorGradient(gradientType, stops_and_colors, xy0, xy1, r01=None):
	if gradientType == "linear":
		grad = cairo.LinearGradient(xy0[0], xy0[1], xy1[0], xy1[1])
	elif gradientType == "radial":
		grad = cairo.RadialGradient(xy0[0], xy0[1], r01[0], xy1[0], xy1[1], r01[1])
	for stop, color in stops_and_colors:
		grad.add_color_stop_rgb(stop, *color)
	return grad

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
	center = np.array([width / 2, height / 2])
	angle = 2 * np.pi * t / duration
	grad_center = width * (0.5 + polar2cartesian(0.1, angle))
	grad = colorGradient(gradientType="radial", stops_and_colors=[(0, color), (1, color / 10)], xy0=grad_center, xy1=grad_center, r01=[0, R * 1.3])
	# grad = colorGradient(gradientType="linear", stops_and_colors=[(0, color), (1, color / 10)], xy0=grad_center - R, xy1=grad_center + R)
	drawCircle(context, x=center[0], y=center[1], r=R, fill=grad)
	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("rotating_gradient2_512x512.gif",fps=5, program="ImageMagick", opt="OptimizePlus", fuzz=10)
