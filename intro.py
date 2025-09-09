######################
# Generate an intro animation with the appropriate
# title for the lecture.
######################
import argparse
from subprocess import call
from ffmpeg import *
from vparams import *
from pathlib import Path

parser = argparse.ArgumentParser(
                    prog='Intro Slide Generator',
                    description='Generates a title slide for a lecture with the module name and CASA logo showing first.',
                    epilog='Text at the bottom of help')
parser.add_argument('-l', '--length', type=float, help="The length of the intro slide talk.")
parser.add_argument('-t', '--talk', type=str, help="The title of the talk, for multi-line separate with \\n")
parser.add_argument('-o', '--output', type=str, help="Name of the ouptut MP4 file.", default=Path('_mp4/intro.mp4'))

args = parser.parse_args()

Path('_mp4').mkdir(exist_ok=True)

# Determine lengths:
# - lfi == lecture fade in
# - stfi == start fade in
# - fil  == fade in length
# - stfo == start fade out
# - fol  == fade out length
# - run_len == total length of video
if args.length != None and args.length > 0:
    lfo  = args.length - (fol + 0.1) # lecture fade out
    run_len = args.length
else:
    lfo  = stfo + fil + 1.0 # lecture fade out
    run_len = lfo + fol

print(f"Start fade in at {stfi:0.2f} for {fil:0.2f}s")
print(f"Start fade out at {stfo:0.2f} for {fol:0.2f}s")
print(f"Lecture fade in at {lfi:0.2f}s")
print(f"Lecture fade out at {lfo:0.2f}s")
print(f"Running length at {run_len:0.2f}s")

# Set up scene
intro = intro(run_len)
intro.color = "42324a" # "#574d62" # dark purple

print(f"+ Video details:\n\tStart fade in at {stfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(stfi+fil):0.2f} to {stfo:0.2f} ({stfo-(stfi+fil):0.2f}s)\n\tStart fade out at {stfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Talk details:\n\tStart fade in at {lfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(lfi+fil):0.2f} to {lfo:0.2f} ({lfo-(lfi+fil):0.2f}s)\n\tStart fade out at {lfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Running length at {run_len:0.2f}.\n")

# Image overlays
bgimg = overlay('0', '0', True)
ccby  = overlay(ccby_position.get_x(), ccby_position.get_y(), True)
logo  = overlay(logo_position.get_x(), logo_position.get_y(), True)

# Course name fading
course_fade_in = txt_fade(True, fil, stfi)
course_fade_out = txt_fade(False, fol, stfo)
course_x_fade = cross_fader(course_fade_in, course_fade_out)

# Lecture title fading
title_fade_in  = txt_fade(True, fil, lfi)
title_fade_out = txt_fade(False, fol, lfo)
xt_fade = cross_fader(title_fade_in, title_fade_out)

# Logo fading
fi = img_fade(True, fil, stfi)
fo = img_fade(False, fol, stfo)

# Background fading
bi = img_fade(True, fil, stfi)
bo = img_fade(False, fol, lfo)

# Course title text
titles = []
middle_index = (len(title.lines) - 1)/2
for i, txt in enumerate(title.lines):
    if len(txt) > 30:
        print(f"*** WARNING: Course title line {i} '{txt}' is quite long ({len(txt)} characters). Consider shortening to improve appearance. ***")
    if i < middle_index:
        y = f"-({round(abs(i-middle_index)*(title.size * leading))})"
    elif i > middle_index:
        y = f"+({round(abs(i-middle_index)*(title.size * leading))})"
    else:
        y = ""
    print(f"Course title line {i} '{txt}' will be positioned at y={y}.")
    print(f"    Position: x={title.position.get_x()}, y={title.position.get_y()}{y}")
    t = text(txt, title.position.get_x(), f"{title.position.get_y()}{y}",
             title.size, color=fontcolor_light, font=title.font, style=title.style,
             halign=title.h_align, valign=title.v_align)
    t.add_fader(course_x_fade)
    titles.append(t)

# Lecture title text
lecture.lines = args.talk.split('\\n') if args.talk != None else lecture.lines
middle_index = (len(lecture.lines) - 1)/2
for i, txt in enumerate(lecture.lines):
    if len(txt) > 30:
        print(f"*** WARNING: Talk title line {i} '{txt}' is quite long ({len(txt)} characters). Consider shortening to improve appearance. ***")
    if i < middle_index:
        y = f"-({round(abs(i-middle_index)*(lecture.size * leading))})"
    elif i > middle_index:
        y = f"+({round(abs(i-middle_index)*(lecture.size * leading))})"
    else:
        y = ""
    print(f"Lecture title line {i} '{txt}' will be positioned at y={y}.")
    print(f"    Position: x={lecture.position.get_x()}, y={lecture.position.get_y()}{y}")
    t = text(txt.replace(':','\\:'), lecture.position.get_x(), f"{lecture.position.get_y()}{y}", 
             lecture.size, color=fontcolor_light, font=lecture.font, style=lecture.style,
             halign=lecture.h_align, valign=lecture.v_align)
    t.add_fader(xt_fade)
    titles.append(t)

# Year for talk
y = f"-({round(middle_index * lecture.size * leading + lecture.size * 0.75 * leading)})"
yr = text(f"{year.lines[0]}/{int(year.lines[0])+1}", year.position.get_x(), year.position.get_y(), 
          year.size, color=fontcolor_light, font=year.font, style=year.style, 
          halign=year.h_align, valign=year.v_align)
yr.add_fader(xt_fade)

# Copyright line
y = f"+({round((middle_index + 1) * lecture.size * leading)})"
copy = text(f"by {author.lines[0]}", author.position.get_x(), author.position.get_y(), 
            author.size, color=fontcolor_light, font=author.font, style=author.style,
            halign=author.h_align, valign=author.v_align)
copy.add_fader(xt_fade)

params = {
    'bg': str(intro),
    'img': f'[0:v]scale=1280:-1,colorchannelmixer=aa=0.175, {bi}, {bo}',
    'logo': f'[1:v]scale=52:-1, {fi}, {fo}',
    'ccby': f'[2:v]{fi}, {bo}'
}

cmd = ''
cmd += f'ffmpeg -hide_banner -y \\\n'
cmd += f'-loop 1 -i {bg_url} -t {intro.length} \\\n'
cmd += f'-loop 1 -i {logo_url} -t {intro.length} \\\n'
cmd += f'-loop 1 -i {ccby_url} -t {intro.length} \\\n'
cmd += f'-filter_complex "\\\n'
for p,v in params.items():
    cmd += f'{v} [{p}]; \\\n'
cmd += f'[bg][img] {bgimg} [bg1]; \\\n'
cmd += f'[bg1][logo] {logo} [bg2]; \\\n'
cmd += f'[bg2][ccby] {ccby}, \\\n'
for t in titles:
    cmd += str(t) + f" \\\n"
cmd += str(yr) + f" \\\n"
cmd += str(copy) + f" \\\n"
cmd += f'" -r 30 -c:v libx264 \\\n'
cmd += f'-pix_fmt yuv420p -tune stillimage {args.output}\n'

print(cmd)
#call(cmd, shell=True)

#ffmpeg -i Test.mp4 -itsoffset 00:00:02 -i fanfare-1.m4a -map 0:0 -map 1:0 -c:v copy -async 1 out.mp4

exit()
