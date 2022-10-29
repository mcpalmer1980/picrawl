#!/bin/python3
'''Picrawl is an viewer that crawls subfolders and shuffles your images
usage available by using pycrawl -h
install with the following command: pip install .

TODO: add get_max_options and get_longest_item to menu
      add menu.create(type, blah, blah)
      add mark button and key
'''

import sys, os, random
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['SDL_RENDER_SCALE_QUALITY'] = '2'
import pygame as pg
import renderpyg
from bisect import bisect_left as bisect
from pygame.locals import *
from pygame._sdl2.video import Renderer, Window, Texture, Image
from pygame._sdl2 import controller as Controller
try:
    from .menu import open_menu, load_menu_data
except:
    from menu import open_menu, load_menu_data


version = '0.001'
window_size = (1600, 900)
mouse_hide_delay = 90
KEY_PAN_SPEED = 20
AXIS_MOD = 2**10 #15
AXIS_MIN = 2**4 # .3
AXIS_PAN = 20
# 10 options for slideshow delays in the format delays[x] = delay in seconds, description
delays = dict(zip(range(10), ((2.5, '2.5 sec'), (5, '5 sec'), (10, '10 sec'),
        (15, '15 sec'), (30, '30 sec'), (60, '1 min'), (90, '1.5 min'),
        (180, '3 min'), (300, '5 min'), (600, '10 min'))))

class global_data:
    'stores global data throughout program'
    mode = current = previous = message_time = 0
    no_names = gridview = slideshow = False
    clip = subfolders = True
    delay = 1
    grid_size = 3
    timer = delays[1][0] * 30 # 30 fps
    fullscreen = False
    next_message = controller = None
    window_size = window_size

    def init(self, path, files, screen, window, tags):
        self.path = path
        self.files = files
        self.screen = screen
        self.window = window
        self.tags, self.tagged = tags

        self.marked = {}
        self.shuffled = list(files)
        random.shuffle(self.shuffled)
g = global_data()

class gridv:
    def __init__(self, images):
        self.images = images
    def draw(self, *args, **kwargs):
        for image, dest, _ in self.images:
            image.draw(dstrect=dest)
    def pick(self, pos):
        for i in self.images:
            if i[1].collidepoint(pos):
                return i
    def highlight(self, pos):
        im = self.pick(pos)
        if im:
            g.screen.draw_color = 255,255,255,255
            g.screen.draw_rect(im[1])
            g.screen.draw_rect(im[1].inflate(1,1))
            g.screen.draw_rect(im[1].inflate(2,2))
    def get_click(self, pos):
        i = self.pick(pos)
        if i:
            g.gridview = False
            g.current = i[2]
            im = g.shuffled[i[2]] if g.mode == 0 else g.files[i[2]]
            return get_image(im)

