######################
# Process a full lecture from start to finish. 
######################
import argparse, tomllib, re
from subprocess import call
from pathlib import Path

DEBUG = False

ppath = Path.home() / "anaconda3" / "envs" / "sds" / "bin"
ppath = ppath.resolve()

parser = argparse.ArgumentParser(
                    prog='process.py',
                    description='Integrates the various steps in extracting and converting a lecture to a video (audio has to be generated separately for now).',
                    epilog='For example: `python flip/process.py -t 3.4-Functions -n "It\'s Functional"`')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=int, help="Name of the lesson in the project.toml configuration file.", default=1)
parser.add_argument('-i', '--noimage', help="Skip export of the slide deck to PNG (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-a', '--noaudio', help="Skip export of the audio files to M4A (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-f', '--force', help="Force generation of new images, audio, and video.", action='store_true')
parser.add_argument('-q', '--quick', help="Quick generation (assumes MP4 segments haven't changed).", action='store_true')

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

# Extract Slides
if not args.noimage:
    print("=" * 40)
    print("=" * 11 + " Extracting deck " + "=" * 12)
    print("=" * 40)
    cmd = ''
    cmd += f'{ppath / "python"} {"deck.py"} \\\n'
    cmd += f'  -p {args.project} \\\n'
    cmd += f'  -l {args.lesson}'

    if DEBUG:
        print(f"- Extracting slides with command:")
        print(f"{cmd}")
    call(cmd, shell=True)
else: 
    print(f"- Skipping extraction of lesson {args.lesson}.")
    print(f"  Add `-i` to force export of slide deck to PNG.")

# Extract Audio
if not args.noaudio:
    print("=" * 40)
    print("=" * 11 + " Extracting audio " + "=" * 12)
    print("=" * 40)
    cmd = ''
    cmd += f'{ppath / "python"} {"audio.py"} \\\n'
    cmd += f'  -p {args.project} \\\n'
    cmd += f'  -l {args.lesson}'

    if DEBUG:
        print(f"- Extracting audio with command:")
        print(f"{cmd}")
    call(cmd, shell=True)
else: 
    print(f"- Skipping extraction of lesson {args.lesson}.")
    print(f"  Add `-a` to force export of narration to segmented M4A files.")

# Merge
print("=" * 40)
print("=" * 15 + " Merging. " + "=" * 15)
print("=" * 40)
cmd = ''
cmd += f'{ppath / "python"} {"merge.py"} \\\n'
cmd += f'  -p {args.project} \\\n'
cmd += f'  -l {args.lesson} \\\n'
if args.force:
    cmd += f'  -f \\\n'
if args.quick:
    cmd += f'  -q \\\n'

if DEBUG:
    print(f"- Merging segments with command:")
    print(f"{cmd}")
call(cmd, shell=True)

print("+ Done.")
exit()
