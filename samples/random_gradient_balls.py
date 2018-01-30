import numpy as np
import matplotlib.pyplot as plt
import cairo
import moviepy.editor as mpy

width, height = 150, 150
duration = 2
nBalls = 60 ## Number of balls
R = 20		## Radius of balls

# Random values of radius, color, center
radii = np.random.randint(0.1 * width, 0.2 * width, nBalls)
colors = np.random.rand(nBalls, 3)
centers = np.random.randint(0, width, (nBalls, 2))

def colorGradient(gradientType, stops_and_colors, xy0, xy1, r01=None):
	if gradientType == "linear":
		grad = cairo.LinearGradient(xy0[0], xy0[1], xy1[0], xy1[1])
	elif gradientType == "radial":
		grad = cairo.RadialGradient(xy0[0], xy0[1], r01[0], xy1[0], xy1[1], r01[1])
	for stop, color in stops_and_colors:
		grad.add_color_stop_rgb(stop, *color)
	return grad

# Draw a circle
def drawCircle(context, x, y, r, fill_rgb=(1, 1, 1), stroke=False, line_width=5.0, gradient=None):
	context.save()
	context.set_line_width(line_width)
	context.arc(x, y, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	if stroke:
		context.stroke_preserve()
	if gradient is None:
		context.set_source_rgb(fill_rgb[0], fill_rgb[1], fill_rgb[2])
		context.fill()
	else:
		context.set_source(gradient)
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
	for radius, color, center in zip(radii, colors, centers):
		angle = 2 * np.pi * (t / duration * np.sign(color[0] - 0.5) + color[1])
		xy = center + polar2cartesian(width / 4, angle)
		grad = colorGradient(gradientType="radial", stops_and_colors=[(0, color), (R, color / 10)], xy0=[xy[0], xy[1]], xy1=[xy[0], xy[1]], r01=[0, R * 1.4])
		drawCircle(context, x=xy[0], y=xy[1], r=R, gradient=grad)
	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("balls60_150x150.gif",fps=60, program="ImageMagick", opt="OptimizePlus", fuzz=10)
