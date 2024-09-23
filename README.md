# Rendering Pre-Recorded Lectures

## Installation

For this you will need to have installed node, decktape, and ffmpeg.

### Homebrew

On a Mac, at least, it's probably best to have [Homebrew](https://docs.brew.sh/Installation) installed (anything else you're on your own) and then run:

```bash
brew update
brew upgrade
brew cleanup
```

Homebrew is generally useful, so you may already have it installed.

### Node and Decktape

To create the stills we need to export the Quarto presentations to PNG files using [decktape](https://github.com/astefanutti/decktape), which is a node (hisssss!) application. To install:

```bash
brew install npm
npm install -g decktape
which decktape
```

### ffmpeg

`ffmpeg` is the tool we'll be using to assemble the audio and video tracks into a working MP4 recording. You *should* find that installing `ffmpeg` also installs `ffprobe`, which we need to work out the length of some audio tracks.

```bash
brew install freetype
brew install ffmpeg
```

[Programming Historian](https://programminghistorian.org/) has a useful [Introduction to ffmpeg](https://programminghistorian.org/en/lessons/introduction-to-ffmpeg#basic-structure-and-syntax-of-ffmpeg-commands). It doesn't cover this use case but it is nonetheless a nice orientation to the basic structure of ffmpeg commands. See also: [Demystifying ffmpeg](https://github.com/privatezero/NDSR/blob/master/Demystifying_FFmpeg_Slides.pdf), the [ffmpeg Presentation](https://docs.google.com/presentation/d/1NuusF948E6-gNTN04Lj0YHcVV9-30PTvkh_7mqyPPv4/present?ueb=true&slide=id.g2974defaca_0_231) and [ffmpeg Wiki](https://trac.ffmpeg.org/wiki/WikiStart) alongside [the documentation](https://www.ffmpeg.org/ffmpeg.html). 

## Generating the Assets

### All in One

The `process.py` script integrates all of the separate steps listed below but, as a result, has a lot of flags to grapple with. These can be viewed by simply running:

```bash
python flip/process.py --help
```

But basic usage is:

```bash
process.py [-h] [-t TALK] [-n NAME] [-s SERVER] [-d] [-a] [-f] [-q]
```

For example:

```bash
python flip/process.py -t 10.1-Visualising_Data -n "Visualising Data" -s 'http://localhost:4200/lectures/' -d -a -f
```

The parameters are:

```
  -h, --help            show this help message and exit
  -t TALK, --talk TALK  The folder name with the talk.
  -n NAME, --name NAME  The name of the talk, for multi-line separate with \n
  -s SERVER, --server SERVER
                        Where to access the Reveal.js slides
  -d, --exportdeck      Skip export of the slide deck to PNG (useful when you are mucking about with the audio and output).
  -a, --exportaudio     Skip export of the audio files to M4A (useful when you are mucking about with the audio and output).
  -f, --force           Force generation of video even if number of slides and audio segments doesn't match.
  -q, --quick           Quick generation (assumes MP4 segments haven't changed).
```

### Exporting Stills

This will extract a Reveal.js deck to a series of PNG files in the `_export` directory. Again, help can be accessed using:

```bash
python flip/extract_deck.py --help
```

But basic usage is:

```bash
extract_deck.py [-h] [-t TALK] [-s SERVER]
```

For example:

```bash
python flip/extract.py -t 3.4-Functions -s https://jreades.github.io/fsds/lectures
```

There are only two parameters:

```
  -h, --help            show this help message and exit
  -t TALK, --talk TALK  The folder name with the talk.
  -s SERVER, --server SERVER
                        Where to access the Reveal.js slides
```

The talks will be exported to `_export/{talk}` with one PNG file per slide in the Reveal.js presentation. Builds are only supported insofar as they are supported by `decktape`.

### Exporting Audio

Audio can be captured however you like, but you will then be segmenting and exporting the source recording into a single M4A file so that `export_audio.py` can then pull out the tracks. [OcenAudio](https://www.ocenaudio.com/en) seems to be able to do this quite effectively and quickly if you want to stick to FOSS.

#### Setting up Segments in a Markdown Table

The best way to allow for the recording to be flexible exported as a set of numbered and named files is to set up your own labels in a markdown table:

The format of the table is reasonably important, including the header that appears immediately before the start of the table. The 'title' for the table should match the `-t` switch passed in to `process.py` (or to `merge.py` if you're running the constituent scripts separately).

**Note**: if you want to skip a slide, simply skip over that number in the `sequence` column of the markdown table. `merge.py` will use the integer id of the PNGs and exported M4A segments to 'zip' up the parts into a movie.

Some tips:

- Individual audio segments can be set to start and end at any valid timestamp within the M4A file.
- By extension, you could repeat the same piece of audio multiple times if you wanted.
- However, from experience I *can* say that setting the stop time of one segment and the start time of the following segment to the *exact* same time is likely to lead to juddering audio effects. It's best to offset the start time by a millisecond.

#### Noise Reduction

If your recording levels are low and/or you discover noise in the recording after the fact then you can remove background noise in Ocen (or Audacity if you still use that) in the following manner:

1. Select (using the 'I'-like selection tool) a region of the recording that has no speech in it.
2. Select `Effect` > `Noise Remove and Repair` > `Noise Reduction...`.
3. In the popup, click the `Get Noise Profile` and click 'OK' (**Important**: nothing has happened yet!)
4. Now select the *entire* recording (`Cmd` + `A`) and open the `Noise Reduction` filter again.
5. Choose the settings (e.g. Noise reduction of 15db, Sensitivity of 8, Frequency smooth (bands) of 6) (**Note**: these settings are a *guess*)
6. Click `Preview` to hear the effect and adjust the settings again if necessary.
7. Once you're happy with the noise reduction amount click 'OK'

## Generating the Movie

So assuming that you have your exported audio in `_audio/{talk}` and your exported stills in `_export/{talk}` then you are ready to `merge` these sources into a finished video. Basic usage would be:

```bash
merge.py [-h] [-n NAME] [-t TALK] [-o OUTPUT] [-f] [-q]
```

For example:

```bash
python flip/merge.py -n "Functions" -t 3.4-Functions -f
```

Here are the options:

```
  -h, --help            show this help message and exit
  -n NAME, --name NAME  The name of the talk, for multi-line separate with \n
  -t TALK, --talk TALK  The folder name with the talk.
  -o OUTPUT, --output OUTPUT
                        Name of the ouptut MP4 file.
  -f, --force           Force generation of video even if number of slides and audio segments doesn't match.
  -q, --quick           Quick generation (assumes MP4 segments haven't changed).
```

This script does five things:

1. Generates an intro video segment by calling `intro.py` using the `-n` (name) to create the title sequence (which involves some copyright info and a fade-in for the title).
2. Generates an 'outro' video segment by calling `outro.py` which is expected to be the same for all talks (since we want consistency across the pre-recorded videos).
3. Generates video segments for each slide using `ffmpeg` to merge the PNG file with the matching M4A file. Currently you can only one, and only one, match between a PNG and a M4A file.
4. Merges these video segments together into a single long-form video.
5. Trims out the first 0.075 seconds of the merged video since, for some reason, this is always a black screen.

The results are exported to `_merged/{talk}.mp4` and this is the final output that can be uploaded to Streams, YouTube, whatever.

## To Dos

- [ ] Move many of the assumptions about output directories and sources to a separate config.py file so that these can be easily changed and also don't have to be configured individually in each script.
- [X] Allow the user to include an existing MP4 file (e.g. 'fireside chat' type thing) that is inserted into the sequence of segments such that you can fade out of the lecture slides to a video of the lecturer talking and then fade back into the next slide in the sequence.
- [ ] Expand the OO-aspect used by `intro.py` and `outro.py` so as to make it easier to set upmore complex effects and on-the-fly rendering of elements.
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
