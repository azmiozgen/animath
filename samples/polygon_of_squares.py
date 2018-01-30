import numpy as np
from scipy.ndimage import rotate
import cairo
import colorsys
import moviepy.editor as mpy

width = height = 400
duration = 5
nSquares = 200
nGon = 3											## Polygon edges
length = width / 8
R = width / 4
minDist = R * np.cos(np.pi / nGon)		## Minimum center-to-edge distance of polygon
BEAT = True								## Beat the polygon like a heart
ROTATION = True						## Rotate whole polygon (Little discontinuity in .gif !!)
FPS = 15

def polar2cartesian(r, theta):
	return  r * np.array([np.cos(theta), np.sin(theta)])

def getImage(surface):
	image = np.frombuffer(surface.get_data(), np.uint8)
	image = image.reshape((surface.get_height(), surface.get_width(), 4))
	image = image[:, :, [2, 1, 0, 3]]
	return image[:, :, :3]

C = np.array([width / 2, height / 2])		## Common center
a = np.linspace(0, 2 * np.pi, nSquares)[:-1]

## Parametric n-gon equation
## https://tpfto.wordpress.com/2011/09/15/parametric-equations-for-regular-and-reuleaux-polygons/
r = np.cos(np.pi / nGon) / (np.cos(a - (np.pi / nGon) * (2 * np.floor((nGon * a) / (2 * np.pi)) + 1 )))

d = np.cumsum(np.sqrt(((r[1:] - r[:-1]) ** 2)))
d = [0] + list(d / d.max())
r = R * r
P = zip(r, a, d)

def half(t, side="left", beat=True, rotation=False):
	ipoint = 0 if side=="left" else nSquares / 2
	points = (P[ipoint:] + P[:ipoint])[::-1]

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	context = cairo.Context(surface)
	for (r, a, d) in points:
		angle = -(6 * np.pi * d + 2 * t * np.pi / duration)		## Angle of squares

		if beat:
			distance = (r - minDist) * np.fabs(np.sin(np.pi * nGon * t / duration + np.pi / 2)) + minDist
		else:
			distance = r
		center = C + polar2cartesian(distance, a)			## Center of the squares

		color = colorsys.hls_to_rgb((2 * d + t / duration) % 1, 0.5, 0.5)
		context.set_line_width(0.005 * width)
		context.set_source_rgb(1, 1, 1)

		context.save()
		context.translate(*center)
		context.rotate(angle)
		context.move_to(0, 0)
		context.rectangle(-length / 2, -length / 2, length, length)
		context.stroke_preserve()
		context.set_source_rgb(*color)
		context.fill()
		context.restore()

	img = getImage(surface)

	# ## Rotate whole polygon (Little discontinuity in .gif !!)
	# if rotation:
	# 	ratio = t / duration
	# 	if ratio <= 0.25 or ratio > 0.75:
	# 		return (img[:, :width / 2] if (side=="left") else img[:, width / 2:])
	# 	else:
	# 		return (img[:, width / 2:] if (side=="left") else img[:, :width / 2])
	# else:
	return (img[:, :width / 2] if (side=="left") else img[:, width / 2:])

def makeFrame(t, beat=BEAT, rotation=ROTATION):
	if rotation:
		whole_angle = 360 * t / duration			## Angle of polygon in deg (if rotation is True)
		img = np.hstack([half(t, "left", BEAT, True), half(t, "right", BEAT, True)])
		return rotate(img, whole_angle, reshape=False)
	else:
		return np.hstack([half(t, "left", BEAT), half(t, "right", BEAT)])


clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
if ROTATION:
	clip.write_gif("polygon{}_of_squares{}_rotating_{}x{}.gif".format(nGon, nSquares, width, height),fps=FPS, program="ImageMagick", opt="OptimizePlus")
else:
	clip.write_gif("polygon{}_of_squares{}_{}x{}.gif".format(nGon, nSquares, width, height),fps=FPS, program="ImageMagick", opt="OptimizePlus")
