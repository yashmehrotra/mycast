from flask import Flask, jsonify, request, render_template
import signal
import pychromecast

import urllib.parse
from config import HOST_PORT, MEDIA_PORT, MEDIA_DIR
from serve_dir import serve, get_dir_listing, get_content_type
import socket

HOST = socket.gethostbyname(socket.gethostname())

p = MEDIA_DIR
proc = serve(p)
def sigint_handler(signum, frame):
    try:
        proc.kill()
    except:
        pass
 
signal.signal(signal.SIGINT, sigint_handler)


app = Flask(__name__)
cast = pychromecast.get_chromecasts()[0]
device = cast.device
media_controller = cast.media_controller

class Media(object):
    def __init__(self, name, state):
        self.name = name
        self.state = state

media_klass = Media('', None)
@app.route('/list')
def list_ep():
    files = get_dir_listing(p)
    return jsonify(files=files)


@app.route('/start')
def start():
    fname = request.args['fname']
    host = f'http://{HOST}:{MEDIA_PORT}'
    endpoint = urllib.parse.urljoin(host, fname)
    print("Endpoint: ", endpoint)
    content_type = get_content_type(fname)
    args = (endpoint, content_type)
    kwargs = {
        'subtitles': fname.replace('mp4', 'vtt').replace(str(MEDIA_PORT), '6667'),
        'subtitles_mime': 'text/vtt',
    }
    media_controller.play_media(*args)
    media_controller.update_status()
    media_controller.enable_subtitle(1)

    # TODO: Add option for subtitle additon, debug why lib not working
    return jsonify(state='start')

@app.route('/get_state')
def get_state():
    return jsonify(state=media_klass.state, name=media_klass.name)

@app.route('/state/<state>')
def handler(state):
    state = state.lower()
    states = ('play', 'pause', 'stop', 'forward', 'backward',
              'volume_up', 'volume_down')
    if state not in states:
        return jsonify(state='Invalid')

    if state == 'play':
        media_klass.state = 'play'
        media_controller.play()

    if state == 'pause':
        media_klass.state = 'pause'
        media_controller.pause()

    if state == 'stop':
        media_klass.state = 'stop'
        media_controller.stop()

    if state == 'volume_up':
        cast.volume_up()

    if state == 'volume_down':
        cast.volume_down()

    if state == 'seek_forward':
        current_time = media_controller.status.adjusted_current_time
        media_controller.seek(current_time + (60 * 2))

    if state == 'seek_backward':
        current_time = media_controller.status.adjusted_current_time
        media_controller.seek(current_time - (60 * 2))

    return jsonify(state=state)


@app.route('/meta')
def hello_world():
    return jsonify(**{
        'device': device.friendly_name,
    })

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=HOST_PORT, debug=True)
