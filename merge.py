######################
# Take a set of audio tracks (.m4a) and still image files
# (.png) and merge them into a talk. We need to do this by
# merging each audio/image file into a MP4 file and then  
# combining the set of generated MP4s into a single lecture. 
######################
import argparse, tomllib
from subprocess import call, check_output
import re, glob, shutil
import math
from pathlib import Path

safe = re.compile(r'[^a-zA-Z0-9\-\.]+')

DEBUG = False

ppath = Path.home() / "anaconda3" / "envs" / "sds" / "bin"
ppath = ppath.resolve()

parser = argparse.ArgumentParser(
                    prog='Lecture Video Generator',
                    description='Generates a pre-recorded lecture from stills and audio files. You need to have generated these following a consistent naming/merge format.',
                    epilog='For example: `python ffmpeg/merge.py -n "Functions" -t 3.4-Functions`')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=int, help="Name of the lesson in the project.toml configuration file.", default=1)
parser.add_argument('-f', '--force', help="Force generation of video even if number of slides and audio segments doesn't match.", action='store_true')
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

parent = Path(conf['outputs']['merge'])
parent.mkdir(parents=True, exist_ok=True)

# ffmpeg is particular about filenames and doesn't like spaces
# or other special characters, so we sanitise the track name
# to create a safe folder name.
args.merge = parent / Path(safe.sub('_', conf['lessons'][str(args.lesson)]['track'].strip()))

# Create the folder for storing the files
if not args.merge.exists():
    args.merge.mkdir(parents=True, exist_ok=True)
    print(f"+ Created {args.merge}")
else:
    print(f"+ Found {args.merge}")
    if not args.quick:
        files = glob.glob(str(args.merge / "*.m4a"))
        if len(files) > 0:
            print(f"  - Emptying directory of already-rendered merge")
            for f in files:
                Path(f).unlink()

args.audio = Path(conf['outputs']['audio']) / conf['lessons'][str(args.lesson)]['track'].strip()
if not args.audio.exists():
    print(f"- Couldn't find audio folder: '{args.audio}'")
    exit()
else:
    print(f"+ Found audio folder {args.audio}.")

args.stills = Path(conf['outputs']['slides']) / conf['lessons'][str(args.lesson)]['track'].strip()
if not args.stills.exists():
    print(f"- Couldn't find stills folder: '{args.stills}'")
    exit()
else:
    print(f"+ Found stills folder {args.stills}.")

args.mp4 = Path(conf['outputs']['video']) / conf['lessons'][str(args.lesson)]['track'].strip()
if not args.mp4.exists():
    print(f"- Couldn't find MP4 folder: '{args.mp4}'")
    print(f"  Treating this as non-fatal since you might not have any MP4s to include.")
else:
    print(f"+ Found MP4 folder {args.mp4}.")

args.final = Path(conf['outputs']['final'])
if not args.final.exists():
    args.final.mkdir(parents=True, exist_ok=True)
    print(f"  Created final output folder {args.final}.")
else:
    print(f"+ Found final output folder {args.final}.")

# Read in the audio and stills filenames
audio_files = [x for x in sorted(args.audio.glob("*.m4a"))]
still_files = [x for x in sorted(args.stills.glob("*.png"))]
video_files = [x for x in sorted(args.mp4.glob("*.mp4"))]

if DEBUG: 
    print(f" + Audio files: {','.join([str(x) for x in audio_files])}")
    print(f" + Stills files: {','.join([str(x) for x in still_files])}")
    print(f" + Video files: {','.join([str(x) for x in video_files])}")

######################
# Organise the stills

# Find the stills indexes
still_pat = re.compile(r'_(\d{1,2})_')
still_map = {int(still_pat.search(str(x))[1]):x for x in still_files}

if DEBUG:
    print(f" Stills map: {still_map}")

######################
# Organise the audio
audio_pat = re.compile(r'_(\d{1,2})_')
audio_map = {int(audio_pat.search(str(x))[1]):x for x in audio_files}

if DEBUG:
    print(f" Audio map: {audio_map}")

######################
# Organise the existing video
video_pat = re.compile(r'_(\d{1,2})_')
video_map = {int(video_pat.search(str(x))[1]):x for x in video_files}

if DEBUG:
    print(f" Video map: {video_map}")

