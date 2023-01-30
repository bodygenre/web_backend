from quart import jsonify
import requests
import hashlib
import base64
import cachetools
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from modules import http_client


letterboxd_cache = cachetools.TTLCache(maxsize=1, ttl=5)
#letterboxd_cache = []
#letterboxd_seen = {}
last_page_1 = 1
last_page_2 = 1


def register(app):
    
    @app.route('/s/<provider>/<search>')
    async def asdf(provider,search):
        print(provider,search)
        return ""

    @app.route('/search/<tracker>/<query>')
    async def search(tracker, query):
        print("searching: ", tracker, query)
        res = []
        if tracker == 'iptorrents':
            return jsonify(res)
        xml = await http_client.get("http://tetsuharu.ap6r0.bysh.me:48868/api/v2.0/indexers/" + tracker + "/results/torznab/?apikey=c64fc140777fbae6449cc736dc539f1d&q=" + query)
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

    @app.route('/add_torrent/<info_hash>')
    async def add_torrent(info_hash):
        info_hash = base64.b64decode(bytes(info_hash, 'utf-8'))
        fname = hashlib.md5(info_hash).hexdigest()
        info_hash = info_hash.decode('utf-8')
        print("decoded info_hash: ", info_hash)
        data = ""
        if info_hash.startswith("http"):
            print("getting http info hash: ", info_hash)
            data = await http_client.get(info_hash)
            print("info hash data: ", data)
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
    
       
    @app.route('/get_active_torrents')
    async def get_active_torrents():
        return jsonify({})
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
    async def get_old_torrents():
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
            return jsonify(data)
    
    
    
    
