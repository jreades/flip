######################
# Generate an intro animation with the appropriate
# title for the lecture.
######################
import argparse
from subprocess import call
from ffmpeg import *
import os

this_year = 2024
logo_url = os.path.join('img','CASA_Logo_Light_with_text.png')

parser = argparse.ArgumentParser(
                    prog='Outro Slide Generator',
                    description='Generates a tail slide for a lecture with the CASA logo and copyright.',
                    epilog='Text at the bottom of help')
parser.add_argument('-l', '--length', type=float, help="The length of the talk.", default=3)
parser.add_argument('-o', '--output', type=str, help="Name of the ouptut MP4 file.", default=os.path.join('_mp4','outro.mp4'))

args = parser.parse_args()

os.makedirs(os.path.dirname(args.output), exist_ok=True)

fol  = 1.2 # fade out length

if args.length != None and args.length > 0:
    stfo = args.length - (fol + 0.1) # lecture fade out
    running_len = args.length
else:
    stfo = 0.175
    running_len  = stfo + fol + 0.1 # lecture fade out

# Set up scene
i = outro(running_len)

print(f"""Video details:
    Fully visible until {stfo:0.2f}
    Start fade out at {stfo:0.2f} and fade out for {fol:0.2f}.""")
print(f"Running length {running_len:0.2f}.\n")

# Logo fading
fo  = img_fade(False, fol, stfo)
tfo = txt_fade(False, fol, stfo)

logo = overlay('main_w/2-overlay_w/2', 'main_h/2-overlay_h/2.4', True)

yr = text(f"{this_year}/{this_year+1}", '(w-text_w)/2', '(h/2-text_h*5)', 24)
copy = text(f"CC-BY-NC-SA {this_year} Jon Reades", '(w-text_w)/2', '(h/2+80)', 12) # *6 on large monitors????
yr.color = "white"
copy.color = "white"
yr.add_fader(tfo)
copy.add_fader(tfo)

params = {
    'bg': str(i),
    'logo': f'[0:v] {fo}'
}

# Note use of the nullsrc audio filter (via lavfi) -- 
# we need this to ensure that the outro segment always
# matches the other segments in terms of configuration
# on both audio and video channels.
cmd = ''
cmd += f'ffmpeg -hide_banner -y -loop 1 -i {logo_url} -f lavfi -i anullsrc=r=44100:cl=stereo:d={args.length}:n=64000 -t {i.length} -filter_complex "\\\n'
for p,v in params.items():
    cmd += f'{v} [{p}]; \\\n'
cmd += f'[bg][logo] {logo}, \\\n'
cmd += str(yr) + f" \\\n"
cmd += str(copy) + f" \\\n"
cmd += f'" -r 30 -c:v libx264 -c:a aac \\\n'
cmd += f'-shortest -pix_fmt yuv420p -tune stillimage {args.output}\n'

#print(f"  -i {cmd}")
call(cmd, shell=True)

#ffmpeg -i Test.mp4 -itsoffset 00:00:02 -i fanfare-1.m4a -map 0:0 -map 1:0 -c:v copy -async 1 out.mp4

exit()
