import re
import requests

from resources.lib import addonutils
from resources.lib.storage import Storage
from resources.lib.channels import *

import web_pdb


VVVVID_BASE_URL = "https://www.vvvvid.it/vvvvid/ondemand/"
VVVVID_LOGIN_URL = 'http://www.vvvvid.it/user/login'
ANIME_CHANNELS_PATH = "anime/channels"
MOVIE_CHANNELS_PATH = "film/channels"
SHOW_CHANNELS_PATH = "show/channels"
SERIES_CHANNELS_PATH = "series/channels"
ANIME_SINGLE_CHANNEL_PATH = "anime/channel/"
MOVIE_SINGLE_CHANNEL_PATH = "film/channel/"
SHOW_SINGLE_CHANNEL_PATH = "show/channel/"
SERIES_SINGLE_CHANNEL_PATH = "series/channel/"
ANIME_SINGLE_ELEMENT_CHANNEL_PATH = 'anime/'
SHOW_SINGLE_ELEMENT_CHANNEL_PATH = 'show/'
MOVIE_SINGLE_ELEMENT_CHANNEL_PATH = 'film/'
SERIES_SINGLE_ELEMENT_CHANNEL_PATH = 'series/'

# manifest server
STREAM_HTTP = 'http://194.116.73.48/videomg/_definst_/mp4:'
VVVID_POSTFIX= 'g=DRIEGSYPNOBI&hdcore=3.6.0&plugin=aasp-3.6.0.50.41'
VVVVID_KENC_SERVER = 'https://www.vvvvid.it/kenc?action=kt'

HTTP_HEADERS = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'

# plugin modes
MODE_MOVIES = '10'
MODE_ANIME = '20'
MODE_SHOWS = '30'
MODE_SERIES = '40'

# menu item names
ROOT_LABEL_MOVIES = 33001
ROOT_LABEL_ANIME = 33002
ROOT_LABEL_SHOWS = 33003
ROOT_LABEL_SERIES = 33004

# video types
AKAMAI_TYPE = 'video/rcs'
KENC_TYPE = 'video/kenc'
ENC_TYPE = 'video/enc'
VVVVID_TYPE = 'video/vvvvid'


def getMainMenu():
    return [
        {
            'label': addonutils.LANGUAGE(ROOT_LABEL_ANIME),
            'params': {
                'mode': 'channels',
                'type': MODE_ANIME,
            },
        },
        {
            'label': addonutils.LANGUAGE(ROOT_LABEL_MOVIES),
            'params': {
                'mode': 'channels',
                'type': MODE_MOVIES,
            },
        },
        {
            'label': addonutils.LANGUAGE(ROOT_LABEL_SHOWS),
            'params': {
                'mode': 'channels',
                'type': MODE_SHOWS,
            },
        },
        {
            'label': addonutils.LANGUAGE(ROOT_LABEL_SERIES),
            'params': {
                'mode': 'channels',
                'type': MODE_SERIES,
            },
        },
    ]


def getChannelsPath(type):
    if type == MODE_MOVIES:
        return MOVIE_CHANNELS_PATH
    elif type == MODE_ANIME:
        return ANIME_CHANNELS_PATH
    elif type == MODE_SHOWS:
        return SHOW_CHANNELS_PATH
    elif type == MODE_SERIES:
        return SERIES_CHANNELS_PATH


def getSingleChannelPath(type):
    if type == MODE_MOVIES:
        return MOVIE_SINGLE_CHANNEL_PATH
    elif type == MODE_ANIME:
        return ANIME_SINGLE_CHANNEL_PATH
    elif type == MODE_SHOWS:
        return SHOW_SINGLE_CHANNEL_PATH
    elif type == MODE_SERIES:
        return SERIES_SINGLE_CHANNEL_PATH


def getChannelsSection(modeType, submode=None, channel_id=None):
    channelUrl = VVVVID_BASE_URL + getChannelsPath(modeType) 
    response = getJsonDataFromUrl(channelUrl)
    for channelData in response or []:
        if submode and channel_id:
            if str(channelData['id']) == channel_id:
                if submode in channelData:
                    web_pdb.set_trace()
                    for data in channelData[submode]:
                        label, id = (data, data) if isinstance(data, str) else (data.get('name'), data.get('id'))
                        yield {
                            'label': label,
                            'params': {
                                'mode': 'single',
                                'type': modeType,
                                'channel_id': channel_id,
                                '%s_id' % submode: id,
                            },
                        }
        elif channel_id:
            yield from getElementsFromChannel(channel_id, modeType)
        else:
            sub = [x for x in ['filter', 'category', 'extras'] if x in channelData]
            sub = sub[0] if sub else None
            yield {
                'label': channelData['name'],
                'params': {
                    'mode': 'channels',
                    'type': modeType,
                    'channel_id': channelData['id'],
                    'submode': sub,
                }
            }


