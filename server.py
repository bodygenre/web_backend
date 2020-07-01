from flask import Flask, abort, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/add_torrent/<info_hash>')
def add_torrent(info_hash):
    url = "magnet:?xt=urn:btih:" + info_hash + "&dn=dummy_dn&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2920%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce"
    f = open('/home/hd1/tetsuharu/torrents/watch/' + info_hash + '.magnet', 'w')
    f.write(url)
    f.close()
    return "success"


app.run(host='0.0.0.0', port=8081)

