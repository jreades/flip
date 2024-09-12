######################
# Take a lecture and extract it to a set of PNG files. 
######################
import argparse
from subprocess import call
import os, re, glob

scrn_size   = "1280x720"
scrn_format = "png"
pause       = 500 # Applied to both --pause and --load-pause

ppath = os.path.join(os.path.expanduser("~"),"anaconda3","envs","sds","bin")

parser = argparse.ArgumentParser(
                    prog='extract_deck.py',
                    description='Generates a set of PNGs from a Reveal.js lecture. Requires node.js and decktape to be installed.',
                    epilog='For example: `python ffmpeg/extract.py -t 3.4-Functions -s https://jreades.github.io/fsds/lectures`')
parser.add_argument('-t', '--talk', type=str, help="The folder name with the talk.")
parser.add_argument('-s', '--server', type=str, help="Where to access the Reveal.js slides", default='http://localhost:4200/lectures')

args = parser.parse_args()

# Strip off the HTML suffix (or any other suffix)
if re.search(r'\.\w{2,4}$', args.talk):
    args.talk = re.sub(r'\.\w{2,4}$','',args.talk)

args.output = os.path.join('_export',args.talk)

# Create the folder for storing the files
if not os.path.exists(args.output):
    os.makedirs(args.output, exist_ok=True)
    print(f"+ Created {args.output}")
else:
    print(f"+ Found {args.output}")
    files = glob.glob(os.path.join(args.output, "*.png"))
    if len(files) > 0:
        print(f"  - Emptying directory of already-rendered output")
        for f in files:
            os.remove(f)

print(f"+ Preparing to extract screenshots.")

# And extract the slides as PNGs to the folder
cmd = ''
cmd += f'decktape \\\n'
cmd += f'  --screenshots --screenshots-directory {args.output} \\\n'
cmd += f'  --size {scrn_size} --screenshots-size {scrn_size} --screenshots-format {scrn_format} \\\n'
cmd += f'  --pause {pause} --load-pause {pause} --headless true \\\n'
cmd += f'  {os.path.join(args.server, args.talk+'.html')} {args.talk + '.pdf'}'

#print(f"  -i: {cmd}")
call(cmd, shell=True)

print(f"+++ PNGs for {args.talk} generated +++")

exit()