def getElementsFromChannel(idChannel, type, idFilter=None, idCategory=None, idExtra=None):
    web_pdb.set_trace()
    middlePath = getSingleChannelPath(type)
    urlPostFix = '/last/'
    if(idFilter):
        urlPostFix += '?filter=' + idFilter
    elif(idCategory):
        urlPostFix += '?category=' + idCategory
    elif(idExtra):
        urlPostFix += '?extras=' + idExtra
    urlToLoad = VVVVID_BASE_URL + middlePath + str(idChannel) + urlPostFix

    response = getJsonDataFromUrl(urlToLoad)
    for elementData in response or []:
        yield {
            'label': elementData['title'],
            'params': {
                'mode': 'item',
                # 'submode': 'item',
                'item_id': elementData['show_id']
            },
            'arts': {
                'icon': elementData['thumbnail'],
                'thumb': elementData['thumbnail'],
            },
        }


# deprecated ???
def getItemPlayable(idItem, idSeason=None):
    urlToLoad = VVVVID_BASE_URL + idItem + '/info'
    response = getJsonDataFromUrl(urlToLoad)
    web_pdb.set_trace()
    return {
        'label': response['title'],
        #'params': {
        #    'mode': 'item',
        #    'item_id': idItem,
        #},
        'seasons': getSeasonsForItem(response['show_id'], idSeason),
        'arts': {
            'thumbnail': response['thumbnail']
        }
    }

    
def getSeasonsForItem(idItem, idSeason=None):
    #web_pdb.set_trace()
    urlToLoad = VVVVID_BASE_URL + str(idItem) + '/seasons'
    response = getJsonDataFromUrl(urlToLoad)
    #itemPlayable.seasons = []
    items = []
    if not idSeason and len(response) == 1:
        return getEpisodesForSeason(idItem, response[0].get('season_id'))

    for seasonData in response:
        if not idSeason:
            items.append({
                'label': seasonData.get('name'),
                'params': {
                    'mode': 'item',
                    'item_id': idItem,
                    'season_id': seasonData.get('season_id'),
                }
            })
    return items

 
def getEpisodesForSeason(idItem, idSeason):
    #web_pdb.set_trace()
    urlToLoad = VVVVID_BASE_URL + str(idItem) + '/season/' + str(idSeason)
    response = getJsonDataFromUrl(urlToLoad)
    #itemPlayable.seasons = []
    items = []

    for episodeData in response:
        if(episodeData['video_id'] != '-1'):
            embed_info = dec_ei(episodeData['embed_info'])
            if episodeData['video_type'] == AKAMAI_TYPE:
                manifest = re.sub(r'https?(://[^/]+)/z/', r'https\1/i/', embed_info).replace('/manifest.f4m', '/master.m3u8')
            item = {
                'label': episodeData['number'] + ' - ' + episodeData['title'],
                'params': {
                    'mode': 'play',
                    'video': manifest,
                },
                'videoInfo': {
                    'title': episodeData['title'],
                    'tvshowtitle': episodeData['show_title'],
                    'season': int(episodeData['season_number']),
                    'episode': int(episodeData['number']),
                    'duration': episodeData['length'],
                    'mediatype': 'episode',
                },
                'arts': {
                    'thumbnail': episodeData['thumbnail'],
                },
                'isPlayable': episodeData['playable'],
            }
            items.append(item)
    return items


def getJsonDataFromUrl(customUrl):
    #web_pdb.set_trace()
    data_storage = Storage()
    conn_id = data_storage.get('conn_id')
    customUrl += ('&' if ('?' in customUrl) else '?') + 'conn_id=' + conn_id
    cookie = data_storage.get('cookie')
    headers = {'User-Agent': HTTP_HEADERS}
    if cookie:
        headers.update({'Cookie': cookie})
    response = requests.get(customUrl, headers=headers)

    response = response.json()
    if response.get('result') == 'ok':
        return response.get('data')
    return None


def f(m):
    l = []
    o = 0
    b = False
    m_len = len(m)
    while ((not b) and o < m_len):
        n = m[o] << 2
        o += 1
        k = -1
        j = -1
        if o < m_len:
            n += m[o] >> 4
            o += 1
            if o < m_len:
                k = (m[o - 1] << 4) & 255
                k += m[o] >> 2
                o += 1
                if o < m_len:
                    j = (m[o - 1] << 6) & 255
                    j += m[o]
                    o += 1
                else:
                    b = True
            else:
                b = True
        else:
            b = True
        l.append(n)
        if k != -1:
            l.append(k)
        if j != -1:
            l.append(j)
    return l


def dec_ei(h):
    g = 'MNOPIJKL89+/4567UVWXQRSTEFGHABCDcdefYZabstuvopqr0123wxyzklmnghij'
    c = []
    for e in h:
        c.append(g.index(e))

    c_len = len(c)
    for e in range(c_len * 2 - 1, -1, -1):
        a = c[e % c_len] ^ c[(e + 1) % c_len]
        c[e % c_len] = a
    c = f(c)
    d = ''
    for e in c:
        d += chr(e)
    return d
