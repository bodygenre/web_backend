import requests
import json
from datetime import datetime, timezone, timedelta
from dateutil.rrule import rrulestr
from dateutil.parser import parse
import pytz
from copy import deepcopy


   

def get_events_at(current_time, events, recurring, cancellations, reschedules):
    current_events = []

    for ev in events:
        if 'date' in ev['start']: continue
        start = parse(ev['start']['dateTime'])
        end = parse(ev['end']['dateTime'])
        summary = ev['summary']
        ev['startDate'] = start.astimezone(pytz.utc)
        ev['endDate'] = end.astimezone(pytz.utc)
        if current_time > start and current_time < end:
            current_events.append(ev)

    for s in reschedules:
        print('testing reschedules for', s['start']['dateTime'], s['originalStartTime']['dateTime'], s['summary'])

    for rec in recurring:
        if 'date' in rec['start']:
            start = parse(rec['start']['date'])
            end = parse(rec['end']['date'])
        else:
            start = parse(rec['start']['dateTime'])
            end = parse(rec['end']['dateTime'])
        duration = end - start

        rule = rrulestr("DTSTART:" + rec['start']['dateTime'] + "\n" + rec['recurrence'][0])
        next_start = start
        next_end = end
        while next_start < current_time and next_end < current_time:
            start = next_start
            end = next_end
            next_start = rule.after(start)
            next_end = next_start + duration

        rec['startDate'] = next_start.astimezone(pytz.utc)
        rec['endDate'] = next_end.astimezone(pytz.utc)

        if current_time > next_start and current_time < next_end:
            not_cancelled = True
            for c in cancellations:
                orgstart = parse(c['originalStartTime']['dateTime'])
                if rec['id'] == c['recurringEventId'] and next_start == orgstart:
                    not_cancelled = False
                    break
            print(len(reschedules))
            for s in reschedules:
                print(s['recurringEventId'], rec['id'])
                if s['recurringEventId'] == rec['id'] and parse(s['originalStartTime']['dateTime']) == next_start:
                    print("rescheduling ", rec['summary'], s['summary'])
                    s['startDate'] = parse(s['start']['dateTime']).astimezone(pytz.utc)
                    s['endDate'] = parse(s['end']['dateTime']).astimezone(pytz.utc)
                    rec = s
            if not_cancelled:
                current_events.append(rec)
            
    return current_events


def get_events_between(time_a, time_b):
    print('getting events between {} and {}'.format(time_a, time_b))

    events, recurring, cancellations, reschedules = get_calendar_parts()

    current_events = []

    for ev in events:
        if 'date' in ev['start']:
            continue
        start = parse(ev['start']['dateTime'])
        end = parse(ev['end']['dateTime'])
        summary = ev['summary']
        ev['startDate'] = start.astimezone(pytz.utc)
        ev['endDate'] = end.astimezone(pytz.utc)
        if start > time_a and end < time_b:
            current_events.append(ev)

    print("asdf")
    print(recurring)
    for rec in recurring:
        print(rec['summary'])
        if 'Rock and the Alien' == rec['summary']:
            print("doing RatA")
        if 'date' in rec['start']:
            start = parse(rec['start']['date'])
            end = parse(rec['end']['date'])
        else:
            start = parse(rec['start']['dateTime'])
            end = parse(rec['end']['dateTime'])
        duration = end - start

        rule = rrulestr("DTSTART:" + rec['start']['dateTime'] + "\n" + rec['recurrence'][0])
        next_start = start
        next_end = end
        while next_start < time_a:
            start = next_start
            end = next_end
            next_start = rule.after(start)
            next_end = next_start + duration
        
        next_start = start
        next_end = end
        while next_start < time_b - timedelta(hours=1):
            crec = deepcopy(rec)
            crec['startDate'] = next_start.astimezone(pytz.utc)
            crec['endDate'] = next_end.astimezone(pytz.utc)
    
            not_cancelled = True
            for c in cancellations:
                orgstart = parse(c['originalStartTime']['dateTime'])
                if crec['id'] == c['recurringEventId'] and next_start == orgstart:
                    not_cancelled = False
            for s in reschedules:
                if s['originalStartTime']['dateTime'] == rec['start']['dateTime']:
                    s['startDate'] = parse(s['start']['dateTime']).astimezone(pytz.utc)
                    s['endDate'] = parse(s['end']['dateTime']).astimezone(pytz.utc)
                    duration = s['endDate'] - s['startDate']
                    rec = s
            if not_cancelled:
                current_events.append(crec)

            rescheduled = False

            start = next_start
            end = next_end
            next_start = rule.after(start)
            next_end = next_start + duration

            
    return current_events


