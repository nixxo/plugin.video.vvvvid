from resources.lib import addonutils
from resources.lib.vvvvid import Vvvvid
import web_pdb


def addItems(items):
    #web_pdb.set_trace()
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
    # web_pdb.set_trace()
    vvvvid = Vvvvid()
    # addonutils.setContent('files')
    params = addonutils.getParams()
    addonutils.log('main, Params = %s' % str(params))
    mode = params.get('mode')
    #web_pdb.set_trace()
    if mode == 'channels':
        #web_pdb.set_trace()
        items = vvvvid.getChannelsSection(
            params.get('type'),
            params.get('submode'),
            params.get('channel_id'),
        )
        addItems(items)

    elif mode == 'single':
        # web_pdb.set_trace()
        items = vvvvid.getElementsFromChannel(
            params.get('channel_id'),
            params.get('type'),
            params.get('filter_id'),
            params.get('category_id'),
            params.get('extras_id')
        )
        # addonutils.setContent('tvshows')
        addItems(items)
    elif mode == 'item':
        # web_pdb.set_trace()
        items = vvvvid.getSeasonsForItem(params.get('item_id'), params.get('season_id'))
        addItems(items)
    elif mode == 'play':
        addonutils.setResolvedUrl(url=params.get('video'), exit=False)
    else:
        # main menu
        items = vvvvid.getMainMenu()
        addItems(items)

    addonutils.endScript(exit=False)
