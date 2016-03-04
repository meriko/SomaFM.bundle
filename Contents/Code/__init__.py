TITLE  = 'SomaFM'
PREFIX = '/music/somafm'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

CHANNEL_URL = 'http://somafm.com/channels.xml'

RE_FILE = Regex('File1=(https?://.+)')

SUPPORT_TITLE         = 'Please support SomaFM!'
SUPPORT_MESSAGE_LONG  = "Visit http://somafm.com/support/ for more information.\r\n\r\nIt's a challenge to run a commercial-free, listener supported radio station in today's economic environment. It seems like we're always begging you for money, and that's because we have to: we rely entirely on you to keep us on the air. So please, make the effort to support SomaFM. We'll be there for you, but we need your financial help.\r\n\r\nWe hope that our music provides you with enjoyment, and we hope you'll offer a little something back our way to finance our continued operation. You can simply make a one-time donation, or sign up for an automatic monthly payment.\r\nSomaFM accepts Visa, Mastercard, Discover, American Express and Paypal online; or you can also send a check or money order drawn on US Dollars."
SUPPORT_MESSAGE_SHORT = 'Please make a donation! Visit http://somafm.com/support/ for more information'

###################################################################################################
def Start():
    ObjectContainer.title1     = TITLE
    ObjectContainer.art        = R(ART)
    DirectoryObject.thumb      = R(ICON)
    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    
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
            summary = SUPPORT_MESSAGE_LONG,
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
    oc = ObjectContainer(title2 = 'Channels')

    channels = XML.ObjectFromURL(CHANNEL_URL)

    for channel in channels.xpath("//channels/channel"):            
        try:
            mp3_url = channel.xpath(".//*[@format='mp3']/text()")[0]
        except:
            mp3_url = None
            
        try:
            aac_url = channel.xpath(".//*[contains(@format,'aac')]/text()")[0]     
        except:
            aac_url = None
            
        if not(mp3_url or aac_url):
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
                try:
                    thumb = channel.xpath(".//image/text()")[0]
                except:
                    thumb = R(ICON)
            
        try:
            summary = channel.xpath(".//description/text()")[0]
        except:
            summary = None
        
        oc.add(
            CreateTrackObject(
                mp3_url = mp3_url,
                aac_url = aac_url,
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
    oc.message = SUPPORT_MESSAGE_SHORT
    
    return oc

####################################################################################################
@route(PREFIX + '/CreateTrackObject', include_container = bool) 
def CreateTrackObject(mp3_url, aac_url, title, thumb, summary, include_container = False):
    items = []

    duration = 86400 * 1000
    
    if mp3_url:
        streams = [
            AudioStreamObject(
                codec = AudioCodec.MP3,
                duration = duration,
                channels = 2
            )
        ]

        items.append(
            MediaObject(
                container = Container.MP3,
                audio_codec = AudioCodec.MP3,
                audio_channels = 2,
                duration = duration,
                parts = [
                    PartObject(
                        key = Callback(PlayMP3, url = mp3_url),
                        streams = streams
                    )
                ]
            )
        )
    
    if aac_url:
        streams = [
            AudioStreamObject(
                codec = AudioCodec.MP3,
                duration = duration,
                channels = 2
            )
        ]
        
        items.append(
            MediaObject(
                container = Container.MP4,
                audio_codec = AudioCodec.AAC,
                audio_channels = 2,
                duration = duration,
                parts = [
                    PartObject(
                        key = Callback(PlayAAC, url = aac_url),
                        streams = streams
                    )
                ]
            )
        )
        
    to = TrackObject(
            key = 
                Callback(
                    CreateTrackObject,
                    mp3_url = mp3_url,
                    aac_url = aac_url,
                    title = title,
                    thumb = thumb,
                    summary = summary,
                    include_container = True
                ),
            rating_key = title,
            title = title,
            thumb = thumb,
            summary = summary,
            items = items
    )
   
    if include_container:
        return ObjectContainer(objects = [to])
    else:
        return to

#################################################################################################### 
@route(PREFIX + '/PlayMP3.mp3')
def PlayMP3(url):
    return PlayAudio(url)
    
#################################################################################################### 
@route(PREFIX + '/PlayAAC.aac')
def PlayAAC(url):
    return PlayAudio(url)
    
#################################################################################################### 
def PlayAudio(url):
    content  = HTTP.Request(url).content
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


