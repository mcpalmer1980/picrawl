
from setuptools import setup

import os
def package_files(root, sub):
    paths = []
    directory = os.path.join(root,sub)
    print(directory)
    for (path, directories, filenames) in os.walk(directory):
        for filename in directories:
            paths.append(os.path.join(path, filename, '*')[len(root):])
            print(paths[-1])
    return paths

def file_fine():
    # Add all folders contain files or other sub directories 
    pathlist=['templates/','scripts/']
    data={}        
    for path in pathlist:
        for root,d_names,f_names in os.walk(path,topdown=True, onerror=None, followlinks=False):
            data[root]=list()
            for f in f_names:
                data[root].append(os.path.join(root, f))                
    
    fn=[(k,v) for k,v in data.items()]    
    return fn

package_data = dict(
        picrawl=['icon.png','nine.png', 'font.ttf', 'exiftool'] + package_files('picrawl/', 'lib'),
        renderpyg=['data/*'])
print(package_data)

def setup2(*args, **kwags):
    return

setup(
    name='PicCrawler',
    author='Chris Palmieri',
    description='Simple image slideshow that recursively shuffles a folder',
    version='0.1',
    py_modules=['picrawl', 'renderpyg', 'menu'],
    packages=['picrawl', 'renderpyg'],
    package_dir={'picrawl': 'picrawl/',
            'renderpyg': 'renderpyg/'},
    package_data=package_data,

    install_requires=[
        'pygame', 'pyperclip',
    ],
    entry_points={
        'console_scripts': [
            'picrawl=picrawl:main']},
)