def get_movie_names_between(time_a, time_b):
    events = get_events_between(time_a, time_b)
    movies = set()
    for ev in events:
        movies.add(ev['summary'])
    return list(movies)


def get_calendar_parts():
    response = requests.get('https://www.googleapis.com/calendar/v3/calendars/f9g8hacuqf2qt8cbblsor1h14o%40group.calendar.google.com/events?key=AIzaSyDDPHXMEURUMKpWMn4E8eQRCFs6LOCTgiA')
    items = response.json()['items']
    
    recurring = []
    events = []
    cancellations = []
    reschedules = []
    for item in items:
        if 'summary' in item and item['summary'].startswith('#'):
            continue
        if 'summary' in item and item['summary'] == 'Rock and the Alien' and 'originalStartTime' in item:
            print('found rock and the alien')
            print(item['start']['dateTime'], item['summary'])
        if 'recurringEventId' in item and item['status'] == 'cancelled':
            print("cancelling", item['summary'] if 'summary' in item else "")
            cancellations.append(item)
        elif 'recurringEventId' in item:
            print("rescheduling", item['summary'] if 'summary' in item else "")
            reschedules.append(item)
        elif 'recurrence' in item:
            recurring.append(item)
        else:
            events.append(item)

    return events, recurring, cancellations, reschedules

def get_event_at(current_time):
    print(current_time)
    events, recurring, cancellations, reschedules = get_calendar_parts()    
    current_events = get_events_at(current_time, events, recurring, cancellations, reschedules)
    latest_event = None
    latest_event_start = current_time-timedelta(days=500)
    for ev in current_events:
        print(ev['startDate'], ev['summary'])
        if ev['startDate'] > latest_event_start:
            latest_event = ev
            latest_event_start = ev['startDate']

    return latest_event_start,latest_event


def get_current_event():
    return get_event_at(datetime.now(timezone.utc))    


if __name__ == "__main__":

    names = get_movie_names_between(
        datetime.now(timezone.utc),
        datetime.now(timezone.utc) + timedelta(days=8)
    )
    for n in names:
        print(n)
    """
    There are 2 real goals:
    1. Generate an accurate calendar from TIME_A to TIME_B
    2. Determine what events are currently happening right now

    the use cases for this:
    - use the calendar from TIME_A to TIME_B to pre-download movies
    - use the 'currently happening' to change what movie is currently playing in VLC

    e.g.
    month_events = patcallib.get_calender(now(), now()+timedelta(days=30))
    now_events = patcallib.get_events_at(now())
    """ 
    #t0 = datetime.now(timezone.utc)
    #t1 = t0 + timedelta(days = 30) # one month after t0

    #month_events = get_events_between(t0, t0 + timedelta(days = 30))

#    start, ev = get_event_at(datetime.now(timezone.utc))
#    if ev is None:
#        print("no event found")
#    else:
#        print()
#        print(start, ev['summary'], (datetime.now(timezone.utc)-start).seconds)


def register(app):
    @app.route("/current_calendar_movie")
    async def current_calendar_movie():
        start, ev = calendar_playlist.get_current_event()
        if ev is None:
            return jsonify({ "movie_name": None, "offset": 0 })
        else:
            return jsonify({ "movie_name": ev['summary'], "offset": (datetime.datetime.now(datetime.timezone.utc)-start).seconds })
    
    
    @app.route("/current_calendar_movie_names")
    async def current_calendar_movie_names():
        names = calendar_playlist.get_movie_names_between(
            datetime.datetime.now(timezone.utc),
            datetime.datetime.now(timezone.utc) + timedelta(days=8)
        )
        return jsonify({ "names": names })
    
