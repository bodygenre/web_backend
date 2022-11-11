from flask import jsonify
from urllib.parse import unquote
import requests
import urllib
import base64

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



def register(app):

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
    
    
    
