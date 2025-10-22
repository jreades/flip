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
   epilog='For example: `python flip.py -p ../ffmpeg/project.toml -i -a -l 11`')
parser.add_argument('-p', '--project', type=str, help="Path to the project.toml configuration file.", default='project.toml')
parser.add_argument('-d', '--defaults', type=str, help="Path to the defaults.toml configuration file.", default='defaults.toml')
parser.add_argument('-l', '--lesson', type=str, help="The number (or range) of the lesson in the project.toml configuration file. Examples include: `1`, `3-5`, `3,7-8,9`", default='-1')
parser.add_argument('-i', '--noimage', help="Skip export of the slide deck to PNG (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-a', '--noaudio', help="Skip export of the audio files to M4A (useful when you are mucking about with the audio and output).", action='store_true')
parser.add_argument('-m', '--nomerge', help="Skip merge of audio and video (assumes MP4 segments haven't changed).", action='store_true')
parser.add_argument('-f', '--force', help="Force generation of new images, audio, and video.", action='store_true')

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

# Unpack the lesson option
lesson_list = []
if args.lesson == '-1':
    lesson_list = list(range(1, len(proj['lessons'])+1))
else:   
    for part in args.lesson.split(','):
        if '-' in part:
            start, end = part.split('-')
            lesson_list.extend(list(range(int(start), int(end)+1)))
        else:
            lesson_list.append(int(part))
    lesson_list = sorted(list(set(lesson_list)))
print(lesson_list)

# Insert loop here -- need to read in 
# the list of available lessons and then
# iterate over them
for l_num in lesson_list:

    if l_num < 1 or l_num > len(proj['lessons']):
        print(f"! Lesson {l_num} is out of range. Skipping.")
        continue

    lesson = proj['lessons'][str(l_num)]
    
    print("=" * 40)
    print(f"= Processing lesson {l_num}: {lesson['title']}")
    print("=" * 40)
    
    # Extract Slides
    if not args.noimage and not args.force:
        print("." * 40)
        print("." * 11 + " Extracting deck " + "." * 12)
        print("." * 40)
        cmd = ''
        cmd += f'{ppath / "python"} {"deck.py"} \\\n'
        cmd += f'  -p {args.project} \\\n'
        cmd += f'  -l {l_num}'

        print(f"  Add `-i` to skip export of slide deck to PNG.")
        if DEBUG:
            print(f"- Extracting slides with command:")
            print(f"{cmd}")
        call(cmd, shell=True)
    else: 
        print(f"- Skipping extraction of lesson {l_num} since `-i` set.")

    # Extract Audio
    if not args.noaudio and not args.force:
        print("." * 40)
        print("." * 11 + " Extracting audio " + "." * 12)
        print("." * 40)
        cmd = ''
        cmd += f'{ppath / "python"} {"audio.py"} \\\n'
        cmd += f'  -p {args.project} \\\n'
        cmd += f'  -l {l_num}'

        print(f"  Add `-a` to skip export of narration to segmented M4A files.")
        if DEBUG:
            print(f"- Extracting audio with command:")
            print(f"{cmd}")
        call(cmd, shell=True)
    else: 
        print(f"- Skipping extraction of lesson {l_num} since `-a` set.")

    # Merge Audio and Video
    if not args.nomerge and not args.force:
        print("." * 40)
        print("." * 15 + " Merging. " + "." * 15)
        print("." * 40)
        cmd = ''
        cmd += f'{ppath / "python"} {"merge.py"} \\\n'
        cmd += f'  -p {args.project} \\\n'
        cmd += f'  -l {l_num} \\\n'
        cmd += f'  -l {l_num} \\\n'

        print(f"  Add `-m` to skip merge of audio and video files.")
        if DEBUG:
            print(f"- Merging segments with command:")
            print(f"{cmd}")
        call(cmd, shell=True)
    else:
        print(f"- Skipping extraction of lesson {l_num} since `-m` set.")

    print(f"  + Done processing lesson {l_num}")
    print(f"=" * 40)
    # End loop here

print("+ Done flipping.")
exit()
