import urllib.parse as parse
import sys
from resources.lib.vvvvid import *
from resources.lib import addonutils
import xbmcplugin
import routing as routing_plugin
import web_pdb

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
routing = routing_plugin.Plugin()


def add_items(items, isFolder=False):
    web_pdb.set_trace()
    for item in items:
        label = None
        label2 = None
        thumb = None
        path = None
        isPlayable = False

        for property, value in item.items():
            if property == "label":
                label = value
            elif property == "label2":
                label2 = value
            elif property == "thumb":
                thumb = value
            elif property == "path":
                path = value
            elif property == "is_playable":
                isPlayable = value
            else:
                # TODO: properties
                pass

        addonutils.addListItem(
            label=label,
            label2=label2,
            path=path,
            params=path,
            thumb=thumb,
            isFolder=not isPlayable)

    xbmcplugin.endOfDirectory(__handle__)


@routing.route("/")
def show_main_channels():
    items = [
        {
            "label": ROOT_LABEL_ANIME,
            "path": routing.url_for(showAnimeChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_MOVIES,
            "path": routing.url_for(showMovieChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_SHOWS,
            "path": routing.url_for(showTvChannels),
            "is_playable": False,
        },
        {
            "label": ROOT_LABEL_SERIES,
            "path": routing.url_for(showSeriesChannels),
            "is_playable": False,
        },
    ]

    add_items(items)


@routing.route("/movie/channels")
def showMovieChannels():
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showMovieChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showMovieChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showMovieChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showMovieSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/filter/<filter>")
@routing.route("/movie/channel/<idChannel>/category/<category>")
@routing.route("/movie/channel/<idChannel>/extra/<extra>")
@routing.route("/movie/channel/<idChannel>")
def showMovieSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_MOVIES, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumb"] = element.thumb
        item["path"] = routing.url_for(showSingleMovieItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/filters")
def showMovieChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/categories")
def showMovieChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/channel/<idChannel>/extras")
def showMovieChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_MOVIES)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showMovieSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/movie/item/<idItem>")
def showSingleMovieItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleMovieItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "movies")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumb"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumb"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=parse.quote_plus(episode.manifest),
                    title=parse.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/movie/item/<seasonId>/<idItem>")
def showSingleMovieItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "movies")
    for season in itemPlayable.seasons:
        if season.season_id == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumb"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumb"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=parse.quote_plus(episode.manifest),
                        title=parse.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


@routing.route("/show/channels")
def showTvShowsChannels():
    channels = get_section_channels(MODE_SHOWS)
    items = []
    for channel in channels:
        print


"""

Start tv
"""


@routing.route("/tv/channels")
def showTvChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(showTvChannelFilters, idChannel=channel.id)
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showTvChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showTvChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showTvSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/filter/<filter>")
@routing.route("/tv/channel/<idChannel>/category/<category>")
@routing.route("/tv/channel/<idChannel>/extra/<extra>")
@routing.route("/tv/channel/<idChannel>")
def showTvSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_SHOWS, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumb"] = element.thumb
        item["path"] = routing.url_for(showSingleTvItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/filters")
def showTvChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/categories")
def showTvChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=channel.id, category=str(category.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/channel/<idChannel>/extras")
def showTvChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showTvSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/tv/item/<idItem>")
def showSingleTvItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleTvItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "tvshows")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumb"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumb"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=parse.quote_plus(episode.manifest),
                    title=parse.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/tv/item/<seasonId>/<idItem>")
def showSingleTvItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "tvshows")
    for season in itemPlayable.seasons:
        if season.season_id == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumb"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumb"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=parse.quote_plus(episode.manifest),
                        title=parse.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""
end tv
"""

"""
start anime
"""


@routing.route("/anime/channels")
def showAnimeChannels():
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showAnimeChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showAnimeChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(showAnimeChannelExtras, idChannel=channel.id)
        else:
            item["path"] = routing.url_for(showAnimeSingleChannel, idChannel=channel.id)
        items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/filter/<filter>")
@routing.route("/anime/channel/<idChannel>/category/<category>")
@routing.route("/anime/channel/<idChannel>/extra/<extra>")
@routing.route("/anime/channel/<idChannel>")
def showAnimeSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_ANIME, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumb"] = element.thumb
        item["path"] = routing.url_for(showSingleAnimeItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/filters")
def showAnimeChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/categories")
def showAnimeChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/channel/<idChannel>/extras")
def showAnimeChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_ANIME)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showAnimeSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/anime/item/<idItem>")
def showSingleAnimeItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            print(
                "showSingleAnimeItem: {} id={} season={}".format(
                    season.title, idItem, season.season_id
                )
            )
            item["path"] = routing.url_for(
                showSingleAnimeItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "tvshows")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumb"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumb"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=parse.quote_plus(episode.manifest),
                    title=parse.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/anime/item/<seasonId>/<idItem>")
def showSingleAnimeItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    #web_pdb.set_trace()
    xbmcplugin.setContent(__handle__, "tvshows")
    for season in itemPlayable.seasons:
        if str(season.season_id) == str(seasonId):
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumb"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumb"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=parse.quote_plus(episode.manifest),
                        title=parse.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""

end anime
"""
"""

Start series
"""


