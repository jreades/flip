######################
# Process a full lecture from start to finish. 
######################
import argparse
from subprocess import call
import os, re

ppath = os.path.join(os.path.expanduser("~"),"anaconda3","envs","sds","bin")

parser = argparse.ArgumentParser(
                    prog='process.py',
                    description='Integrates the various steps in extracting and converting a lecture to a video (audio has to be generated separately for now).',
                    epilog='For example: `python flip/process.py -t 3.4-Functions -n "It\'s Functional"`')
parser.add_argument('-t', '--talk', type=str, help="The folder name with the talk.")
parser.add_argument('-n', '--name', type=str, help="The name of the talk, for multi-line separate with \\n")
parser.add_argument('-s', '--server', type=str, help="Where to access the Reveal.js slides", default='http://localhost:4200/lectures')
parser.add_argument('-d', '--exportdeck', help="Skip export of the slide deck to PNG (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-a', '--exportaudio', help="Skip export of the audio files to M4A (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-f', '--force', help="Force generation of video even if number of slides and audio segments doesn't match.", action='store_true')
parser.add_argument('-q', '--quick', help="Quick generation (assumes MP4 segments haven't changed).", action='store_true')

args = parser.parse_args()

# Extract Slides
if args.exportdeck:
    print("=" * 40)
    print("=" * 14 + " Extracting deck " + "=" * 14)
    print("=" * 40)
    cmd = ''
    cmd += f'{ppath}/python {os.path.join("flip","extract_deck.py")} \\\n'
    cmd += f'  -t {args.talk} \\\n'
    cmd += f'  -s {args.server}'

    #print(f"  -i: {cmd}")
    call(cmd, shell=True)
else: 
    print(f"- Skipping extraction of {args.talk}.")
    print(f"  Add `-d` to force export of slide deck to PNG.")

# Extract Audio
if args.exportaudio:
    print("=" * 40)
    print("=" * 14 + " Extracting audio " + "=" * 14)
    print("=" * 40)
    cmd = ''
    cmd += f'{ppath}/python {os.path.join("ffmpeg","extract_audio.py")} \\\n'
    cmd += f'  -t {args.talk}'

    #print(f"  -i: {cmd}")
    call(cmd, shell=True)
else: 
    print(f"- Skipping extraction of {args.talk}.")
    print(f"  Add `-a` to force export of narration to segmented M4A files.")

# Merge
print("=" * 40)
print("=" * 15 + " Merging. " + "=" * 15)
print("=" * 40)
cmd = ''
cmd += f'{ppath}/python {os.path.join("ffmpeg","merge.py")} \\\n'
cmd += f'  -t {args.talk} \\\n'
cmd += f'  -n "{args.name}" {"-f" if args.force else ""} {"-q" if args.quick else ""}'

print(f"  -i: {cmd}")
call(cmd, shell=True)

print("+ Done.")
exit()
