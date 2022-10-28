'''
butt_padding // 2 might be wrong @ 495
Main 7: Info, Mark, GridView, Slideshow, File, Options, Exit
File 6: Browse, *Copy, Delete, Invert, *Move, Rename, Remove
Options 5: Fullscreen, Subfolders, Crawl Image Folder, Filter Images, Scan For Tags, Slideshow Delay

modals: Add a Tag*, Confirm update tags, New Folder, *cancel=False
'''
import os, sys, random, math

import subprocess as sp
import pygame as pg
from pygame._sdl2 import Window, Renderer, Texture, Image
import renderpyg as pyg
from renderpyg import Sprite, TextureFont, keyrange, load_texture, sr
from renderpyg import fetch_images, NinePatch, Menu, keyframes, round_patch
from random import randrange
from renderpyg.tfont import char_map


wanted_data = {
    'File Name': 'Name', 'Directory': 'Folder', 'File Size': 'Size', 
    'tagsList': 'Tags2', 'Image Size': 'Resolution', 'MIME Type': 'Type',
    'File Modification Date/Time': 'Date', 'Keywords': 'Tags'}

loaded_data = None
def load_menu_data(screen, reload=False, scale=.8):
    global loaded_data
    if loaded_data and not reload:
        return loaded_data

    EXAMPLE_DATA = os.path.join(os.path.dirname(__file__), 'renderpyg', 'data', '')
    MENU_DATA = os.path.join(os.path.dirname(__file__), '')

    render_rect = screen.target.get_rect()
    texture = load_texture(screen, MENU_DATA+'nine.png', scale=scale)
    pg.font.init()

    if render_rect.w > 640 and render_rect.h > 480:
        font_size = int(screen.target.get_rect().h * 0.05)
        tfont, font = TextureFont.multi_font(screen, (
            (MENU_DATA+'font.ttf', font_size),
            (MENU_DATA+'font.ttf', int(font_size*.8))))

        sr.amount = scale
        dialog = NinePatch(texture, sr(36,110,36,82), sr(0,0, 501, 278)) 
        button = NinePatch(texture, sr(12,6,12,6), sr(0, 283, 74, 80))
        box_fill = NinePatch(texture, sr(12,6,12,6), sr(81, 283, 74, 80))
        box = button
        arrow_r, arrow_l = fetch_images(
            texture, rects=(
                sr(162 , 283, 48, 80), # 80 80
                sr(162 , 283, 48, 80)))
        arrow_r.flipX = True
        anim_light = dict(move=(2,0), rotate=7)
        title = 'PicRawl'

        #dialog = round_patch(screen,
        #    12, (150,150,150), (4,8), ((0,0,0), (200,200,200)) )

        menu = Menu(
            screen, font, spacing=8, press_color=(255,150,255),
            patch=dialog, but_patch=button, but_padding=(32, 12),
            sel_patch=button, width = render_rect.w/2, position='mouse',
            opt_left=arrow_l, opt_right=arrow_r, #alpha=175,
            box=box, box_fill=box_fill, box_textc=(0,50,50),
            text_font=tfont, text_scale =.7, title_offset = 90*scale,
            title_font=tfont, title_scale=1.25, title_color=(0,0,200))
        menu.dialog_width = render_rect.w * .4
        menu.info_width = render_rect.w * .65

    else:
        font_size = int(screen.target.get_rect().h * 0.07)
        anim_light = dict(move=(2,0), rotate=7)
        frame = (0,0,0), (255,255,255), 6
        font = TextureFont(screen,
            EXAMPLE_DATA+'font2.ttf', font_size)
        menu = Menu(
            screen, font,
            box=((255,255,255), (0,0,0), 4), 
            color=(150,150,150), label=(200,200,200),
            sel_color=(255,255,255), frame=frame, alpha=100,
            position = 'mouse', text_scale=.66)
        menu.title_anim = anim_light
        menu.dialog_width = render_rect.w * .8
        menu.info_width = menu.dialog_width
        menu.set_background(screen.target)
    
    icon, check, glass = fetch_images(texture, rects=(
        sr(394,282, 106,81),
        sr(296,282, 74,81),
        sr(216,282, 74,81) ))    
    loaded_data = menu, (icon, glass, check)
    return loaded_data

def open_menu(glob, which=None, center=False):
    if not loaded_data:
        menu, _, = load_menu_data(glob.screen)
    menu, images = loaded_data
    pg.mouse.set_visible(True)
    buffer = glob.buffer
    screen = glob.screen
    menu.set_background(buffer)
    if glob.controller:
        menu.joystick = glob.controller.as_joystick(), 0, 1

    if which == 'info':
        info_menu(menu, glob)
    else:
        main_menu(menu, glob)
    menu.position = 5 if center else 'mouse'

    menu.return_values = {}
    running = True
    while menu.alive:
        screen.target = None
        buffer.draw()
        menu.handle()
        screen.present()
    return menu.return_values

