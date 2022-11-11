#import asyncio
#import aiohttp
import requests
import base64
from PIL import Image
from io import BytesIO
import random
import datetime
import time

def gen_images(query):
    data = {"prompt": query}
    url = "https://backend.craiyon.com/generate"
    print(url, data)
    resp = requests.post(url, json=data)
    print(f"{query} -- {resp}")
    return [ base64.b64decode(img) for img in resp.json()['images'] ]

def gen_image(query, retries=2):
    if retries < 0:
        print(f"ran out of retries for {query}")
        return None

    try:
        imgs = gen_images(query)
        dest = Image.new('RGB', (734, 734))
        img = Image.open(BytesIO(imgs[0]))
        dest.paste(img, (0,0))
    
        r = int(random.random()*1000000000000)
        dest.save(f"tmp_{r}.png")
        with open(f"tmp_{r}.png", "rb") as f:
            d = f.read()
    
        return d
    except Exception as e:
        print(f"exception for {query}", e)
        time.sleep(1)
        return gen_image(query, retries=retries-1)
        
        return None



def gen_image_grid(query, retries=2):
    if retries < 0:
        print(f"ran out of retries for {query}")
        return None

    print(f"gen_image_grid for {query} -- {retries}")

    try:
        imgs = gen_images(query)
        #imgs = []
        #for i in range(9):
        #    with open(f"millhouse_{i}.png", "rb") as f:
        #        imgs.append(f.read())
        dest = Image.new('RGB', (734*3, 734*3))
        for i in range(9):
            y = i%3
            x = int(i/3)
            img = Image.open(BytesIO(imgs[i]))
            dest.paste(img, (x*734, y*734))
    
        r = int(random.random()*1000000000000)
        dest.save(f"tmp_{r}.png")
        with open(f"tmp_{r}.png", "rb") as f:
            d = f.read()
        #os.remove(f"tmp_{r}.png")
    
        return d
    except Exception as e:
        print(f"exception for {query}", e)
        time.sleep(1)
        return gen_image_grid(query, retries=retries-1)
        
        return None

def main():
    print("hello")
    img = gen_image_grid("millhouse batallion")
    with open('c.png','wb') as f:
        f.write(img)
    #for i in range(len(imgs)):
    #    print(i)
    #    with open(f"millhouse_{i}.png", "wb") as f:
    #        f.write(imgs[i])
    
    print("done")
    
if __name__ == "__main__":
    main()


