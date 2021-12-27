import datetime
import re
import requests

from simplecache import SimpleCache

from resources.lib import addonutils
from resources.lib.translate import translatedString as T
import web_pdb


VVVVID_BASE_URL = 'https://www.vvvvid.it/vvvvid/ondemand/'
VVVVID_LOGIN_URL = 'http://www.vvvvid.it/user/login'
VVVVID_SEASONS_URL = VVVVID_BASE_URL + '{item}/seasons'
VVVVID_SEASON_URL = VVVVID_BASE_URL + '{item}/season/{season}'
VVVVID_ELEMENTS_URL = VVVVID_BASE_URL + '{path}{item}/last/'
VVVVID_INFO_URL = VVVVID_BASE_URL + '{item}/info/'
ANIME_CHANNELS_PATH = 'anime/channels'
MOVIE_CHANNELS_PATH = 'film/channels'
SHOW_CHANNELS_PATH = 'show/channels'
SERIES_CHANNELS_PATH = 'series/channels'
ANIME_SINGLE_CHANNEL_PATH = 'anime/channel/'
MOVIE_SINGLE_CHANNEL_PATH = 'film/channel/'
SHOW_SINGLE_CHANNEL_PATH = 'show/channel/'
SERIES_SINGLE_CHANNEL_PATH = 'series/channel/'
ANIME_SINGLE_ELEMENT_CHANNEL_PATH = 'anime/'
SHOW_SINGLE_ELEMENT_CHANNEL_PATH = 'show/'
MOVIE_SINGLE_ELEMENT_CHANNEL_PATH = 'film/'
SERIES_SINGLE_ELEMENT_CHANNEL_PATH = 'series/'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
USER_AGENT_UE = 'Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20WOW64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F52.0.2743.82%20Safari%2F537.36'

# plugin modes
MODE_MOVIES = '10'
MODE_ANIME = '20'
MODE_SHOWS = '30'
MODE_SERIES = '40'

# video types
AKAMAI_TYPE = 'video/rcs'
KENC_TYPE = 'video/kenc'
ENC_TYPE = 'video/enc'
VVVVID_TYPE = 'video/vvvvid'

# TODO: uri='plugin://plugin.video.youtube/play/?video_id='+video_id
# xbmc.executebuiltin('RunPlugin(plugin://plugin.video.youtube/channel/UCaBf1a-dpIsw8OxqH4ki2Kg/?addon_id=plugin.video.example)')

DEVMODE = addonutils.getSettingAsBool('dev_mode')

MAIN_MENU = [
{
    'label': T('menu.anime'),
    'params': {
        'mode': 'channels',
        'type': MODE_ANIME,
    },
}, {
    'label': T('menu.movies'),
    'params': {
        'mode': 'channels',
        'type': MODE_MOVIES,
    },
}, {
    'label': T('menu.shows'),
    'params': {
        'mode': 'channels',
        'type': MODE_SHOWS,
    },
}, {
    'label': T('menu.series'),
    'params': {
        'mode': 'channels',
        'type': MODE_SERIES,
    },
},
]

