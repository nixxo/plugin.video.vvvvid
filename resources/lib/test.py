from resources.lib import addonutils
from resources.lib import vivid
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
    addonutils.setContent('files')
    params = addonutils.getParams()
    addonutils.log('main, Params = %s' % str(params))
    mode = params.get('mode')
    #web_pdb.set_trace()
    if mode == 'channels':
        #web_pdb.set_trace()
        items = vivid.getChannelsSection(
            params.get('type'),
            params.get('submode'),
            params.get('channel_id'),
        )
        addItems(items)

    elif mode == 'single':
        #web_pdb.set_trace()
        items = []
        if params.get('submode'):
            pass
        else:
            items = vivid.getElementsFromChannel(
                params.get('channel_id'),
                params.get('type'),
                params.get('filter_id'),
                params.get('category_id'),
                params.get('extras_id')
            )
            addonutils.setContent('tvshows')
            addItems(items)
    elif mode == 'item':
        #web_pdb.set_trace()
        items = vivid.getSeasonsForItem(params.get('item_id'), params.get('season_id'))
        addItems(items)
    elif mode == 'play':
        addonutils.setResolvedUrl(url=params.get('video'), exit=False)
    else:
        # main menu
        items = vivid.getMainMenu()
        addItems(items)

    addonutils.endScript(exit=False)
