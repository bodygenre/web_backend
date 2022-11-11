from flask import jsonify

import requests
import datetime
from bs4 import BeautifulSoup


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



def register(app):
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




