import asyncio
from flask import Flask, abort, request, jsonify, render_template, send_file
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
import datetime
from datetime import timedelta, timezone
from bs4 import BeautifulSoup
#from imdb import IMDb
import calendar_playlist

import socket
import cachetools
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import hashlib
import base64
from copy import deepcopy

import io

from dalle import gen_image
import asyncio

loop = asyncio.get_event_loop()
app = Flask(__name__, static_url_path='/public', static_folder='public', template_folder="templates")
CORS(app)

vlc_cache = cachetools.TTLCache(maxsize=1, ttl=1)
last_query = "shrek 2"

letterboxd_cache = cachetools.TTLCache(maxsize=1, ttl=5)
#letterboxd_cache = []
#letterboxd_seen = {}
last_page_1 = 1
last_page_2 = 1


@app.route('/craiyon')
def dalle():
    q = request.args.get('q')
    print("dalle", q)
    img = gen_image(q)
    fimg = io.BytesIO(img)
    return send_file(fimg, mimetype="image/png", download_name=f"{q}.png")


@app.route('/search/<tracker>/<query>')
def search(tracker, query):
    global last_query
    last_query = unquote(query)
    res = []
    xml = requests.get("http://tetsuharu.ap6r0.bysh.me:48868/api/v2.0/indexers/" + tracker + "/results/torznab/?apikey=c64fc140777fbae6449cc736dc539f1d&q=" + query).content
    rss = ET.XML(xml)
    items = rss.find('channel').findall('item')
    for item in items:
        magnet = item.find('link').text
        size = item.find('size').text
        title = item.find('title').text
        seeds = 0
        peers = 0
        for e in item:
            n = e.get('name')
            if n == 'seeders': seeds = int(e.get('value'))
            if n == 'peers': peers = int(e.get('value'))
        if seeds > 0:
            res.append({
                "name": title,
                "leechers": peers-seeds,
                "seeders": seeds,
                "size": size,
                "info_hash": magnet
            })

    return jsonify(res)

@app.route('/last_search')
def last_search():
    global last_query
    return jsonify({"last_query": last_query})

@app.route('/add_torrent/<info_hash>')
def add_torrent(info_hash):
    info_hash = base64.b64decode(bytes(info_hash, 'utf-8'))
    fname = hashlib.md5(info_hash).hexdigest()
    info_hash = info_hash.decode('utf-8')
    print("decoded info_hash: ", info_hash)
    data = ""
    if info_hash.startswith("http"):
        print("getting http info hash: ", info_hash)
        data = requests.get(info_hash).content
        print("getting http info hash: ", data)
        f = open('/home/hd1/tetsuharu/torrents/watch/' + fname + '_http.torrent', 'wb')
        print("writing to .torrent file: ", data)
        f.write(data)
        f.close()
        return "success"
    elif info_hash.startswith("magnet:"):
        fname += "_magnet"
        data = info_hash
    else:
        print("getting magnet info hash by building it: ", info_hash)
        fname += "_builtmagnet"
        data = "magnet:?xt=urn:btih:" + info_hash + "&dn=dummy_dn&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce"

    f = open('/home/hd1/tetsuharu/torrents/watch/' + fname + '.magnet', 'w')
    print("writing to .magnet file: ", data)
    f.write(data)
    f.close()
    return "success"

@app.route('/search_existing/<terms>')
def search_existing(terms):
    #files = glob.glob('/home/hd1/tetsuharu/media/B Movies/**') + glob.glob('/home/hd1/tetsuharu/media/Movies/**') + glob.glob('/home/hd1/tetsuharu/media/TV Shows/**')
    files = glob.glob('/home/hd1/tetsuharu/media/B Movies/*/*') + glob.glob('/home/hd1/tetsuharu/media/Movies/*/*') + glob.glob('/home/hd1/tetsuharu/media/TV Shows/**/**/*')
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
    if not (to.startswith("B Movies/") or to.startswith("Movies/") or to.startswith("TV Shows/")):
        return "to does not begin with B Movies or Movies"
    if not (fro.startswith("B Movies/") or fro.startswith("Movies/") or fro.startswith("TV Shows/")):
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
    time.sleep(5)
    os.system('nohup /home/hd1/tetsuharu/bin/stream_to_owncast "/home/hd1/tetsuharu/media/' + path + '" &')
    return ""

