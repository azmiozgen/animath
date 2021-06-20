import numpy as np
import cairo
import moviepy.editor as mpy

class Circle(object):
    """Circle class"""

    def __init__(self, context, x, y, r, fill_rgb=(1, 1, 1), stroke=False, line_width=5.0, gradient=None, scaling=None):
        self.context = context
        self.x = x
        self.y = y
        self.r = r
        self.fill_rgb = fill_rgb
        self.stroke = stroke
        self.line_width = line_width
        self.gradient = gradient
        self.scaling = scaling

    def draw(self):
        self.context.save()
        if self.gradient is None:
            self.context.set_source_rgb(self.fill_rgb[0], self.fill_rgb[1], self.fill_rgb[2])
        else:
            self.context.set_source(self.gradient)
        self.context.set_line_width(self.line_width)
        if self.scaling is not None:
            self.context.translate(self.x, self.y)
            self.context.scale(self.scaling[0], self.scaling[1])
            self.context.arc(0, 0, self.r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
        else:
            self.context.arc(self.x, self.y, self.r, 0, 2 * np.pi)   ## (x, y, r, theta_start, theta_end)
        if self.stroke:
            self.context.stroke_preserve()
        self.context.fill()
        self.context.restore()

class Arrow(object):
    """Arrow class"""

    def __init__(self, context, x, y, length, angle, fill_rgb=(1, 1, 1), stroke=False, line_width=1.0, stroke_rgb=(0, 0, 0), gradient=None, scaling=None):
        self.context = context
        self.x = x
        self.y = y
        self.length = length
        self.angle = angle
        self.points = [(x, y)]
        self.points.append((x + self.length * np.cos(self.angle), y - self.length * np.sin(self.angle)))
        self.points.append((x + (self.length * 0.9) * np.cos(self.angle + 0.20), y - (self.length * 0.9) * np.sin(self.angle + 0.20)))
        self.points.append((x + (self.length * 0.9) * np.cos(self.angle - 0.20), y - (self.length * 0.9) * np.sin(self.angle - 0.20)))

        self.fill_rgb = fill_rgb
        self.stroke = stroke
        self.line_width = line_width
        self.stroke_rgb = stroke_rgb
        self.gradient = gradient
        self.scaling = scaling

    def draw(self):
        self.context.save()
        self.context.set_line_width(self.line_width)
        self.context.set_source_rgb(*self.stroke_rgb)

        self.context.move_to(*self.points[0])
        self.context.line_to(*self.points[1])
        self.context.line_to(*self.points[2])
        self.context.move_to(*self.points[1])
        self.context.line_to(*self.points[3])

        self.context.move_to(0, 0)
        self.context.stroke_preserve()

        self.context.restore()
