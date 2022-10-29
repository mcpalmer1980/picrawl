# PiCrawl

Picrawl is a viewer that crawls subfolders and shuffles your images. It is
useful for randomly browsing large photographic collections while ignoring
the underlying directory structure. A single button press toggles between
shuffled and sorted modes, allowing related images to be viewed when you
find one you want to see.

- Easily toggle between shuffled and ordered navigation
- Grid view, slideshow, file details, and tag editing features
- Can be controlled by a keyboard, mouse, or game controller

__command line:__  picrawl -flags WINDOWxSIZE path

```
flags:
  h - show this Help message          g - start in Grid view
  s - Sort instead of shuffle         c - skip Clipboard copy upon exit
  f - start Fullscreen                n - disable file Name popup messages
  p - Play slideshow at startup     2-5 - set grid size 2x2 to 5x5
  i - Ignore Subfolders
```

_WINDOWxSIZE:_ set window size to (width)x(height) like 640x480

_path:_ file or folder where images shuffled from all subfolders

## Controls: (Keyboard and Mouse)

```
  next image: right key, mouse wheel    prev image: right key, mouse wheel
  menu: m key, mouse 3                  exit: escape, use menu
  change mode: enter, mouse 2           slideshow: p key, long mouse 2
  fullscreen: f key, menu, mouse 4      gridview: g key, mouse 2 + 1
  zoom: up/down keys, mouse 2 + wheel   scroll: wasd keys, mouse 2 + cursor
  mark/unmark: k
```

## Controls: (Controller)

```
  next image: d-pad right, A button     prev image: dpad left, B button
  menu: start button                    exit: select+start, use menu
  change mode: select button            slideshow: L1 button
  fullscreen: X button                  gridview: Y button
  zoom: d-pad up/down                   scroll: left stick
  gridview cursor: left stick           gridview select: Y button
  mark/unmark: R1 button
```

## Menu Options

- **Info** - Display image details such as path, size, and tags
- **Mark** - Mark current image for batch changes or to copy into clipboard
- **Grid View** - Switch to grid view to view multiple images simultaneously
- **Slideshow** - Start a slideshow with the currently set delay
- **Files**
  - **Browse** - Change viewer to another folder and rescan them
  - **Copy** - Copy current or marked images to another folder
  - **Delete** - Delete current or marked images
  - **Invert Marks** - Invert selection, marking unmarked images and unmarking marked ones
  - **Move** - Move current or marked images to another folder
  - **Rename** - Rename current image
  - **Remove** - Remove current or marked image from the list of scanned images
- **Options**
  - **Fullscreen** - Turn on or off fullscreen mode (toggle between fullscreen and window)
  - **Subfolders** - Turn on or off subfolder scanning and rescan images
  - **Gridsize** - Change the number of images shown in gridview mode
  - **Filter Images** - Only show images that include a chosen tag or a string in its filename
  - **Scan for Tags** - Scan all images for keyword tags and generate a tags.txt file
  - **Slideshow Delay** - Change the delay for slideshow mode

## tags.txt
PiCrawl supports keyword tags and loads data from tags.txt if it's present in a folder
opened either from the command line or from the browse option in the menu. Tag files found in subfolders are ignored.

The first line of tags.txt is a list of tags, each separated by a single space. Each remaining line should be a filename and a list of tags separated by the following 3 characters: '::=' Multiple tags are allowed for each file and are separated by a space in tags.txt.

Example:

```
action fighting platformer shooter sports
Primal Rage.png::=fighting
Spider-Man - Web of Fire.png::=action
NBA Jam Tournament Edition.png::=sports
Darxide.png::=shooter
Brutal - Above the Claw.png::=fighting
Space Harrier.png::=shooter
Tempo.png::=platformer action
```