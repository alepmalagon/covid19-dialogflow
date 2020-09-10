
# A very simple Flask Hello World app for you to get started with...
import sys
import unicodedata
import requests
import random
import html
from flask import Flask, request, make_response, jsonify

from forecast import Forecast, validate_params

app = Flask(__name__)
log = app.logger



url = 'http://public-api.wordpress.com/wp/v2/sites/ampmbot.home.blog/'
url_win = 'http://public-api.wordpress.com/wp/v2/sites/wampmbot.wordpress.com/'

translate_tags = {
                    'actuacion': 345911,
                    'animacion': 15460,
                    'artista-novel': 33415385,
                    'cancion-balada': 173751769,
                    'coreografico': 17063051,
                    'del-ano': 3827638,
                    'direccion': 256770,
                    'direccion-de-arte': 23919,
                    'diseno-de-vestuario': 1412009,
                    'edicion': 367299,
                    'efectos-visuales': 683445,
                    'fotografia': 1378,
                    'fusion': 53189,
                    'hip-hop': 31276,
                    'making-of': 207776,
                    'mas-popular': 55212990,
                    'musica-instrumental': 1437873,
                    'musica-para-ninos': 1580924,
                    'musica-pop': 593374,
                    'musica-tradicional': 1084519,
                    'rock': 1433,
                    'musica-urbana': 3838229,
                    'opera-prima': 1968064,
                    'pop-house-electronico': 663889658,
                    'pop-rock': 121091,
                    'pop-urbano-tropical': 663894947,
                    'popular-bailable': 70389641,
                    'produccion': 65067,
                    'trova': 332831
                }
cat_artistas = 20500
cat_directors = 3716

