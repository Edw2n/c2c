import urllib.request
import pathlib

url = "https://i.imgur.com/ExdKOOz.png"
id =1
FILE_NAME = None
# urllib.request.urlretrieve(url, FILE_NAME)

def save_img(relative_path,url,id):
    urllib.request.urlretrieve(url,p_dir/f'{id}.jpg')

p_dir = pathlib.Path('images/')
urllib.request.urlretrieve(url,p_dir/f'{id}.jpg')
