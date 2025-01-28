## To Dos

- [ ] Move many of the assumptions about output directories and sources to a separate config.py file so that these can be easily changed and also don't have to be configured individually in each script.
- [ ] Do the same for the intro and outro scripts.
- [ ] Add watermarking feature (possibly as an overlay/filter effect).
- [x] Allow the user to include an existing MP4 file (e.g. 'fireside chat' type thing) that is inserted into the sequence of segments such that you can fade out of the lecture slides to a video of the lecturer talking and then fade back into the next slide in the sequence.
- [ ] Expand the OO-aspect used by `intro.py` and `outro.py` so as to make it easier to set up more complex effects and on-the-fly rendering of elements.
- [ ] Allow a 'talking head' type thing to be overlayed across all slides (e.g. this recording of me talking in green-screened in to the lower-right corner along with the PNG background).
- [ ] Allow for slide transitions to be simulated in ffmpeg using filters.

### Adding Filters

I think I'll need to this later: [see docs](https://trac.ffmpeg.org/wiki/FilteringGuide).

Ooooh, and a [cheatsheet](https://gist.github.com/martinruenz/537b6b2d3b1f818d500099dde0a38c5f)

Consider also adding filters on audio and video channeles:

- `atadenoise` denoising [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-atadenoise)
- `blend` for blending one layer into another (watermarking?) [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-blend-1)
- `chromakey` for green-screening [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-blend-1) (also has useful thing for overlaying on a static black background)
- `colorize` is  [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-colorize)
- `colortemperature` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-colortemperature)
- `coreimage` to make use of Apple's CoreImage API [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-coreimage-1)
- `crop` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-crop)
- `dblur` for directional blur could be fun on intro/outro [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-dblur)
- `decimate` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-decimate-1)
- `displace` (probably a bad idea but...) is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-displace)
- `drawtext` (for writing in date/year) is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-drawtext-1) (requires libfreetype)
- `fade` (to fade-in/out the input video) is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-fade)
- `frames per second` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-fps-1) not sure how it differs from [framerate](https://www.ffmpeg.org/ffmpeg-filters.html#toc-framerate)
- `Gaussian blur` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-gblur)
- `Hue/saturation/intensity` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-huesaturation)
- `Colour adjustment` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-Color-adjustment)
- `Loop` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-loop)
- `Monochrome` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-monochrome) and could be used with colourisation on live video, for instance
- `Normalise` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-normalize) for mapping input histogram on to output range
- `Overlay` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-overlay-1) and will be useful for adding an intro/outro
- `Perspective correction` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-perspective)
- `Scale` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-scale-1) to rescale inputs.
- `Trim` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-trim)
- `Variable blur` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-varblur) and could be useful for background blurring behind a talking head.
- `Vibrance` to increase/change saturation is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-vibrance)
- `Vstack` as faster alternative to Overlay and Pad is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-vstack)
- `Xfade` to perform cross-fading between input streams is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-xfade)
- `Zoom` and `pan` is [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-zoompan)

Currently available video sources are [here](https://www.ffmpeg.org/ffmpeg-filters.html#toc-Video-Sources)

<a rel="me" href="https://mapstodon.space/@jreades">Mastodon</a>