# There should be one fewer stills files because
# we are going to cut the intro slide from the
# stills (and replace that with an auto-generated)
# one, and cut the 'Resources' slide from the end.
if len(still_map) - len(audio_map) > 2:
    print("!" * 30)
    print(f"Unequal number of stills ({len(still_map)}) and audio ({len(audio_map)}) files found.")
    if max(still_map.keys()) - max(audio_map.keys()) > 2:
        print(f"  Still files: {', '.join([str(x) for x in sorted(still_map.keys())])}")
        print(f"  Audio files: {', '.join([str(x) for x in sorted(audio_map.keys())])}")
    else:
        print("You appear to be skipping some slides, which is fine.")
        print("In that case, we skip the final two slides on the assumption they are references and a thank you.")
    print("!" * 30)
    if not args.quick: exit()

###############
# For the first slide...
print("=" * 25)
print("o Generating first slide...")
fn_out = Path(args.merge / safe.sub('_', str(still_map[1].stem) + ".mp4"))
if args.force or not fn_out.exists():
    # Find out how long the intro audio track is
    probe =  f'ffprobe -hide_banner -sexagesimal -show_entries format=duration '
    probe += f'{re.escape(str(audio_map[1]))}'

    # Capture the duration
    merge = check_output(probe, shell=True).decode("utf-8").split("\n")[1]
    duration = re.match(r'duration=(\d{1,}):(\d{2}):(\d{2})\.(\d{3})\d+',merge)

    hrs = int(duration[1])
    mns = int(duration[2])
    sec = int(duration[3])
    ms  = math.ceil(float(duration[4])/10)

    # Translate single- and double-quotes to 
    # their 'fancy' equivalents
    transl_table = dict( [ (ord(x), ord(y)) for x,y in zip(u"'''\"\"--", u"‘’´“”–-") ] )
    
    cmd = ''
    cmd += f'{ppath / "python"} {"intro.py"} \\\n'
    cmd += f'  --project {args.project} \\\n'
    cmd += f'  --defaults {args.project.replace("project","intro")} \\\n'
    cmd += f'  --running {hrs * 60 * 60 + mns * 60 + sec + ms/100} \\\n'
    cmd += f'  --lesson {str(int(args.lesson))} \\\n'
    
    if DEBUG:
        print(f"  o {cmd}")
    call(cmd, shell=True)
    
    fn_in = str(Path(args.mp4 / f"{conf['lessons'][str(args.lesson)]['track'].strip()}_01_Intro.mp4"))

    cmd = ''
    cmd += f'ffmpeg -hide_banner -y \\\n'
    cmd += f'-i {re.escape(fn_in)} \\\n'
    cmd += f'-i {re.escape(str(audio_map[1]))} \\\n'
    cmd += f'-c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac \\\n'
    cmd += f'{re.escape(str(fn_out))}'
    
    if DEBUG:
        print(f"  o {cmd}")
    call(cmd, shell=True)

    print("  + First slide generated.")
    print("=" * 25)
else:
    print(f"+ Found existing Intro slide {fn_out}. Skipping...")

# Now get rid of the first slide
del(still_map[1])

