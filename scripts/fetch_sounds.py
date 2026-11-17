"""從 Freesound 下載 CC0 動物叫聲試聽檔，存到 sounds/，並記錄來源到 sounds/credits.json。"""
import json, os, pathlib, time, urllib.parse, urllib.request

TOKEN = os.environ.get('FS_TOKEN') or 'f2vSMzeHQJr6ylMjzs3x4qIpQOaRI6GLBZ1AXGvq'
PER_KEY = 3
QUERIES = {
    'sheep':  'sheep baa',
    'hen':    'hen cluck',
    'chick':  'chick chirp',
    'duck':   'duck quack',
    'goose':  'goose honk',
    'cow':    'cow moo',
    'cowbell':'cowbell cow',
    'cat':    'cat meow',
    'purr':   'cat purring',
    'dog':    'dog bark',
    'pig':    'pig oink',
    'piglet': 'piglet squeal',
    'rooster':'rooster crow',
}
UA = {'User-Agent': 'animal-sound-fetcher/1.0'}
out = pathlib.Path('sounds'); out.mkdir(exist_ok=True)
credits = {}

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()

for key, q in QUERIES.items():
    params = {
        'query': q,
        'filter': 'duration:[0.3 TO 4] license:"Creative Commons 0"',
        'sort': 'rating_desc',
        'fields': 'id,name,username,url,license,previews,duration,avg_rating',
        'page_size': '15',
        'token': TOKEN,
    }
    try:
        data = json.loads(get('https://freesound.org/apiv2/search/text/?' + urllib.parse.urlencode(params)))
    except Exception as e:
        print('search failed', key, e); continue
    picked = 0
    for r in data.get('results', []):
        if picked >= PER_KEY: break
        mp3 = r['previews'].get('preview-hq-mp3') or r['previews'].get('preview-lq-mp3')
        if not mp3: continue
        fn = out / f'{key}_{picked + 1}.mp3'
        try:
            fn.write_bytes(get(mp3))
        except Exception as e:
            print('download failed', key, e); continue
        picked += 1
        credits.setdefault(key, []).append({
            'file': fn.name, 'id': r['id'], 'name': r['name'], 'author': r['username'],
            'url': r['url'], 'license': r['license'], 'duration': r['duration'],
        })
        time.sleep(.3)
    print(key, picked)

(out / 'credits.json').write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding='utf-8')