def main():
    global image, dest
    # prepare options and the timer
    controller_init()
    path, first_file = set_options()
    timer = pg.time.Clock()
    timer.tick()


    # get list of files or exit if none found
    files, total, tags = get_files(path)
    if not files:
        option_error('No images found!')
    print(f'  {len(files)} images found among {total} files in {timer.tick()}ms')

    # sort files regardless of case
    files.sort(key=lambda s: s.lower())

    # initialize the display
    screen, window = make_window()
    g.init(path, files, screen, window, tags)
    g.quit = quit
    image, dest = first_image(first_file)

    # -------------------------
    # PREP AND START EVENT LOOP
    pan = dict(x=0, y=0) # for keyboard panning
    r_mod = r_mod_used = False # for mouse pan and zoom
    mouse_timer = 0
    running = True 
    while running: # start event loop
        screen.target = g.buffer
        for ev in pg.event.get():
            x, y = pg.mouse.get_pos()
            if ev.type == pg.QUIT: # exit on window close or Alt-F4
                running = False

            # handle key navigation
            elif ev.type == pg.KEYDOWN:
                if ev.key == pg.K_ESCAPE: # exit
                    running = False
                elif ev.key == K_f:
                    dest = toggle_fullscreen(image)
                elif ev.key == K_g:
                    g.gridview = True
                    image, dest = next_image()
                elif ev.key == K_p:
                    start_slideshow()
                elif ev.key in (pg.K_RIGHT, pg.K_SPACE):
                    image, dest = next_image()
                elif ev.key == pg.K_LEFT:
                    image, dest = next_image(False)
                elif ev.key in (pg.K_RETURN, pg.K_KP_ENTER) and not g.gridview:
                    change_mode()
                elif ev.key == pg.K_UP and not g.gridview:
                    scale_rect(1, dest)
                elif ev.key == pg.K_DOWN and not g.gridview:
                    scale_rect(-1, dest)
                elif ev.key == K_m:
                    menu()
                elif ev.key == K_k:
                    g.marked[g.last_file] = not g.marked.get(g.last_file, False)

                # handle key panning
                elif ev.key == pg.K_w: pan['y'] = 1
                elif ev.key == pg.K_s: pan['y'] = -1
                elif ev.key == pg.K_a: pan['x'] = 1
                elif ev.key == pg.K_d: pan['x'] = -1
            elif ev.type == pg.KEYUP:
                if ev.key == pg.K_w: pan['y'] = 0
                elif ev.key == pg.K_s: pan['y'] = 0
                elif ev.key == pg.K_a: pan['x'] = 0
                elif ev.key == pg.K_d: pan['x'] = 0

            # handle mouse navigation
            elif ev.type == pg.MOUSEBUTTONDOWN:
                mouse_timer = mouse_hide_delay
                pg.mouse.set_visible(True)
                if ev.button == 1:
                    if get_icon_click():
                        pass
                    elif g.gridview:
                        results = image.get_click(pg.mouse.get_pos())
                        if results:
                            image, dest = results
                    elif r_mod:
                        g.gridview = True
                        image, dest = next_image()
                        r_mod_used = True
                        r_mod = False
                    else:
                        image, dest = next_image()
                if ev.button == 2:
                    if r_mod:
                        r_mod_used = True
                        dest = toggle_fullscreen(image)
                    else:
                        menu() 
                elif ev.button == 3 and not g.gridview:
                    r_mod = 1
                    g.window.relative_mouse = True
                elif ev.button == 4:
                    dest = toggle_fullscreen(image)
                elif ev.button == 5:
                    g.gridview = True
                    image, dest = next_image()
            elif ev.type == pg.MOUSEWHEEL:
                if r_mod: # zoom if right button held
                    r_mod_used = True
                    scale_rect(ev.y, dest)
                elif g.slideshow:
                    g.delay = (min(9, max(0, g.delay + ev.y)))
                    g.timer = delays[g.delay][0] * 30
                    show_message('slideshow delay set to ' + delays[g.delay][1])
                else:
                    if ev.y < 0:
                        image, dest = next_image(False)
                    else:
                        image, dest = next_image()

            elif ev.type == pg.MOUSEBUTTONUP:
                if ev.button == 3:
                    if not g.gridview: # only change mode if user didn't pan or zoom
                        if not r_mod_used:
                            change_mode()
                    r_mod = r_mod_used = False
                    pg.mouse.set_visible(True)
                    mouse_timer = mouse_hide_delay
                    g.window.relative_mouse = False
            elif ev.type == pg.MOUSEMOTION: # pan if right button held
                if mouse_timer < 1:
                    mouse_timer = mouse_hide_delay
                    pg.mouse.set_visible(True)
                if r_mod:
                    r_mod_used = True
                    pan_image(dest, *ev.rel, True)
                if ev.pos[1] < 5:
                    show_message(os.path.split(g.last_file)[-1])
            
            # handle controller events
            elif ev.type == pg.CONTROLLERDEVICEADDED:
                controller_init(ev.device_index)
            elif ev.type == pg.CONTROLLERBUTTONDOWN: # adjust slideshow timer
                if g.slideshow and ev.button in (
                        CBUTT['left'], CBUTT['right']):
                    x = -1 if ev.button == CBUTT['left'] else 1
                    g.delay = (min(9, max(0, g.delay + x)))
                    g.timer = delays[g.delay][0] * 30
                    show_message('slideshow delay set to ' + delays[g.delay][1])
                elif ev.button == CBUTT['fullscreen']:
                    dest = toggle_fullscreen(image)
                elif ev.button == CBUTT['gridview']:
                    if g.gridview:
                        pg.event.post(pg.event.Event(
                            pg.MOUSEBUTTONDOWN, button=1))
                    else:
                        g.gridview = True
                        image, dest = next_image()
                elif ev.button == CBUTT['sel'] and g.gridview:
                  pg.event.post(pg.event.Event(
                        pg.MOUSEBUTTONDOWN, button=1))                    
                elif ev.button in CBUTT['next']:
                    if g.gridview and ev.button == CBUTT['next'][0]:
                        pg.event.post(pg.event.Event(
                            pg.MOUSEBUTTONDOWN, button=1))
                    else:
                        image, dest = next_image()
                elif ev.button in CBUTT['prev']:
                    image, dest = next_image(False)
                elif ev.button == CBUTT['menu']:
                    if g.controller.get_button(CBUTT['mode']):
                        quit()
                    else:
                        menu(center=True)
                elif ev.button == CBUTT['mode'] and not g.gridview:
                    change_mode()
                    g.controller.rumble(.1,.7, 150)
                elif ev.button == CBUTT['zin'] and not g.gridview:
                    scale_rect(1, dest)
                elif ev.button == CBUTT['zout'] and not g.gridview:
                    scale_rect(-1, dest)
                elif ev.button == CBUTT['play']:
                    start_slideshow()
                elif ev.button == CBUTT['mark']:
                    g.marked[g.last_file] = not g.marked.get(g.last_file, False)

        # keyboard panning
        if not g.gridview:
            pan_image(dest,
                pan['x'] * -KEY_PAN_SPEED,
                pan['y'] * -KEY_PAN_SPEED)

        # controller panning and pointing
        if g.controller:
            dx = g.controller.get_axis(CBUTT['horz'])
            dy = g.controller.get_axis(CBUTT['vert'])
            dx = dx / AXIS_MOD if abs(dx) > AXIS_MIN else dx
            dy = dy / AXIS_MOD if abs(dy) > AXIS_MIN else dy
            if g.gridview:
                pg.mouse.set_visible(True)
                x, y = pg.mouse.get_pos()
                pg.mouse.set_pos((x+dx, y+dy))
            else:
                pan_image(dest, dx, dy)
        
        # mouse hiding
        if mouse_timer > 0 and not g.gridview:
            mouse_timer -= 1
            if mouse_timer == 0:
                pg.mouse.set_visible(False)

        # handle slideshow timer and change image 
        if g.slideshow:
            g.timer -= 1
            if g.timer == 0:
                g.timer = delays[g.delay][0] * 30
                image, dest = next_image()
        if r_mod:
            r_mod += 1
            if r_mod > 40 and not r_mod_used:
                r_mod_used = True
                start_slideshow()

        # update the screen 30 frames per second
        screen.draw_color = 0,0,0,255
        screen.clear()
        image.draw(dstrect=dest)

        if pg.mouse.get_visible():
            g.checkmark[0].alpha = 150 if g.marked.get(g.last_file, False) else 50
            g.checkmark[0].draw(dstrect=g.checkmark[1])
            g.glass[0].draw(dstrect=g.glass[1])
        elif g.marked.get(g.last_file, False):
            g.checkmark[0].alpha = 50
            g.checkmark[0].draw(dstrect=g.checkmark[1])

        if g.gridview:
            image.highlight(pg.mouse.get_pos())
        if g.message_time > 0:
            g.message_time -= 1
            g.message.draw(dstrect=g.message_dest)
        if g.next_message:
            show_message(*g.next_message)
            g.next_message = None

        screen.target = None
        g.buffer.draw()
        screen.present()
        timer.tick(30)
    # END OF EVENT LOOP
    # -----------------

    quit()

