import requests
import re
import time

curr = None
while True:
  try:
    j = requests.get('https://bodygen.re:8081/vlc/current', verify=False).json()
    if j['current_title'] != curr:
      t = j['current_title']
      t = re.sub(r"\.+[^\.]*$","",re.sub(r"^.*/","",t))
      msg = "videojunki.es currently playing: " + t
      res = requests.post("http://di0.cat", data=msg, headers={"Content-Type": "application/x-www-form-urlencoded"})
      print(res.content)
      curr = j['current_title']
  except:
    print('failed something')
  time.sleep(60)