@app.route('/get_active_torrents')
def get_active_torrents():
    return "{}"
    with requests.Session() as s:
        s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "auth.login", "id": "asdff", "params": ["friendship"] })
        #fields = ["name","download_payload_rate","eta","hash","is_finished","max_download_speed","message","paused","progress","ratio","seeds_peers_ratio","state","total_done","total_payload_download","total_size","upload_payload_rate"]
        #fields = ['name', 'comment', 'hash', 'save_path']
        fields = [ "name", "hash", "progress", "download_payload_rate", "eta", "state" ]
        data = s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "webapi.get_torrents", "id": "asdff", "params": [None, fields] }).json()
        # only include records that have non-0 progress?
        # only include records that have non-0 download_payload_rate ?
        print(data)
        data = [ t for t in data['result']['torrents'] if t['download_payload_rate'] > 0 or t['state'] == 'Seeding' ]
        #print(json.dumps(data, indent=4))
        return jsonify(data)

@app.route('/get_old_torrents')
def get_old_torrents():
    with requests.Session() as s:
        s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "auth.login", "id": "asdff", "params": ["friendship"] })
        #fields = ["name","download_payload_rate","eta","hash","is_finished","max_download_speed","message","paused","progress","ratio","seeds_peers_ratio","state","total_done","total_payload_download","total_size","upload_payload_rate"]
        #fields = ['name', 'comment', 'hash', 'save_path']
        fields = [ "name", "hash", "progress", "download_payload_rate", "eta", "state" ]
        data = s.post("http://tetsuharu.ap6r0.bysh.me:3385/json", json={"method": "webapi.get_torrents", "id": "asdff", "params": [None, fields] }).json()
        # only include records that have non-0 progress?
        # only include records that have non-0 download_payload_rate ?
        for t in data['result']['torrents'][:10]:
            print(t);
        data = [ t for t in data['result']['torrents'] if t['download_payload_rate'] > 0 or t['state'] == 'Seeding' ]
        #print(json.dumps(data, indent=4))
        return jsonify(data)



@app.route('/vlc/<action>')
def vlc_action(action):
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

@app.route('/make_download_link')
def make_download_link():
  path = request.args.get('path')
  if not re.match(r"^(B Movies|Movies|TV Shows)/.+", path):
    return

  with requests.Session() as s:
    login = s.post('http://tetsuharu.ap6r0.bysh.me/filebrowser/api/login', data='{"username":"tetsuharu","password":"friendship"}', headers={ "Accept-Encoding": "gzip, deflate" })
    link = s.post('http://tetsuharu.ap6r0.bysh.me/filebrowser/api/share/media/'+path+'?expires=48&unit=hours', headers={ "X-Auth": login.content })
    return jsonify(link.json())

@app.route('/post_vlc_status')
def post_vlc_status():
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
def get_current_movie():
    return open("current_movie_url").read().strip()


def getLetterboxdPage(url):
    print(url)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    #deets = soup.find_all('li', 'film-detail')
    pagination = soup.find('div', 'pagination')
    if pagination is None:
        lastpag = 0
    else:
        lastpag = int(pagination.find_all('li')[-1].text)
    ret = { "movies": [], "last_page": lastpag }
    for i in soup.find_all('div', 'film-detail-content'):
        moviename = i.find('a').text
        meta = ""
        try:
            meta = i.find('small', 'metadata').text
        except:
            pass
        ret['movies'].append("{} ({})".format(moviename, meta))
    return ret

def addMovies(movies):
    for m in movies:
        if m in letterboxd_seen:
            return False
        letterboxd_cache.append(m)
        letterboxd_seen[m] = True
    return True

letterboxd_pages = []
#def addLetterboxPage(