def menu(which=None, center=False):
    global image, dest

    show_message(os.path.split(g.last_file)[-1])
    g.message.draw(dstrect=g.message_dest)

    results = open_menu(g, which)
    if results.get('toggle_fullscreen', False):
        dest = toggle_fullscreen(image)
    if results.get('grid_view', False):
        if g.gridview:
            g.gridview = False
            image, dest = next_image()
        else:
            g.gridview = True
            image, dest = grid_view()
    if results.get('slideshow', False):
        start_slideshow()
    if results.get('scan', False):
        path = results['scan']
        show_message(f'Rescanned {path}')
        files, total, tags = get_files(results['scan'])
        g.path = path
        g.files = sorted(files, key=lambda s: s.lower())
        g.shuffled = list(files)
        random.shuffle(g.shuffled)
        first = g.last_file if g.last_file in g.files else None
        image, dest = first_image(first)
    if results.get('next', False):
        image, dest = next_image()

    show_message(os.path.split(g.last_file)[-1])

def get_files(path, extensions=('.jpg', '.jpeg', '.png', '.gif', 'bmp')):
    'Create image list from given path and file extensions'
    depth = len(path[1:].split(os.sep))
    files = []
    total = 0
    if g.subfolders:
        for (dirpath, dirnames, filenames) in os.walk(path):
            sp = dirpath[1:].split(os.sep)
            dots = '.'*(len(sp) - depth)
            in_folder = 0
            for filename in filenames:
                total += 1
                if os.path.splitext(filename)[-1].lower() in extensions:
                    files.append(os.path.join(dirpath, filename))
                    in_folder += 1
            if in_folder:
                print(f'  {dots}{sp[-1]}: {in_folder} images')
    else:
        for f in os.listdir(path):
            if os.path.splitext(f)[-1].lower() in extensions:
                files.append(os.path.join(path, f))
                total += 1
    
    tags = []
    tagged = {}
    tag_file = os.path.join(path, 'tags.txt')
    if os.path.exists(tag_file):
        with open(tag_file, 'r') as f:
            tags, *lines = f.readlines()
            tags = tags.strip().split(' ')
            for line in lines:
                if not line or '::=' not in line:
                    continue
                try:
                    fn, *t = line.split('::=')
                    tagged[os.path.join(path, fn)] = t[0].strip().split(' ')
                except:
                    print('error in tag.txt: ', line)
        print(f'  found tags.txt: {len(tagged)} tagged images')
    return files, total, (tags, tagged)

