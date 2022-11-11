from flask import request, jsonify

import requests
import glob
import re


def register(app):
    
    
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
        
    
    
    @app.route('/make_download_link')
    def make_download_link():
      path = request.args.get('path')
      if not re.match(r"^(B Movies|Movies|TV Shows)/.+", path):
        return
    
      with requests.Session() as s:
        login = s.post('http://tetsuharu.ap6r0.bysh.me/filebrowser/api/login', data='{"username":"tetsuharu","password":"friendship"}', headers={ "Accept-Encoding": "gzip, deflate" })
        link = s.post('http://tetsuharu.ap6r0.bysh.me/filebrowser/api/share/media/'+path+'?expires=48&unit=hours', headers={ "X-Auth": login.content })
        return jsonify(link.json())
    
    
    
