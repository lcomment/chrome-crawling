import os
from urllib.request import urlretrieve


def save_image(name, url):
    if not os.path.isdir('./image'):
        folder = './image'

    urlretrieve(url, f'./image/{name}.png')