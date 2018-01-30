import numpy as np
import cairo
import moviepy.editor as mpy

width, height = 200, 75
duration = 5
R = 10		## Radius of ball
jw = 50		## Jump width
jh = 35		## Jump height
ground = 0.75 * height
ball_color = np.array([1, 0, 0])

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

# Draw a circle
def drawCircle(context, x, y, r, fill_rgb=(1, 1, 1), stroke=False, line_width=5.0, gradient=None, scaling=None):
	context.save()
	if gradient is None:
		context.set_source_rgb(fill_rgb[0], fill_rgb[1], fill_rgb[2])
	else:
		context.set_source(gradient)
	context.set_line_width(line_width)
	if scaling is not None:
		context.translate(x, y)
		context.scale(scaling[0], scaling[1])
		context.arc(0, 0, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	else:
		context.arc(x, y, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	if stroke:
		context.stroke_preserve()
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
	x = (-width / 3) + (5 * width / 3) * (t / duration)
	y = ground - jh * 4 * (x % jw) * (jw - (x % jw)) / jw ** 2
	coefficient = (jh - y) / jh

	ball_grad = colorGradient(gradientType="radial", stops_and_colors=[(0, ball_color), (1, ball_color / 10)],
								xy0=[x + R * 0.3, y - R * 0.3], xy1=[x, y], r01=[0, R * 1.4])
	shadow_grad = colorGradient(gradientType="radial", stops_and_colors=[(0, (0, 0, 0, 0.3 - coefficient / 4.0)), (1, (0, 0, 0, 0))],
								xy0=[x, ground + R / 2], xy1=[x, ground + R / 2], r01=[0, R * 1.4])


	drawCircle(context, x=x, y=y, r=R, gradient=ball_grad)
	drawCircle(context, x=x, y=ground + R / 2, r=R - coefficient / 4, gradient=shadow_grad, scaling=[1.0, 0.8])

	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("jumping_ball2_500x200.gif",fps=25, program="ImageMagick", opt="OptimizePlus")
