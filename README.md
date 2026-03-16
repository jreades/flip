# About Flip

Flip is a small utility — making use of open source software — designed to streamline the process of 'flipping' lectures built using open source presentation frameworks such as Reveal.js. At its heart, flip is performing the following tasks:

1. Converting each slide of an HTML/JavaScript-based presentation to a static PNG.
2. Converting these PNGs into a video by synchronising the PNGs with a pre-recording audio track.
3. Optionally generating intro- and outro-elements to make it easy to add a title slide and copyright notice.

Provided you have already recorded the audio, these three tasks can be performed in one go, and because the intro and outro are dynamically generated, this can be performed much more quickly and easily than using a non-Command Line (CLI) tool such as Camtasia. Obviously, the feature set is also more limited than Camtasia, though there is scope to include video from other sources in the rendering pipeline.

## Requirements

For flip, you will need to have installed the following open source tools: `node`, `decktape` (a node application), and `ffmpeg` and `freetype`. More *general* information about each of tehse can be found on the respective sites:

1. https://nodejs.org/en
2. https://www.npmjs.com/package/decktape / https://github.com/astefanutti/decktape
3. https://www.ffmpeg.org/
4. https://freetype.org/

### Homebrew

On a Mac it's easiest to make use of [Homebrew](https://docs.brew.sh/Installation) to manage the majority of the above:

```bash
brew update
brew upgrade
brew cleanup
```

#### Node and Decktape

