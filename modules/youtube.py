from flask import jsonify

import cachetools
import subprocess

from apiclient.discovery import build

k = open('youtube_token').read().strip()
youtube = build('youtube','v3',developerKey = k)



def register(app):

    @app.route('/youtube/search/<youtube_term>')
    def youtubesearch(youtube_term):
        r = youtube.search().list(q=youtube_term, part='snippet', type='video', maxResults=10).execute()
        return jsonify(r)

    @app.route('/youtube/download/<youtube_id>')
    def youtubedownload(youtube_id):
        subprocess.Popen(["/home/hd1/tetsuharu/bin/youdown", 'https://www.youtube.com/watch?v=' + youtube_id])
        return 'hello'

