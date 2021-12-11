class Channel():
    id = ''
    title = ''
    filterList = []
    categoryList = []
    extraList = []
    type = ''
    
    def __init__(self, id, title, filter, category, extra):
        self.id = id
        self.title = title
        self.filterList = filter
        self.categoryList = category
        self.extraList = extra
        self.type = type


class ChannelCategory():
    id = ''
    name = ''
    
    def __init__(self, id, name):
        self.id = id
        self.name = name


class ChannelExtra():
    id = ''
    name = ''
    
    def __init__(self, id, name):
        self.id = id
        self.name = name


class ElementChannel():
    title = ''
    thumb = ''
    show_id = 0
    id = 0
    ondemand_type = 0
    show_type = 0

    def __init__(self, id, show_id, title, thumb, ondemand_type, show_type):
        self.title = title
        self.thumb = thumb
        self.show_id = show_id
        self.id = id
        self.ondemand_type = ondemand_type
        self.show_type = show_type


class ItemPlayableChannel():
    title = ''
    thumb = ''
    show_id = 0
    id = 0
    ondemand_type = 0
    show_type = 0
    seasons = []


class ItemPlayableSeason():
    id = ''
    show_id = ''
    season_id = ''
    episodes = []
    title = ''


class SeasonEpisode():
    show_id = ''
    season_id = ''
    manifest = ''
    title = ''
    thumb = ''