def main_menu(menu, g):
    def handle(i, option):
        if option == 'Exit':
            g.quit()
        elif option == 'Info':
            info_menu(menu, g)
        elif option in ('Mark', 'Unmark'):
            g.marked[g.last_file] = not g.marked.get(g.last_file, False)
        elif option == 'Grid View':
            menu.return_values['grid_view'] = True
        elif option == 'Slideshow':
            menu.return_values['slideshow'] = True
        elif option == 'Files':
            file_menu(menu, g)
        elif option == 'Options':
            option_menu(menu, g)
        return True

    marked = 'Unmark' if g.marked.get(g.last_file, False) else 'Mark'
    result = menu.select(
            ('Info', marked, 'Grid View', 'Slideshow', 'Files',
            'Options', 'Exit'), "Main Menu",
            can_cancel=True, modeless=True, call_back=handle)

def file_menu(menu, g):
    def handle(i, option):
        if option == 'Remove':
            remove_menu(menu, g)
        elif option == 'Rename':
            rename_menu(menu, g)
        elif option == 'Delete':
            delete_menu(menu, g)
        elif option == 'Browse':
            browse_menu(menu, g)
        elif option == 'Copy':
            copy_selector(menu, g)
        elif option == 'Move':
            copy_selector(menu, g, True)
        elif option == 'Invert Marks':
            for f in g.files:
                if g.marked.get(f, False):
                    g.marked.pop(f)
                else:
                    g.marked[f] = True        

    result = menu.select(
            ('Browse', 'Copy', 'Delete', 'Invert Marks',
            'Move', 'Rename', 'Remove'), "File Menu",
            can_cancel=True, modeless=True, call_back=handle)

def info_menu(menu, glob):
    def handle(sel):
        if sel == 'Tags':
            edit_tags(menu, glob, handle.info)
        return

    text, dinfo = get_image_info(glob.last_file)
    handle.info = dinfo
    result = menu.dialog(text, 'Info', ('Okay', 'Tags'),
            can_cancel=True, call_back=handle, modeless=True,
            width=menu.info_width)

def get_image_info(filename):
    cmd = os.path.join(os.path.dirname(__file__), 'exiftool')
    date = ('-d', """%d-%b-%Y_%H:%M:%S""")
    results = sp.run((cmd, *date, filename), 
            stdout=sp.PIPE, text=True)

    dinfo = {} 
    sinfo = ''
    for l in results.stdout.split('\n'):
        if l:
            try:
                key, data = l.split(': ')
            except:
                key, data = 'Error', l
            dinfo[key.strip()] = data.strip()

    mx = 50 # max size
    if len(dinfo['File Name']) > mx:
        dinfo['File Name'] = '...' + dinfo['File Name'][-mx:]
    if len(dinfo['Directory']) > mx:
        dinfo['Directory'] = '...' + dinfo['Directory'][-mx:]

    dinfo['Keywords'] = dinfo.get('Keywords', None) or dinfo.pop('tagsList', None)
    outp = {}
    for key in wanted_data.keys():
        if key not in ('tagsList', ):
            sinfo += f'{wanted_data[key]}:  {dinfo.get(key, "_None")}\n'
            outp[wanted_data[key]] = dinfo.get(key, None)
    return sinfo, outp

def edit_tags(menu, glob, info):
    def handle(sel, option):
        menu, glob, info, tags = handle.info
        if option in tags[1:]:
            tags.remove(option)
            info['Tags'] = ' '.join(tags[1:])
            edit_tags(menu, glob, info)
            menu.changed = True
        elif sel == 0:
            #new = menu.input("Enter a new tag", width=glob.render_rect.w*.4)[0]
            new = add_tag(menu, glob)
            if new and ' ' not in new:
                tags.append(new)
                info['Tags'] = ' '.join(tags[1:])
                edit_tags(menu, glob, info)
                menu.changed = True
        elif menu.changed:
            results = menu.dialog('Would you like to update the tags for this file?',
                    "Confirm", ('Yes', 'No'), width=menu.dialog_width)
            if results == 'Yes':
                cmd = os.path.join(os.path.dirname(__file__), 'exiftool')
                tags = info.get('Tags', '')
                if tags:
                    results = sp.run((cmd, glob.last_file, '-overwrite_original',
                        '-Keywords='+tags), stdout=sp.PIPE, text=True)
                    glob.tagged[glob.last_file] = tags.split(' ')
        return

    tags = ['<ADD TAG>']
    if info.get('Tags'):
        tags += [tag.strip(',. ') for tag in info.get('Tags', []).split()]
    handle.info = menu, glob, info, tags
    menu.changed = False

    results = menu.select(tags, "Edit Tags",
            modeless=True, call_back=handle, can_cancel=True)

