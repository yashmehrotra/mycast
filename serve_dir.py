import os
import soldier

from config import MEDIA_PORT

def serve(path):
    if not os.path.exists(path):
        raise Exception("Wrong path provided")

    current_dir = os.getcwd()
    os.chdir(path)
    proc = soldier.run(f'python3 -m http.server {MEDIA_PORT}', background=True)
    os.chdir(current_dir)
    if not proc.is_alive():
        raise Exception(proc.error)

    return proc

def get_dir_listing(path):
    files = os.listdir(path)

    allowed_extenstions = ['mp4', 'mp3', 'mkv']
    files = filter(lambda x: x.split('.')[-1] in allowed_extenstions, files)
    return list(files)

def get_content_type(fname):
    ext = fname.split('.')[-1]
    mapping = {
        'mp4': 'video/mp4',
        'mkv': 'video/x-matroska',
    }
    return mapping.get(ext, mapping['mp4'])