@app.route('/',  methods=['GET', 'POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook

    This is meant to be used in conjunction with the weather Dialogflow agent
    """

    print("**************** debug ***************", file=sys.stderr)
    print(request, file=sys.stderr)


    req = request.get_json(force=True)

    try:
        action = req.get('queryResult').get('action')

    except AttributeError:
        return make_response(jsonify({'fulfillmentText': 'hubo un error'}))

    print(action, file=sys.stderr)

    if action == 'nominaciones.por.categoria':
        res = nominaciones_por_categoria(req)
    elif action == 'nominaciones.de.video':
        res = nominaciones_de_video(req)
    elif action == 'nominaciones.de.artista':
        res = nominaciones_de_artista(req)
    elif action == 'nominaciones.de.director':
        res = nominaciones_de_director(req)
    elif action == 'ganadores.por.categoria':
        res = ganadores_por_categoria(req)
    elif action == 'ganadores.por.artista':
        res = ganadores_por_artista(req)
    elif action == 'ganadores.por.director':
        res = ganadores_por_director(req)
    elif action == 'ganadores.por.video':
        res = ganadores_por_video(req)
    else:
        log.error('Unexpected action.')


    print('Action: ' + action, flush=True)
    print('Response: ' + res, flush=True)

    return make_response(jsonify({'fulfillmentText': res}))

def nominaciones_por_categoria(req):

    try:
        cat = req.get('queryResult').get('parameters').get('categoria')[0]

    except AttributeError:
        return '¿Podrías especificar una categoría?'
    print(str(cat), file=sys.stderr)
    if str(cat)=='':
        return 'Lo siento pero los Premios Lucas no tienen esa categoría. :D'

    resp_list = ['Los nominados en esta categoría son ', 'Estos son los nominados en la categoría ', 'Nominados estaban ']

    tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url+'posts?tags='+str(tag),
        params=data
    )

    rjson = response.json()
    r = random.choice(resp_list)
    list = []
    for video in rjson:
        #print(str(video[0]), file=sys.stderr)
        list.append(video.get('title').get('rendered'))
        #r = r + video.get('title').get('rendered') + ', '
    r = r + and_last_comma(str(list).replace('[','').replace(']', '').replace('\'',''))
    return html.unescape(r)

def nominaciones_de_video(req):

    try:
        video = req.get('queryResult').get('parameters').get('video')

    except AttributeError:
        return '¿Podrías especificar el nombre de un video?'

    if str(video)=='':
        return 'Mmmm, no conozco ese video.'
    resp_list = ['Estaba nominado a ', 'Sus nominaciones fueron ', 'Lo nominaron a ']
    print(str(video), file=sys.stderr)

    slug = str(unicodedata.normalize('NFKD', video)).lower().replace(" ", "-")

    print(slug, file=sys.stderr)

    #tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url+'posts?slug='+slug,
        params=data
    )

    rjson = response.json()[0]

    tags = rjson.get('tags')

    r = 'tags?include='
    r = r + str(tags).replace('[','').replace(']', '')

    response = requests.get(
        url+r,
        params=data
    )
    rjson = response.json()
    print(str(rjson), file=sys.stderr)
    video_cats = []
    r = random.choice(resp_list)
    for categoria in rjson:
        #print(str(video[0]), file=sys.stderr)
        print(str(categoria), file=sys.stderr)
        video_cats.append(categoria.get('description'))

    r = r + and_last_comma(str(video_cats).replace('[','').replace(']', '').replace('\'',''))

    return html.unescape(r)

def nominaciones_de_artista(req):

    try:
        artista = req.get('queryResult').get('parameters').get('artista')

    except AttributeError:
        return '¿Podrías especificar el nombre de un artista?'
    if str(artista)=='':
        return 'Estas seguro de que esa persona esta compitiendo?. Lucas acá me dice que no.'
    print(str(artista), file=sys.stderr)

    slug = str(unicodedata.normalize('NFKD', artista)).lower().replace(" ", "-")

    print(slug, file=sys.stderr)

    #tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url+'categories?slug='+slug,
        params=data
    )

    rjson = response.json()

    cat_id = rjson[0].get('id') # need cat id to get posts/videos
    print(cat_id, file=sys.stderr)
    r = 'posts?categories='+str(cat_id)

    response = requests.get(
        url+r,
        params=data
    )

    rjson = response.json()
    answer = 'Este artista fue nominado a '
    i=0
    for video in rjson:
        answer = answer + 'por el video "'+ video.get('title').get('rendered') + '"('+ video.get('link') +') en '
        slug = video.get('slug')
        data = {}
        response = requests.get(
            url+'posts?slug='+slug,
            params=data
        )

        _rjson = response.json()[0]

        tags = _rjson.get('tags')

        r = 'tags?include='
        r = r + str(tags).replace('[','').replace(']', '')

        response = requests.get(
            url+r,
            params=data
        )
        _rjson = response.json()
        print(str(_rjson), file=sys.stderr)
        video_cats = []

        for categoria in _rjson:
            #print(str(video[0]), file=sys.stderr)
            print(str(categoria), file=sys.stderr)
            video_cats.append(categoria.get('description'))

        answer = answer + and_last_comma(str(video_cats).replace('[','').replace(']', '').replace('\'','')) + ''
        if i != len(rjson) - 1:
            answer = answer + ', por '
        i = i+1
    return html.unescape(answer)



def ganadores_por_categoria(req):

    try:
        cat = req.get('queryResult').get('parameters').get('categoria')

    except AttributeError:
        return '¿Podrías especificar una categoría?'
    print(str(cat), file=sys.stderr)
    if str(cat)=='':
        return 'Lo siento pero los Premios Lucas no tienen esa categoría. :D'

    resp_list = ['El ganador fue ', 'Ganó ', 'Se llevo el premio ']

    tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url_win+'posts?tags='+str(tag),
        params=data
    )

    rjson = response.json()
    r = random.choice(resp_list)
    list = []
    for video in rjson:
        #print(str(video[0]), file=sys.stderr)
        response = requests.get(
            url_win+'categories/?post='+ str(video.get('id')) +'&parent=20500',
            params=data
        )
        _rjson = response.json()
        artists = []
        for artist in _rjson:
            artists.append(artist.get('name'))
        #print(str(artists), file=sys.stderr)
        list.append(video.get('title').get('rendered')+' de ' + and_last_comma(str(artists).replace('[','').replace(']', '').replace('\'','')))
        #r = r + video.get('title').get('rendered') + ', '
    r = r + and_last_comma(str(list).replace('[','').replace(']', '').replace('\'',''))
    return html.unescape(r)

def ganadores_por_video(req):

    try:
        video = req.get('queryResult').get('parameters').get('video')

    except AttributeError:
        return '¿Podrías especificar el nombre de un video?'

    if str(video)=='':
        return 'Mmmm, no conozco ese video.'
    resp_list = ['Este video ganó en ', 'Fue premiado en ']
    print(str(video), file=sys.stderr)

    slug = str(unicodedata.normalize('NFKD', video)).lower().replace(" ", "-")

    print(slug, file=sys.stderr)

    #tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url_win+'posts?slug='+slug,
        params=data
    )

    rjson = response.json()[0]

    tags = rjson.get('tags')

    r = 'tags?include='
    r = r + str(tags).replace('[','').replace(']', '')

    response = requests.get(
        url_win+r,
        params=data
    )
    rjson = response.json()
    if type(rjson)!=list:
        return "Este video no obtuvo premios"
    print(str(rjson), file=sys.stderr)
    video_cats = []
    r = random.choice(resp_list)
    for categoria in rjson:
        #print(str(video[0]), file=sys.stderr)
        print(str(categoria), file=sys.stderr)
        video_cats.append(categoria.get('description'))

    r = r + and_last_comma(str(video_cats).replace('[','').replace(']', '').replace('\'',''))

    return html.unescape(r)

def ganadores_por_artista(req):

    try:
        artista = req.get('queryResult').get('parameters').get('artista')

    except AttributeError:
        return '¿Podrías especificar el nombre de un artista?'
    if str(artista)=='':
        return 'Estas seguro de que esa persona esta compitiendo?. Lucas acá me dice que no.'
    print(str(artista), file=sys.stderr)

    slug = str(unicodedata.normalize('NFKD', artista)).lower().replace(" ", "-")

    print(slug, file=sys.stderr)

    #tag = translate_tags[cat]
    data = {}
    response = requests.get(
        url_win+'categories?slug='+slug,
        params=data
    )

    rjson = response.json()
    print(str(rjson), file=sys.stderr)
    cat_id = rjson[0].get('id') # need cat id to get posts/videos
    print(cat_id, file=sys.stderr)
    r = 'posts?categories='+str(cat_id)

    response = requests.get(
        url_win+r,
        params=data
    )

    rjson = response.json()
    answer = 'Este artista ganó '
    i=0
    for video in rjson:

        slug = video.get('slug')
        data = {}
        response = requests.get(
            url_win+'posts?slug='+slug,
            params=data
        )

        _rjson = response.json()[0]

        tags = _rjson.get('tags')

        r = 'tags?include='
        r = r + str(tags).replace('[','').replace(']', '')

        response = requests.get(
            url_win+r,
            params=data
        )
        _rjson = response.json()
        if type(_rjson)!=list:
            continue
        print('tags----' + str(_rjson), file=sys.stderr)
        video_cats = []
        answer = answer + 'por el video "'+ video.get('title').get('rendered') + '" en '
        for categoria in _rjson:
            #print(str(video[0]), file=sys.stderr)
            print(str(categoria), file=sys.stderr)
            video_cats.append(categoria.get('description'))

        answer = answer + and_last_comma(str(video_cats).replace('[','').replace(']', '').replace('\'','')) + ''
        if i != len(rjson) - 1:
            answer = answer + ', por '
        i = i+1
    if answer=="Este artista ganó ":
        return "Este artista no obtuvo premios"
    return html.unescape(answer)

def and_last_comma(s, old=',', new=' y'):
    return (s[::-1].replace(old[::-1],new[::-1], 1))[::-1]
