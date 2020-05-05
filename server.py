from flask import Flask
import requests

app = Flask(__name__)

@app.route('/add_torrent/<info_hash>')
def add_torrent(info_hash):
    r = requests.get('http://torcache.net/torrent/' + info_hash + '.torrent')
    f = open('/home/hd2/tetsuharu/torrents/watch/' + info_hash + '.torrent', 'w')
    f.write(r.content)
    f.close()
    return "success"

app.run(host='0.0.0.0', port=8081)
