from quart import jsonify

import urllib
import re
import glob
import time
import json

import socket
from urllib.parse import unquote
import cachetools

vlc_cache = cachetools.TTLCache(maxsize=1, ttl=1)


def register(app):

    @app.route('/stream_movie')
    async def stream_movie():
        path = request.args.get('path')
        path = urllib.parse.unquote(path)
        if '../' in path:
            return "bad path"
        subprocess.Popen(['killall', 'vlc'])
        time.sleep(5)
        os.system('nohup /home/hd1/tetsuharu/bin/stream_to_owncast "/home/hd1/tetsuharu/media/' + path + '" &')
        return ""


    @app.route('/vlc/<action>')
    async def vlc_action(action):
      if action == 'current':
        if 'vlc/current' in vlc_cache:
          return vlc_cache['vlc/current']
    
        currTitle ="No video" 
        scrubPos = 0
        videoLen = 0
        try:
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 44500))
      
            s.send(b"get_title\n")
            s.send(b"get_time\n")
            s.send(b"get_length\n")
            time.sleep(0.03)
            lines = s.recv(1024).decode().split("\n")
            curr = lines[2].strip().replace("> /home/hd1/tetsuharu/media/", "")
            scrubPos = int(lines[3].strip())
            videoLen = int(lines[4].replace(">","").strip())
      
            vlc_cache['vlc/current'] = { "current_title": curr, "current_time": scrubPos, "video_length": videoLen }
            return jsonify(vlc_cache['vlc/current'])
        except:
          return "" #jsonify({"current_title":"no video", "current_time": 0, "video_length": 0})
    
    
    @app.route('/post_vlc_status')
    async def post_vlc_status():
        movie_file = request.args.get('file')
        movie_file = urllib.parse.unquote(movie_file).lower()
        current_movie_file = movie_file
        files = glob.glob('/home/hd1/tetsuharu/media/B Movies/*/*') + glob.glob('/home/hd1/tetsuharu/media/Movies/*/*') + glob.glob('/home/hd1/tetsuharu/media/TV Shows/**/**/*')
        files = [ f.replace('/home/hd1/tetsuharu/media/','') for f in files if 'Plex Versions' not in f ]
        ex = [ f for f in files if movie_file in f.lower() ]
        if len(ex) > 0:
            name = re.sub("^[^/]+/", "", re.sub("/[^/]+$", "", ex[0]))
            m = IMDb()
            mov = m.search_movie(name)[0]
            url = f"https://www.imdb.com/title/tt{mov.getID()}/"
            with open("current_movie_url", "w") as f:
                f.write(url)
            return url
        return ""
    
    @app.route("/get_current_movie")
    async def get_current_movie():
        return open("current_movie_url").read().strip()
    
    
    
