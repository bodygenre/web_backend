from flask import jsonify, request

import urllib
import requests
import re


def register(app):

    @app.route('/imdb_info')
    def imdb_info():
        q = request.args.get('q')
        url = f"https://v3.sg.media-imdb.com/suggestion/titles/x/{urllib.parse.quote(q)}.json"
        r = requests.get(url).json()
        d = r['d'][0]
        movie_id = d['id']
        movie_title = d['l']
        year = d['y']
        imgurl = d['i']['imageUrl']
        movie_url = f"https://www.imdb.com/title/{movie_id}/"
        
        r2 = requests.get(movie_url, headers={"User-Agent": "chrome"})

        rating = None
        for line in r2.iter_lines():
          line = line.decode("utf-8")
          if "ratingValue" in line:
            line = line.split("ratingValue\":")[1][0:50]
            rating = float(line.split("}")[0])
            break
        
        return jsonify({ "movie_title": movie_title, "rating": rating, "year": year, "image": imgurl, "movie_id": movie_id })



