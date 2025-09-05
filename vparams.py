######################
# Params for the rendered introductory slide.
######################
from pathlib import Path
from ffmpeg import textblock

fontface = "Hanken Grotesk"
fontcolor = "4f3d57"  # dark purple
fontcolor_light = "ffffff" # white

bg_url    = Path('img/title-slide.png')
logo_url  = Path('img/CASA_logo.png')
ccby_url  = Path('img/by-nc-sa.png')

stfi = 0.15             # start fade in
fil  = 1.2              # fade in length
stfo = stfi + fil + 1.0 # start fade out
fol  = 0.4              # fade out length

lfi  = stfo + (fol - fol/2) # lecture fade in -- crossfade

author  = textblock("Jon Reades", halign="left", size=18)
title   = textblock("Foundations of\nSpatial Data Science", halign="center", size=48, style="Bold")
lecture = textblock("Lecture Title", halign="left", size=48, style="Bold")
year    = textblock("2025", halign="center", size=24)

leading = 1.05  # line spacing multiplier