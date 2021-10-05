from flask import Flask, abort, request, jsonify
from flask_cors import CORS
import requests
import urllib
import os
import re
import glob
import shutil
import subprocess
import time
import json

app = Flask(__name__)
CORS(app)

@app.route('/search/<query>')
def search(query):
    return jsonify(requests.get("https://apibay.org/q.php?q=" + query).json())

@app.route('/add_torrent/<info_hash>')
def add_torrent(info_hash):
    url = "magnet:?xt=urn:btih:" + info_hash + "&dn=dummy_dn&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce"
    f = open('/home/hd1/tetsuharu/torrents/watch/' + info_hash + '.magnet', 'w')
    f.write(url)
    f.close()
    return "success"

@app.route('/search_existing/<terms>')
def search_existing(terms):
    #files = glob.glob('/home/hd1/tetsuharu/media/B Movies/**') + glob.glob('/home/hd1/tetsuharu/media/Movies/**') + glob.glob('/home/hd1/tetsuharu/media/TV Shows/**')
    files = glob.glob('/home/hd1/tetsuharu/media/B Movies/*/*') + glob.glob('/home/hd1/tetsuharu/media/Movies/*/*')
    files = [ f.replace('/home/hd1/tetsuharu/media/','') for f in files if 'Plex Versions' not in f ]
    #files = glob.glob('/home/hd1/tetsuharu/torrents/data/*')
    #files = [ f.replace('/home/hd1/tetsuharu/torrents/data/','') for f in files ]
    terms = re.sub(r"[^a-zA-Z0-9]", ".*", terms)
    matches = [ f for f in files if re.match('^.*'+terms+'.*$', f, re.IGNORECASE) ]
    return jsonify({ 'matches': matches })


@app.route('/move_movie')
def move_movie():
    fro = request.args.get('from')
    to = request.args.get('to')
    if not (to.startswith("B Movies/") or to.startswith("Movies/")):
        return "to does not begin with B Movies or Movies"
    if not (fro.startswith("B Movies/") or fro.startswith("Movies/")):
        return "fro does not begin with B Movies or Movies"
    if '../' in to or '../' in fro:
        return "contais ../, bad"
    if not re.match('^.*/$', to) or not re.match('^.*/$', fro):
        return 'path isnt a directory (must end with /)'
    fro = '/home/hd1/tetsuharu/media/' + fro
    to = '/home/hd1/tetsuharu/media/' + to
    shutil.move(fro, to)
    return ""
    
@app.route('/stream_movie')
def stream_movie():
    path = request.args.get('path')
    path = urllib.parse.unquote(path)
    if '../' in path:
        return "bad path"
    subprocess.Popen(['killall', 'vlc'])
    time.sleep(1)
    os.system('/home/hd1/tetsuharu/bin/stream_to_owncast "/home/hd1/tetsuharu/media/' + path + '" &')
    return ""

@app.route('/get_active_torrents')
def get_active_torrents():
    with requests.Session() as s:
        s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "auth.login", "id": "asdff", "params": ["friendship"] })
        fields = ["name","download_payload_rate","eta","hash","is_finished","max_download_speed","message","paused","progress","ratio","seeds_peers_ratio","state","total_done","total_payload_download","total_size","upload_payload_rate"]
        #fields = ['name', 'comment', 'hash', 'save_path']
        data = s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "webapi.get_torrents", "id": "asdff", "params": [None, fields] }).json()
        #print(json.dumps(data, indent=4))
        return jsonify(data)


#app.run(host='0.0.0.0', port=8081)
app.run(host='0.0.0.0', port=8081, ssl_context=('bodygen_re.crt', 'bodygen_re.key'))

