from subprocess import Popen, PIPE
import time, os, sys

def get_tags(path, workers):
    types = ('.jpg', '.png', '.tif', '.gif', '.bmp')
    files = [path+fn for fn in os.listdir(path) if fn[-4:].lower() in types]
    cmd = os.path.join(os.path.dirname(__file__), 'exiftool')
    params = cmd, '-Keywords', '-tagsList', '-S', '-f'
    count = min(workers, len(files))
    procs = [
        (Popen((*params, f), stdout=PIPE, stderr=PIPE), f) for f in files[:count] ]
    if len(files) > len(procs):
        files = files[workers:]

    results = []
    while procs:
        for proc, fn in procs:
            retcode = proc.poll()
            if retcode is not None: # Process finished.
                sys.stdout.write('.')
                sys.stdout.flush()
                results.append((fn, proc.communicate()[0]))
                procs.remove((proc, fn))
                if files:
                    f = files.pop()
                    procs.append((Popen((*params, f), stdout=PIPE, stderr=PIPE), f))
                break
        else: # No process is done, wait a bit and check again.
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

path = '/tmp/ramdisk/images/'

for workers in (10,):
    st = time.time()
    results = get_tags(path, workers)
    info, full = process_tags(results)
    print('full: ', full)
    print(f'\n{len(results)} images with {workers} workers: {time.time() - st}ms')

with open(os.path.join(path, 'tags.txt'), 'w') as outp:
    print(' '.join(full), file=outp)
    for fn, tags in info.items():
        print('{}::={}'.format(
            os.path.relpath(fn, path),
            " ".join(tags)), file=outp)