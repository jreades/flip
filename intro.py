######################
# Generate an scene animation with the appropriate
# title for the lecture.
######################
import argparse, tomllib
from subprocess import call
from ffmpeg import *
from pathlib import Path

DEBUG = False

parser = argparse.ArgumentParser(
                    prog='Intro Slide Generator',
                    description='Generates a title slide for a lecture with the module name and CASA logo showing first.',
                    epilog='Text at the bottom of help')
parser.add_argument('-d', '--defaults', type=str, help="Path to the scene.toml configuration file.")
parser.add_argument('-l', '--length', type=float, help="The length of the scene slide talk.")
parser.add_argument('-t', '--talk', type=str, help="The title of the talk, for multi-line separate with \\n")
parser.add_argument('-o', '--output', type=str, help="Name of the ouptut MP4 file.", default=Path('_mp4/scene.mp4'))

args = parser.parse_args()

Path('_mp4').mkdir(exist_ok=True)

if args.defaults != None and Path(args.defaults).exists():
    with open(args.defaults, 'rb') as f:
        conf = tomllib.load(f)

# Determine lengths:
# - lfi == lecture fade in
# - stfi == start fade in
# - fil  == fade in length
# - stfo == start fade out
# - fol  == fade out length
# - run_len == total length of video
stfi = conf['timings']['start_fade_in']
fil  = conf['timings']['fade_in_duration']
stfo = conf['timings']['start_fade_out']
fol  = conf['timings']['fade_out_duration']
lfi  = stfo + (fol - fol/2) # crossfade

if args.length != None and args.length > 0:
    lfo  = args.length - (fol + 0.1) # lecture fade out
    run_len = args.length
else:
    lfo  = stfo + fil + 1.0 # lecture fade out
    run_len = lfo + fol

if DEBUG:
    print(f"- Start fade in at {stfi:0.2f} for {fil:0.2f}s")
    print(f"- Start fade out at {stfo:0.2f} for {fol:0.2f}s")
    print(f"- Lecture fade in at {lfi:0.2f}s")
    print(f"- Lecture fade out at {lfo:0.2f}s")
    print(f"- Running length at {run_len:0.2f}s")

# Start building the command
cmd      = [f'ffmpeg -hide_banner -y'] #  \\\n
filters  = {}
overlays = {}

print(f"+ Module details:\n\tStart fade in at {stfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(stfi+fil):0.2f} to {stfo:0.2f} ({stfo-(stfi+fil):0.2f}s)\n\tStart fade out at {stfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Lecture details:\n\tStart fade in at {lfi:0.2f} and fade in for {fil:0.2f}\n\tFully visible from {(lfi+fil):0.2f} to {lfo:0.2f} ({lfo-(lfi+fil):0.2f}s)\n\tStart fade out at {lfo:0.2f} and fade out for {fol:0.2f}.")
print(f"+ Running length at {run_len:0.2f}.\n")

############################
# Start with the image elements
############################
def build_filter(pos:int=0, conf:dict={}) -> str:
    str = f'[{len(filters)-1}:v] '
    if conf.get('scale', None) != None:
        str += f'scale={conf["scale"]}, '
    if conf.get('alpha', None) != None:
        str += f'colorchannelmixer=aa={conf["alpha"]}, '
    return str

# Set up the overall 'scene'
scene = scene(run_len)
scene.color = conf['bg'].get('color', '000000')
filters['bg'] = f'{str(scene)}'

# Image overlays
if conf['bgimg'].get('has', False) and Path(conf['bgimg']['path']).exists():
    print(f"+ Found background image {conf['bgimg']['path']}")
    cmd.append(f'-loop 1 -i {conf["bgimg"]["path"]} -t {scene.length}')

    # Build the filter for the background image
    bi = img_fade(True, fil, stfi)
    bo = img_fade(False, fol, lfo)
    filters['bgimg'] = f'{build_filter(len(filters), conf["bgimg"])} {bi}, {bo}'

    overlays['bgimg'] = overlay('0', '0', True)

if conf['logo'].get('has', False) and Path(conf['logo']['path']).exists():
    print(f"+ Found logo image {conf['logo']['path']}")
    cmd.append(f'-loop 1 -i {conf["logo"]["path"]} -t {scene.length}')

    # Build the filter for the logo image
    fi = img_fade(True, fil, stfi)
    fo = img_fade(False, fol, stfo)
    filters['logo'] = f'{build_filter(len(filters), conf["logo"])} {fi}, {fo}'

    x = img_position.x(conf['logo'].get('x',0))
    y = img_position.y(conf['logo'].get('y',0))
    overlays['logo'] = overlay(x, y, True)

if conf['copyright'].get('has', False) and Path(conf['copyright']['path']).exists():
    print(f"+ Found copyright image {conf['copyright']['path']}")
    cmd.append(f'-loop 1 -i {conf["copyright"]["path"]} -t {scene.length}')

    # Build the filter for the logo image
    fi = img_fade(True, fil, stfi)
    fo = img_fade(False, fol, stfo)
    filters['copy'] = f'{build_filter(len(filters), conf["copyright"])} {fi}, {fo}'

    x = img_position.x(conf['copyright'].get('x',0))
    y = img_position.y(conf['copyright'].get('y',0))
    overlays['copy'] = overlay(x, y, True)

# Now add the filters
cmd.append(f'-filter_complex "') # That double-quote is important!

for f,v in filters.items():
    cmd.append(f'{v} [{f}];')

