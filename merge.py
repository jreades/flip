######################
# Take a set of audio tracks (.m4a) and still image files
# (.png) and merge them into a talk. We need to do this by
# merging each audio/image file into a MP4 file and then  
# combining the set of generated MP4s into a single lecture. 
######################
import argparse
from subprocess import call, check_output
import os, re, glob
import math

ppath = os.path.join(os.path.expanduser("~"),"anaconda3","envs","sds","bin")
os.makedirs('_output', exist_ok=True)

parser = argparse.ArgumentParser(
                    prog='merge.py',
                    description='Generates a pre-recorded lecture from stills and audio files. You need to have generated these following a consistent naming/output format.',
                    epilog='For example: `python ffmpeg/merge.py -n "Functions" -t 3.4-Functions`')
parser.add_argument('-n', '--name', type=str, help="The name of the talk, for multi-line separate with \\n")
parser.add_argument('-t', '--talk', type=str, help="The folder name with the talk.")
parser.add_argument('-o', '--output', type=str, help="Name of the ouptut MP4 file.")
parser.add_argument('-f', '--force', help="Force generation of video even if number of slides and audio segments doesn't match.", action='store_true')
parser.add_argument('-q', '--quick', help="Quick generation (assumes MP4 segments haven't changed).", action='store_true')

args = parser.parse_args()

args.merge = os.path.join('_merge',args.talk)
if not os.path.exists(args.merge):
    os.makedirs(args.merge, exist_ok=True)
    print(f"+ Created {args.merge}")
else:
    print(f"+ Found {args.merge}")
    if not args.quick:
        files = glob.glob(os.path.join(args.merge, "*.mp4"))
        if len(files) > 0:
            print(f"  - Emptying directory of already-rendered output")
            for f in files:
                os.remove(f)

if args.output is None or args.output=='':
    args.output = os.path.join('_output',args.talk)

args.audio = os.path.join('_audio',args.talk)
if not os.path.exists(args.audio):
    print(f"- Couldn't find audio folder: '{args.audio}'")
    exit()
else:
    print(f"+ Found audio folder {args.audio}")

args.stills = os.path.join('_export',args.talk)
if not os.path.exists(args.stills):
    print(f"- Couldn't find stills folder: '{args.stills}'")
    exit()
else:
    print(f"+ Found stills folder {args.stills}")

# Read in the audio and stills filenames
audio_files = [x for x in sorted(os.listdir(args.audio)) if x.endswith('.m4a')]
still_files = [x for x in sorted(os.listdir(args.stills)) if x.endswith('.png')]
#print(audio_files)
#print(still_files)

######################
# Organise the stills

# Find the stills indexes
still_pat = re.compile(r'_(\d{1,2})_\d+x\d+\.')
still_map = {int(still_pat.search(x)[1]):x for x in still_files}

# Remove first and last slides
first_slide = still_map.pop(1)
#still_map.pop(max(still_map.keys()))
#print(still_map)

######################
# Organise the audio
audio_pat = re.compile(r'(?<!m)(\d{1,2})(?!a)')
audio_map = {int(audio_pat.match(x)[1]):x for x in audio_files}
#print(audio_map)

# There should be one fewer stills files because
# we are going to cut the intro slide from the
# stills (and replace that with an auto-generated)
# one, and cut the 'Resources' slide from the end.
if len(still_map.keys())+1 != len(audio_map.keys()):
    print("!" * 20)
    print(f"Unequal number of stills ({len(still_map.keys())+1}) and audio ({len(audio_map.keys())}) files found.")
    print("!" * 20)
    if not args.force: exit()

if not args.quick:
    ###############
    # For the first slide...
    print("=" * 25)

    print("o Generating first slide...")

    # Find out how long the intro audio track is
    probe =  f'ffprobe -hide_banner -sexagesimal -show_entries format=duration '
    probe += f'{re.escape(os.path.join(args.audio,audio_map[1]))}'

    # Capture the duration
    output = check_output(probe, shell=True).decode("utf-8").split("\n")[1]
    print(output)
    duration = re.match(r'duration=(\d{1,}):(\d{2}):(\d{2})\.(\d{3})\d+',output)

    hrs = int(duration[1])
    mns = int(duration[2])
    sec = int(duration[3])
    ms  = math.ceil(float(duration[4])/10)

    # Translate single- and double-quotes to 
    # their 'fancy' equivalents
    transl_table = dict( [ (ord(x), ord(y)) for x,y in zip(u"'''\"\"--", u"‘’´“”–-") ] )

    cmd = ''
    cmd += f'{ppath}/python {os.path.join("ffmpeg","intro.py")} \\\n'
    cmd += f'  -l {hrs * 60 * 60 + mns * 60 + sec + ms/100} \\\n'
    cmd += f'  -t "{args.name.translate( transl_table )}" \\\n'
    cmd += f'  -o {re.escape(os.path.join(args.stills,first_slide.replace(".png",".mp4")))}'

    print(f"  o {cmd}")
    call(cmd, shell=True)

    cmd = ''
    cmd += f'ffmpeg -hide_banner -y \\\n'
    cmd += f'-i {re.escape(os.path.join(args.stills,first_slide.replace(".png",".mp4")))} \\\n'
    cmd += f'-i {re.escape(os.path.join(args.audio,audio_map[1]))} \\\n'
    #cmd += f'-map 0:0 -map 1:0 -c:v copy \\\n'
    cmd += f'-c:v libx264 -tune stillimage -pix_fmt yuv420p -c:a aac \\\n'
    cmd += f'{os.path.join(args.merge,first_slide.replace(".png",".mp4"))}'

    print(f"  o {cmd}")
    call(cmd, shell=True)
    
    print("  + First slide generated.")
    print("=" * 25)

