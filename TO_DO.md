## To Dos

- [x] Move many of the assumptions about output directories and sources to a separate config.py file so that these can be easily changed and also don't have to be configured individually in each script.
- [x] Do the same for the intro and outro scripts.
- [ ] Add watermarking feature (possibly as an overlay/filter effect).
- [x] Allow the user to include an existing MP4 file (e.g. 'fireside chat' type thing) that is inserted into the sequence of segments such that you can fade out of the lecture slides to a video of the lecturer talking and then fade back into the next slide in the sequence.
- [ ] Expand the OO-aspect used by `intro.py` and `outro.py` so as to make it easier to set up more complex effects and on-the-fly rendering of elements.
- [ ] Allow a 'talking head' type thing to be overlayed across all slides (e.g. this recording of me talking in green-screened in to the lower-right corner along with the PNG background).
- [ ] Allow for slide transitions to be simulated in ffmpeg using filters.

