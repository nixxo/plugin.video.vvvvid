import urllib.parse as parse
import requests
import re
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
VVVVID_KENC_SERVER = 'https://www.vvvvid.it/kenc?action=kt'

CHANNEL_MODE = "channel"
SINGLE_ELEMENT_CHANNEL_MODE = "elementchannel"
# plugin modes
MODE_MOVIES = '10'
MODE_ANIME = '20'
MODE_SHOWS = '30'
MODE_SERIES = '40'

# parameter keys
PARAMETER_KEY_MODE = "mode"


# menu item names
ROOT_LABEL_MOVIES = "Movies"
ROOT_LABEL_ANIME = "Anime"
ROOT_LABEL_SHOWS = "Shows"
ROOT_LABEL_SERIES = "Series"

# episode stream type
F4M_TYPE = '10'
M3U_TYPE = '20'     # .m3u8 is the unicode version of .m3u

# video types
AKAMAI_TYPE = 'video/rcs'
KENC_TYPE = 'video/kenc'
ENC_TYPE = 'video/enc'
VVVVID_TYPE = 'video/vvvvid'

# manifest server
STREAM_HTTP = 'http://194.116.73.48/videomg/_definst_/mp4:'

HTTP_HEADERS = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'


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


def get_section_channels(modeType):
    channelUrl = VVVVID_BASE_URL + getChannelsPath(modeType) 
    response = getJsonDataFromUrl(channelUrl)
    channels = response['data']
    listChannels = []
    for channelData in channels:
        filter = ''
        path=''
        listCategory = []
        listFilters = []
        listExtras = []
        if 'filter' in channelData:
            for filter in channelData['filter']:
                listFilters.append(filter)
        if 'category' in channelData:
            for category in channelData['category']:
                channelCategoryElem = ChannelCategory(category['id'],category['name'])
                listCategory.append(channelCategoryElem)
        if 'extras' in channelData:
            for extra in channelData['extras']:
                channelExtrasElem = ChannelExtra(extra['id'],extra['name'])
                listExtras.append(channelExtrasElem)

        channel = Channel(channelData['id'],channelData['name'],listFilters,listCategory,listExtras) 
        listChannels.append(channel)
    return listChannels

def get_elements_from_channel(idChannel, type, idFilter='', idCategory='', idExtra=''):
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
    elements = response.get('data') or []
    listElements = []
    for elementData in elements:
        elementChannel = ElementChannel(
            elementData['id'],
            elementData['show_id'],
            elementData['title'],
            elementData['thumbnail'],
            elementData['ondemand_type'],
            elementData['show_type']
        )
        listElements.append(elementChannel)
    return listElements


def get_item_playable(idItem):
    urlToLoad = VVVVID_BASE_URL + idItem + '/info'
    response = getJsonDataFromUrl(urlToLoad)
    info = response['data']
    #web_pdb.set_trace()
    itemPlayable = ItemPlayableChannel()
    itemPlayable.title = info['title']
    itemPlayable.thumb = info['thumbnail']
    itemPlayable.id = info['id']
    itemPlayable.show_id = info['show_id']
    itemPlayable.ondemand_type = info['ondemand_type']
    itemPlayable.show_type = info['show_type']
    itemPlayable = get_seasons_for_item(itemPlayable)
    return itemPlayable
    
def get_seasons_for_item(itemPlayable):
    #web_pdb.set_trace()
    urlToLoad = VVVVID_BASE_URL + str(itemPlayable.show_id) + '/seasons'
    response = getJsonDataFromUrl(urlToLoad)
    result = response['data']
    itemPlayable.seasons = []
    for seasonData in result:
        season = ItemPlayableSeason()
        season.id = seasonData['show_id']
        season.show_id = seasonData ['show_id']
        season.season_id = seasonData['season_id']
        if 'name' in seasonData:
            season.title = seasonData['name']
        else:
            season.title = itemPlayable.title
        urlToLoadSeason = VVVVID_BASE_URL+str(itemPlayable.show_id) + '/season/' + str(season.season_id)
        responseSeason = getJsonDataFromUrl(urlToLoadSeason)
        resultSeason = responseSeason.get('data')
        listEpisode = []
        for episodeData in resultSeason:
            if(episodeData['video_id'] != '-1'):
                episode = SeasonEpisode()
                embed_info = dec_ei(episodeData['embed_info'])
                episode.show_id = season.show_id
                episode.season_id = season.season_id
                prefix = ''
                video_type = episodeData['video_type']
                postfix= 'g=DRIEGSYPNOBI&hdcore=3.6.0&plugin=aasp-3.6.0.50.41'
                #xbmcgui.Dialog().ok('VVVVID.it',video_type)
                if video_type == ENC_TYPE:
                    episode.stream_type = F4M_TYPE
                    episode.manifest = STREAM_HTTP+embed_info+postfix
                elif video_type == KENC_TYPE:
                    episode.stream_type = F4M_TYPE
                    response = getJsonDataFromUrl(VVVVID_KENC_SERVER+'&url='+parse.quote_plus(embed_info))
                    embed_info_plus = dec_ei(response['message'])#;xbmcgui.Dialog().ok('VVVVID.it',embed_info_plus)
                    episode.manifest = embed_info+'?'+embed_info_plus+'&'+postfix
                elif video_type == VVVVID_TYPE:
                    episode.stream_type = F4M_TYPE
                    episode.manifest = STREAM_HTTP+embed_info+'/manifest.f4m'
                elif video_type == AKAMAI_TYPE:
                    episode.stream_type = M3U_TYPE
                    episode.manifest = re.sub(r'https?(://[^/]+)/z/', r'https\1/i/', embed_info).replace('/manifest.f4m', '/master.m3u8')
                else:
                    episode.stream_type = F4M_TYPE
                    episode.manifest = embed_info+'?'+postfix
                #episode.manifest = prefix +  episodeData['embed_info'] + postfix
                episode.title = ((episodeData['number'] + ' - ' + episodeData['title'])).encode('utf-8','replace')
                episode.thumb = episodeData['thumbnail']
                listEpisode.append(episode)
        season.episodes = listEpisode
        itemPlayable.seasons.append(season)
    return itemPlayable

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
    return response.json()

def manageLogin(credentials):
    data_storage = Storage()
    cookie = data_storage.get('cookie')

    headers = {'User-Agent': HTTP_HEADERS}
    if cookie:
        headers.update({'Cookie': cookie})
    
    response = requests.get(VVVVID_LOGIN_URL, headers=headers)

    data = response.json()
    if data["result"] != "ok":
        post_data = {
            'action': 'login',
            'email': credentials['username'],
            'password': credentials['password'],
            'login_type': 'force',
            'reminder': 'true',
        }

        response = requests.post("http://www.vvvvid.it/user/login", headers=headers, data=post_data)
        
        data = response.json()
        if data["result"] != "first" and data["result"] != "ok":
            xbmcgui.Dialog().ok("VVVVID.it", "Impossibile eseguire login")
            sys.exit(0)
        data_storage.set('conn_id', data["data"]["conn_id"])

        prova = requests.utils.dict_from_cookiejar(response.cookies)

        data_storage.set('cookie', response.headers['set-cookie'])
    else:
        data_storage.set('conn_id', data["data"]["conn_id"])

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
