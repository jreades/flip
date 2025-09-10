######################
# Take a lecture narration and extract it to a set of M4A files (one per slide). 
######################
import argparse, tomllib
from pydub import AudioSegment
from subprocess import call
import re, glob
from pathlib import Path

DEBUG = False

parser = argparse.ArgumentParser(
                    prog='Audio Segment Generator',
                    description='Generates a set of audio segments from a single m4a file. Requires Audacity to be installed and running.',
                    epilog='For example: `python ffmpeg/extract_audio.py -t 6.2-Randomness`')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=str, help="Name of the lesson in the project.toml configuration file.", default='1')

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

parent = Path(conf['outputs']['audio'])
parent.mkdir(parents=True, exist_ok=True)

args.output = parent / conf['lessons'][str(args.lesson)]['track'].strip()

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

######################
# Find the appropriate metadata
print(f"+ Finding segment metadata in the Markdown file.")

args.markdown = Path(conf['project']['cuts'])

if args.markdown.exists():
    print(f"  + Found {args.markdown}")
else:
    print(f"  - Couldn't find {args.markdown}")
    exit()

audio_meta = []
loading    = False

header_remove = re.compile('^## ')
with open(args.markdown, 'r') as f:
    for i in f.readlines():
        txt = i.strip()
        if txt.startswith('## '):
            if txt.replace('## ','') == conf['lessons'][args.lesson]['track'].strip():
                #print("Found it...")
                loading = True
            else:
                loading = False
        elif loading == True:
            audio_meta.append(txt)

# Convert it to a data structure
audio_meta = [[y.strip() for y in x.split('|') if y != ''] for x in audio_meta if x != '' and not x.startswith('| -')]            

print(f"  + Found {len(audio_meta)} rows.")

header = audio_meta.pop(0)
audio_ds = {x:[] for x in header}

hmsm = re.compile(r'^(?:(\d{1,2})\:)?(\d{1,2}):(\d{1,2})\.(\d+)$')
for i in audio_meta:
    for jdx, j in enumerate(i):
        if hmsm.match(j):
            #print(f"Match! {j}")
            ts = hmsm.search(j)
            audio_ds[header[jdx]].append(str(float(0 if ts.group(1) is None else (float(ts.group(1)))) * 60 * 60 + float(ts.group(2)) * 60 + float(ts.group(3)) + float('0.' + ts.group(4))))
        elif re.match(r'^\d+$',j):
            #print(f"{int(j):02d}")
            audio_ds[header[jdx]].append(f"{int(j):02d}")
        else:
            audio_ds[header[jdx]].append(j)

print(f"  + Data structure created.")

######################
# Load the source file, assign the labels 
# from the metadata, and save to segments.
print(f"+ Preparing to extract audio.")

audio_src = Path(conf['project']['audio']) / f"{conf['lessons'][args.lesson]['track'].strip()}.m4a"
if not audio_src.exists():
    print(f"Couldn't find file: {audio_src}")
    exit()

track = AudioSegment.from_file(audio_src, format="m4a")
print(f"Loaded {len(track):,}ms ({len(track)/(1000*60):0.2f}mn) of recording!")
print()

for row in range(0, len(audio_ds[header[0]])):
    print(f"  + Narration for slide {row} exporting: {audio_ds['Name'][row]}")

    start_ts = float(audio_ds['Start'][row])
    end_ts   = float(audio_ds['End'][row])
    nm       = "_".join([audio_ds['Sequence'][row],audio_ds['Name'][row]])
    
    segment = track[start_ts * 1000:end_ts*1000]
    segment.export((Path(args.output / f"{conf['lessons'][str(args.lesson)]['track'].strip()}_{nm}.m4a")), format="ipod")

print(f"+++ Audio segments for {conf['lessons'][args.lesson]['track'].strip()} generated +++")

exit()
