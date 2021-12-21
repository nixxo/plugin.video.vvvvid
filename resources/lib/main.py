from resources.lib import addonutils
from resources.lib.vvvvid import Vvvvid


def addItems(items):
    for item in items:
        addonutils.addListItem(
            label=item.get('label'),
            label2=item.get('label2'),
            path=item.get('path'),
            params=item.get('params'),
            videoInfo=item.get('videoInfo'),
            arts=item.get('arts'),
            isFolder=False if item.get('isPlayable') else True,
        )


def main():
    vvvvid = Vvvvid()
    params = addonutils.getParams()
    vvvvid.log('main, Params = %s' % str(params), 1)
    mode = params.get('mode')
    if mode == 'channels':
        items = vvvvid.getChannelsSection(
            params.get('type'),
            params.get('submode'),
            params.get('channel_id'),
        )
        addItems(items)

    elif mode == 'single':
        items = vvvvid.getElementsFromChannel(
            params.get('channel_id'),
            params.get('type'),
            params.get('filter_id'),
            params.get('category_id'),
            params.get('extras_id'),
        )
        addItems(items)
    elif mode == 'item':
        items = vvvvid.getSeasonsForItem(
            params.get('item_id'), params.get('season_id'))
        addItems(items)
    elif mode == 'play':
        item = vvvvid.getVideo(
            params.get('item_id'), params.get('season_id'), params.get('video_id'))

        item = addonutils.createListItem(
            label=item.get('label'), path=item.get('url'),
            videoInfo=item.get('videoInfo'),
            arts=item.get('arts'), isFolder=False)

        addonutils.setResolvedUrl(item=item, exit=False)
    else:
        # main menu
        items = vvvvid.getMainMenu()
        addItems(items)

    addonutils.endScript(exit=False)