# For the remaining stills
print("=" * 25)
print("o Generating remaining slide...")
for idx in sorted(still_map.keys()):
    print(f"{'-' * 25}")
    print(f"o Generating slide {idx}...")

    fn_out = Path(args.merge / safe.sub('_', str(still_map[idx].stem) + ".mp4"))
    if fn_out.exists() and not args.force:
        print(f"  - Output file {fn_out} already exists. Skipping.")
        continue
    elif video_map.get(idx, False) and video_map[idx].endswith('.mp4'):
        try:
            print(f"  + Found MP4 file to include {idx}:{video_map[idx]}")
            # Transcode to the correct format
            cmd = ''
            cmd += f'ffmpeg -hide_banner -y -r 30 \\\n'
            cmd += f'-i {re.escape(str(video_map[idx]))} \\\n'
            cmd += f'-c:v libx264 -pix_fmt yuv420p \\\n'
            cmd += f'-b:a 64k \\\n'
            cmd += f'{re.escape(str(fn_out))}'
            if DEBUG:
                print(f"  o {cmd}")
            call(cmd, shell=True)
            
            print(f"  + Slide {idx} generated.")
        except:
            print(f"  - Problem using MP4 file: {video_map.get(idx, 'N/A')}")
    elif still_map.get(idx, False) and audio_map.get(idx, False):
        try:
            print(f"  o Matching {still_map[idx]} -> {audio_map[idx]}")
            cmd = ''
            cmd += f'ffmpeg -hide_banner -y -r 30 -loop 1 \\\n'
            cmd += f'-i {re.escape(str(still_map[idx]))} \\\n'
            cmd += f'-i {re.escape(str(audio_map[idx]))} \\\n'
            cmd += f'-c:v libx264 -tune stillimage -shortest -pix_fmt yuv420p \\\n'
            cmd += f'-b:a 64k \\\n'
            cmd += f'{re.escape(str(fn_out))}'
            if DEBUG:
                print(f"  o {cmd}")
            call(cmd, shell=True)
        
            print(f"  + Slide {idx} generated.")
        except:
            print(f"  - Problem linking video and audio files:")
            print(f"    o {video_map.get(idx, 'N/A')}")
            print(f"    o {audio_map.get(idx, 'N/A')}")
    else:
        print(f"  - Unable to find both audio and still files for Slide {idx}")
        continue
print("+ All segments generated.")

print("=" * 25)
print("o Generating outro slide...")
fn_out = Path(args.merge / safe.sub('_',f"{conf['lessons'][str(args.lesson)]['track'].strip()}_99_Outro.mp4"))
if args.force or not fn_out.exists():

    cmd = ''
    cmd += f'{ppath / "python"} {"outro.py"} \\\n'
    cmd += f'  --project {args.project} \\\n'
    cmd += f'  --defaults {args.project.replace("project","outro")} \\\n'
    cmd += f'  --lesson {str(int(args.lesson))} \\\n'

    if DEBUG:
        print(f"  i {cmd}")
    call(cmd, shell=True)

    fn_in = str(Path(args.mp4 / f"{conf['lessons'][str(args.lesson)]['track'].strip()}_99_Outro.mp4"))
    shutil.copy(str(fn_in), str(fn_out))

    print("  + Outro video file created.")
    print("=" * 25)
else:
    print(f"+ Found existing outro slide {fn_out}. Skipping...")

# Now stitch together the MP4 segments
print("=" * 25)
print("o Stitching segments together...")

merge_pat = re.compile(f"{safe.sub('_',conf['lessons'][str(args.lesson)]['track'].strip())}" + r'_(\d{1,2})_')
merge_map = {int(merge_pat.search(str(x))[1]):x for x in args.merge.glob("*.mp4")}

if DEBUG:
    print(merge_map)

with open(Path(args.merge / 'segments.txt'), 'w') as f:
    for s in sorted(merge_map.keys()):
        f.write(f"file '{(str(merge_map[s].name))}'\n")
    f.write("")

fn_tmp = args.merge / f"{safe.sub('_', conf['lessons'][str(args.lesson)]['track'].strip())}.mp4"
fn_out = args.final / f"{conf['lessons'][str(args.lesson)]['week']}.{conf['lessons'][str(args.lesson)]['sequence']}-{safe.sub('_', conf['lessons'][str(args.lesson)]['track'].strip())}.mp4"

cmd = ''
cmd += f"ffmpeg -hide_banner -y -f concat -safe 1 "
cmd += f"-i {str(args.merge / 'segments.txt')} "
cmd += f"-c:v libx264 -af aresample=async=1000 -pix_fmt yuv420p \\\n"
cmd += f"{fn_tmp}"

if DEBUG: 
    print(f"  o {cmd}")
call(cmd, shell=True)

print("  + Unified (temporary) video file created.")

print("=" * 25)
print("o Removing leading black frames...")

cmd  = ''
cmd += f"ffmpeg -hide_banner -y -ss 00:00:00.075 "
cmd += f"-i {re.escape(str(fn_tmp))} -c:v copy -c:a copy {re.escape(str(fn_out))}"
if DEBUG: 
    print(f"  i {cmd}")
call(cmd, shell=True)

print("  o Removing temp file")
fn_tmp.unlink(missing_ok=True)

print("  + Done.")

print("=" * 25)

print(f"+++ {conf['lessons'][str(args.lesson)]['track'].strip()} talk generated +++")

exit()
