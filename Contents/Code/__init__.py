TITLE  = 'Soma FM'
PREFIX = '/music/somafm'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

CHANNEL_URL = 'http://somafm.com/channels.xml'

RE_FILE = Regex('File1=(https?://.+)')

SUPPORT_TITLE   = 'Please support SomaFM!'
SUPPORT_MESSAGE = "Visit http://somafm.com/support/ for more information.\r\n\r\nIt's a challenge to run a commercial-free, listener supported radio station in today's economic environment. It seems like we're always begging you for money, and that's because we have to: we rely entirely on you to keep us on the air. So please, make the effort to support SomaFM. We'll be there for you, but we need your financial help.\r\n\r\nWe hope that our music provides you with enjoyment, and we hope you'll offer a little something back our way to finance our continued operation. You can simply make a one-time donation, or sign up for an automatic monthly payment.\r\nSomaFM accepts Visa, Mastercard, Discover, American Express and Paypal online; or you can also send a check or money order drawn on US Dollars."

###################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = R(ART)
    DirectoryObject.thumb  = R(ICON)
    HTTP.CacheTime         = CACHE_1HOUR
    
###################################################################################################
@handler(PREFIX, TITLE, thumb = ICON, art = ART)
def MainMenu():
    oc = ObjectContainer()
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Support
                ),
            title = SUPPORT_TITLE,
            summary = SUPPORT_MESSAGE,
            thumb = R(ICON)
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Channels
                ),
            title = 'Channels',
            thumb = R(ICON)
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/Channels')
def Channels():
    oc = ObjectContainer()
    
    channels = XML.ObjectFromURL(CHANNEL_URL)

    for channel in channels.xpath("//channels/channel"):
        try:
            id = channel.xpath("./@id")[0]
        except:
            continue
            
        try:
            title = channel.xpath(".//title/text()")[0]
        except:
            title = None
            
        try:
            thumb = channel.xpath(".//xlimage/text()")[0]
        except:
            try:
                thumb = channel.xpath(".//largeimage/text()")[0] 
            except:
                thumb = R(ICON)
            
        try:
            summary = channel.xpath(".//description/text()")[0]
        except:
            summary = None
        
        oc.add(
            CreateTrackObject(
                id = id,
                title = title,
                thumb = thumb,
                summary = summary
            )
        )
    
    return oc

####################################################################################################
@route(PREFIX + '/Support') 
def Support():
    oc = ObjectContainer()
    
    oc.header  = SUPPORT_TITLE
    oc.message = SUPPORT_MESSAGE
    
    return oc

####################################################################################################
@route(PREFIX + '/CreateTrackObject', include_container = bool) 
def CreateTrackObject(id, title, thumb, summary, include_container = False):
    to = TrackObject(
            key = 
                Callback(
                    CreateTrackObject,
                    id = id,
                    title = title,
                    thumb = thumb,
                    summary = summary,
                    include_container = True
                ),
            rating_key = title,
            title = title,
            thumb = thumb,
            summary = summary,
            items = [
                MediaObject(
                    container = Container.MP4,
                    audio_codec = AudioCodec.AAC,
                    audio_channels = 2,
                    bitrate = 130,
                    parts = [
                        PartObject(
                            key = Callback(PlayAudio, id = id, fmt = 'aac', ext = 'aac')
                        )
                    ]
                ),
                MediaObject(
                    container = Container.MP3,
                    audio_codec = AudioCodec.MP3,
                    audio_channels = 2,
                    bitrate = 128,
                    parts = [
                        PartObject(
                            key = Callback(PlayAudio, id = id, fmt = 'mp3', ext = 'mp3')
                        )
                    ]
                )
            ]
    )
   
    if include_container:
        return ObjectContainer(objects = [to])
    else:
        return to

####################################################################################################
def PlayAudio(id, fmt):
    channels = XML.ObjectFromURL(CHANNEL_URL)

    for channel in channels.xpath("//channels/channel"):
        if id != channel.xpath("./@id")[0]:
            continue
        
        if fmt == 'mp3':
            url = channel.xpath(".//fastpls/text()")[0]
        else:
            url = channel.xpath(".//highestpls/text()")[0]
        
        content  = HTTP.Request(url, cacheTime = 0).content
        file_url = RE_FILE.search(content)
    
        if file_url:
            stream_url = file_url.group(1)
            if stream_url[-1] == '/':
                stream_url += ';'
            else:
                stream_url += '/;'
            return Redirect(stream_url)
        else:
            raise Ex.MediaNotAvailable
            
    raise Ex.MediaNotAvailable

