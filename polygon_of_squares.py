import colorsys
import os
import sys

import cairo
import moviepy.editor as mpe
import numpy as np
from scipy.ndimage import rotate

from lib import polar2cartesian
from lib import PI

WIDTH = 700  ## Frame width
HEIGHT = 700  ## Frame height
LENGTH = WIDTH / 6  ## Length of the small squares
N_SQUARES = 200
N_GON = 3  ## # of polygon edges
RADIUS = WIDTH / 3

BEAT = True  ## Beat the polygon like a heart
BEAT_COEFF = 0.81
MIN_DIST = 0.75 * RADIUS * np.cos(PI / N_GON)  ## Minimum center-to-edge distance of polygon

ROTATION = False  ## Rotate whole polygon (Little discontinuity in .gif !!)

DURATION = 6.06  ## Animation duration
PSEUDO_DURATION = 6.06  ## Animation duration with empty frames at the end
FPS = 20

EXTENSION = 'mp4'
AUDIO_FILE = "./asset/analog-vintage-loop_double.mp3"


def get_image(surface):
    image = np.frombuffer(surface.get_data(), np.uint8)
    image = image.reshape((surface.get_height(), surface.get_width(), 4))
    image = image[:, :, [2, 1, 0, 3]]
    return image[:, :, :3]

def half(context, t,
         side="left",
         rotation=False,
         duration=DURATION,
         width=WIDTH,
         height=HEIGHT,
         radius=RADIUS,
         length=LENGTH,
         n_squares=N_SQUARES,
         n_gon=N_GON,
         beat=True,
         beat_coeff=BEAT_COEFF,
         min_dist=MIN_DIST):

    ipoint = 0 if side=="left" else n_squares // 2
    points1 = (P1[ipoint:] + P1[:ipoint])[::-1]
    points2 = (P2[ipoint:] + P2[:ipoint])[::-1]

    context.set_source_rgb(0, 0, 0)
    context.rectangle(0, 0, WIDTH, HEIGHT)
    context.fill()

    ## For Instagram
    if t > DURATION:
        img = get_image(surface)
        return (img[:, :width // 2] if (side == "left") else img[:, width // 2:])

    ## Inner polygon
    for (r1, a, d1) in points1:
        r1 = (radius / 4) * r1
        angle = -(6 * PI * d1 + 2 * t * PI / duration)  ## Rotational angle of the small squares

        distance = r1
        square_center = center + polar2cartesian(distance, a)  ## Center of the small squares

        color = colorsys.hls_to_rgb((2 * d1 + t / duration) % 1, 0.5, 0.5)
        context.set_line_width(0.0005 * width)
        context.set_source_rgb(0, 0, 0)  ## Square border colors

        context.save()
        context.translate(*square_center)
        context.rotate(angle)
        context.move_to(0, 0)
        context.rectangle(-length / 8, -length / 8, length / 4, length / 4)
        context.stroke_preserve()
        context.set_source_rgb(*color)
        context.fill()
        context.restore()

    ## Outer polygon
    for (r2, a, d2) in points2:
        r2 = radius * r2
        angle = -(6 * PI * d2 + 2 * t * PI / duration)  ## Rotational angle of the small squares

        if beat:
            distance = (r2 - min_dist) * np.fabs(np.sin(PI * (n_gon + 2) * beat_coeff * t / duration + PI / 2)) + min_dist
        else:
            distance = r2
        square_center = center + polar2cartesian(distance, a)  ## Center of the small squares

        color = colorsys.hls_to_rgb((2 * d2 + t / duration) % 1, 0.5, 0.5)
        context.set_line_width(0.0015 * width)
        context.set_source_rgb(0, 0, 0)  ## Square border colors

        context.save()
        context.translate(*square_center)
        context.rotate(angle)
        context.move_to(0, 0)
        context.rectangle(-length / 2, -length / 2, length, length)
        context.stroke_preserve()
        context.set_source_rgb(*color)
        context.fill()
        context.restore()

    img = get_image(surface)
    return (img[:, :width // 2] if (side == "left") else img[:, width // 2:])

def make_frame(t):
    left_half = half(context, t, side='left')
    right_half = half(context, t, side='right')
    img = np.hstack([left_half, right_half])
    if ROTATION:
        whole_angle = 360 * t / DURATION
        return rotate(img, whole_angle, reshape=False)
    else:
        return img


if __name__ == "__main__":    

    if EXTENSION not in ['gif', 'mp4']:
        print('Choose one of the extension: gif, mp4')
        sys.exit()

    if EXTENSION != '.gif' and not os.path.isfile(AUDIO_FILE):
        print(AUDIO_FILE, 'not found. Making .gif file.')
        EXTENSION = 'gif'

    if ROTATION:
        output_file_wo_ext = "polygon{}_of_squares{}_rotating_{}x{}".format(N_GON, N_SQUARES, WIDTH, HEIGHT)
    else:
        output_file_wo_ext = "polygon{}_of_squares{}_{}x{}".format(N_GON, N_SQUARES, WIDTH, HEIGHT)
    output_file = os.path.join('output', output_file_wo_ext + '.' + EXTENSION)
    os.makedirs('output', exist_ok=True)

    if os.path.isfile(output_file):
        print(output_file, 'exists. Exiting.')
        sys.exit()

    ## Set surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    context = cairo.Context(surface)
    context.set_source_rgb(0, 0, 0)
    context.rectangle(0, 0, WIDTH, HEIGHT)
    context.fill()

    center = np.array([WIDTH // 2, HEIGHT // 2])  ## Common center
    a = np.linspace(0, 2 * PI, N_SQUARES)[:-1]  ## Polar angles of the center of small squares

    ## Parametric n-gon equation for 
    ## https://tpfto.wordpress.com/2011/09/15/parametric-equations-for-regular-and-reuleaux-polygons/
    r1 = np.cos(PI / N_GON) / (np.cos(a - (PI / N_GON) * (2 * np.floor((N_GON * a) / (2 * PI)) + 1)))
    r2 = np.cos(PI / (N_GON + 2)) / (np.cos(a - (PI / (N_GON + 2)) * (2 * np.floor(((N_GON + 2) * a) / (2 * PI)) + 1)))

    d1 = np.cumsum(np.sqrt(((r1[1:] - r1[:-1]) ** 2)))
    d1 = [0] + list(d1 / (d1.max()) + 1e-10)
    d2 = np.cumsum(np.sqrt(((r2[1:] - r2[:-1]) ** 2)))
    d2 = [0] + list(d2 / (d2.max()) + 1e-10)
    P1 = list(zip(r1, a, d1))
    P2 = list(zip(r2, a, d2))

    videoclip = mpe.VideoClip(make_frame=make_frame, duration=PSEUDO_DURATION)
    if EXTENSION == 'gif':
        videoclip.write_gif(output_file, fps=FPS, program='ImageMagick', opt='OptimizePlus')
    else:
        _audioclip = mpe.AudioFileClip(AUDIO_FILE)
        audioclip = mpe.CompositeAudioClip([_audioclip])
        videoclip.audio = audioclip
        videoclip.write_videofile(output_file, fps=FPS)
