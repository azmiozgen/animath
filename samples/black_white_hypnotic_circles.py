import numpy as np
import matplotlib.pyplot as plt
import cairo
import moviepy.editor as mpy

width, height = 512, 512
duration = 2
nCircles = 2 # Number of circles

# Draw a circle
def circle(context, x, y, r, fill_rgb, stroke=False, line_width=5.0):
	context.save()
	context.set_line_width(line_width)
	context.arc(x, y, r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
	if stroke:
		context.stroke_preserve()
	context.set_source_rgb(fill_rgb[0], fill_rgb[1], fill_rgb[2])
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
	for i in range(nCircles):
		angle = 2 * np.pi * (1.0 * i / nCircles + t / duration)
		center = width * (0.5 + polar2cartesian(0.1, angle))
		circle(context, x=center[0], y=center[1],
						r=(width * (1.0 - 1.0 * i / nCircles)),
						fill_rgb=(i % 2, i % 2, i % 2))
	return getImage(surface)

clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
clip.write_gif("circles2_512x512.gif",fps=60, program="ImageMagick", opt="OptimizePlus", fuzz=10)
