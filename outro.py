######################
# Generate an intro animation with the appropriate
# title for the lecture.
######################
import argparse, tomllib
from subprocess import call
from ffmpeg import *
from pathlib import Path

DEBUG = False

parser = argparse.ArgumentParser(
                    prog='Outro Slide Generator',
                    description='Generates a tail slide for a lecture with the CASA logo and copyright.',
                    epilog='Text at the bottom of help')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='outro.toml')
parser.add_argument('-r', '--running', type=float, help="The length of the intro slide talk.", default=4.0)
parser.add_argument('-l', '--lesson', type=int, help="The lesson key from the project.toml configuration file.", default=1)

args = parser.parse_args()

if args.defaults != None and Path(args.defaults).exists():
    with open(args.defaults, 'rb') as f:
        conf = tomllib.load(f)
else:
    conf = {}

if args.project != None and Path(args.project).exists():
    with open(args.project, 'rb') as f:
        proj = tomllib.load(f)
else:
    proj = {}

# Merge project settings into conf
for k,v in proj.items():
    if k not in conf:
        conf[k] = v

parent = Path(conf['outputs']['video'])
parent.mkdir(parents=True, exist_ok=True)

args.output = parent / conf['lessons'][str(args.lesson)]['track'].strip()
Path(args.output).mkdir(parents=True, exist_ok=True)

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

if args.running != None and args.running > 0:
    stfo = args.running - (fol + 0.1) # lecture fade out
    running_len = args.running
else:
    stfo = 0.175
    running_len  = stfo + fol + 0.1 # lecture fade out

if DEBUG:
    print(f"- Start fade in at {stfi:0.2f} for {fil:0.2f}s")
    print(f"- Start fade out at {stfo:0.2f} for {fol:0.2f}s")
    print(f"- Running length at {running_len:0.2f}s")

# Start building the command
cmd      = [f'ffmpeg -hide_banner -y']
filters  = {}
overlays = {}

print(f"""Video details:
    Fully visible until {stfo:0.2f}
    Start fade out at {stfo:0.2f} and fade out for {fol:0.2f}.""")
print(f"Running length {running_len:0.2f}.\n")

############################
# Common faders here
############################
fo  = img_fade(False, fol, stfo)
tfo = txt_fade(False, fol, stfo)

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
scene = scene(running_len, size=tuple(conf['project']['size'].split('x')))
scene.color = conf['bg'].get('color', '000000')
filters['bg'] = f'{str(scene)}'

# Image overlays
if conf['bgimg'].get('has', False) and Path(conf['bgimg']['path']).exists():
    print(f"+ Found background image {conf['bgimg']['path']}")
    cmd.append(f'-loop 1 -i {conf["bgimg"]["path"]} -t {scene.length}')

    # Build the filter for the background image
    filters['bgimg'] = f'{build_filter(len(filters), conf["bgimg"])} {fo}'

    overlays['bgimg'] = overlay('0', '0', True)

if conf['logo'].get('has', False) and Path(conf['logo']['path']).exists():
    print(f"+ Found logo image {conf['logo']['path']}")
    cmd.append(f'-loop 1 -i {conf["logo"]["path"]} -t {scene.length}')

    # Build the filter for the logo image
    filters['logo'] = f'{build_filter(len(filters), conf["logo"])} {fo}'

    x = img_position.x(conf['logo'].get('x',0))
    y = img_position.y(conf['logo'].get('y',0))
    overlays['logo'] = overlay(x, y, True)

if conf['copyright'].get('has', False) and Path(conf['copyright']['path']).exists():
    print(f"+ Found copyright image {conf['copyright']['path']}")
    cmd.append(f'-loop 1 -i {conf["copyright"]["path"]} -t {scene.length}')

    # Build the filter for the logo image
    filters['copy'] = f'{build_filter(len(filters), conf["copyright"])} {fo}'

    x = img_position.x(conf['copyright'].get('x',0))
    y = img_position.y(conf['copyright'].get('y',0))
    overlays['copy'] = overlay(x, y, True)

# Add null audio track
cmd.append(f'-f lavfi -i anullsrc=r=44100:cl=stereo:d={running_len}:n=64000')

# Now add the filters
cmd.append(f'-filter_complex "') # That double-quote is important!

for f,v in filters.items():
    cmd.append(f'{v} [{f}];')

last_filter = None
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

# Year for talk
if conf['year'].get('text', None) != None:
    try:
        txt = f"{int(conf['year']['text'])}/{int(conf['year']['text'])+1}"
    except:
        txt = conf['year']['text']

    x = txt_position.x(conf['year'].get('x',0))
    y = txt_position.y(conf['year'].get('y',0))
    #y = f"{ymin} - ({(conf['lecture']['size'] * conf['fonts']['leading'] * 0.55):0.0f})" 
    
    yr = text(txt, x, y, 
            size=conf['year']['size'], color=conf['fonts']['fontcolor_light'], 
            font=conf['fonts']['fontface'], style=conf['year']['style'], 
            halign=conf['year']['halign'], valign=conf['year']['valign'])
    yr.add_fader(tfo)
    cmd.append(str(yr))

# Copyright line
if conf['author'].get('text', None) != None:
    txt = f"{conf['author']['text']}"

    x = txt_position.x(conf['author'].get('x',0))
    y = txt_position.y(conf['author'].get('y',0))
    #y = f"{ymax} + ({(conf['lecture']['size'] * conf['fonts']['leading'] * 0.90):0.0f})" 

    author = text(txt, x, y, 
                size=conf['author']['size'], color=conf['fonts']['fontcolor_light'], 
                font=conf['fonts']['fontface'], style=conf['author']['style'],
                halign=conf['author']['halign'], valign=conf['author']['valign'])
    author.add_fader(tfo)
    cmd.append(str(author))

out = str(Path(args.output / '99-Outro.mp4')).replace(' ','\ ')

cmd.append(f'" -r 30 -c:v libx264 -c:a aac -shortest') # That double-quote is important!
cmd.append(f'-pix_fmt yuv420p -tune stillimage')
cmd.append(f'{out}')

if DEBUG != False:
    print("=" * 30)
    print(" \\\n".join(cmd))
    print("=" * 30)

call(" \\\n".join(cmd), shell=True)

exit()