# For the remaining stills
if not args.quick:
    for idx in sorted(still_map.keys()):
        print(f"o Generating slide {idx}...")

        try:
            print(f"  o Matching {still_map[idx]} -> {audio_map[idx]}")

            # Generate the introductory slide
            # ffmpeg -r 30 \
            #   -loop 1 
            #   -i 2.3-Python_the_Basics_1_1280x720.png \
            #   -i 2.3-1.m4a \
            # 	-c:v libx264 -tune stillimage -shortest -pix_fmt yuv420p \
            # 	-b:a 64k \
            # 	out1.mp4
            if os.path.exists(os.path.join(args.stills,still_map[idx])) and \
                os.path.exists(os.path.join(args.audio,audio_map[idx])):
                cmd = ''
                cmd += f'ffmpeg -hide_banner -y -r 30 -loop 1 \\\n'
                cmd += f'-i {re.escape(os.path.join(args.stills,still_map[idx]))} \\\n'
                cmd += f'-i {re.escape(os.path.join(args.audio,audio_map[idx]))} \\\n'
                cmd += f'-c:v libx264 -tune stillimage -shortest -pix_fmt yuv420p \\\n'
                cmd += f'-b:a 64k \\\n'
                cmd += f'{os.path.join(args.merge,still_map[idx].replace(".png",".mp4"))}'
                print(f"  o {cmd}")
                call(cmd, shell=True)
                
                print(f"  + Slide {idx} generated.")
            else:
                print(f"  - Unable to find both audio and still files for Slide [idx]")
        except KeyError:
            print(f"  - Unable to match {idx}:{still_map[idx]} in audio_map")
            continue

    print("+ All segments generated.")
    print("=" * 25)

if not args.quick:
    print("o Generating outro slide...")

    cmd = ''
    cmd += f'{ppath}/python {os.path.join("ffmpeg","outro.py")} \\\n'
    cmd += f'  -o {re.escape(os.path.join(args.merge,"outro.mp4"))}'

    #print(f"  i {cmd}")
    call(cmd, shell=True)

    print("  + Outro video file created.")
    print("=" * 25)

print("o Stitching segments together...")

sequence = [still_map[x] for x in sorted(still_map.keys())]
sequence.insert(0,first_slide.replace('.png','.mp4'))
sequence.append('outro.mp4')
# print(sequence)

with open(os.path.join(args.merge,'segments.txt'), 'w') as f:
    for s in sequence:
        if os.path.exists(os.path.join(args.merge, s.replace('.png','.mp4'))):
            print(f"Sequence: {s}")
            f.write(f"file '{s.replace('.png','.mp4')}'\n")
    f.write("")

cmd  = f"ffmpeg -hide_banner -y -f concat -safe 1 "
cmd += f"-i {os.path.join(args.merge,'segments.txt')} "
#cmd += f'-c:v libx264 -tune stillimage -pix_fmt yuv420p \\\n'
#cmd += f'-b:a 64k -shortest '
#cmd += f"-c:v copy -c:a copy {args.output + '-tmp.mp4'}"
cmd += f"-c:v libx264 -af aresample=async=1000 -pix_fmt yuv420p \\\n"
cmd += f"{args.output + '-tmp.mp4'}"
print(f"  o {cmd}")
call(cmd, shell=True)

print("  + Temp video file created.")

print("=" * 25)

print("o Removing leading black frames...")

# Strip out the extraneous black frames at the start
#ffmpeg -y -ss 00:00:00.075 -i _output/2.5-Lists.mp4 -c:v copy -c:a copy test.mp4

cmd = f"ffmpeg -hide_banner -y -ss 00:00:00.075 -i {args.output + '-tmp.mp4'} -c:v copy -c:a copy {args.output + '.mp4'}"
print(f"  i {cmd}")
call(cmd, shell=True)

print("  o Removing temp file")
os.remove(args.output + '-tmp.mp4')

print("  + Done.")

print("=" * 25)

print(f"+++ Talk {args.talk} generated +++")

exit()