def get_icon_click():
    pos = pg.mouse.get_pos()
    if g.checkmark[1].collidepoint(pos):
        g.marked[g.last_file] = not g.marked.get(g.last_file, False)
        return True
    elif g.glass[1].collidepoint(pos):
        menu('info')
        return True

def make_window():
    'Setup window or fullscreen display'
    os.environ['SDL_RENDER_SCALE_QUALITY'] = '2'

    # create pygame._sdl2 window
    if g.fullscreen:
        window = Window("Viewer {}".format(version), fullscreen_desktop=True)
        g.render_rect = pg.Rect(0,0,*window.size)
        g.fullscreen = True
    else:
        window = Window("Viewer {}".format(version), size=g.window_size)
        g.render_rect = pg.Rect(0,0,*window.size)
        g.fullscreen = False

    # initialize render and buffer
    screen = Renderer(window, vsync=True)
    g.window = window
    g.buffer = Texture(screen, g.render_rect.size, target=True)
    screen.target = g.buffer

    # load images and set application icon
    _, data = load_menu_data(screen)
    icon, checkmark, glass = data
    icon = pg.image.load(
        os.path.join(os.path.dirname(__file__), 'icon.png'))
    window.set_icon(icon)

    # prep onscreen icons
    size = int(g.render_rect.h *.1)
    r = pg.Rect(0,0,size,size)
    g.checkmark = checkmark, r
    glass.alpha = 50
    g.glass = glass, r.move(0, size)


    # prep font for popup messages
    g.font = pg.font.SysFont('Ariel', int(g.render_rect.h*.07))
    return screen, window

