from quart import jsonify, request
from urllib.parse import unquote
import requests
from modules import http_client
import urllib
import base64
import json
import asyncio


async def dosearch(tracker, q, minseeds=2):
    print("query:", tracker, q)
    try:
        res = await http_client.get("https://bodygen.re:8081/search/" + tracker + "/" + urllib.parse.quote(q))
        res = json.loads(res)
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
        #http_client.get('https://bodygen.re:8081/add_torrent/' + h.decode('utf-8'))
        return { "success": True, "torrent_name": f"{chosen['name']} - ({chosen['leechers']} leech / {chosen['seeders']} seed) - {int(int(chosen['size'])/1073741824*100)/100}gb" }
        #return jsonify({ "success": True, "torrent_name": f"{chosen['name']} - ({chosen['leechers']} leech / {chosen['seeders']} seed) - {int(int(chosen['size'])/1073741824*100)/100}gb" })

    return None

async def _getbest(query):
    # search for results
    # find one with filesize > 1g
    # choose the one with the most seeds
    
    # try with 1080p first
    # try with bluray if 1080p doesnt work
    # try with base query last

    with open("logs/searches", "a+") as f:
        f.write(query+"\n")

    async def test_in_order(tracker, query, minseeds=2):
        a = await dosearch(tracker, query + " 1080p")
        if a: return a
        a = await dosearch(tracker, query + " bluray")
        if a: return a
        a = await dosearch(tracker, query)
        if a: return a
        return None

    #for tracker in ["rarbg", "iptorrents"]:
    trackers = ["thepiratebay", "rarbg", "iptorrents"]
    jobs = [ test_in_order(tracker, query) for tracker in trackers ]
    res = await asyncio.gather(*jobs)
    for a in res:
        if a is not None:
            return a
    jobs = [ test_in_order(tracker, query, minseeds=1) for tracker in trackers ]
    res = await asyncio.gather(*jobs)
    for a in res:
        if a is not None:
            return a

    # TODO: refactor ^^^ to use asyncio.gather to parallelize the requests a bit

    # if a search failed, log it to failed log
    with open("logs/searches.failed", "a+") as f:
        f.write(query+"\n")

    return { "success": False }

 


def register(app):

    @app.route("/getbest/<query>")
    async def getbest(query):
        return jsonify(await _getbest(query))

    @app.route("/getbest_twilio", methods=['GET','POST'])
    async def getbest_twilio():
        query = request.form.get("Body", None)
        a = await _getbest(query)
        if a['success'] == False:
            return '<?xml version="1.0" encoding="UTF-8"?><Response><Message>something went wrong, sorry. didnt download.</Message></Response>' 
        else:
            return '<?xml version="1.0" encoding="UTF-8"?><Response><Message>Queued: ' + a['torrent_name'] + '</Message></Response>' 
    
