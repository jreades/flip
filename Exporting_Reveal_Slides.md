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

