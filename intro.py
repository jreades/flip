######################
# Generate an intro animation with the appropriate
# title for the lecture.
######################
import argparse
from subprocess import call
from config import *
import os

this_year = 2024
logo_url = os.path.join('img','CASA_logo.png')
ccby_url = os.path.join('img','by-nc-sa.png')

parser = argparse.ArgumentParser(
                    prog='Intro Slide Generator',
                    description='Generates a title slide for a lecture with the module name and CASA logo showing first.',
                    epilog='Text at the bottom of help')
parser.add_argument('-l', '--length', type=float, help="The length of the intro slide talk.")
parser.add_argument('-t', '--talk', type=str, help="The title of the talk, for multi-line separate with \\n")
parser.add_argument('-o', '--output', type=str, help="Name of the ouptut MP4 file.", default=os.path.join('_mp4','intro.mp4'))

args = parser.parse_args()

os.makedirs('_mp4', exist_ok=True)

stfi = 0.15 # start fade in
fil  = 1.2  # fade in length
stfo = stfi + fil + 1.0 # start fade out
fol  = 0.4  # fade out length

lfi  = stfo + (fol - fol/2) # lecture fade in -- crossfade
if args.length != None and args.length > 0:
    lfo  = args.length - (fol + 0.1) # lecture fade out
    running_len = args.length
else:
    lfo  = stfo + fil + 1.0 # lecture fade out
    running_len = lfo + fol

# Set up scene
i = intro(running_len)

print(f"+ Video details:\n\tStart fade in at {stfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(stfi+fil):0.2f} to {stfo:0.2f} ({stfo-(stfi+fil):0.2f}s)\n\tStart fade out at {stfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Talk details:\n\tStart fade in at {lfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(lfi+fil):0.2f} to {lfo:0.2f} ({lfo-(lfi+fil):0.2f}s)\n\tStart fade out at {lfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Running length at {running_len:0.2f}.\n")

# Course name fading
course_fade_in = txt_fade(True, fil, stfi)
course_fade_out = txt_fade(False, fol, stfo)
course_x_fade = cross_fader(course_fade_in, course_fade_out)

# Logo fading
fi = img_fade(True, fil, stfi)
fo = img_fade(False, fol, stfo)

# Lecture fading
title_fade_in  = txt_fade(True, fil, lfi)
title_fade_out = txt_fade(False, fol, lfo)
xt_fade = cross_fader(title_fade_in, title_fade_out)

ccby = overlay('main_w/2-overlay_w/2', 'main_h/2+150', True)
logo = overlay('main_w/2-overlay_w/2', 'main_h/2+overlay_h*0.175', True)

t1 = text("Foundations of", '(w-text_w)/2', '(h/2-text_h*2.45)', 48)
t2 = text("Spatial Data Science", '(w-text_w)/2', '(h/2-text_h*0.75)', 48)
t1.add_fader(course_x_fade)
t2.add_fader(course_x_fade)

yr = text(f"{this_year}/{this_year+1}", '(w-text_w)/2', '(h/2-text_h*4)', 24)
title1 = text(args.talk.split("\\n")[0].replace(':','\\:'), '(w-text_w)/2', '(h/2-text_h/1.5)', 48)
if "\\n" in args.talk:
    title2 = text(args.talk.split("\\n")[1].replace(':','\\:'), '(w-text_w)/2', '(h/2+text_h/1.5)', 48)
    title2.add_fader(xt_fade)
    copy = text("by Jon Reades & Fulvio Lopane", '(w-text_w)/2', '(h/2+text_h*5.75)', 18) # 4.75 on small and 5.75 on large monitor???
else:
    copy = text("by Jon Reades & Fulvio Lopane", '(w-text_w)/2', '(h/2+text_h*2)', 18) # 2.35 on small and 3 on large monitor???
yr.add_fader(xt_fade)
title1.add_fader(xt_fade)
copy.add_fader(xt_fade)

params = {
    'bg': str(i),
    'logo': f'[0:v]{fi}, {fo}',
    'ccby': f'[1:v]{fi}, {fo}'
}

cmd = ''
cmd += f'ffmpeg -hide_banner -y \\\n'
cmd += f'-loop 1 -i {logo_url} -t {i.length} \\\n'
cmd += f'-loop 1 -i {ccby_url} -t {i.length} \\\n'
cmd += f'-filter_complex "\\\n'
for p,v in params.items():
    cmd += f'{v} [{p}]; \\\n'
cmd += f'[bg][logo] {logo} [bg1]; \\\n'
cmd += f'[bg1][ccby] {ccby}, \\\n'
cmd += str(t1) + f" \\\n"
cmd += str(t2) + f"  \\\n"
cmd += str(title1) + f" \\\n"
if 'title2' in locals():
    cmd += str(title2) + f" \\\n"
cmd += str(yr) + f" \\\n"
cmd += str(copy) + f" \\\n"
cmd += f'" -r 30 -c:v libx264 \\\n'
cmd += f'-pix_fmt yuv420p -tune stillimage {args.output}\n'

print(cmd)
call(cmd, shell=True)

#ffmpeg -i Test.mp4 -itsoffset 00:00:02 -i fanfare-1.m4a -map 0:0 -map 1:0 -c:v copy -async 1 out.mp4

exit()