class Vvvvid:
    def __init__(self):
        self.cache = SimpleCache()

        headers = {
            'User-Agent': USER_AGENT,
            'Cookie': self.cache.get(f"{addonutils.ID}.cookie"),
        }

        response = requests.get(VVVVID_LOGIN_URL, headers=headers)

        data = response.json()
        if data['result'] != 'ok':
            self.log('__init__, starting login.', 1)
            credentials = self.getCredentials()
            if not credentials:
                self.log('__init__, no credentials provided.', 2)
                addonutils.showOkDialog(line=T('no.credentials'))
                addonutils.endScript()

            post_data = {
                'action': 'login',
                'email': credentials['username'],
                'password': credentials['password'],
                'login_type': 'force',
                'reminder': 'true',
            }

            response = requests.post(
                VVVVID_LOGIN_URL,
                headers=headers, data=post_data)

            data = response.json()
            if data['result'] != 'first' and data['result'] != 'ok':
                self.log('__init__, login failed,', 3)
                addonutils.showOkDialog(line=T('login.error'))
                addonutils.endScript()
            self.log('__init__, login successfull,', 1)
            self.cache.set(f"{addonutils.ID}.conn_id", data['data']['conn_id'])
            self.cache.set(f"{addonutils.ID}.cookie", response.headers['set-cookie'])
        else:
            self.log('__init__, logged in.')
            self.cache.set(f"{addonutils.ID}.conn_id", data['data']['conn_id'])

    def log(self, msg, level=0):
        if DEVMODE:
            addonutils.log(msg, 1 if level == 0 else level)
        elif level >= 3:
            addonutils.log(msg, level)

    def getCredentials(self):
        import xbmcgui
        username = addonutils.getSetting('username')
        if not username:
            self.log('getCredentials, requesting username.')
            username = xbmcgui.Dialog().input(T('input.email'))
            self.log('getCredentials, saving username.')
            addonutils.setSetting('username', username)

        password = addonutils.getSetting('password')
        if not password:
            self.log('getCredentials, requesting password.')
            password = xbmcgui.Dialog().input(
                T('input.password'),
                option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if addonutils.getSettingAsBool('save_password'):
                self.log('getCredentials, saving password.')
                addonutils.setSetting('password', password)

        if not username or not password:
            return None

        return {'username': username, 'password': password}

    def createArt(self, thumb, **kwargs):
        arts = {'thumb': f"{thumb}|User-Agent={USER_AGENT_UE}"}
        for k in kwargs:
            if kwargs[k]:
                arts[k] = f"{kwargs[k]}|User-Agent={USER_AGENT_UE}"
        return arts

    def getMainMenu(self):
        return MAIN_MENU

    def getChannelsPath(self, type, single=False):
        if type == MODE_MOVIES:
            return MOVIE_SINGLE_CHANNEL_PATH if single else MOVIE_CHANNELS_PATH
        elif type == MODE_ANIME:
            return ANIME_SINGLE_CHANNEL_PATH if single else ANIME_CHANNELS_PATH
        elif type == MODE_SHOWS:
            return SHOW_SINGLE_CHANNEL_PATH if single else SHOW_CHANNELS_PATH
        elif type == MODE_SERIES:
            return SERIES_SINGLE_CHANNEL_PATH if single else SERIES_CHANNELS_PATH

    def getChannelsSection(self, mode_type, submode=None, channel_id=None):
        url = VVVVID_BASE_URL + self.getChannelsPath(mode_type)
        self.log(f"getChannelsSection, url = {url}")
        response = self.getJsonDataFromUrl(url)
        for channel_data in response or []:
            if submode and channel_id:
                if str(channel_data['id']) == channel_id:
                    if submode in channel_data:
                        for data in channel_data[submode]:
                            label, id = (data, data) if isinstance(
                                data, str) else (data.get('name'), data.get('id'))
                            self.log(f"getChannelsSection, yield \"{label}/{mode_type}/{channel_id}/{submode}/{id}\"")
                            yield {
                                'label': label,
                                'params': {
                                    'mode': 'single',
                                    'type': mode_type,
                                    'channel_id': channel_id,
                                    f"{submode}_id": id,
                                },
                            }
            elif channel_id:
                self.log(f"getChannelsSection, getting elements for {channel_id}", 1)
                yield from self.getElementsFromChannel(channel_id, mode_type)
                break
            else:
                sub = [x for x in ['filter', 'category',
                                   'extras'] if x in channel_data]
                sub = sub[0] if sub else None
                self.log(f"getChannelsSection, yield \"{channel_data['name']}/{mode_type}/{channel_data['id']}/{sub}\"")
                if channel_data['name'] == 'Extra':
                    self.log('getChannelsSection, skipping "Extra" element', 1)
                    continue
                yield {
                    'label': channel_data['name'],
                    'params': {
                        'mode': 'channels',
                        'type': mode_type,
                        'channel_id': channel_data['id'],
                        'submode': sub,
                    }
                }

    def getElementsFromChannel(self, channel_id, type,
            filter_id=None, category_id=None, extras_id=None):
        # web_pdb.set_trace()
        path = self.getChannelsPath(type, single=True)
        params = {
            'filter': filter_id,
            'category': category_id,
            'extras': extras_id
        }
        url = VVVVID_ELEMENTS_URL.format(path=path, item=channel_id)
        self.log('getElementsFromChannel, url="%s"' % url)

        response = self.getJsonDataFromUrl(url, params=params)
        for element_data in response or []:
            self.log('getElementsFromChannel, yield "%s/%s"' % (
                element_data['title'], element_data['show_id']))
            url = VVVVID_INFO_URL.format(item=element_data['show_id'])
            # web_pdb.set_trace()
            data = self.getJsonDataFromUrl(url)
            # data.get('show_type')
            # 6 show tv
            # 5 anime
            # 4 tv series
            # 3 film
            yield {
                'label': element_data['title'],
                'params': {
                    'mode': 'item',
                    'item_id': element_data['show_id']
                },
                'videoInfos': {
                    'tvshowtitle': data.get('title'),
                    'plot': data.get('description'),
                    'year': data.get('date_published'),
                    'mediatype': 'tvshow',
                },
                'arts': self.createArt(
                    thumb=element_data['thumbnail'])
            }

    def getSeasonsForItem(self, item_id, season_id=None):
        if season_id:
            yield from self.getEpisodesForSeason(item_id, season_id)
        else:
            url = VVVVID_SEASONS_URL.format(item=item_id)
            self.log('getSeasonsForItem, url="%s"' % url)
            response = self.getJsonDataFromUrl(url)

            # if only one element load it directly
            if len(response) == 1:
                yield from self.getSeasonsForItem(
                    item_id, response[0].get('season_id'))
            else:
                for season_data in response:
                    self.log('getSeasonsForItem, yield "%s/%s/%s"' % (
                        season_data.get('name'), item_id, season_data.get('season_id')))
                    yield {
                        'label': season_data.get('name'),
                        'params': {
                            'mode': 'item',
                            'item_id': item_id,
                            'season_id': season_data.get('season_id'),
                        }
                    }

    def getEpisodesForSeason(self, item_id, season_id):
        url = VVVVID_SEASON_URL.format(item=item_id, season=season_id)
        self.log('getEpisodesForSeason, url="%s"' % url)
        response = self.getJsonDataFromUrl(url)
        # web_pdb.set_trace()
        for episode_data in response:
            if episode_data['video_id'] != '-1':
                info = {
                    'label': episode_data['number'] + ' - ' + episode_data['title'],
                    'params': {
                        'mode': 'play',
                        'item_id': item_id,
                        'season_id': season_id,
                        'video_id': episode_data['video_id'],
                    },
                    'videoInfo': {
                        'title': episode_data['title'],
                        'duration': episode_data['length'],
                    },
                    'arts': self.createArt(episode_data['thumbnail']),
                    'isPlayable': episode_data['playable'],
                }
                if episode_data.get('show_type') == 3:
                    # Movie
                    info['videoInfo'].update({
                        'mediatype': 'movie',
                    })
                elif episode_data.get('show_type') in [4, 5, 6]:
                    # episode of a series, anime, show
                    info['videoInfo'].update({
                        'tvshowtitle': episode_data['show_title'],
                        'season': int(episode_data['season_number']),
                        'episode': int(episode_data['number']),
                        'mediatype': 'episode',
                    })
                yield info

    def getVideo(self, item_id, season_id, video_id):
        url = VVVVID_SEASON_URL.format(item=item_id, season=season_id)
        self.log('getVideo, url="%s" video_id="%s"' % (url, video_id))
        response = self.getJsonDataFromUrl(url)

        episode_data = [x for x in response if str(
            x.get('video_id')) == video_id][-1]
        embed_info = dec_ei(episode_data['embed_info'])
        if episode_data['video_type'] == AKAMAI_TYPE:
            manifest = re.sub(
                r'https?(://[^/]+)/z/', r'https\1/i/', embed_info
            ).replace('/manifest.f4m', '/master.m3u8')
            self.log('getVideo, manifest="%s"' % manifest, 1)
        else:
            addonutils.notify(episode_data['video_type'])
            self.log(episode_data['video_type'], 3)
        return {
            'label': episode_data['number'] + ' - ' + episode_data['title'],
            'url': manifest or embed_info,
            'videoInfo': {
                'title': episode_data['title'],
                'tvshowtitle': episode_data['show_title'],
                'season': int(episode_data['season_number']),
                'episode': int(episode_data['number']),
                'duration': episode_data['length'],
                'mediatype': 'episode',  # TODO movie
            },
            'arts': self.createArt(episode_data['thumbnail']),
            'isPlayable': episode_data['playable'],
        }

    def getJsonDataFromUrl(self, url, params={}):
        data = self.cache.get(
            '%s.getJsonDataFromUrl, url = %s' % (
                addonutils.ID, addonutils.parameters(params, url)))
        if data:
            return data

        params.update({'conn_id': self.cache.get(
            '%s.conn_id' % addonutils.ID)})
        headers = {
            'User-Agent': USER_AGENT,
            'Cookie': self.cache.get('%s.cookie' % addonutils.ID),
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == requests.codes.ok:
            response.encoding = 'utf-8'
            response = response.json()
            if response.get('result') == 'ok':
                self.cache.set(
                    '%s.getJsonDataFromUrl, url = %s' % (
                        addonutils.ID, addonutils.parameters(params, url)),
                    response.get('data'),
                    expiration=datetime.timedelta(hours=2))
                return self.getJsonDataFromUrl(url, params)
            return None
        else:
            response.raise_for_status()


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