def toggle_fullscreen(image):
    if g.fullscreen:
        g.fullscreen = False
        g.window.size = g.window_size
        g.window.set_windowed()
        g.render_rect = pg.Rect(0,0, *g.window_size)
    else:
        g.fullscreen = True
        g.window.set_fullscreen(True)
        info = pg.display.Info()
        g.render_rect = pg.Rect(0,0, info.current_w, info.current_h)

    g.buffer = Texture(g.screen, g.render_rect.size, target=True)
    g.screen.target = g.buffer
    load_menu_data(g.screen, reload=True)

    if g.gridview:
        wi = g.render_rect.w // g.grid_size
        hi = g.render_rect.h // g.grid_size
        r = pg.Rect(0,0, wi,hi)

        im = 0
        for y in range(g.grid_size):
            for x in range(g.grid_size):
                r.topleft = wi*x, hi*y
                dest = image.images[im][1]                
                dest.update(*dest.fit(r))
                im += 1
        return

    return image.get_rect().fit(g.render_rect)

def first_image(first):
    'Load first image based on starting mode'
    i = 0
    if g.mode == 1: # sorted
        if first:
            g.current = g.files.index(first)
    else: # shuffled
        if first:
            g.current = g.shuffled.index(first)
    g.previous = g.current
    g.current -= 1
    return next_image()

