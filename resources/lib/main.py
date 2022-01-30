from resources.lib import addonutils
from resources.lib.vvvvid import Vvvvid
# import web_pdb


def addItems(items):
    folder_type = []
    for item in items:
        if item.get('videoInfo'):
            folder_type.append(item['videoInfo'].get('mediatype'))
        addonutils.addListItem(
            label=item.get('label'),
            label2=item.get('label2'),
            path=item.get('path'),
            params=item.get('params'),
            videoInfo=item.get('videoInfo'),
            arts=item.get('arts'),
            isFolder=False if item.get('isPlayable') else True,
        )
    folder_type = list(dict.fromkeys(folder_type))
    if len(folder_type) == 1:
        addonutils.setContent(f"{folder_type[0]}s")


def main():
    vvvvid = Vvvvid()
    params = addonutils.getParams()
    vvvvid.log(f"main, Params = {params}", 1)
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