# Now we have to combine the filters
all_filters = list(filters.keys())
for f in range(1, len(all_filters)):
    cmd.append(f'[f{f-1}][{all_filters[f]}] {overlays[all_filters[f]]} [f{f}];')
    if f==1:
        cmd[-1] = cmd[-1].replace(f'[f{f-1}]', f'[{all_filters[f-1]}]') # first one is different
    if f==len(all_filters)-1:
        cmd[-1] = cmd[-1].replace(f'[f{f}];', ',') # remove the trailing semicolon

############################
# Now add the text elements
############################
course_x_fade  = cross_fader(txt_fade(True, fil, stfi), txt_fade(False, fol, stfo))
lecture_x_fade = cross_fader(txt_fade(True, fil, lfi), txt_fade(False, fol, lfo))

# Course title text
if conf['course'].get('text', None) != None:
    
    lines = conf['course']['text'].split('\n')
    idx   = (len(lines) - 1)/2

    for i, txt in enumerate(lines):

        print(f"Course title line {i}: '{txt}'.")

        if len(txt) > 30:
            print(f"*** WARNING: Course title line {i} '{txt}' is quite long ({len(txt)} characters). Consider shortening to improve appearance. ***")
        
        if i < idx:
            ymod = f"-({round(abs(i-idx)*(conf['course']['size'] * conf['fonts']['leading']))})"
        elif i > idx:
            ymod = f"+({round(abs(i-idx)*(conf['course']['size'] * conf['fonts']['leading']))})"
        else:
            ymod = ""

        x = txt_position.x(conf['course'].get('x',0))
        y = txt_position.y(conf['course'].get('y',0)) + ymod
    
        print(f" Position: x={x}, y={y}")

        course = text(txt.replace(':','\\:'), x, y,
                size=conf['course']['size'], color=conf['fonts']['fontcolor_light'], 
                font=conf['fonts']['fontface'], style=conf['course']['style'], 
                halign=conf['course']['halign'], valign=conf['course']['valign'])
        course.add_fader(course_x_fade)
        cmd.append(str(course))

# Lecture title text
ymin = ""
ymax = ""

if conf['lecture'].get('text', None) != None or args.talk != None:
    if args.talk != None:
        lines = args.talk.split('\\n')
    else:
        lines = conf['lecture']['text'].split('\n')
    
    idx = (len(lines) - 1)/2

    for i, txt in enumerate(lines):

        print(f"Lecture title line {i} '{txt}'.")

        if len(txt) > 30:
            print(f"*** WARNING: Talk title line {i} '{txt}' is quite long ({len(txt)} characters). Consider shortening to improve appearance. ***")
        if i < idx:
            ymod = f"-({round(abs(i-idx)*(conf['lecture']['size'] * conf['fonts']['leading']))})"
        elif i > idx:
            ymod = f"+({round(abs(i-idx)*(conf['lecture']['size'] * conf['fonts']['leading']))})"
        else:
            ymod = ""

        x = txt_position.x(conf['lecture'].get('x',0))
        y = txt_position.y(conf['lecture'].get('y',0)) + ymod
        if i==0:
            ymin = y
        if i==len(lines)-1:
            ymax = y
        print(f"    Position: x={x}, y={y}")
        lecture = text(txt.replace(':','\\:'), x, y, 
                size=conf['lecture']['size'], color=conf['fonts']['fontcolor_light'], 
                font=conf['fonts']['fontface'], style=conf['lecture']['style'], 
                halign=conf['lecture']['halign'], valign=conf['lecture']['valign'])
        lecture.add_fader(lecture_x_fade)
        cmd.append(str(lecture))

print(f"  - Lecture title spans y={ymin} to y={ymax}")

# Year for talk
if conf['year'].get('text', None) != None:
    try:
        txt = f"{int(conf['year']['text'])}/{int(conf['year']['text'])+1}"
    except:
        txt = conf['year']['text']

    x = txt_position.x(conf['year'].get('x',0))
    #y = txt_position.y(conf['year'].get('y',0))
    y = f"{ymin} - ({(conf['lecture']['size'] * conf['fonts']['leading'] * 0.55):0.0f})" 
    
    yr = text(txt, x, y, 
            size=conf['year']['size'], color=conf['fonts']['fontcolor_light'], 
            font=conf['fonts']['fontface'], style=conf['year']['style'], 
            halign=conf['year']['halign'], valign=conf['year']['valign'])
    yr.add_fader(lecture_x_fade)
    cmd.append(str(yr))

# Copyright line
if conf['author'].get('text', None) != None:
    txt = f"{conf['author']['text']}"

    x = txt_position.x(conf['author'].get('x',0))
    #y = txt_position.y(conf['author'].get('y',0))
    y = f"{ymax} + ({(conf['lecture']['size'] * conf['fonts']['leading'] * 0.90):0.0f})" 

    author = text(txt, x, y, 
                size=conf['author']['size'], color=conf['fonts']['fontcolor_light'], 
                font=conf['fonts']['fontface'], style=conf['author']['style'],
                halign=conf['author']['halign'], valign=conf['author']['valign'])
    author.add_fader(lecture_x_fade)
    cmd.append(str(author))

cmd.append(f'" -r 30 -c:v libx264') # That double-quote is important!
cmd.append(f'-pix_fmt yuv420p -tune stillimage')
cmd.append(f'{args.output}')

if DEBUG:
    print("=" * 30)
    print(" \\\n".join(cmd))
    print("=" * 30)

call(" \\\n".join(cmd), shell=True)

exit()
