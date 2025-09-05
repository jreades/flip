######################
# Params for the rendered introductory slide.
######################
from pathlib import Path
from ffmpeg import textblock, iposition, tposition

fontface = "Hanken Grotesk"
fontcolor = "4f3d57"  # dark purple
fontcolor_light = "ffffff" # white

bg_url    = Path('img/title-slide.png')
logo_url  = Path('img/transparent_lg.png')
ccby_url  = Path('img/by-nc-sa.png')

# Module name timings
stfi = 0.15             # start fade in
fil  = 1.2              # fade in length
stfo = stfi + fil + 1.0 # start fade out
fol  = 0.4              # fade out length

# Course name timings
lfi  = stfo + (fol - fol/2) # lecture fade in -- crossfade

title   = textblock("Foundations of\nSpatial Data Science", halign="left", valign="top", size=40, style="Bold")
lecture = textblock("Lecture Title", halign="left", valign="top", size=75, style="Bold")
author  = textblock("Jon Reades", halign="left", size=30)
year    = textblock("2025", halign="center", size=30)

# x, y
title.position = tposition(0.10, 0.13)
logo_position  = iposition(0.04, 0.1)
ccby_position  = iposition(0.9, 0.915)

lecture.position = tposition(0.1, 0.25)
author.position  = tposition(0.1, 0.427)
year.position    = tposition(0.1, 0.502)

leading = 1.05  # line spacing multiplier