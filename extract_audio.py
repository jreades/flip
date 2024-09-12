######################
# Take a lecture narration and extract it to a set of M4A files (one per slide). 
######################
import argparse
from pydub import AudioSegment
from subprocess import call
from config import *
import os, re, glob

ppath = os.path.join(os.path.expanduser("~"),"anaconda3","envs","sds","bin")

parser = argparse.ArgumentParser(
                    prog='Audio Segment Generator',
                    description='Generates a set of audio segments from a single m4a file. Requires Audacity to be installed and running.',
                    epilog='For example: `python ffmpeg/extract_audio.py -t 6.2-Randomness`')
parser.add_argument('-t', '--talk', type=str, help="The file name of the talk (this needs to match both in the audio_segments.md file and the M4A file).")

args = parser.parse_args()

# Strip off the HTML suffix (or any other suffix)
if re.search(r'\.\w{2,4}$', args.talk):
    args.talk = re.sub(r'\.\w{2,4}$','',args.talk)

# Only the slides use the '_'
args.src = re.sub(r'_',' ',args.talk)

args.output = os.path.join('_audio',args.talk)

# Create the folder for storing the files
if not os.path.exists(args.output):
    os.makedirs(args.output, exist_ok=True)
    print(f"+ Created {args.output}")
else:
    print(f"+ Found {args.output}")
    files = glob.glob(os.path.join(args.output, "*.m4a"))
    if len(files) > 0:
        print(f"  - Emptying directory of already-rendered output")
        for f in files:
            os.remove(f)

######################
# Find the appropriate metadata
print(f"+ Finding segment metadata in Markdown file.")

audio_meta = []
loading    = False

header_remove = re.compile('^## ')
with open(os.path.join('ffmpeg','audio_segments.md'), 'r') as f:
    for i in f.readlines():
        txt = i.strip()
        if txt.startswith('## '):
            if txt.replace('## ','') == args.src:
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

audio_root = '/Users/jreades/Library/CloudStorage/OneDrive-UniversityCollegeLondon/CASA0013/Audio'
#audio_root = os.path.expanduser("~"),'Desktop','Audio'

audio_src = os.path.join(audio_root,args.src+'.m4a')
if not os.path.exists(audio_src):
    print(f"Couldn't find file: {audio_src}")
    exit()

track = AudioSegment.from_file(audio_src, format="m4a")
print(f"Loaded {len(track):,}ms ({len(track)/(1000*60):0.2f}mn) of recording!")
print()

for row in range(0, len(audio_ds[header[0]])):
    print(f"  + Narration for slide {row} exporting: {audio_ds['Name'][row]}")

    start_ts = float(audio_ds['Start'][row])
    end_ts   = float(audio_ds['End'][row])
    nm       = "-".join([audio_ds['Sequence'][row],audio_ds['Name'][row]])
    
    segment = track[start_ts * 1000:end_ts*1000]
    segment.export(os.path.join(args.output,f"{nm}.m4a"), format="ipod")

print(f"+++ Audio segments for {args.talk} generated +++")

exit()