@app.route("/nilbog_seen")
def nilbog_seen():
    # get last page
    # add any missing movies
    # if the last page number has changed, add those
    if 'seen' in letterboxd_cache:
        movies = letterboxd_cache['seen']
    else:
        movies = []

        urlfmt2 = "https://letterboxd.com/comrie/list/nilbog-2-the-race-to-2000/detail/by/added/page/{}/"
        page = getLetterboxdPage(urlfmt2.format('1'))
        movies += page['movies']
        for i in range(2,page['last_page']+1):
            page = getLetterboxdPage(urlfmt2.format(str(i)))
            movies += page['movies']

        urlfmt = "https://letterboxd.com/comrie/list/nilbog-1-the-beginning/detail/by/added/page/{}/"
        page = getLetterboxdPage(urlfmt.format('1'))
        movies += page['movies']
        for i in range(2,page['last_page']+1):
            print(i)
            page = getLetterboxdPage(urlfmt.format(str(i)))
            movies += page['movies']

        letterboxd_cache['seen'] = movies
    
    #movies = letterboxd_cache[::-1]

    goal = 2000

    td = datetime.datetime(2021,12,31,23,59) - datetime.datetime.now()
    days_left = td.total_seconds()/60/60/24
    movies_per_day = float(goal-len(movies))/days_left
    xmas_td = datetime.datetime(2021,12,25,00,00) - datetime.datetime.now()
    xmas_days_left = xmas_td.total_seconds()/60/60/24
    movies_per_day_xmas = float(goal-len(movies))/xmas_days_left

    return render_template("nilbog_seen.html", movies=movies, movies_per_day=movies_per_day, xmas=movies_per_day_xmas, days_left=days_left, xmas_days_left=xmas_days_left)

@app.route("/wordle")
def wordle():
    return ""
    return render_template("wordle.html")


@app.route("/getbest/<query>")
def getbest(query):
    # search for results
    # find one with filesize > 1g
    # choose the one with the most seeds
    
    # try with 1080p first
    # try with bluray if 1080p doesnt work
    # try with base query last

    with open("logs/searches", "a+") as f:
        f.write(query+"\n")

    def dosearch(tracker, q, minseeds=2):
        print("query:", tracker, q)
        try:
            res = requests.get("https://bodygen.re:8081/search/" + tracker + "/" + urllib.parse.quote(q), verify=False).json()
        except Exception as e:
            print("Search request broke:", e)
            return None
        chosen = None
        maxseeders = 0
        minsize = 500000000
        for r in res:
            print('info hash:', r['info_hash'])
            if r['info_hash'].startswith('http'): continue
            if int(r['size']) < minsize: continue
            if int(r['seeders']) < minseeds: continue
            if chosen is None or int(r['seeders']) > int(chosen['seeders']):
                chosen = r
                print("switched chosen")

        if chosen is None:
            for r in res:
                if int(r['size']) < minsize: continue
                if int(r['seeders']) < minseeds: continue
                if chosen is None or int(r['seeders']) > int(chosen['seeders']):
                    chosen = r

        if chosen is not None:
            print(1, chosen)
            h = chosen['info_hash']
            if type(h) is str:
                h = bytes(h, 'utf-8')
            h = base64.b64encode(h)
            requests.get('https://bodygen.re:8081/add_torrent/' + h.decode('utf-8'), verify=False)
            return jsonify({ "success": True, "torrent_name": f"{chosen['name']} - ({chosen['leechers']} leech / {chosen['seeders']} seed) - {int(int(chosen['size'])/1073741824*100)/100}gb" })

        return None

    #for tracker in ["rarbg", "iptorrents"]:
    for tracker in ["thepiratebay", "rarbg", "iptorrents"]:
        a = dosearch(tracker, query + " 1080p")
        if a: return a
        a = dosearch(tracker, query + " bluray")
        if a: return a
        a = dosearch(tracker, query)
        if a: return a
        a = dosearch(tracker, query + " 1080p", minseeds=1)
        if a: return a
        a = dosearch(tracker, query + " bluray", minseeds=1)
        if a: return a
        a = dosearch(tracker, query, minseeds=1)
        if a: return a

    # if a search failed, log it to failed log
    with open("logs/searches.failed", "a+") as f:
        f.write(query+"\n")

    return jsonify({ "success": False })


@app.route("/current_calendar_movie")
def current_calendar_movie():
    start, ev = calendar_playlist.get_current_event()
    if ev is None:
        return jsonify({ "movie_name": None, "offset": 0 })
    else:
        return jsonify({ "movie_name": ev['summary'], "offset": (datetime.datetime.now(datetime.timezone.utc)-start).seconds })


@app.route("/current_calendar_movie_names")
def current_calendar_movie_names():
    names = calendar_playlist.get_movie_names_between(
        datetime.datetime.now(timezone.utc),
        datetime.datetime.now(timezone.utc) + timedelta(days=8)
    )
    return jsonify({ "names": names })


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8081)
    app.run(host='0.0.0.0', port=8081, ssl_context=('bodygen_re.crt', 'bodygen_re.key'))


