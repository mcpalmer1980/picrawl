# PiCrawl

Picrawl is an viewer that crawls subfolders and shuffles your images

- Easily toggle between shuffled and ordered navigation
- Grid view, slideshow, image info, and tag editing features
- Can be controlled with keyboard, mouse, or game controller

__command line:  picrawl -flags WINDOWxSIZE path__

```
flags:
  h - show this Help message            g - start in Grid view
  s - Sort instead of shuffle           c - skip Clipboard copy upon exit
  f - start Fullscreen                  n - disable file Name popup messages
  p - Play slideshow at startup       2-5 - set grid size 2x2 to 5x5
  i - Ignore Subfolders
```

_WINDOWxSIZE:_ set window size to (width)x(height) like 640x480

_path:_ file or folder where images shuffled from all subfolders

Controls: (Keyboard and Mouse)

```
  next image: right key, mouse wheel    prev image: right key, mouse wheel
  menu: m key, mouse 3                  exit: escape, use menu
  change mode: enter, mouse 2           slideshow: p key, long mouse 2
  fullscreen: f key, menu, mouse 4      gridview: g key, mouse 2 + 1
  zoom: up/down keys, mouse 2 + wheel   scroll: wasd keys, mouse 2 + move cursor
```

  Controls: (Controller)

```
  next image: d-pad right, A button     prev image: dpad left, B button
  menu: start button                    exit: select+start, use menu
  change mode: select button            slideshow: L1 button
  fullscreen: X button                  gridview: Y button
  zoom: d-pad up/down                   scroll: left stick
  gridview cursor: left stick           gridview select: Y button
```