@routing.route("/series/channels")
def showSeriesChannels():
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    items = []
    for channel in currentGlobalChannels:
        item = dict()
        item["label"] = channel.title
        item["is_playable"] = False
        if len(channel.filterList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelFilters, idChannel=channel.id
            )
        elif len(channel.categoryList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelCategories, idChannel=channel.id
            )
        elif len(channel.extraList) != 0:
            item["path"] = routing.url_for(
                showSeriesChannelExtras, idChannel=channel.id
            )
        else:
            item["path"] = routing.url_for(
                showSeriesSingleChannel, idChannel=channel.id
            )
        items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/filter/<filter>")
@routing.route("/series/channel/<idChannel>/category/<category>")
@routing.route("/series/channel/<idChannel>/extra/<extra>")
@routing.route("/series/channel/<idChannel>")
def showSeriesSingleChannel(idChannel, filter="", category="", extra=""):
    channelsElements = get_elements_from_channel(
        idChannel, MODE_SERIES, filter, category, extra
    )
    items = []
    for element in channelsElements:
        item = dict()
        item["label"] = element.title
        item["is_playable"] = False
        item["icon"] = element.thumb
        item["thumb"] = element.thumb
        item["path"] = routing.url_for(showSingleSeriesItem, idItem=element.show_id)
        items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/filters")
def showSeriesChannelFilters(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for filter in channel.filterList:
                item = dict()
                item["label"] = str(filter)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel, idChannel=channel.id, filter=str(filter)
                )
                items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/categories")
def showSeriesChannelCategories(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for category in channel.categoryList:
                item = dict()
                item["label"] = str(category.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel,
                    idChannel=channel.id,
                    category=str(category.id),
                )
                items.append(item)

    add_items(items)


@routing.route("/series/channel/<idChannel>/extras")
def showSeriesChannelExtras(idChannel):
    items = []
    channels = get_section_channels(MODE_SHOWS)
    currentGlobalChannels = channels
    for channel in currentGlobalChannels:
        if channel.id == idChannel:
            for extra in channel.extraList:
                item = dict()
                item["label"] = str(extra.name)
                item["is_playable"] = False
                item["path"] = routing.url_for(
                    showSeriesSingleChannel, idChannel=extra.id, extra=str(extra.id)
                )
                items.append(item)

    add_items(items)


@routing.route("/series/item/<idItem>")
def showSingleSeriesItem(idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    if len(itemPlayable.seasons) > 1:
        for season in itemPlayable.seasons:
            item = dict()
            item["label"] = season.title
            item["is_playable"] = False
            item["path"] = routing.url_for(
                showSingleSeriesItemSeason, idItem=idItem, seasonId=season.season_id
            )
            items.append(item)
    else:
        episodes = itemPlayable.seasons[0].episodes
        xbmcplugin.setContent(__handle__, "series")
        for episode in episodes:
            item = dict()
            item["label"] = episode.title
            item["icon"] = episode.thumb
            item["thumb"] = episode.thumb
            props = dict()
            props.update(fanart_image=item["thumb"])
            item["properties"] = props
            if episode.stream_type == F4M_TYPE:
                item["path"] = routing.url_for(
                    playManifest,
                    manifest=parse.quote_plus(episode.manifest),
                    title=parse.quote_plus(episode.title),
                )
                item["is_playable"] = False
            elif episode.stream_type == M3U_TYPE:
                item["path"] = episode.manifest
                item["is_playable"] = True
            items.append(item)

    add_items(items)


@routing.route("/series/item/<seasonId>/<idItem>")
def showSingleSeriesItemSeason(seasonId, idItem):
    items = []
    itemPlayable = get_item_playable(idItem)
    xbmcplugin.setContent(__handle__, "series")
    for season in itemPlayable.seasons:
        if season.season_id == seasonId:
            for episode in season.episodes:
                item = dict()
                item["label"] = episode.title
                item["icon"] = episode.thumb
                item["thumb"] = episode.thumb
                props = dict()
                props.update(fanart_image=item["thumb"])
                item["properties"] = props
                if episode.stream_type == F4M_TYPE:
                    item["path"] = routing.url_for(
                        playManifest,
                        manifest=parse.quote_plus(episode.manifest),
                        title=parse.quote_plus(episode.title),
                    )
                    item["is_playable"] = False
                elif episode.stream_type == M3U_TYPE:
                    item["path"] = episode.manifest
                    item["is_playable"] = True
                items.append(item)

    add_items(items)


"""
end series
"""

def runPlugin():
    routing.run()
