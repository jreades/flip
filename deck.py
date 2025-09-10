######################
# Take a lecture and extract it to a set of PNG files. 
######################
import argparse, tomllib
from subprocess import call
import re, glob
from pathlib import Path

DEBUG = False

parser = argparse.ArgumentParser(
                    prog='extract_deck.py',
                    description='Generates a set of PNGs from a Reveal.js lecture. Requires node.js and decktape to be installed.',
                    epilog='For example: `python ffmpeg/extract.py -t 3.4-Functions -s https://jreades.github.io/fsds/lectures`')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=int, help="Name of the lesson in the project.toml configuration file.", default=1)

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

parent = Path(conf['outputs']['slides'])
parent.mkdir(parents=True, exist_ok=True)

args.output = parent / conf['lessons'][str(args.lesson)]['track'].strip()

scrn_size   = conf['project'].get('size', '1280x720')
scrn_format = conf['project'].get('format', 'png')
pause       = conf['project'].get('pause', 500)

# Create the folder for storing the files
if not args.output.exists():
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"+ Created {args.output}")
else:
    print(f"+ Found {args.output}")
    files = glob.glob(str(args.output / "*.m4a"))
    if len(files) > 0:
        print(f"  - Emptying directory of already-rendered output")
        for f in files:
            Path(f).unlink()

print(f"+ Preparing to extract screenshots.")

server_path = f"{conf['project']['server']}/" \
                f"{conf['lessons'][str(args.lesson)]['week']}." \
                f"{conf['lessons'][str(args.lesson)]['sequence']}-" \
                f"{re.sub(r'[^a-zA-Z0-9]+','_',conf['lessons'][str(args.lesson)]['track'].strip())}" \
                ".html"
print(server_path)

# And extract the slides as PNGs to the folder
cmd = ''
cmd += f'decktape \\\n'
cmd += f'  --screenshots --screenshots-directory {args.output} \\\n'
cmd += f'  --size {scrn_size} --screenshots-size {scrn_size} --screenshots-format {scrn_format} \\\n'
cmd += f'  --pause {pause} --load-pause {pause} --headless true \\\n'
cmd += f"  {server_path} {conf['lessons'][str(args.lesson)]['track'].strip() + '.pdf'}"

if re.DEBUG:
    print(f"  -i: {cmd}")
call(cmd, shell=True)

print(f"+ PNGs for {conf['lessons'][str(args.lesson)]['track'].strip()} generated +++")

exit()