def add_tag(menu, glob):
    if not glob.tags:
        return menu.input("Enter a new tag", width=menu.dialog_width)[0]
    new = menu.select(['<New Tag>']+glob.tags, "Add a Tag")[1]
    if new == '<New Tag>':
        new = menu.input("Enter a new tag", width=menu.dialog_width)[0]
    return new

def remove_menu(menu, glob):
    def handle(sel):
        def remove(fn):
            g = handle.glob
            g.files.remove(fn)
            g.shuffled.remove(fn)

        if sel == 'Shown':
            remove(glob.last_file)

        elif sel == 'Marked':
            for m in glob.marked:
                if glob.marked[m]:
                    remove(m)
                    glob.marked[m] = False
            glob.marked = {}
    
    handle.glob = glob
    buttons = ('Shown', 'None', 'Marked') if glob.marked else ('Shown', 'None')
    menu.dialog('Remove shown image or all marked images from viewing list?',
            'Remove', buttons, modeless=True, width=menu.dialog_width,
            call_back=handle)

def rename_menu(menu, glob):
    def handle(text, i, button):
        g = handle.glob
        path, fn = os.path.split(g.last_file)
        name, ext = os.path.splitext(fn)
        if button == 'Okay':
            target = os.path.join(path, text+ext)
            if text and target != fn and not os.path.exists(target):
                fn = g.last_file
                os.rename(fn, target)
                g.files[g.files.index(fn)] = target
                g.shuffled[g.shuffled.index(fn)] = target
                g.last_file = target
            else:
                handle.glob.next_message = f'"{target}" not valid', 6


    name, ext = os.path.splitext(os.path.split(glob.last_file)[1])
    handle.glob = glob
    menu.input('Rename Image', ('Okay', 'Cancel'),
            default_text='', modeless=True, call_back=handle,
            can_cancel=True, width=menu.info_width)

def delete_menu(menu, glob):
    def handle(sel):
        def remove(fn):
            g = handle.glob
            g.files.remove(fn)
            g.shuffled.remove(fn)
            os.remove(fn)

        if sel == 'Shown':
            remove(glob.last_file)

        elif sel == 'Marked':
            for m in glob.marked:
                if glob.marked[m]:
                    remove(m)
                    glob.marked[m] = False
            glob.marked = {}
    
    handle.glob = glob
    buttons = ('Shown', 'None', 'Marked') if glob.marked else ('Shown', 'None')
    menu.dialog('Delete shown image or all marked images from disk?\n'+
            'Warning this action cannot be reversed!\n',
            'Delete', buttons, modeless=True, width=menu.dialog_width,
            call_back=handle)

def option_menu(menu, glob):
    def handle(key, sel, options):
        if sel == 'Okay':
            if (options['screen']['value'] == 'On') != glob.fullscreen:
                menu.return_values['toggle_fullscreen'] = True
            if int(options['folders']['selected']) != glob.subfolders:
                glob.subfolders = not glob.subfolders
                menu.return_values['scan'] = glob.path
        elif key == 'crawl':
            menu.return_values['scan'] = os.path.dirname(glob.last_file)
        elif key == 'scan':
            get_all_tags(glob)
        elif key == 'filter':
            filter_menu(menu, glob)
            return
        glob.delay = options['speed']['value']

    screen = 0 if glob.fullscreen else 1
    folders = 1 if glob.subfolders else 0
    options = dict(
        screen=dict(type='OPTION', options=('On', 'Off'),
                pre='Fullscreen: ', post='', selected=screen),
        folders=dict(type='OPTION', options=('Off', 'On'),
                pre='Subfolders: ', post='', selected=folders),
        crawl=('Crawl Image Folder',),
        filter=('Filter Images',),
        scan=('Scan for Tags',),
        sp1= dict(type='SPACER', amount=0.3),
        lab1='Slideshow Delay',
        speed=dict( type='SLIDER',
                min=0, max=9, step=1, value=glob.delay))
    if glob.gridview: options.pop('grid')

    menu.options(options, 'Options',
            modeless=True, call_back=handle, can_cancel=True)

def filter_menu(menu, glob):
    def handle(sel, option):
        from random import shuffle
        files = []

        if sel == 0:
            text, _, confirm = menu.input('Enter Search Term',
                ('Okay', 'Cancel'), menu.dialog_width,
                can_cancel=True)
            if confirm != 'Okay':
                return
            text = text.lower()
            for f in glob.files:
                if f.lower().find(text) >= 0:
                    files.append(f)
            if not files:
                glob.next_message = 'No matches found', 3
                return
        elif option in glob.tags:
            for fn, tags in glob.tagged.items():
                if option in tags:
                    files.append(fn)
        else:
            return

        menu.return_values['next'] = True  
        files.sort(key=lambda s: s.lower())
        glob.files = list(files)
        shuffle(files)
        glob.shuffled = files


    menu.select(['<-Other->'] + glob.tags, 'Filter Tag',
            modeless=True, call_back=handle, can_cancel=True)

