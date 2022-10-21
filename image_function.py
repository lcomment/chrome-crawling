import os
from urllib.request import urlretrieve


def save_image(name, url, idx):
    folder = './image'
    path = folder
    if not os.path.isdir(folder):
        os.mkdir(folder)
    if not os.path.isdir(folder + '/' + name):
        path += ('/' + name)
        os.mkdir(path)
    urlretrieve(url, f'{path}/{name}{idx}.png')