def get_image(fn):
    'Load image with fn filename and scale it to fill window'
    g.last_file = fn # used to print/clipboard image viewed upon exit
    w, h = g.render_rect.size
    try: # basic error handling for bad images
        surf = pg.image.load(fn)
    except: # create blank surface and error message for user
        surf = pg.Surface((w//4, h//4))
        fn = 'error loading file'
    image = Texture.from_surface(g.screen, surf)
    if not g.no_names and not g.gridview:
        show_message(os.path.split(fn)[-1])
    alpha = 150 if g.last_file in g.marked else 50
    g.checkmark[0].alpha = alpha
    return image, image.get_rect().fit(pg.Rect(0, 0 , *g.render_rect.size))

def grid_view(forward=True):
    pg.mouse.set_visible(True)
    if g.controller:
        g.window.grab = True
        pg.mouse.set_pos(g.render_rect.center)
        g.window.grab = False

    size = g.grid_size
    images = []
    wi = g.render_rect.w // size
    hi = g.render_rect.h // size
    r = pg.Rect(0,0, wi,hi)
    render_rect, g.render_rect = g.render_rect, r

    for _ in range(size * size):
        image, rect = next_image(forward, True)
        images.append((image, rect, g.current))

    im = 0
    for y in range(size):
        for x in range(size):
            r.topleft = wi*x, hi*y
            _, dest, _ = images[im]
            dest.center = r.center
            im += 1

    g.render_rect = render_rect
    return gridv(images), r
    
def next_image(forward=True, from_grid=False):
    'Load next image in the shuffled or sorted list'
    if len(g.files) < 1:
        print('Image list is empty. Exiting...')
        quit()

    if g.gridview and not from_grid:
        return grid_view(forward)
    if forward:
        g.current = (g.current + 1) % len(g.files)
    else: # Load the previous image instead
        g.current = (g.current - 1) % len(g.files)

    if g.mode in (0,2): # get shuffled image in shuffle/slideshow mode
        return get_image(g.shuffled[g.current])
    elif g.mode == 1: # get image from sorted list
        return get_image(g.files[g.current])

def start_slideshow():
    if g.slideshow:
        show_message('slideshow stopped')
        g.slideshow = False
    else:
        g.timer = delays[g.delay][0] * 30
        g.slideshow = True
        show_message(f'Slideshow started: {delays[g.delay][1]} delay')

def change_mode():
    'Toggle to the next mode (shuffled, sorted, slideshow)'
    if g.slideshow:
        g.slideshow = False
        show_message('slideshow stopped')
    elif g.mode == 0:
        show_message('switching to sorted mode')
        g.mode = 1
        g.previous = g.current
        if g.last_file in g.files:
            g.current = g.files.index(g.last_file)
        else:
            g.current = min(bisect(g.files, g.last_file), len(g.files)-1)
    elif g.mode == 1:
        show_message('switching to shuffled mode')
        g.current = min(g.previous, len(g.files)-1)
        g.mode = 0

def show_message(text, time = 4, force=True):
    'Display a message for time seconds'

    # que message if already displaying one unless force=False
    if g.message_time > 0 and not force:
        g.next_message = text, int(time * 30)
        return

    # create texture from text using
    surf = g.font.render(text, True, (255,255,255), (0,0,0))
    g.message = Texture.from_surface(g.screen, surf)
    g.message_time = time * 30

    # center it
    r = g.message.get_rect()
    r.centerx = g.render_rect.w / 2
    if r.width > g.render_rect.w:
        r = g.message.get_rect().fit(pg.Rect(0, 0 , *g.render_rect.size))
    r.top = g.render_rect.h * .01
    g.message_dest = r

def scale_rect(scale, dest):
    'Scale destination rect for zooming'
    am = .2 if scale > 0 else -.2
    r = dest.inflate(dest.w*am, dest.h*am)
    if g.render_rect.contains(r):
        dest.update(*dest.fit(g.render_rect))
    else:
        dest.inflate_ip(dest.w*am, dest.h*am)

def pan_image(dest, dx, dy, reverse=False):
    if reverse:
        dx, dy = -dx, -dy
    if dest.w >= g.render_rect.w:
        dest.x += dx    
        dest.right = max(dest.right, g.render_rect.right)
        dest.left = min(dest.left, 0)
    if dest.h >= g.render_rect.h:
        dest.y += dy    
        dest.bottom = max(dest.bottom, g.render_rect.bottom)
        dest.top = min(dest.top, 0)

CBUTT = dict(
    mode=4, menu=6, zin=11, zout=12, next=(0,14), prev=(1,13), sel=1,
    horz=0, vert=1, left=13, right=14, fullscreen=3, gridview=2,
    mark=10, play=9)

def controller_init(index=0):
    if not Controller.init() and Controller.get_count() > 0:
        print(f'controller found: {Controller.name_forindex(index)}')
        g.controller = Controller.Controller(index)
    else:
        print('No controller found')

def set_options():
    'Handle command line parameters'
    argc = len(sys.argv) - 1
    flags = path = ''
    size = None

    # parse command line
    if argc:
        for i, arg in enumerate(sys.argv[1:]):
            if arg.startswith('-'):
                if arg == '-':
                    option_error(f'{arg} is not a supported flag')
                flags += arg[1:]
            elif i == argc-1:
                path = arg
            elif s := is_resolution(arg):
                size = s
            else:
                option_error(f'{arg} is not a supported flag')                
    verify_flags(flags) # verify command line flags

    # set path to scan based on command parameters and current directory
    first_file = None
    wd =  os.getcwd()
    if path:
        rel = os.path.join(wd, path)
        if os.path.exists(rel):
            path = rel
            if os.path.isfile(path):
                first_file = path
                path = os.path.dirname(path)

        else: # display error and exit if path invalid
            option_error(f'{path} is not a valid path')
    else:
        # default to current directory if no path in command line
        path = wd

    # display message before file scanning begins
    print(f'PicCrawler v{version} scanning {path}')
    return path, first_file

def verify_flags(flags):
    'Verify all commandline flags are valid then process them'
    valid_flags = 'fsh?pchngi2345'
    if not flags: # return if no flags found
        return None

    d = {} # check for duplicate flags
    for f in flags:
        if d.get(f, None):
            option_error(f'duplicate {f} flags in command line')
        elif f not in (valid_flags):
            option_error(f'{f} is not an valid flag')
        else:
            d[f] = True

    # process the verified flags
    for f in flags:
        if f == 'f':
            g.fullscreen = True
        elif f == 's': # sorted instead of shuffled
            g.slideshow = True
        elif f in 'h?':
            print(help_message)
            exit()
        elif f == 'p':
            #FIXME
            g.mode = 2
        elif f == 'c':
            g.clip = False
        elif f == 'n':
            g.no_names = True
        elif f == 'g':
            g.gridview = True
        elif f == 'i':
            g.subfolders = False
        elif f in '2345':
            g.grid_size = int(f)

def is_resolution(flag):
    '''Check if parameter is formated as a window size.
    Proper syntax is (width)x(height) where width and height are
    integer values'''
    if 'x' in flag:
        sides = flag.split('x')
        if len(sides) != 2:
            option_error(f'{flag} is not a valid window size')
        try:
            w = int(sides[0])
            h = int(sides[1])
            g.window_size = w, h
        except:
            g.window_size = window_size
            option_error(f'{flag} is not a valid window size')
        return w, h

def option_error(message):
    'Display an error message and exit'
    print(help_message)
    print('!! COMMAND LINE ERROR !!\n ', message)
    exit()

help_message = '''
Picrawl is an viewer that crawls subfolders and shuffles your images
Easily toggle between shuffled and ordered navigation 
Grid view, slideshow, image info, and tag editing features
Can be controlled with keyboard, mouse, or game controller

command line:  picrawl -flags WINDOWxSIZE path

flags:
  h - show this Help message            g - start in Grid view
  s - Sort instead of shuffle           c - skip Clipboard copy upon exit
  f - start Fullscreen                  n - disable file Name popup messages
  p - Play slideshow at startup       2-5 - set grid size 2x2 to 5x5
  i - Ignore Subfolders
   
WINDOWxSIZE: set window size to (width)x(height) like 640x480
path: file or folder where images shuffled from all subfolders

Controls: (Keyboard and Mouse)
  next image: right key, mouse wheel    prev image: right key, mouse wheel
  menu: m key, mouse 3                  exit: escape, use menu
  change mode: enter, mouse 2           slideshow: p key, long mouse 2
  fullscreen: f key, menu, mouse 4      gridview: g key, mouse 2 + 1
  zoom: up/down keys, mouse 2 + wheel   scroll: wasd keys, mouse 2 + move cursor
Controls: (Controller)
  next image: d-pad right, A button     prev image: dpad left, B button
  menu: start button                    exit: select+start, use menu
  change mode: select button            slideshow: L1 button
  fullscreen: X button                  gridview: Y button 
  zoom: d-pad up/down                   scroll: left stick
  gridview cursor: left stick           gridview select: Y button
'''[1:]

def save_tags():
    if not g.tags:
        return
    with open(os.path.join(g.path, 'tags.txt'), 'w') as outp:
        print(' '.join(g.tags), file=outp)
        for fn, tags in g.tagged.items():
            print('{}::={}'.format(
                os.path.relpath(fn, g.path),
                ' '.join(tags)), file=outp)

def quit():
    clip = False
    where = 'the terminal'
    if g.clip:
        try:
            import pyperclip
            clip = True
            where = 'clipboard and the terminal'
        except:
            print('could not import clipboard module')
            clip = False
  
    
    if True in g.marked.values():
        message = 'Writing marked images to ' + where
    else:
        message = 'Writing last viewed image to ' + where

    outp = ''
    if g.marked:
        for f, marked in g.marked.items():
            if marked:
                outp += f + '\n'
    else:
        outp += g.last_file + '\n'

    print('\n' + message)
    print(outp.strip())
    if clip:
        pyperclip.copy(outp)
    
    save_tags()
    pg.quit()
    exit()

if __name__ == "__main__":
    main()