def get_all_tags(glob):
    import time
    workers = 10
    path = glob.path
    screen = glob.screen
    target, screen.target = screen.target, None
    screen.present()
    w, h = glob.render_rect.size
    full_rect = pg.Rect(0,0,w//3, h//20)
    full_rect.center = glob.render_rect.center
    screen.fill_rect(full_rect.inflate(20,20))
    screen.draw_color = (255, 255, 255, 255)
    screen.fill_rect(full_rect.inflate(10,10))
    screen.draw_color = (0,0,0,255)
    screen.fill_rect(full_rect)
    screen.draw_color = (255, 255, 255, 255)
    full_rect.w, max_width = 1, full_rect.w
    drawinfo = screen, full_rect, max_width

    print('scanning for tags', end='', flush=True)
    st = time.time()
    results = get_tags(path, workers, drawinfo)
    tag_data, tag_list = process_tags(results)
    print(f'\n{len(results)} images with {workers} workers: {int((time.time() - st)*1000)}ms')
    screen.target = target 


def get_tags(path, workers, drawinfo):
    from subprocess import Popen, PIPE
    import time, os, sys

    types = ('.jpg', '.png', '.tif', '.gif', '.bmp')
    files = [path+fn for fn in os.listdir(path) if fn[-4:].lower() in types]
    cmd = os.path.join(os.path.dirname(__file__), 'exiftool')
    params = cmd, '-Keywords', '-tagsList', '-S', '-f'
    total = len(files)
    count = min(workers, total)
    procs = [
        (Popen((*params, f), stdout=PIPE, stderr=PIPE), f) for f in files[:count] ]
    if len(files) > len(procs):
        files = files[workers:]

    screen, rect, wi = drawinfo 
    finished = 0
    results = []
    while procs:
        for proc, fn in procs:
            retcode = proc.poll()
            if retcode is not None: # Process finished.
                finished += 1
                sys.stdout.write('.')
                sys.stdout.flush()
                results.append((fn, proc.communicate()[0]))
                procs.remove((proc, fn))
                if files:
                    f = files.pop()
                    procs.append((Popen((*params, f), stdout=PIPE, stderr=PIPE), f))
                break
        else: # No process is done, wait a bit and check again.
            am = (finished+1) / total
            rect.w = wi * am
            screen.fill_rect(rect)
            screen.present()
            time.sleep(.1)
            continue
    return results

def process_tags(results):
    processed = {}
    full_tags = []
    for fn, r in results:
        try:
            key, tag, *_ = r.decode().split('\n')
            key = key.split(': ')[1]
            tag = tag.split(': ')[1]
        except:
            continue
        tags = []
        if key != '-':
            tags = key.split(' ')
        elif tag != '-':
            tags = tag.split(' ')
        if tags:
            processed[fn] = tags
            print(f'{fn} - {tags}')
            full_tags += tags
    return processed, sorted(list(set(full_tags)))

def write_tags(info, tags, path):
    with open(os.path.join(path, 'tags.txt'), 'w') as outp:
        print(' '.join(tags), file=outp)
        for fn, tags in info.items():
            print('{}::={}'.format(
                os.path.relpath(fn, path),
                " ".join(tags)), file=outp)

def browse_menu(menu, glob):
    def handle(path):
        menu.return_values['scan'] = path

    path = os.path.dirname(glob.last_file)
    menu.file_selector(path, allow='folder', call_back=handle)

def copy_selector(menu, glob, move=False):
    def handle(dest):
        if dest:
            copy_menu(*handle.info, dest, move)

    handle.info = menu, glob
    menu.file_selector(
            os.path.dirname(glob.last_file),
            'both', 'folder', handle, True)

def copy_menu(menu, glob, dest, move):
    from shutil import copy, move as mv
    def handle(sel):
        which = 'moved' if move else 'copied'
        command = mv if move else copy
        if sel == 'Shown':
            command(glob.last_file, dest)
            print(f'{which} {glob.last_file} to {dest}')

        elif sel == 'Marked':
            for f in glob.marked:
                command(f, dest)
                print(f'{which} {f} to {dest}')

    which = 'Move' if move else 'Copy'
    buttons = ('Shown', 'None', 'Marked') if glob.marked else ('Shown', 'None')
    menu.dialog(f'{which} shown file or marked files to target?\n{dest}',
            which, buttons, modeless=True, width=menu.dialog_width,
            call_back=handle)