To create the stills we need to export the Quarto presentations to PNG files using [decktape](https://github.com/astefanutti/decktape), which is a node (hisssss!) application. To install:

```bash
brew install npm
npm install -g decktape
which decktape
```

#### ffmpeg

`ffmpeg` is the tool we'll be using to assemble the audio and video tracks into a working MP4 recording. You *should* find that installing `ffmpeg` also installs `ffprobe`, which we need to work out the length of some audio tracks.

```bash
brew install freetype
brew install ffmpeg
```

[Programming Historian](https://programminghistorian.org/) has a useful [Introduction to ffmpeg](https://programminghistorian.org/en/lessons/introduction-to-ffmpeg#basic-structure-and-syntax-of-ffmpeg-commands). It doesn't cover this use case but it is nonetheless a nice orientation to the basic structure of ffmpeg commands. See also: [Demystifying ffmpeg](https://github.com/privatezero/NDSR/blob/master/Demystifying_FFmpeg_Slides.pdf), the [ffmpeg Presentation](https://docs.google.com/presentation/d/1NuusF948E6-gNTN04Lj0YHcVV9-30PTvkh_7mqyPPv4/present?ueb=true&slide=id.g2974defaca_0_231) and [ffmpeg Wiki](https://trac.ffmpeg.org/wiki/WikiStart) alongside [the documentation](https://www.ffmpeg.org/ffmpeg.html). 

## Generating the Assets

### Structure

There are seven scripts, but *normally* only some of them are called directly:

- `flip.py` — all-in-one script to extract PNGs, extract audio, and stich everything together. 
- `extract_deck.py` — script used to extract an HTML/JS-based presentation to a series of PNG images. Can be called directly during development/testing, but normally called from `flip.py`.
- `extract_audio.py` — script used to extract a set of M4A sub-files from a source M4A track (chosen for simplicity). It will look in an `audio_segments.md` file for a header that matches the filename of the talk and use the markdown table immediately below that to select start/stop positions.
- `merge.py` — script used to merge PNGs and M4A audio track into a single output MP4 file that is ready for posting online. Can be run separately to test output prior to scaling the process to module/course level.
- `intro.py` – script used to create an 'intro' movie clip that can replace the 'Welcome' slide in a typical presentation. This makes use of the classes provided by `ffmpeg.py` to make it a bit easier to interact with ffmpeg when rendering dynamic content.
- `outry.py` – script used to create the 'outro' equivalent of the introductory clip. Generally, it's fading out and showing copyright, thanks, or other relevant material.

You *might* find it easier to try playing around with the `extract`, `merge`, `intro`, and `outro` scripts separately *before* using `flip.py` so that you can be confident of having an effective workflow and all of the configuration parameters configured correctly.

Because everything here is scriptable, you could create a shell script to (re)generate the videos for each and every flipped lecture in a module/course. This could be particularly useful for bulk-updates (such as a change of year, copyright notice, or name). 

A 'perk' here is that by making it easy to embed the the year this helps to protect the academic from the re-use of their materials: students might rightly ask why they are being shown content from two or more years ago.

### All in One

The `flip.py` script integrates all of the separate steps listed below but, as a result, has a lot of flags to grapple with. These can be viewed by simply running:

```bash
python flip/flip.py --help
```

Normally, you will have set up a project TOML file that provides all of the information needed for your module. If you are rendering *multiple* modules then you might want to move the more generic parameters to a defaults TOML file that you can also specify. The parameters of the two files are merged at render time with any duplicate keys from defaults being overwritten by the project. The overall process could probably use some tweaking, but basically, `flip` will look in the project file for the lesson number that you want to render and use that to drive the extraction and generationg process.

So a simple use-case would be:

```bash
python flip.py -p toml/project.toml -l 1
```

## Audio

The source audio can be captured however you like, but [OcenAudio](https://www.ocenaudio.com/en) seems to be able to do this quite effectively and quickly if you want to stick to FOSS. I particularly appreciated the availability of VST plugins that could be used here, such as, [AconDigital’s Extract:Dialogue](https://acondigital.com/products/extract-dialogue).

#### Audio Capture

I've assumed that the simplest way to capture the audio needed for a flipped teaching session is as a single file: this allows you to get into the 'flow' and then worry about tidying things up later. So your workflow for audio capture would most often be:

1. Set up your audio recording equipment.
2. Record your talk.
3. Save the audio file to the `audio` folder specified in the project TOML file.

This audio file is presumed to provide the source for each paired audio+PNG segment, so the next thing is to tell `flip` how to perform this task.

#### Setting up Audio Segments

To allow for all of the information required to manage a complete module/course to be saved in one area, `flip` uses a Markdown file where the headers-of-interest are assumed to match the filename of the talk (so the same as the `talk` parameter provided to `decktape`) and a table underneath that provides the timings, sequencing, and name for each.

So the format of the table is important, and this **includes** the format of the header that appears immediately before the start of the table. The 'title' for the table should match the `-t` switch passed in to `process.py` (or to `merge.py` if you're running the constituent scripts separately). For example:

```markdown
## 2.3-Python the Basics

| Start   | End     | Sequence | Name         |
| ------- | ------- | -------- | ------------ |
| 0:00.00 | 0:41.11 | 1        | Introduction |
| 0:41.11 | 1:23.07 | 2        | Variables    |
| 1:23.07 | 3:41.05 | 4        | Types        |
| 3:41.05 | 5:49.08 | 5        | Change That  |
```

**Note**: as in the example above, if you want to skip a slide from your talk or change the sequence, simply manipulate the `sequence` column of the markdown table (3 is ommitted here). `merge.py` will use the integer id of the PNGs and exported M4A segments to 'zip' up the parts into a movie. That said, I do need to work a bit on how this works as I often find that the wrong slide/audio are stitched together when I try to get too clever with manipulating the sequence rather than just updating the slide deck.

Some tips:

- Individual audio segments can be set to start and end at any valid timestamp within the M4A file.
- By extension, you could repeat the same piece of audio multiple times if you wanted.

However, from experience I *can* say that setting the stop time of one segment and the start time of the following segment to the *exact* same time is likely to lead to juddering audio effects. It's best to offset the start time by a millisecond.

#### Noise Reduction

If your recording levels are low and/or you discover noise in the recording after the fact then you can remove background noise in Ocen Audio. 

Or in Audacity, if you still use that, you can do it in the following manner:

1. Select (using the 'I'-like selection tool) a region of the recording that has no speech in it.
2. Select `Effect` > `Noise Remove and Repair` > `Noise Reduction...`.
3. In the popup, click the `Get Noise Profile` and click 'OK' (**Important**: nothing has happened yet!)
4. Now select the *entire* recording (`Cmd` + `A`) and open the `Noise Reduction` filter again.
5. Choose the settings (e.g. Noise reduction of 15db, Sensitivity of 8, Frequency smooth (bands) of 6) (**Note**: these settings are a *guess*)
6. Click `Preview` to hear the effect and adjust the settings again if necessary.
7. Once you're happy with the noise reduction amount click 'OK'

## Quick Start

In principle, if you've installed the tools, then the following code should work to render two short videos based on the current (as of early 2026) slide order for my [Foundations of Spatial Data Science](https://jreades.github.io/sds/) module and the supplied audio in the GitHub repo.

Code to do this is:

```bash
python flip.py -p toml/project.toml -l 1 -q
python flip.py -p toml/project.toml -l 4 -q
```

The `-q` option tells flip to ignore the mismatch between then number of slides it extracted and the number of audio segments supplied in `lessons.md`. 

You should then find the constituent parts in the various `_<step>` folders with the final video appearing in `_output`.
