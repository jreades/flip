######################
# Take a set of audio tracks (.m4a) and still image files
# (.png) and merge them into a talk. We need to do this by
# merging each audio/image file into a MP4 file and then  
# combining the set of generated MP4s into a single lecture. 
######################
import argparse, tomllib
from subprocess import call, check_output
import re, glob, shutil, math, sys
from pathlib import Path

safe = re.compile(r'[^a-zA-Z0-9\-\.]+')

DEBUG = False

ppath = Path.home() / "anaconda3" / "envs" / "sds" / "bin"
ppath = ppath.resolve()

# Sibling scripts are resolved relative to this file so that
# flip can be run from any working directory.
script_dir = Path(__file__).resolve().parent

parser = argparse.ArgumentParser(
    prog='Lecture Video Generator',
    description='Generates a pre-recorded lecture from stills and audio files. You need to have generated these following a consistent naming/merge format.',
    epilog='For example: `python flip/merge.py -n "Functions" -t 3.4-Functions`'
)
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=int, help="Name of the lesson in the project.toml configuration file.", default=1)
parser.add_argument('-f', '--force', help="Regenerate output even if it appears to be up to date.", action='store_true')
parser.add_argument('-y', '--yes', help="Render even if there are more stills than expected (normally prompts or stops).", action='store_true')

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

