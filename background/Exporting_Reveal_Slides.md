# Exporting PNGs from Reveal.js

This file tracks how I learned to export PNG stills from Quarto Reveal.js presentations for use in the `merge.py` script. 

Use the [README](README.md) to learn how to generate the movies.

## Exporting from Quarto

To create the outputs we need to export the Quarto presentations to PNG files. This can be done using [decktape](https://github.com/astefanutti/decktape), which is a node (hisssss!) application. To install:

```bash
npm install -g decktape
decktape
```

Then to extract:

```bash
export LECTURE='3.2-LOLs'
mkdir $LECTURE
decktape --screenshots --screenshots-directory $LECTURE \
  --screenshots-size 1280x720 --screenshots-format png --headless true -p 500  \
  http://jreades.github.io/lectures/$LECTURE.html $LECTURE.pdf
#  http://localhost:4200/lectures/$LECTURE.html $LECTURE.pdf
```