# Intermediate segments are re-encoded in the final concat, so they use a
# higher quality (lower CRF) to limit generation loss. Defaults to crf/2.
icrf = conf['project'].get('icrf', int(conf['project']['crf']) // 2)

def media_length(fn):
    """Length of a media file in seconds, used to cut each segment to its narration."""
    probe = f'ffprobe -v error -show_entries format=duration -of csv=p=0 {re.escape(str(fn))}'
    return float(check_output(probe, shell=True).decode("utf-8").strip())

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

if len(still_files) == 0:
    print(f"- No stills (PNGs) found in {args.stills}. Re-run the deck export without `-i`.")
    exit()

# Clips can also be listed in the cuts file by giving a path (relative to
# the working directory) ending in `.mp4` in the Name column, e.g.:
# | - | - | 18 | videos/Sheffield.mp4 |
# These take precedence over any clip for the same slide in the MP4 folder.
clip_map = {}
cuts = Path(conf['project']['cuts'])
if cuts.exists():
    loading = False
    for line in cuts.read_text().splitlines():
        txt = line.strip()
        if txt.startswith('## '):
            loading = txt[3:].strip() == conf['lessons'][str(args.lesson)]['track'].strip()
        elif loading and txt.startswith('|'):
            cells = [x.strip() for x in txt.strip('|').split('|')]
            if len(cells) >= 4 and cells[2].isdigit() and cells[3].lower().endswith('.mp4'):
                clip_map[int(cells[2])] = Path(cells[3])

missing = [str(x) for x in clip_map.values() if not x.exists()]
if len(missing) > 0:
    print(f"- Couldn't find MP4 file(s) listed in {cuts}: {', '.join(missing)}")
    print(f"  Paths are resolved relative to the working directory: {Path.cwd()}")
    exit()
elif len(clip_map) > 0:
    print(f"+ Found {len(clip_map)} MP4 file(s) listed in {cuts}.")

fn_final = args.final / f"{conf['lessons'][str(args.lesson)]['week']}.{conf['lessons'][str(args.lesson)]['sequence']}-{safe.sub('_', conf['lessons'][str(args.lesson)]['track'].strip())}.mp4"

# Skip if the final video is newer than all of its inputs. The intro and 
# outro MP4s are regenerated on every merge so we use their settings instead.
inputs  = audio_files + still_files
inputs += [x for x in video_files if not x.stem.endswith(('_01_Intro', '_99_Outro'))]
inputs += list(clip_map.values())
inputs += [Path(args.project).with_name(f"{x}.toml") for x in ('intro', 'outro')]
inputs  = [x for x in inputs if x.exists()]

if not args.force and fn_final.exists() and len(inputs) > 0 \
        and fn_final.stat().st_mtime > max(x.stat().st_mtime for x in inputs):
    print(f"+ {fn_final} is up to date. Use `-f` to force regeneration.")
    exit()

files = glob.glob(str(args.merge / "*.mp4"))
if len(files) > 0:
    print(f"  - Emptying directory of already-rendered merge")
    for f in files:
        Path(f).unlink()

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
try:
    video_map = {int(video_pat.search(str(x))[1]):x for x in video_files}
except TypeError:
    print(f"No matches on pattern {video_pat.pattern} in video files: {', '.join([str(x) for x in video_files])}.")
    video_map = {}
    exit()
video_map.update(clip_map)

if DEBUG:
    print(f" Video map: {video_map}")

# There should be 1-3 more stills (PNGs) than audio
# files (M4As) because we are going to cut the following
# from the PNG run: the intro slide, the 'Resources', the 
# 'Thank you' and, if it exists, the 'Accessibility Report'
# generated by AXE in Quarto.
cutoff = 3 # This should cover the maximal case
if len(still_map) - (len(audio_map) + len(video_map)) > cutoff:
    print("!" * 30)
    print(f"Quite a few more stills ({len(still_map)}) than audio ({len(audio_map)}) files found.")
    if max(still_map.keys()) - max(audio_map.keys()) > cutoff:
        print(f"  Still files: {', '.join([str(x) for x in sorted(still_map.keys())])}")
        print(f"  Audio files: {', '.join([str(x) for x in sorted(audio_map.keys())])}")
    else:
        print("You appear to be skipping some slides, which is fine.")
        print("In that case, we skip the final few slides on the assumption they are references, a thank you, and an optional accessibility report.")
    print("To ignore this and render the video anyway use `-y`.")
    print("!" * 30)
    if args.yes:
        print("  `-y` set, continuing.")
    elif sys.stdin.isatty() and input("Continue anyway? [y/N] ").strip().lower() in ('y', 'yes'):
        print("  Continuing.")
    else:
        exit()

###############
# For the first slide...
print("-" * 25)
print("o Generating first slide...")
fn_out = Path(args.merge / safe.sub('_', str(still_map[1].stem) + ".mp4"))
if True:
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
    cmd += f'{ppath / "python"} {script_dir / "intro.py"} \\\n'
    cmd += f'  --project {args.project} \\\n'
    cmd += f'  --defaults {Path(args.project).with_name("intro.toml")} \\\n'
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
    cmd += f'-r {conf["project"].get("fps", 30)} -c:v {conf["project"]["vcodec"]} -crf {icrf} {conf["project"].get("vopts", "")} -pix_fmt yuv420p \\\n'
    cmd += f'-c:a {conf["project"]["acodec"]} -ar 48000 -ac 2 \\\n'
    cmd += f'{re.escape(str(fn_out))}'
    
    if DEBUG:
        print(f"  o {cmd}")
    call(cmd, shell=True)

    print("  + First slide generated.")
    print("." * 25)

# Now get rid of the first slide
del(still_map[1])

# For the remaining stills
print("-" * 25)
print("o Generating remaining slide...")
for idx in sorted(still_map.keys()):
    print(f"{'-' * 25}")
    print(f"o Generating slide {idx}...")

    fn_out = Path(args.merge / safe.sub('_', str(still_map[idx].stem) + ".mp4"))
    if video_map.get(idx, False) and str(video_map[idx].resolve()).endswith('.mp4'):
        try:
            print(f"  + Found MP4 file to include {idx}:{video_map[idx]}")
            # Transcode to the correct format
            cmd = ''
            cmd += f'ffmpeg -hide_banner -y -fflags +genpts \\\n'
            cmd += f'-i {re.escape(str(video_map[idx]))} \\\n'
            cmd += f'-r {conf["project"].get("fps", 30)} -c:v {conf["project"]["vcodec"]} -crf {icrf} {conf["project"].get("vopts", "")} -pix_fmt yuv420p \\\n'
            cmd += f'-c:a {conf["project"]["acodec"]} -b:a 64k -ar 48000 -ac 2 \\\n' # -map 0 -avoid_negative_ts make_zero \\\n'
            cmd += f'{re.escape(str(fn_out))}'
            if DEBUG:
                print(f"  o {cmd}")
            call(cmd, shell=True)
            
            print(f"  + Slide {idx} generated.")
        except Exception as e:
            print(f"  - Problem using MP4 file: {video_map.get(idx, 'N/A')}: {e}")
    elif still_map.get(idx, False) and audio_map.get(idx, False):
        try:
            print(f"  o Matching {still_map[idx]} -> {audio_map[idx]}")
            cmd = ''
            # -shortest overshoots by up to ~1s with x265 (frames buffered in the
            # encoder), which accumulates as drift once segments are concatenated.
            cmd += f'ffmpeg -hide_banner -y -framerate {conf["project"].get("fps", 30)} -loop 1 \\\n'
            cmd += f'-i {re.escape(str(still_map[idx]))} \\\n'
            cmd += f'-i {re.escape(str(audio_map[idx]))} \\\n'
            cmd += f'-t {media_length(audio_map[idx]):.3f} -r {conf["project"].get("fps", 30)} \\\n'
            cmd += f'-c:v {conf["project"]["vcodec"]} -crf {icrf} {conf["project"].get("vopts", "")} -pix_fmt yuv420p \\\n'
            cmd += f'-c:a {conf["project"]["acodec"]} -b:a 64k -ar 48000 -ac 2 \\\n'
            cmd += f'{re.escape(str(fn_out))}'
            if DEBUG:
                print(f"  o {cmd}")
            call(cmd, shell=True)
        
            print(f"  + Slide {idx} generated.")
        except Exception as e:
            print(f"  - Problem linking video and audio files: {e}")
            print(f"    o {video_map.get(idx, 'N/A')}")
            print(f"    o {audio_map.get(idx, 'N/A')}")
    else:
        print(f"  - Unable to find both audio and still files for Slide {idx}")
        continue
print("+ All segments generated.")

print("-" * 25)
print("o Generating outro slide...")
fn_out = Path(args.merge / safe.sub('_',f"{conf['lessons'][str(args.lesson)]['track'].strip()}_99_Outro.mp4"))
if True:
    cmd = ''
    cmd += f'{ppath / "python"} {script_dir / "outro.py"} \\\n'
    cmd += f'  --project {args.project} \\\n'
    cmd += f'  --defaults {Path(args.project).with_name("outro.toml")} \\\n'
    cmd += f'  --lesson {str(int(args.lesson))} \\\n'

    if DEBUG:
        print(f"  i {cmd}")
    call(cmd, shell=True)

    fn_in = str(Path(args.mp4 / f"{conf['lessons'][str(args.lesson)]['track'].strip()}_99_Outro.mp4"))
    shutil.copy(str(fn_in), str(fn_out))

    print("  + Outro video file created.")
    print("." * 25)

# Now stitch together the MP4 segments
print("=" * 25)
print("o Stitching segments together...")

merge_pat = re.compile(f"{safe.sub('_',conf['lessons'][str(args.lesson)]['track'].strip())}" + r'_(\d{1,2})_')
merge_map = {int(merge_pat.search(str(x))[1]):x for x in [y for y in args.merge.glob("*.mp4") if merge_pat.search(str(y)) is not None]}

if DEBUG:
    print(", ".join([f"{k} -> {merge_map[k]}" for k in sorted(merge_map.keys())]))

with open(Path(args.merge / 'segments.txt'), 'w') as f:
    for s in sorted(merge_map.keys()):
        f.write(f"file '{(str(merge_map[s].name))}'\n")
    f.write("")

fn_tmp = args.merge / f"{safe.sub('_', conf['lessons'][str(args.lesson)]['track'].strip())}.mp4"
fn_out = fn_final

cmd = ''
cmd += f"ffmpeg -hide_banner -y -f concat -safe 1 "
cmd += f"-i {str(args.merge / 'segments.txt')} "
cmd += f"-r {conf["project"].get("fps", 30)} -c:v {conf["project"]["vcodec"]} -crf {conf["project"]["crf"]} {conf["project"].get("vopts", "")} -c:a {conf["project"]["acodec"]} \\\n" #  -fps_mode vfr (variable frame rate)
cmd += f'-af "aresample=async=1:first_pts=0" -pix_fmt yuv420p \\\n'
cmd += f"{fn_tmp}"

if DEBUG: 
    print(f"  o {cmd}")
call(cmd, shell=True)

print("  + Unified (temporary) video file created.")

print("=" * 25)
print("o Removing leading black frames...")

cmd  = ''
cmd += f"ffmpeg -hide_banner -y -ss 00:00:00.075 "
cmd += f"-i {re.escape(str(fn_tmp))} -c:v copy -c:a copy "
if 'hvc1' in conf["project"].get("vopts", ""):
    cmd += "-tag:v hvc1 "
cmd += f"{re.escape(str(fn_out))}"
if DEBUG: 
    print(f"  i {cmd}")
call(cmd, shell=True)

print("  o Removing temp file")
fn_tmp.unlink(missing_ok=True)

print("  + Done.")

print("=" * 35)

print(f"+++ {conf['lessons'][str(args.lesson)]['track'].strip()} talk generated +++")

exit()
