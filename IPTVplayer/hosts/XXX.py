# -*- coding: utf-8 -*-
 
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.icomponents.ihost import IHost, CDisplayListItem, RetHost, CUrlItem
import Plugins.Extensions.IPTVPlayer.libs.pCommon as pCommon
from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvtools import printDBG, CSearchHistoryHelper, CSelOneLink, GetTmpDir, GetCookieDir, iptv_system, GetPluginDir
from Plugins.Extensions.IPTVPlayer.iptvdm.iptvdh import DMHelper
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser 
from Plugins.Extensions.IPTVPlayer.itools.iptvfilehost import IPTVFileHost
from Plugins.Extensions.IPTVPlayer.dToolsSet.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError 
###################################################
# FOREIGN import
###################################################
import re, urllib, urllib2, base64, math, hashlib, random
try:
    import simplejson
except:
    import json as simplejson   
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import config, ConfigSelection, ConfigYesNo, ConfigText, ConfigInteger, getConfigListEntry, ConfigPIN, ConfigDirectory
from time import sleep, time as time_time
from os import remove as os_remove, path as os_path, system as os_system
###################################################
# E2 GUI COMMPONENTS 
###################################################
from Plugins.Extensions.IPTVPlayer.icomponents.asynccall import MainSessionWrapper, iptv_js_execute
from Screens.MessageBox import MessageBox 
###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.xxxwymagajpin = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxlist = ConfigDirectory(default = "/hdd/")
config.plugins.iptvplayer.xxxsortuj = ConfigYesNo(default = True)
config.plugins.iptvplayer.xxxsearch = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortmfc = ConfigYesNo(default = False)
config.plugins.iptvplayer.xxxsortall = ConfigYesNo(default = True)
config.plugins.iptvplayer.camsoda = ConfigSelection(default="0", choices = [("0",_("https")), ("1",_("rtmp"))])
config.plugins.iptvplayer.delay = ConfigInteger(2, (0, 5))   
config.plugins.iptvplayer.xhamstertag = ConfigYesNo(default = False)
config.plugins.iptvplayer.xhamsterchannel = ConfigYesNo(default = False)

def GetConfigList():
    optionList = []
    optionList.append( getConfigListEntry( "Wymagaj pin:", config.plugins.iptvplayer.xxxwymagajpin ) )
    optionList.append( getConfigListEntry( "Lokalizacja pliku xxxlist.txt :", config.plugins.iptvplayer.xxxlist) )
    optionList.append( getConfigListEntry( "Sortuj xxxlist :", config.plugins.iptvplayer.xxxsortuj) )
    optionList.append( getConfigListEntry( "Sortuj Myfreecams :", config.plugins.iptvplayer.xxxsortmfc) )
    optionList.append( getConfigListEntry( "Globalne wyszukiwanie :", config.plugins.iptvplayer.xxxsearch) )
    optionList.append( getConfigListEntry( "Globalne sortowanie :", config.plugins.iptvplayer.xxxsortall) )
    optionList.append( getConfigListEntry( "Camsoda stream :", config.plugins.iptvplayer.camsoda) )
    optionList.append( getConfigListEntry( "UPDATE delay :", config.plugins.iptvplayer.delay) )
    optionList.append( getConfigListEntry( "Dodaj tagi do XHAMSTER :", config.plugins.iptvplayer.xhamstertag) )
    optionList.append( getConfigListEntry( "Dodaj channel do XHAMSTER :", config.plugins.iptvplayer.xhamsterchannel) )

    return optionList
###################################################

###################################################
# Title of HOST
###################################################
def gettytul():
    return 'XXX'

class IPTVHost(IHost):
    LOGO_NAME = 'XXXlogo.png'
    PATH_TO_LOGO = resolveFilename(SCOPE_PLUGINS, 'Extensions/IPTVPlayer/icons/logos/' + LOGO_NAME )

    def __init__(self):
        printDBG( "init begin" )
        self.host = Host()
        self.prevIndex = []
        self.currList = []
        self.prevList = []
        printDBG( "init end" )
        
    def isProtectedByPinCode(self):
        return config.plugins.iptvplayer.xxxwymagajpin.value
    
    def getLogoPath(self):  
        return RetHost(RetHost.OK, value = [self.PATH_TO_LOGO])

    def getInitList(self):
        printDBG( "getInitList begin" )
        self.prevIndex = []
        self.currList = self.host.getInitList()
        self.host.setCurrList(self.currList)
        self.prevList = []
        printDBG( "getInitList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( "getListForItem begin" )
        self.prevIndex.append(Index)
        self.prevList.append(self.currList)
        self.currList = self.host.getListForItem(Index, refresh, selItem)
        printDBG( "getListForItem end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getPrevList(self, refresh = 0):
        printDBG( "getPrevList begin" )
        if(len(self.prevList) > 0):
            self.prevIndex.pop()
            self.currList = self.prevList.pop()
            self.host.setCurrList(self.currList)
            printDBG( "getPrevList end OK" )
            return RetHost(RetHost.OK, value = self.currList)
        else:
            printDBG( "getPrevList end ERROR" )
            return RetHost(RetHost.ERROR, value = [])

    def getCurrentList(self, refresh = 0):
        printDBG( "getCurrentList begin" )
        printDBG( "getCurrentList end" )
        return RetHost(RetHost.OK, value = self.currList)

    def getLinksForVideo(self, Index = 0, item = None):
        return RetHost(RetHost.NOT_IMPLEMENTED, value = [])
        
    def getResolvedURL(self, url):
        printDBG( "getResolvedURL begin" )
        if url != None and url != '':        
            ret = self.host.getResolvedURL(url)
            if ret != None and ret != '':        
               printDBG( "getResolvedURL ret: "+str(ret))
               list = []
               list.append(ret)
               printDBG( "getResolvedURL end OK" )
               return RetHost(RetHost.OK, value = list)
            else:
               printDBG( "getResolvedURL end" )
               return RetHost(RetHost.NOT_IMPLEMENTED, value = [])                
        else:
            printDBG( "getResolvedURL end" )
            return RetHost(RetHost.NOT_IMPLEMENTED, value = [])

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "getSearchResults begin" )
        printDBG( "getSearchResults pattern: " +pattern)
        self.prevIndex.append(0)
        self.prevList.append(self.currList)
        self.currList = self.host.getSearchResults(pattern, searchType)
        printDBG( "getSearchResults end" )
        return RetHost(RetHost.OK, value = self.currList)

    ###################################################
    # Additional functions on class IPTVHost
    ###################################################

class Host:
    XXXversion = "21.0.6.9"
    XXXremote  = "0.0.0.0"
    currList = []
    MAIN_URL = ''
    SEARCH_proc = ''
    
    def __init__(self):
        printDBG( 'Host __init__ begin' )
        self.cm = pCommon.common()
        self.up = urlparser() 
        self.history = CSearchHistoryHelper('xxx')
        self.sessionEx = MainSessionWrapper() 
        self.currList = []
        _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/blob/master/IPTVPlayer/hosts/hostXXX.pyDISABLED'
        query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        try:
           data = self.cm.getURLRequestData(query_data)
           #printDBG( 'Host init data: '+data )
           r=re.search( r'XXXversion.*?class="s">"(.*?)"',data)
           if r:
              printDBG( 'release = '+r.group(1) )
              self.XXXremote=r.group(1)
        except:
           printDBG( 'Host init query error' )
        printDBG( 'Host __init__ end' )
        
    def setCurrList(self, list):
        printDBG( 'Host setCurrList begin' )
        self.currList = list
        printDBG( 'Host setCurrList end' )
        return 

    def getInitList(self):
        printDBG( 'Host getInitList begin' )
        self.currList = self.listsItems(-1, '', 'main-menu')
        printDBG( 'Host getInitList end' )
        return self.currList

    def getListForItem(self, Index = 0, refresh = 0, selItem = None):
        printDBG( 'Host getListForItem begin' )
        valTab = []
        if len(self.currList[Index].urlItems) == 0:
           return valTab
        valTab = self.listsItems(Index, self.currList[Index].urlItems[0], self.currList[Index].urlSeparateRequest)
        self.currList = valTab
        printDBG( 'Host getListForItem end' )
        return self.currList

    def getSearchResults(self, pattern, searchType = None):
        printDBG( "Host getSearchResults begin" )
        printDBG( "Host getSearchResults pattern: " +pattern)
        valTab = []
        valTab = self.listsItems(-1, pattern, 'SEARCH')
        self.currList = valTab
        printDBG( "Host getSearchResults end" )
        return self.currList

    def getPage(self, baseUrl, cookie_domain, cloud_domain, params={}, post_data=None):
        COOKIEFILE = os_path.join(GetCookieDir(), cookie_domain)
        #self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
        self.USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
        self.HEADER = {'User-Agent': self.USER_AGENT, 'Accept': 'text/html'}
        params['cloudflare_params'] = {'domain':cloud_domain, 'cookie_file':COOKIEFILE, 'User-Agent':self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, params, post_data)

    def listsItems(self, Index, url, name = ''):
        printDBG( 'Host listsItems begin' )
        printDBG( 'Host listsItems url: '+url )
        valTab = []

        if name == 'main-menu':
           printDBG( 'Host listsItems begin name='+name )
           if self.XXXversion <> self.XXXremote and self.XXXremote <> "0.0.0.0":
              valTab.append(CDisplayListItem('---UPDATE---','UPDATE MENU',        CDisplayListItem.TYPE_CATEGORY,           [''], 'UPDATE',  '', None)) 
           valTab.append(CDisplayListItem('4TUBE',          'www.4tube.com',      CDisplayListItem.TYPE_CATEGORY, ['http://www.4tube.com/tags'],          '4tube',   'http://cdn1.ht.ui.4tube.com/assets/img/layout/4tube-logo-1f503fd81c.png', None)) 
           valTab.append(CDisplayListItem('EPORNER',        'www.eporner.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.eporner.com/categories/'],   'eporner', 'http://static.eporner.com/new/logo.png', None)) 
           valTab.append(CDisplayListItem('TUBE8',          'www.tube8.com',      CDisplayListItem.TYPE_CATEGORY, ['http://www.tube8.com/categories.html'], 'tube8',   'http://cdn1.static.tube8.phncdn.com/images/t8logo.png', None)) 
           valTab.append(CDisplayListItem('YOUPORN',        'wwww.youporn.com',   CDisplayListItem.TYPE_CATEGORY, ['http://www.youporn.com/categories/alphabetical/'],'youporn', 'http://cdn1.static.youporn.phncdn.com/cb/bundles/youpornwebfront/images/l_youporn_black.png', None)) 
           valTab.append(CDisplayListItem('PORNHUB',        'www.pornhub.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhub.com/categories'],    'pornhub', 'http://cdn1.static.pornhub.phncdn.com/images/pornhub_logo.png', None)) 
           valTab.append(CDisplayListItem('HDPORN',         'www.hdporn.net',     CDisplayListItem.TYPE_CATEGORY, ['http://www.hdporn.net/channels/'],      'hdporn',  'http://www.hdporn.com/gfx/logo-404.jpg', None)) 
           valTab.append(CDisplayListItem('REDTUBE',        'www.redtube.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.redtube.com/channels'],      'redtube', 'http://img02.redtubefiles.com/_thumbs/design/logo/redtube_260x52_black.png', None)) 
           valTab.append(CDisplayListItem('XHAMSTER',       'xhamster.com',       CDisplayListItem.TYPE_CATEGORY, ['http://xhamster.com/channels.php'],     'xhamster','http://eu-st.xhamster.com/images/tpl2/logo.png', None)) 
           valTab.append(CDisplayListItem('HENTAIGASM',     'hentaigasm.com',     CDisplayListItem.TYPE_CATEGORY, ['http://hentaigasm.com'],                'hentaigasm','http://hentaigasm.com/wp-content/themes/detube/images/logo.png', None)) 
           valTab.append(CDisplayListItem('XVIDEOS',        'www.xvideos.com',    CDisplayListItem.TYPE_CATEGORY, ['http://www.xvideos.com'],               'xvideos', 'http://www.savido.net/img/xvideos_logo.png', None)) 
           valTab.append(CDisplayListItem('XNXX',           'www.xnxx.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.xnxx.com'],                  'xnxx',    'http://www.naughtyalysha.com/tgp/xnxx/xnxx-porn-recip.jpg', None)) 
           valTab.append(CDisplayListItem('BEEG',           'beeg.com',           CDisplayListItem.TYPE_CATEGORY, ['http://api2.beeg.com/api/v6/1738/index/main/0/mobile'],                      'beeg',    'http://staticloads.com/img/logo/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNRABBIT',     'www.pornrabbit.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornrabbit.com/page/categories/'],'pornrabbit','http://cdn1.static.pornrabbit.com/pornrabbit/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNHD',     'www.pornhd.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornhd.com/category'],'pornhd','http://f90f5c1c633346624330effd22345bfc.lswcdn.net/image/logo.png', None)) 
           valTab.append(CDisplayListItem('AH-ME',     'www.ah-me.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.ah-me.com/channels.php'],'AH-ME','http://ahmestatic.fuckandcdn.com/ah-me/ahmestatic/v20/common/ah-me/img/logo.jpg', None)) 
           valTab.append(CDisplayListItem('AMATEURPORN',     'www.amateurporn.net', CDisplayListItem.TYPE_CATEGORY, ['http://www.amateurporn.net/channels/'],'AMATEURPORN', 'http://www.amateurporn.net/images/amateur-porn.png', None)) 
           valTab.append(CDisplayListItem('YOUJIZZ',     'http://www.youjizz.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.youjizz.com/categories'],'YOUJIZZ', 'http://www.sample-made.com/cms/content/uploads/2015/05/youjizz_logo-450x400.jpg', None)) 
           valTab.append(CDisplayListItem('DACHIX',     'http://www.dachix.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.dachix.com/categories'],'DACHIX', 'http://thumbs.dachix.com/images/dachixcom_logo_noir.png', None)) 
           valTab.append(CDisplayListItem('DRTUBER',     'http://www.drtuber.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.drtuber.com/categories'],'DRTUBER', 'http://static.drtuber.com/templates/frontend/mobile/images/logo.png', None)) 
           valTab.append(CDisplayListItem('TNAFLIX',     'https://www.tnaflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.tnaflix.com/categories'],'TNAFLIX', 'https://pbs.twimg.com/profile_images/1109542593/logo_400x400.png', None)) 
           valTab.append(CDisplayListItem('EL-LADIES - JUST-EROPROFILE',     'http://search.el-ladies.com', CDisplayListItem.TYPE_CATEGORY, ['http://search.el-ladies.com'],'EL-LADIES', 'http://amateurblogs.eroprofile.com/img/ep_new_gallery_header.png', None)) 
           valTab.append(CDisplayListItem('EXTREMETUBE',     'http://www.extremetube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.extremetube.com/video-categories'],'EXTREMETUBE', 'http://www.wp-tube-plugin.com/feed-images/extremetube.png', None)) 
           valTab.append(CDisplayListItem('RUPORN',     'http://ruporn.video/', CDisplayListItem.TYPE_CATEGORY, ['http://ruporn.video/categories.html'],'RUSPORN', 'http://ruporn.video/App_Themes/ruporn/img/logo.png?12013', None)) 
           valTab.append(CDisplayListItem('PORN720',     'http://porn720.net/', CDisplayListItem.TYPE_CATEGORY, ['http://porn720.net/'],'PORN720', 'http://porn720.net/wp-content/themes/porn720/img/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNTREX   (python > v2.7.9)',     'http://www.porntrex.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.porntrex.com/categories/'],'PORNTREX', 'https://www.porntrex.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNDOE',     'http://www.porndoe.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.porndoe.com/categories'],'PORNDOE', 'http://porndoe.com/themes/frontend/white/assets/images/logo_fb.jpg', None)) 
           valTab.append(CDisplayListItem('PORNfromCZECH',     'http://www.pornfromczech.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.pornfromczech.com/'],'PORNFROMCZECH', 'http://pornfromczech.com/wp-content/uploads/2013/03/PfC_logo.png', None)) 
           valTab.append(CDisplayListItem('FILMYPORNO',     'http://www.filmyporno.tv', CDisplayListItem.TYPE_CATEGORY, ['http://www.filmyporno.tv/channels/'],'FILMYPORNO', 'http://www.filmyporno.tv/templates/default_tube2016/images/logo.png', None)) 
           valTab.append(CDisplayListItem('CLIPHUNTER',     'http://www.cliphunter.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.cliphunter.com/categories/'],'CLIPHUNTER', 'http://www.cliphunter.com/gfx/new/logo.png', None)) 
           valTab.append(CDisplayListItem('EMPFLIX',     'http://www.empflix.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.empflix.com/categories.php'],'EMPFLIX', 'http://pornoracle.com/wp-content/uploads/2013/11/empflix1.jpg', None)) 
           valTab.append(CDisplayListItem('PORNOHUB',     'http://pornohub.su/', CDisplayListItem.TYPE_CATEGORY, ['http://pornohub.su/'],'PORNOHUB', 'http://st.pornohub.su/pornohub.png', None)) 
           valTab.append(CDisplayListItem('THUMBZILLA',     'http://www.thumbzilla.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.thumbzilla.com/'],'THUMBZILLA', 'https://cdn-d-static.pornhub.com/tz-static/images/pc/logo.png?cache=2016111010', None)) 
           valTab.append(CDisplayListItem('YUVUTU',     'http://www.yuvutu.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.yuvutu.com/categories/'],'YUVUTU', 'http://www.yuvutu.com/themes/yuvutu_v2/images/yuvutu_logo.png', None)) 
           valTab.append(CDisplayListItem('X3XTUBE',     'http://www.x3xtube.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.x3xtube.com/channels.php'],'X3XTUBE', 'http://img.x3xtube.com/vids/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNICOM',     'http://pornicom.com', CDisplayListItem.TYPE_CATEGORY, ['http://pornicom.com/categories/'],'PORNICOM', 'http://pornicom.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('HDZOG',     'http://www.hdzog.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hdzog.com/categories/'],'HDZOG', 'https://pbs.twimg.com/profile_images/484686238402629632/5fzwWkJQ_bigger.png', None)) 
           valTab.append(CDisplayListItem('HCLIPS',     'http://www.hclips.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.hclips.com/categories/'],'HCLIPS', 'http://www.hclips.com/images/logo.png', None)) 
           valTab.append(CDisplayListItem('PORNOMENGE',     'https://www.pornomenge.com', CDisplayListItem.TYPE_CATEGORY, ['https://www.pornomenge.com/kategorien/'],'PORNOMENGE', 'https://th.servitubes.com/videos/8/1/b/5/1/81b51795337b047be07d3b3790b97c923535dffb.mp4-preview-3.jpg', None)) 
           if config.plugins.iptvplayer.xxxsortall.value:
               valTab.sort(key=lambda poz: poz.name)
           self.SEARCH_proc=name
           if config.plugins.iptvplayer.xxxsearch.value:
               valTab.insert(0,CDisplayListItem('---Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
               valTab.insert(0,CDisplayListItem('---Szukaj',  'Szukaj filmów',             CDisplayListItem.TYPE_SEARCH,             [''], '',        '', None)) 
           valTab.append(CDisplayListItem('FOTKA-PL-KAMERKI',     'http://www.fotka.pl/kamerki', CDisplayListItem.TYPE_CATEGORY, ['http://api.fotka.pl/v2/cams/get?page=1&limit=100&gender=f'],'FOTKA-PL-KAMERKI', 'https://pbs.twimg.com/profile_images/3086758992/6fb5cc2ee2735c334d0363bcb01a52ca_400x400.png', None)) 
           valTab.append(CDisplayListItem('CHATURBATE',     'chaturbate.com', CDisplayListItem.TYPE_CATEGORY, ['https://chaturbate.com'],'CHATURBATE','http://webcamstartup.com/wp-content/uploads/2014/12/chaturbate.jpg', None)) 
           valTab.append(CDisplayListItem('XHAMSTERLIVE',       "Kamerki",       CDisplayListItem.TYPE_CATEGORY,['http://xhamsterlive.com'], 'xhamster-cams', 'https://cdn.stripchat.com/assets/common/images/favicon_xh.png',None))
           valTab.append(CDisplayListItem('CAM4 - KAMERKI',     'http://www.cam4.pl', CDisplayListItem.TYPE_CATEGORY, ['http://www.cam4.pl/female'],'CAM4-KAMERKI', 'https://static.cam4.com/web/images/logo.png', None)) 
           valTab.append(CDisplayListItem('MYFREECAMS',     'http://www.myfreecams.com', CDisplayListItem.TYPE_CATEGORY, ['http://www.myfreecams.com/#Homepage'],'MYFREECAMS', 'http://goatcheesedick.com/wp-content/uploads/2015/08/myfreecams-logo1.png', None)) 
           valTab.append(CDisplayListItem('LIVEJASMIN',     'http://new.livejasmin.com', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/girl/free+chat?selectedFilters=12'],'LIVEJASMIN', 'http://livejasmins.fr/livejasmin-france.png', None)) 
           valTab.append(CDisplayListItem('BONGACAMS',     'https://pl.bongacams.com/', CDisplayListItem.TYPE_CATEGORY, ['https://pl.bongacams.com/'],'BONGACAMS', 'http://i.bongacams.com/images/bongacams_logo3_header.png', None)) 
           valTab.append(CDisplayListItem('RAMPANT',     'https://www.rampant.tv', CDisplayListItem.TYPE_CATEGORY, ['https://www.rampant.tv/channels'],'RAMPANT', 'https://www.rampant.tv/new-images/rampant_logo.png', None)) 
           valTab.append(CDisplayListItem('SHOWUP   - live cams',       'showup.tv',          CDisplayListItem.TYPE_CATEGORY, ['http://showup.tv'],                     'showup',  'http://mamstartup.pl/i/articles/3619_newl.jpg', None)) 
           valTab.append(CDisplayListItem('ZBIORNIK - live cams',       'zbiornik.tv',       CDisplayListItem.TYPE_CATEGORY, ['http://zbiornik.com/live/'],            'zbiornik','http://static.zbiornik.com/images/zbiornikBig.png', None)) 
           valTab.append(CDisplayListItem('CAMSODA',       'http://www.camsoda.com',       CDisplayListItem.TYPE_CATEGORY, ['http://www.camsoda.com/api/v1/browse/online'],            'CAMSODA','https://www.sodacdn.com/assets/img/camsoda-logo-160x50.png', None)) 
           valTab.append(CDisplayListItem('ADULT-CHANNELS',     'http://adult-channels.com', CDisplayListItem.TYPE_CATEGORY, ['http://adult-channels.com/'],'ADULT', 'http://adult-channels.com/wp-content/uploads/2015/09/adult-channels-logo.png', None)) 
           valTab.append(CDisplayListItem('+++ XXXLIST +++',     'xxxlist.txt', CDisplayListItem.TYPE_CATEGORY, [''],'XXXLIST', '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab

        # ########## #
        if 'HISTORY' == name:
           printDBG( 'Host listsItems begin name='+name )
           for histItem in self.history.getHistoryList():
               valTab.append(CDisplayListItem(histItem['pattern'], 'Szukaj ', CDisplayListItem.TYPE_CATEGORY, [histItem['pattern'],histItem['type']], 'SEARCH', '', None))          
           printDBG( 'Host listsItems end' )
           return valTab           
        # ########## #
        if 'SEARCH' == name:
           printDBG( 'Host listsItems begin name='+name )
           pattern = url 
           if Index==-1: 
              self.history.addHistoryItem( pattern, 'video')
           if self.SEARCH_proc == '': return []               
           if self.SEARCH_proc == 'main-menu':
              valTab=[]
              valtemp = self.listsItems(-1, url, 'tube8-search')
              for item in valtemp: item.name='tube8 - '+item.name
              valTab = valTab + valtemp 
              valtemp = self.listsItems(-1, url, 'xnxx-search')
              for item in valtemp: item.name='xnxx - '+item.name
              valTab = valTab + valtemp 
              valtemp = self.listsItems(-1, url, 'xhamster-search')
              for item in valtemp: item.name='xhamster - '+item.name              
              valTab = valTab + valtemp 
              valtemp = self.listsItems(-1, url, 'xvideos-search')
              for item in valtemp: item.name='xvideos - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, '4tube-search')
              for item in valtemp: item.name='4tube - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'PORNFROMCZECH-search')
              for item in valtemp: item.name='PORNFROMCZECH - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'porndoe-search')
              for item in valtemp: item.name='porndoe - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'PORNOHUB-search')
              for item in valtemp: item.name='PORNOHUB - '+item.name              
              valTab = valTab + valtemp 

              valtemp = self.listsItems(-1, url, 'THUMBZILLA-search')
              for item in valtemp: item.name='THUMBZILLA - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'pornhub-search')
              for item in valtemp: item.name='pornhub - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'x3xtube-search')
              for item in valtemp: item.name='x3xtube - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'pornicom-search')
              for item in valtemp: item.name='pornicom - '+item.name              
              valTab = valTab + valtemp

              valtemp = self.listsItems(-1, url, 'hdzog-search')
              for item in valtemp: item.name='hdzog - '+item.name              
              valTab = valTab + valtemp

              return valTab
           valTab = self.listsItems(-1, url, self.SEARCH_proc)
           printDBG( 'Host listsItems end' )              
           return valTab

        if 'tube8' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.tube8.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'categoriesFooterFontSize', '</ul>', False)[1]
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''['"]>([^"^']+?)</a>''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'tube8-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Featured videos ---', 'Featured videos', CDisplayListItem.TYPE_CATEGORY, ['http://www.tube8.com'], 'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Most Viewed ---', 'Most Viewed',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/most-viewed/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Top Rated ---', 'Top Rated',                 CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/top/page/1/'],       'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Longest ---', 'Longest', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/longest/page/1/'],      'tube8-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/newest/page/1/'],       'tube8-clips', '', None)) 
           self.SEARCH_proc='tube8-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'tube8-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.tube8.com/searches.html?q='+url, 'tube8-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'tube8-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           nextPage = self.cm.ph.getDataBeetwenMarkers(data, '<div class="footer-pagination"', '</div>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<!-- Video box', '</div><!-- /#boxVideo')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''data-video_url=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phTime = self.cm.ph.getSearchGroups(item, '''duration">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phTime: ' +phTime )                  
              valTab.append(CDisplayListItem(phTitle,'['+phTime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           #printDBG( 'Host match: '+str(nextPage) )
           match = re.findall('href="(.*?)"', nextPage, re.S)
           if match:
              printDBG( 'Host match: '+match[-1] )
              phUrl = match[-1]
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'xnxx' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xnxx.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('cats.write\((.*?), false', data, re.S)
           if not parse: return valTab
           #printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 phUrl = str(item["url"].replace('\/','/'))  
                 phTitle = str(item["label"]) 
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'xnxx-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem('--- Hits ---', 'Hits',               CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hits/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Hot ---', 'Hot',                 CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hot/'],       'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],      'xnxx-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/new/'],       'xnxx-clips', '', None)) 
           self.SEARCH_proc='xnxx-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'xnxx-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xnxx.com/?k='+url, 'xnxx-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'xnxx-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           if not data: return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<div id="video.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)".*?duration">(.*?)<', data, re.S)
           if phMovies:
              for (phUrl, phImage, phTitle, phTime ) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phTime: ' +phTime )                  
                  phTitle = decodeHtml(phTitle)
                  valTab.append(CDisplayListItem(phTitle,phTime+'\n'+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.search("pagination(.*?)Next", data, re.S)
           if match: match = re.findall('href="(.*?)"', match.group(1), re.S)
           if match:
              phUrl = match[-1]
              #printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'zbiornik' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://zbiornik.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'zbiornik.cookie')
           try: data = self.cm.getURLRequestData({ 'url': 'http://zbiornik.tv/accept/yes/Lw==', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           sex = ''
           hash = ''
           ph1 = re.search('var streams = (.*?)}];', data, re.S)
           if ph1: 
              ph1 = ph1.group(1)+'}]'
              #printDBG( 'Host listsItems json: '+ph1 )
              result = simplejson.loads(ph1)
              if result:
                 for item in result:
                     phash = re.search('"phash":"(.*?)"', data, re.S)
                     if phash: hash=phash.group(1)
                     if str(item["accType"])=='1': sex = 'male'
                     if str(item["accType"])=='2': sex = 'female'
                     if str(item["accType"])=='3': sex = 'couple'
                     printDBG( 'Host listsItems nick: '+item["nick"] )
                     printDBG( 'Host listsItems broadcasturl: '+item["broadcasturl"] )
                     phImage = 'http://camshot.zbiornik.com/'+str(item["broadcasturl"])+'-224.jpg'
                     printDBG( 'Host listsItems phImage: '+phImage )
                     streamUrl = 'rtmp://'+str(item["server"])+'/videochat/?'+hash+' playpath='+str(item["broadcasturl"])+' swfUrl=http://zbiornik.tv/wowza.swf?v50&b=100 pageUrl=http://zbiornik.tv/'+str(item["nick"])+' live=1'
                     printDBG( 'Host listsItems streamUrl: '+streamUrl )
                     if str(item["accType"])<>'1':
                        valTab.append(CDisplayListItem(str(item["nick"])+'    {'+sex+'}',str(item["nick"]),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', streamUrl, 0)], 0, phImage, None)) 
              printDBG( 'Host listsItems end' )
           return valTab

        if 'showup' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://showup.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           try: data = self.cm.getURLRequestData({ 'url': 'http://showup.tv/site/accept_rules/yes?ref=http://showup.tv/', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="stream-frame">.*?data-original="(.*?)".*?href="(.*?)".*?class="stream-name">(.*?)<.*?class="stream-desc">(.*?)<', data, re.S)
           if phMovies:
              for (phImage, phUrl, phTitle, phDesc ) in phMovies:
                  phImage = self.MAIN_URL+'/'+phImage
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phDesc: '+phDesc )
                  valTab.append(CDisplayListItem(phTitle,phTitle+'     '+decodeHtml(phDesc),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab

        if 'xvideos' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.xvideos.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('class="main-categories".*?href="(.*?)</div>', data, re.S)
           if parse:
              phCats = re.findall('<a href="(.*?)".*?>(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'xvideos-clips', '', None)) 
              valTab.sort(key=lambda poz: poz.name) 
           #valTab.insert(0,CDisplayListItem('--- Pornstars ---',   'Pornstars',   CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/pornstars'], 'xvideos-pornstars', '', None)) 
           valTab.insert(0,CDisplayListItem('--- Best Videos ---', 'Best Videos', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/best/'],     'xvideos-clips', '', None)) 
           valTab.insert(0,CDisplayListItem('--- New Videos ---',  'New Videos',  CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],              'xvideos-clips', '', None)) 
           self.SEARCH_proc='xvideos-search'
           valTab.insert(0,CDisplayListItem('---Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('---Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'xvideos-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="thumbProfile".*?href="(.*?)".*?img src="(.*?)".*?href=".*?">(.*?)<', data, re.S)
           if phCats:
              for (phUrl, phImage, phTitle) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '  +phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl.replace('pornstars-click/3','profiles')+'#_tabVideos'],'xvideos-clips', phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'xvideos-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xvideos.com/?k='+url, 'xvideos-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'xvideos-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="thumb".*?img src="(.*?)".*?href="(/video.*?)" title="(.*?)".*?<strong>(.*?)</strong>', data, re.S)
           if phMovies:
              for (phImage, phUrl, phTitle, Runtime ) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems Runtime: '+Runtime )
                  valTab.append(CDisplayListItem(phTitle,'['+Runtime.strip()+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           next = re.search('pagination(.*?)>Next<', data, re.S)
           if next:
              match = re.findall('a href="(.*?)"', next.group(1), re.S)
              if match:
                 phUrl = match[-1]
                 if phUrl[0] <> '/'[0]:
                    phUrl = '/'+phUrl
                 valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'hentaigasm' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://hentaigasm.com' 
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('Genres(.*?)</div></div>', data, re.S|re.I)
           if not parse: return valTab
           phCats = re.findall("<a href='(.*?)'.*?>(.*?)<", parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'hentaigasm-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- New ---", "New",        CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL], 'hentaigasm-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'hentaigasm-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<div class="thumb">.*?title="(.*?)" href="(.*?)".*?<img src="(.*?)"', data, re.S)
           if phMovies:
              for (phTitle, phUrl, phImage) in phMovies:
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.search("<div class='wp-pagenavi'>(.*?)</div>", data, re.S)
           if match: match = re.findall("href='(.*?)'", match.group(1), re.S)
           if match:
                  phUrl = match[-1]
                  #printDBG( 'Host listsItems page phUrl: '+phUrl )
                  valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'youporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youporn.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'sublist-item', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''categories_([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](/category/[^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              if phTitle: 
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'youporn-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Discussed ---",     "Most Discussed",     CDisplayListItem.TYPE_CATEGORY,["http://www.youporn.com/most_discussed/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Favorited ---",     "Most Favorited",     CDisplayListItem.TYPE_CATEGORY,["http://www.youporn.com/most_favorited/"],                   'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",        "Most Viewed",        CDisplayListItem.TYPE_CATEGORY,["http://www.youporn.com/most_viewed/"],                      'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",          "Top Rated",          CDisplayListItem.TYPE_CATEGORY,["http://www.youporn.com/top_rated/"],                        'youporn-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",                "New",                CDisplayListItem.TYPE_CATEGORY,["http://www.youporn.com/"],                                  'youporn-clips', '',None))
           self.SEARCH_proc='youporn-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'youporn-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.youporn.com/search/?query=%s' % url, 'youporn-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'youporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           COOKIEFILE = os_path.join(GetCookieDir(), 'youporn.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = re.findall('class="skip next".*?class="prev-next".*?href="(.*?)" data-page-number', data, re.S)
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'data-video-id', 'video-box-title')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''video-box-duration['"]>([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems phRuntime: '+phRuntime )
              phUrl = phUrl.replace("&amp;","&")
              if len(phUrl)>5:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime.strip()+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              next = next[0].replace("&amp;","&")
              if next.startswith('/'): next = self.MAIN_URL + next
              valTab.append(CDisplayListItem('Next', 'Next: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'redtube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.redtube.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="video">.*?<a href="(.*?)" title="(.*?)">.*?data-src="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phTitle, phImage) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'redtube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Favored ---", "Most Favored", CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostfavored?period=alltime"], 'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",  "Most Viewed",  CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/mostviewed?period=alltime"],  'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",    "Top Rated",    CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/top?period=alltime"],         'redtube-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.redtube.com/"],                           'redtube-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'redtube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="video-duration".*?>(.*?)<.*?data-src="(.*?)".*?<a href="(.*?)" title="(.*?)".*?<span class="video-views">(.*?)<', data, re.S)
           if phMovies:
              for (phRuntime, phImage, phUrl, phTitle, phViews) in phMovies:
                  if phImage[:2] == "//": phImage = "http:" + phImage
                  phRuntime = phRuntime.strip()
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  printDBG( 'Host listsItems phViews: '+phViews )
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] ['+phViews+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<link rel="next" href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', match[0], CDisplayListItem.TYPE_CATEGORY, [match[0]], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'xhamster' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamster.com' 
           self.COOKIEFILE = os_path.join(GetCookieDir(), 'xhamster.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           self.header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': self.header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'letter-categories', 'id="footer">', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''<span\s>([^"^']+?)<''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/categories/[^"^']+?)['"]''', 1, True)[0]
              if config.plugins.iptvplayer.xhamsterchannel.value and not phUrl:
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/channels/[^"^']+?)['"]''', 1, True)[0] 
                 if phUrl and phTitle: phTitle = phTitle+'   (channels)'
              if config.plugins.iptvplayer.xhamstertag.value and not phUrl:
                 phUrl = self.cm.ph.getSearchGroups(item, '''href=['"](https://xhamster.com/tags/[^"^']+?)['"]''', 1, True)[0] 
                 if phUrl and phTitle: phTitle = phTitle+'   (tags)'
              if phUrl and phTitle:
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 valTab.append(CDisplayListItem(phTitle.strip(),phTitle.strip(),CDisplayListItem.TYPE_CATEGORY, [phUrl],'xhamster-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://xhamster.com/"], 'xhamster-clips', '',None))
           self.SEARCH_proc='xhamster-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'xhamster-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.xhamster.com/search.php?from=suggestion&q=%s&qcat=video' % url, 'xhamster-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'xhamster-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'header': self.header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next=''
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pager', '</div></div>', False)[1]
           next_page = self.cm.ph.getAllItemsBeetwenMarkers(next_page, '<a', '</a>')
           for item in next_page:
              next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video">', '</div></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''<b>([^"^']+?)</b>''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phRuntime: '+phRuntime )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              if next.startswith('/'): next = self.MAIN_URL + next
              next = next.replace('&amp;','&')
              valTab.append(CDisplayListItem('Next', 'Page: '+next, CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'xhamster-cams' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://xhamsterlive.com' 
           url='http://xhamsterlive.com/api/front/models'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"models":(.*?),"ttl":', data, re.S) 
           if not parse: return valTab
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 ID = str(item["id"]) 
                 Name = str(item["username"])
                 BroadcastServer = str(item["broadcastServer"])
                 Image = str(item["previewUrl"].replace('\/','/'))  
                 status = str(item["status"])
                 printDBG( 'Host listsItems ID: '+ID )
                 printDBG( 'Host listsItems Name: '+Name )
                 printDBG( 'Host listsItems BroadcastServer: '+BroadcastServer )
                 printDBG( 'Host listsItems Image: '+Image )
                 if status == "public":
                    valTab.append(CDisplayListItem(Name,Name,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', ID, 1)], 0, Image, None)) 
           printDBG( 'Host listsItems end' )
           return valTab

        if 'eporner' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.eporner.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'div class="categoriesbox', '</div> </div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              phTitle = phTitle.replace(' movies', '').replace('Porn Videos', '')
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'eporner-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",        "HD",        CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/hd/"], 'eporner-clips', '','/hd/'))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---", "Top Rated", CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/top_rated/"], 'eporner-clips', '','/top_rated/'))
           valTab.insert(0,CDisplayListItem("--- Popular ---",   "Popular",   CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/weekly_top/"], 'eporner-clips', '','/weekly_top/'))
           valTab.insert(0,CDisplayListItem("--- On Air ---",    "On Air",    CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/currently/"], 'eporner-clips', '','/currently/'))
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://www.eporner.com/"], 'eporner-clips', '',''))
           self.SEARCH_proc='eporner-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'eporner-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.eporner.com/search/%s/' % url, 'eporner-clips')
           printDBG( 'Host listsItems end' )
           return valTab    
        if 'eporner-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="mb".*?>\s*<a\shref="(.*?)"\stitle="(.*?)".*?src="(.*?)".*?"mbtim">(.*?)</div>', data, re.S)
           if not phMovies:
              phMovies = re.findall('class="mb hdy".*?>\s*<a\shref="(.*?)"\stitle="(.*?)".*?src="(.*?)".*?"mbtim">(.*?)</div>', data, re.S)
           if phMovies:
              for (phUrl, phTitle, phImage, phRuntime) in phMovies:
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems phImage: '+phImage )
                 printDBG( 'Host listsItems phRuntime: '+phRuntime )
                 valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<div class="numlist2">.*?>NEXT', data, re.S)
           if match:
              printDBG( 'Host listsItems page match: '+match[0] )
              match = re.findall("<a href=(.*?)title", match[0], re.S)
              if match:
                 printDBG( 'Host listsItems page phUrl: '+match[-1] )
                 phUrl = match[-1].replace("'","").replace('"','')
                 valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'pornhub' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhub.com' 
           self.COOKIEFILE = os_path.join(GetCookieDir(), 'pornhub.cookie')
           host = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
           self.header = {'User-Agent': host, 'Accept':'application/json','Accept-Language':'en,en-US;q=0.7,en;q=0.3','X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': self.header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="category-wrapper">', 'class="cat_pic"')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornhub-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",         "HD",          CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?c=38"], 'pornhub-clips', 'http://cdn1a.static.pornhub.phncdn.com/images/categories/38.jpg',None))
           valTab.insert(0,CDisplayListItem("--- Longest ---",    "Longest",     CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=lg"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",  "Top Rated",   CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=tr"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---","Most Viewed", CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=mv"], 'pornhub-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---","Most Recent", CDisplayListItem.TYPE_CATEGORY,["http://www.pornhub.com/video?o=mr"], 'pornhub-clips', '',None))
           self.SEARCH_proc='pornhub-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'pornhub-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.pornhub.com/video/search?search=%s' % url, 'pornhub-clips')
           printDBG( 'Host listsItems end' )
           return valTab    
        if 'pornhub-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'header': self.header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host2 getResolvedURL data: '+data )
           next = self.cm.ph.getSearchGroups(data, '''"page_next"><a href=['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="videoblock', '</li>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].replace('&amp;','&') 
              phImage = self.cm.ph.getSearchGroups(item, '''data-mediumthumb=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"duration">([^"^']+?)<''', 1, True)[0] 
              #phViews = self.cm.ph.getSearchGroups(item, '''"views"><var>([^"^']+?)<''', 1, True)[0] 
              phAdded = self.cm.ph.getSearchGroups(item, '''class="added">([^"^']+?)<''', 1, True)[0] 
              OldImage = self.cm.ph.getSearchGroups(item, '''data-image=['"]([^"^']+?)['"]''', 1, True)[0] 

              phUrl = self.MAIN_URL+phUrl
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems phRuntime: '+phRuntime )
              #printDBG( 'Host listsItems phViews: '+phViews )
              printDBG( 'Host listsItems phAdded: '+phAdded )
              if not OldImage:
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+phRuntime+'] [Added: '+phAdded+'] '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Next '+re.sub('.+page=', '', next), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+next.replace('&amp;','&')], name, '', None))        
           printDBG( 'Host listsItems end' )
           return valTab

        if '4tube' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.4tube.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('All categories(.*?)</div></div>', data, re.S)
           if not parse: return []
           phCats = re.findall('<li><a href="(.*?)" title=".*?">(.*?)<span>', parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats:
                  phTitle = phTitle.strip()
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  phTitle = phTitle.title()
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'4tube-clips', '', None)) 
           #valTab.sort()
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Channels ---","Channels",   CDisplayListItem.TYPE_CATEGORY,["http://www.4tube.com/channels"]  ,         '4tube-channels', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornstars ---","Pornstars", CDisplayListItem.TYPE_CATEGORY,["http://www.4tube.com/pornstars"],          '4tube-pornstars','',None))
           valTab.insert(0,CDisplayListItem("--- Most viewed ---","Most viewed",     CDisplayListItem.TYPE_CATEGORY,["http://www.4tube.com/videos?sort=views&time=month"],             '4tube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Highest Rated ---","Highest Rated", CDisplayListItem.TYPE_CATEGORY,["http://www.4tube.com/videos?sort=rating&time=month"],             '4tube-clips',    '',None))
           valTab.insert(0,CDisplayListItem("--- Lastest ---","Lastest",     CDisplayListItem.TYPE_CATEGORY,["http://www.4tube.com/videos"],             '4tube-clips',    '',None))
           self.SEARCH_proc='4tube-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if '4tube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.4tube.com/search?q=%s' % url, '4tube-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if '4tube-channels' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<a class="thumb-link" href="(.*?)" title="(.*?)".*?<i class="icon icon-video"></i>(.*?)<.*?<img data-original="(.*?)"',data,re.S) 
           if phMovies:
              for (phUrl, phTitle, phVid, phImage ) in phMovies:           
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phVid: '+phVid )
                  valTab.append(CDisplayListItem(phTitle,'[Video: '+phVid+'] '+phTitle,CDisplayListItem.TYPE_CATEGORY, ['http://www.4tube.com'+phUrl], '4tube-clips', phImage, None)) 
           match = re.findall('<ul class="pagination">.*?</a></li><li><a href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', match[0], CDisplayListItem.TYPE_CATEGORY, [match[0]], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab
        if '4tube-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<a class="thumb-link" href="(.*?)" title="(.*?)".*?<i class="icon icon-video"></i>(.*?)<.*?<img data-original="(.*?)"',data,re.S) 
           if phMovies:
              for (phUrl, phTitle, phVid, phImage ) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phVid: '+phVid )
                  valTab.append(CDisplayListItem(phTitle,'[Video: '+phVid+'] '+phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl], '4tube-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           match = re.findall('<ul class="pagination">.*?</a></li><li><a href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', match[0], CDisplayListItem.TYPE_CATEGORY, [match[0]], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab
        if '4tube-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<div class="col thumb_video".*?href="(.*?)".*?title="(.*?)".*?<img data-master="(.*?)".*?class="duration-top">(.*?)<',data,re.S) 
           if phMovies:
              for (phUrl, phTitle, phImage, phRuntime) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  if phUrl.startswith('/videos/'):
                      valTab.append(CDisplayListItem(phTitle,'['+phRuntime+']  '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<a class="page " href="(.*?)"', data, re.S)
           if match:
              for (phPageUrl) in match: 
                  printDBG( 'Host listsItems phPageUrl: '  +phPageUrl )
                  valTab.append(CDisplayListItem('Page', phPageUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phPageUrl], name, '', None))                
           match = re.findall('<a class="last" href="(.*?)" title="Last page">', data, re.S)
           if match:
              for (phPageUrl) in match: 
                  printDBG( 'Host listsItems phPageUrl: '  +phPageUrl )
                  valTab.append(CDisplayListItem('Last Page', phPageUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phPageUrl], name, '', None))                
           match = re.findall('<link rel="next" href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', 'Next Page', CDisplayListItem.TYPE_CATEGORY, [match[0]], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'hdporn' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdporn.net'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="content">.*?href="(.*?)".*?src="(.*?)".*?alt="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phImage, phTitle) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'hdporn-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Top Rated ---","Top Rated",           CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top-rated/"]  , 'hdporn-clips','',phUrl))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---","Most Popular",     CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/most-viewed/"], 'hdporn-clips','',phUrl))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'hdporn-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           printDBG( 'Host listsItems cat-url: '+catUrl )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('class="content.*?href="(.*?)".*?itle="(.*?)".*?src="(.*?)".*?TIME:  (.*?)</div>', data, re.S)
           if phMovies:
              for (phUrl, phTitle, phImage, phRuntime) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<div id="pagination">.*?</div>', data, re.S)
           if not match: return valTab
           printDBG( 'Host listsItems len match: '+str(len(match)))
           #printDBG( 'Host listsItems match: '+match[0])
           match = re.findall("</a><a href='(.*?)'>", match[0], re.S)
           if not match: return valTab
           printDBG( 'Host listsItems len match: '+str(len(match)))
           #printDBG( 'Host listsItems match: '+match[0])
           if len(match)>0:
              valTab.append(CDisplayListItem('Next', 'Next Page', CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+catUrl+match[0]], 'hdporn-clips', '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab
  
        if 'UPDATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab.append(CDisplayListItem(self.XXXversion+' - Local version',   'Local  XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem(self.XXXremote+ ' - Remote version',  'Remote XXXversion', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           valTab.append(CDisplayListItem('ZMIANY W WERSJI',                    'ZMIANY W WERSJI',   CDisplayListItem.TYPE_CATEGORY, ['https://gitlab.com/iptv-host-xxx/iptv-host-xxx/commits/master.atom'], 'UPDATE-ZMIANY', '', None)) 
           valTab.append(CDisplayListItem('Update Now',                         'Update Now',        CDisplayListItem.TYPE_CATEGORY, [''], 'UPDATE-NOW',    '', None)) 
           valTab.append(CDisplayListItem('Update Now & Restart Enigma2',                         'Update Now & Restart Enigma2',        CDisplayListItem.TYPE_CATEGORY, ['restart'], 'UPDATE-NOW',    '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'UPDATE-ZMIANY' == name:
           printDBG( 'Host listsItems begin name='+name )
           try:
              data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall("<entry>.*?<title>(.*?)</title>.*?<updated>(.*?)</updated>.*?<name>(.*?)</name>", data, re.S)
           if phCats:
              for (phTitle, phUpdated, phName ) in phCats:
                  phUpdated = phUpdated.replace('T', '   ')
                  phUpdated = phUpdated.replace('Z', '   ')
                  phUpdated = phUpdated.replace('+01:00', '   ')
                  phUpdated = phUpdated.replace('+02:00', '   ')
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phUpdated: '+phUpdated )
                  printDBG( 'Host listsItems phName: '+phName )
                  valTab.append(CDisplayListItem(phUpdated+' '+phName+'  >>  '+phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [''],'', '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'UPDATE-NOW' == name:
           printDBG( 'HostXXX listsItems begin name='+name )
           tmpDir = GetTmpDir() 
           source = os_path.join(tmpDir, 'iptv-host-xxx.tar.gz') 
           dest = os_path.join(tmpDir , '') 
           _url = 'https://gitlab.com/iptv-host-xxx/iptv-host-xxx/repository/archive.tar.gz?ref=master'              
           output = open(source,'wb')
           query_data = { 'url': _url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              output.write(self.cm.getURLRequestData(query_data))
              output.close()
              os_system ('sync')
              printDBG( 'HostXXX pobieranie iptv-host-xxx.tar.gz' )
           except:
              if os_path.exists(source):
                 os_remove(source)
              printDBG( 'HostXXX Błąd pobierania master.tar.gz' )
              valTab.append(CDisplayListItem('ERROR - Blad pobierania: '+_url,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab
           if os_path.exists(source):
              printDBG( 'HostXXX Jest plik '+source )
           else:
              printDBG( 'HostXXX Brak pliku '+source )

           cmd = 'tar -xzf "%s" -C "%s" 2>&1' % ( source, dest )  
           try: 
              os_system (cmd)
              os_system ('sync')
              printDBG( 'HostXXX rozpakowanie  ' + cmd )
           except:
              printDBG( 'HostXXX Błąd rozpakowania iptv-host-xxx.tar.gz' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx*' % dest)
              valTab.append(CDisplayListItem('ERROR - Blad rozpakowania %s' % source,   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab

           printDBG( 'HostXXX sleep %s' % str(config.plugins.iptvplayer.delay.value) )
           sleep(config.plugins.iptvplayer.delay.value)

           try:
              import commands
              cmd = 'ls '+dest+' | grep iptv-host-xxx-master*'
              katalog = commands.getoutput(cmd)
              printDBG( 'HostXXX katalog list > '+ cmd )
              filepath = '%s%s/IPTVPlayer' % (dest, katalog)
              if os_path.exists(filepath):
                 printDBG( 'HostXXX Jest rozpakowany katalog '+katalog )
              else:
                 printDBG( 'HostXXX Brak katalogu '+filepath )
           except:
              printDBG( 'HostXXX error commands.getoutput ' )

           printDBG( 'HostXXX sleep %s' % str(config.plugins.iptvplayer.delay.value) )
           sleep(config.plugins.iptvplayer.delay.value)

           try:
              os_system ('cp -rf %siptv-host-xxx*/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/' % dest)
              os_system ('sync')
              printDBG( 'HostXXX kopiowanie hostXXX do IPTVPlayer: '+'cp -rf %siptv-host-xxx*/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/' % dest )
           except:
              printDBG( 'HostXXX blad kopiowania' )
              os_system ('rm -f %s' % source)
              os_system ('rm -rf %siptv-host-xxx*' % dest)
              valTab.append(CDisplayListItem('ERROR - blad kopiowania',   'ERROR', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
              return valTab

           printDBG( 'HostXXX sleep %s' % str(config.plugins.iptvplayer.delay.value) )
           sleep(config.plugins.iptvplayer.delay.value)

           try:
              cmd = '/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/hosts/hostXXX.py'
              with open(cmd, 'r') as f:  
                 data = f.read()
                 f.close() 
                 wersja = re.search('XXXversion = "(.*?)"', data, re.S)
                 aktualna = wersja.group(1)
                 printDBG( 'HostXXX aktualna wersja wtyczki '+aktualna )
           except:
              printDBG( 'HostXXX error openfile ' )


           printDBG( 'HostXXX usuwanie plikow tymczasowych' )
           os_system ('rm -f %s' % source)
           os_system ('rm -rf %siptv-host-xxx*' % dest)

           if url:
              try:
                 info = 'Zaraz nastąpi Restart GUI .\n \n Wersja hostXXX w tunerze %s' % aktualna
                 self.sessionEx.open(MessageBox, info, type = MessageBox.TYPE_INFO, timeout = 2 )
                 from enigma import quitMainloop
                 quitMainloop(3)
              except: pass
           valTab.append(CDisplayListItem('Update End. Please manual restart enigma2',   'Restart', CDisplayListItem.TYPE_CATEGORY, [''], '', '', None)) 
           printDBG( 'HostXXX listsItems end' )
           return valTab

        if 'beeg' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://beeg.com' 
           query_data = { 'url': self.MAIN_URL, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           version = re.search('src="//static\.beeg\.com/cpl/(.*?)\.js' , data, re.S)
           if version:
              self.beeg_version = str(version.group(1))
           url = 'http://api2.beeg.com/api/v6/%s/index/main/0/mobile' % self.beeg_version
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.tags = 'popular'
           self.page = -1
           parse = re.search('"%s":\[(.*?)\]' % self.tags, data, re.S)
           if parse:
              phCats = re.findall('"(.*?)"', parse.group(1), re.S)
              if phCats:
                 for Title in phCats:
                     phUrl = 'http://api2.beeg.com/api/v6/%s/index/tag/$PAGE$/mobile?tag=%s' % (self.beeg_version, Title)
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+Title )
                     valTab.append(CDisplayListItem(Title,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'beeg-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'beeg-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           next = url
           self.page += 1
           url = url.replace('$PAGE$', '%s' % str(self.page))
           printDBG( 'Host current url: '+url )
           printDBG( 'Host current next: '+next )
           printDBG( 'Host current page: '+ str(self.page) )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'beeg-clips data: '+data )
           phVideos = re.findall('\{"title":"(.*?)","id":"(.*?)",.*?,"ps_name"', data, re.S)
           if phVideos:
              for (phTitle, phVideoId) in phVideos:
                 phUrl = 'http://api2.beeg.com/api/v6/%s/video/%s' % (self.beeg_version, phVideoId)
                 phImage = 'http://img.beeg.com/236x177/%s.jpg' % phVideoId
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems phImage: '+phImage )
                 valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'pornrabbit' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornrabbit.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('<div class="cat">.*?href="(.*?)".*?<h2>(.*?)<small>(.*?)<.*?img src="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phTitle,phTitle2,phImage) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle+phTitle2,phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornrabbit-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Most Recent ---", "Most Recent", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+'/videos/'], 'pornrabbit-clips', '','/videos/'))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'pornrabbit-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           x = 0
           Movies = re.findall('class="video">.*?<a href="(.*?)" title="(.*?)".*?<img.*?src="(.*?)".*?views: <b>(.*?)</b>.*?runtime: <b>(.*?)</b>', data, re.S)
           if Movies:
              for (Url, Title, Image, Views, Runtime) in Movies:
                  valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+Url, 1)], 0, Image, None)) 
                  x = x + 1
           match = re.findall(r'&nbsp;<a href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', self.MAIN_URL+catUrl+match[0].replace(r'../',''), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+catUrl+match[0].replace(r'../','')], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'pornhd' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornhd.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('class="tag-150-list">(.*?)class="footer-zone">', data, re.S)
           if not parse: return valTab
           phCats = re.findall('href="(.*?)".*?alt="(.*?)".*?data-original="(.*?)"', parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle, phImage) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'pornhd-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'pornhd-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('<a class="thumb" href="(.*?)".*?alt="(.*?)".*?data-original="(.*?)".*?<time>(.*?)</time>.*?', data, re.S)
           if Movies:
              for (Url, Title, Image, Runtime) in Movies:
                  valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+Url, 1)], 0, Image, None)) 
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', 'Page : '+match.group(1), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+match.group(1)], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'AH-ME' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.ah-me.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 1
           phCats = re.findall('class="category">.*?<a\shref="(.*?)page1.html">.*?="thumb"\ssrc="(.*?)".*?alt="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phImage, phTitle) in phCats:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '  +phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'AH-ME-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Long movies ---",       "Long movies",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/long-movies/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---",       "Top rated",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/top-rated/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- High definition ---",       "High definition",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/high-definition/page1.html"], 'AH-ME-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most favorited ---",       "Most favorited",       CDisplayListItem.TYPE_CATEGORY,["https://www.ah-me.com/mostfavorites/page1.html"], 'AH-ME-clips', '',None))
		   
           self.SEARCH_proc='ahme-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'ahme-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'https://www.ah-me.com/search/%s/' % url, 'AH-ME-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'AH-ME-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next = self.cm.ph.getDataBeetwenMarkers(data, 'next"><a class="color" href="', '">Next', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="moviec', '/span></p>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              Title = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0] 
              Image = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Url = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Runtime = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems Title: '+Title )
              printDBG( 'Host listsItems Url: '  +Url )
              printDBG( 'Host listsItems Image: '  +Image )
              printDBG( 'Host listsItems Runtime: '+Runtime )
              valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+decodeHtml(Title),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Image, None)) 
           if next:
              printDBG( 'Host next: '+next )
              valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'CHATURBATE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://chaturbate.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 1
           valTab.append(CDisplayListItem('Featured', 'Featured',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Female', 'Female',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/female-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Couple', 'Couple',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/couple-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Transsexual', 'Transsexual',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/transsexual-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('HD', 'HD',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/hd-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Teen (18+)', 'Teen',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/teen-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('18 to 21', '18 to 21',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/18to21-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('20 to 30', '20 to 30',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/20to30-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('30 to 50', '30 to 50',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/30to50-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Euro Russian', 'Euro Russian',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/euro-russian-cams/'],'CHATURBATE-clips', '', None)) 
           valTab.append(CDisplayListItem('Exhibitionist', 'Exhibitionist',CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+'/exhibitionist-cams/'],'CHATURBATE-clips', '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'CHATURBATE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('class="list">(.*)class="paging">', data, re.S)
           if parse:
              Movies = re.findall('<li>.*?<a\shref="(.*?)".*?<img\ssrc="(.*?)".*?gender(\w)">(\d+)</span>.*?<li\stitle="(.*?)">.*?location.*?>(.*?)</li>.*?class="cams">(.*?)</li>.*?</div>.*?</li>', parse.group(1), re.S) 
              if Movies:
                 for (Url, Image, Gender, Age, Description, Location, Viewers) in Movies:
                     valTab.append(CDisplayListItem(Url.strip('\/'),Url.strip('\/')+'   [Age: '+Age+'           Location: '+Location+']',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+Url, 1)], 0, Image, None)) 
                     printDBG( 'Host listsItems phUrl: '  +Url )
                     printDBG( 'Host listsItems phImage: '  +Image )
                     printDBG( 'Host listsItems Age: '+Age )
                     printDBG( 'Host listsItems Description: '+Description )
                     printDBG( 'Host listsItems Location: '+Location )
                     printDBG( 'Host listsItems Viewers: '+Viewers )

           match = re.search('class="endless_separator".*?<li><a href="(.*?)"', data, re.S)
           if match:
              printDBG( 'Host listsItems Next: '  +match.group(1) )
              valTab.append(CDisplayListItem('Next', match.group(1), CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+match.group(1)], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'AMATEURPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.amateurporn.net' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 0
           parse = re.search('channellist(.*?)searchbox', data, re.S)
           if parse:
              phCats = re.findall('<a href="(.*?)"\stitle=".*?">(.*?)</a>', parse.group(1), re.S)
           if phCats:
              for (phUrl, phTitle) in phCats: 
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,self.MAIN_URL+phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'AMATEURPORN-clips', '', self.MAIN_URL+phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'AMATEURPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page += 1
           Movies = re.findall('class="video">.*?<a\shref="(.*?)".*?<img src="(.*?)"\salt="(.*?)".*?margin-top:2px;">(.*?)\sviews</span>.*?text-align:right;\'>(.*?)<br\s/>', data, re.S) 
           if Movies:
              for (Url, Pic, Title, Views, Runtime) in Movies:
                  Pic = Pic.replace(' ','%20')
                  Runtime = Runtime.strip()
                  valTab.append(CDisplayListItem(decodeHtml(Title),'['+Runtime+'] '+Title,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, Pic, None)) 
           match = re.findall(r'href="page(.*?)"', data, re.S)
           if match:
              valTab.append(CDisplayListItem('Next', 'Page : '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [catUrl+'page%s.html' % str(self.page)], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'FOTKA-PL-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = url 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"rooms":(.*?),"status":"OK"', data, re.S)
           if not parse: return valTab
           printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 try:
                    Name = str(item["name"])
                    Age = str(item["age"])
                    Playpath = str(item["liveCastId"])
                    Host = str(item["host"])
                    Url = str(item["streamUrl"].replace('\/','/'))

                    Url = 'rtmp://%s:1935/fotka.pl/ playpath=%s swfUrl=https://s.fotka.com/js/jwplayer/jwplayer.flash.swf live=1 pageUrl=https://fotka.com/kamerka/%s' % (Host, Playpath, Name)
                    Image = str(item["av_126"].replace('\/','/')) 
                    Title = str(item["title"])
                    Viewers = str(item["viewers"])
                    printDBG( 'Host listsItems page Name: '+Name )
                    printDBG( 'Host listsItems page Age: '+Age )
                    printDBG( 'Host listsItems page Url: '+Url )
                    printDBG( 'Host listsItems page Image: '+Image )
                    printDBG( 'Host listsItems page Title: '+Title )
                    printDBG( 'Host listsItems page viewers: '+Viewers )
                    valTab.append(CDisplayListItem(Name,'[Age : '+Age+']'+'   [Views:  '+Viewers+']      '+Title, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 0)], 0, Image, None)) 
                 except: pass
           printDBG( 'Host listsItems end' )
           return valTab

        if 'CAM4-KAMERKI' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.cam4.pl' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/cams/hd"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Poland ---",       "Polskie",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/poland-cams"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Couples ---",       "Pary",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/couple"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/male"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/shemale"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/new"], 'CAM4-KAMERKI-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety",       CDisplayListItem.TYPE_CATEGORY,["http://www.cam4.pl/female"], 'CAM4-KAMERKI-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'CAM4-KAMERKI-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error' )
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           vr=''
           phCats = re.findall('class="profileDataBox.*?<a href="(.*?)".*?data-src="(.*?)"(.*?)class="flag flag-(.*?)"', data, re.S) 
           if phCats:
              for (phUrl, phImage, vr, phCountry) in phCats: 
                  phTitle = phUrl.strip('/')
                  try:
                      parse = re.search('input type="checkbox" name="country" value="%s".*?<label>(.*?)</label>' % phCountry, data, re.S)
                      phCountry = parse.group(1)
                  except:
                      pass
                  if 'vrStreamIcon' in vr: 
                      vr=' (VR)'
                  else:
                      vr=''
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '  +phImage )
                  printDBG( 'Host listsItems phCountry: '  +phCountry )
                  printDBG( 'Host listsItems vr: '  +vr )
                  valTab.append(CDisplayListItem(phTitle+vr,phTitle+vr+'   [Country: '+phCountry+']   ',CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('directoryPager.*?> Next <', data, re.S)
           if match:
              printDBG( 'Host listsItems page match: '+match[0] )
              match = re.findall('href="(.*?)".*?data-page="(.*?)"', match[0], re.S)
           if match:
              for (phUrl, phTitle) in match:
                  printDBG( 'Host listsItems page phUrl: '+phUrl )
                  printDBG( 'Host listsItems page phTitle: '+phTitle )
              valTab.append(CDisplayListItem('Next '+phTitle, 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'CAMSODA' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.camsoda.com/' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           dane = re.search('"results":(.*?)}]}', data, re.S)
           if dane: 
              dane = dane.group(1)+'}]'
              #printDBG( 'Host listsItems json: '+dane )
              result = simplejson.loads(dane)
              if result:
                 for item in result:
                     Name = item["display_name"].encode("utf-8")
                     Image = str(item["thumb"])
                     status = str(item["status"])
                     camhouse = ''
                     videourl = "https://www.camsoda.com/api/v1/video/vtoken/" + item['username'] + "?username=guest_" + str(random.randrange(100, 55555))
                     if Image.startswith('//'): Image = 'http:' + Image 
                     if config.plugins.iptvplayer.camsoda.value == '1': videourl = 'rtmp'+videourl
                     printDBG( 'Host listsItems Name: '+Name )
                     printDBG( 'Host listsItems Image: '+Image )
                     printDBG( 'Host listsItems videourl: '+videourl )
                     if status=='online':
                        valTab.append(CDisplayListItem(Name+'   '+camhouse, Name, CDisplayListItem.TYPE_VIDEO, [CUrlItem('', videourl, 1)], 0, Image, None)) 
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'YOUJIZZ' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.youjizz.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'category">', '</ul>', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           #printDBG( 'Host2 data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)<''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'YOUJIZZ-clips', '', None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- HD ---",       "HD",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/search/HighDefinition-1.html#"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/top-rated/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",       "Newest",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/newest-clips/1.html"], 'YOUJIZZ-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---",       "Popular",       CDisplayListItem.TYPE_CATEGORY,["http://www.youjizz.com/most-popular/1.html"], 'YOUJIZZ-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'YOUJIZZ-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           url = url.replace(' ','%20')
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           next_page = self.cm.ph.getAllItemsBeetwenMarkers(next_page, '<li', '</li>')
           for item in next_page:
              next = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0]
           if next.startswith('/'): next = self.MAIN_URL + next
           printDBG( 'Host listsItems next_page: '+next )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-thumb', 'format-views')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''html'>([^"^']+?)</a>''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phRuntime = self.cm.ph.getSearchGroups(item, '''"time">([^"^']+?)<''', 1, True)[0] 
              if phImage.startswith('//'): phImage = 'http:' + phImage
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phRuntime: '+phRuntime )
              valTab.append(CDisplayListItem(decodeHtml(phTitle).strip(),'['+phRuntime+'] '+decodeHtml(phTitle).strip(),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next:
              valTab.append(CDisplayListItem('Next', 'Next', CDisplayListItem.TYPE_CATEGORY, [next], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'DACHIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.dachix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('class="listing-categories">.*?<a\shref="(.*?)".*?class="title">(.*?)</b>.*?src="(.*?)"', data, re.S)
           if phCats:
              for (phUrl, phTitle, phImage) in phCats:
                  phTitle = phTitle.strip(' ')
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl+"/videos"],'DACHIX-clips', phImage, None)) 
           valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- Longest ---",       "Longest",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=longest"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Popular ---",       "Most Popular",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=popular"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---",       "Most Viewed",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=viewed"], 'DACHIX-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Rated ---",       "Top Rated",       CDisplayListItem.TYPE_CATEGORY,["http://www.dachix.com/videos?sort=rated"], 'DACHIX-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'DACHIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('itemprop="video".*?title="(.*?)".*?content="(.*?)".*?src="(.*?)".*?duration"\scontent=".*?">(.*?)\s-', data, re.S) 
           if phMovies:
              for (phTitle, phUrl, phImage, phRuntime) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('link rel="next" href="(.*?)"', data, re.S)
           if match:
                  phUrl = match[0]
                  printDBG( 'Host listsItems page phUrl: '+phUrl )
                  valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'DRTUBER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.drtuber.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('contain_cols(.*?)<div class="drop_inner">', data, re.S) 
           if parse:
              Cats = re.findall('<a href="(.*?)">(.*?)</a>', parse.group(1), re.S)
              if Cats:
                 for (phUrl, phTitle) in Cats:
                    printDBG( 'Host listsItems phUrl: '  +self.MAIN_URL+phUrl )
                    printDBG( 'Host listsItems phTitle: '+phTitle )
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'DRTUBER-clips', '', None)) 
                 valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'DRTUBER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('heading bg_round(.*?)pagination', data, re.S) 
           if not parse: return valTab
           phMovies = re.findall('><a\shref="(.*?)".*?src="(.*?)"\salt="(.*?)".*?time.*?<em>(.*?)<', parse.group(1), re.S)  
           if phMovies:
              for (phUrl, phImage, phTitle, phRuntime) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<ul class="pagination".*?<div class="holder">', data, re.S)
           if match:
              match = re.findall('class="next"><a href="(.*?)"', match[0], re.S)
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'MYFREECAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.myfreecams.com' 
           url = 'https://www.myfreecams.com/mfc2/php/online_models_splash.php'
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phCats = re.findall('model_detail=(.*?)&.*?img src=(.*?jpg).*?</div>', data, re.S) 
           if phCats:
              for (phTitle, phImage) in phCats: 
                  printDBG( 'Host listsItems phTitle: '  +phTitle )
                  printDBG( 'Host listsItems phImage: '  +phImage )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phTitle, 1)], 0, phImage, None)) 
                  if config.plugins.iptvplayer.xxxsortmfc.value: valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'TNAFLIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.tnaflix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('Categories</h2>(.*?)<footer class="clear', data, re.S) 
           if parse:
              genre = re.findall('class="thumb"\shref="(.*?)".*?src="(.*?)".*?title="(.*?)"', parse.group(1), re.S)
              if genre:
                 for phUrl, phImage, phTitle in genre:
                    phTitle = decodeHtml(phTitle)
                    if phImage[:2] == "//":
                       phImage = "http:" + phImage
                    printDBG( 'Host listsItems phUrl: '  +phUrl )
                    printDBG( 'Host listsItems phTitle: '+phTitle )
                    printDBG( 'Host listsItems phImage: '+phImage )
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'TNAFLIX-clips', phImage, None)) 
                    valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'TNAFLIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall("data-vid=.*?data-original='(.*?)'.*?lt=\"(.*?)\".*?videoDuration'>(.*?)<.*?href='(.*?)'", data, re.S)  
           if phMovies:
              for ( phImage, phTitle, phRuntime, phUrl ) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.findall('class="llNav.*?href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'LIVEJASMIN' == name:
           printDBG( 'Host listsItems begin name='+name )
           #valTab.insert(0,CDisplayListItem('--- boy ---', 'boy', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/boy'], 'LIVEJASMIN-clips', '', None))
           #valTab.insert(0,CDisplayListItem('--- gay ---', 'gay', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/gay'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Transgender ---', 'Transgender', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/transgender'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Couple ---', 'Couple', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/couple'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Mature ---', 'Mature', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/mature'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Fetish ---', 'Fetish', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/fetish'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Lesbian ---', 'Lesbian', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/lesbian'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Soul_mate ---', 'Soul_mate', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/soul_mate'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Hot_flirt ---', 'Hot_flirt', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/hot_flirt'], 'LIVEJASMIN-clips', '', None))
           valTab.insert(0,CDisplayListItem('--- Girl ---', 'Girl', CDisplayListItem.TYPE_CATEGORY, ['http://new.livejasmin.com/en/girl'], 'LIVEJASMIN-clips', '', None))
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'LIVEJASMIN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://new.livejasmin.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           sessionID = self.cm.ph.getSearchGroups(data, '''"jsm2session":['"]([^"^']+?)['"]''')[0] 
           data = self.cm.ph.getDataBeetwenMarkers(data, 'listPagePerformers =', '];', False)[1]
           result = simplejson.loads(data+']')
           age = ''
           ethnicity = ''
           phImage = ''
           if result:
              for item in result:
                 try:
                    phTitle = str(item["pid"])
                    phUrl = 'http://new.livejasmin.com/en/chat/'+phTitle+'?session='+sessionID
                    try:
                       phImage = str(item["profilePictureUrl"])
                       age = str(item["age"])
                       ethnicity = str(item["ethnicity"])
                    except: pass
                    printDBG( 'Host listsItems phTitle: '  +phTitle )
                    printDBG( 'Host listsItems phUrl: '  +phUrl )
                    printDBG( 'Host listsItems phImage: '  +phImage )
                    valTab.append(CDisplayListItem(phTitle,'['+age+']  ['+ethnicity+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 except: pass
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'EL-LADIES' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://search.el-ladies.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('<select id="selSearchNiche"(.*?)</select>', data, re.S)  
           if parse:
              genre = re.findall('<option value="(\d{0,2})">(.*?)<', parse.group(1), re.S) 
              if genre:
                 for ID, phTitle in genre: 
                    if not re.match('(Bizarre|Gay|Men|Piss|Scat)', phTitle):
                       phTitle = decodeHtml(phTitle)
                       printDBG( 'Host listsItems phUrl: '  +ID )
                       printDBG( 'Host listsItems phTitle: '+phTitle )
                       phUrl = '%s/?search=%s&fun=0&niche=%s&pnum=%s&hd=%s' % (self.MAIN_URL, phTitle, ID, str(1), 1) 
                       printDBG( 'Host listsItems phUrl: '  +phUrl )
                       valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'EL-LADIES-clips', '', None)) 
                       valTab.sort(key=lambda poz: poz.name)
           valTab.insert(0,CDisplayListItem("--- New ---",       "New",       CDisplayListItem.TYPE_CATEGORY,["http://just.eroprofile.com/rss.xml"], 'EL-LADIES-new', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'EL-LADIES-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('<a\shref="http://just.eroprofile.com/play/(.*?)".*?<img\ssrc="(.*?)".*?<div>(.*?)</div>', data, re.S) 
           if phMovies:
              for (ID, phImage, Cat) in phMovies:
                  phImage = phImage.replace('&amp;','&') 
                  phTitle = decodeHtml(Cat) + ' - ' + ID
                  phTitle2 = phTitle
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  #query_data = { 'url': 'http://just.eroprofile.com/play/'+ID, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                  #try:
                  #   data = self.cm.getURLRequestData(query_data)
                  #except:
                  #   printDBG( 'Host listsItems query error' )
                  #   printDBG( 'Host listsItems query error url: '+url )
                  #   return valTab
                  #printDBG( 'Host listsItems title: '+data )
                  #tytul = re.search('<title>(.*?)</title>', data, re.S)  
                  valTab.append(CDisplayListItem(phTitle,phTitle2,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', 'http://just.eroprofile.com/play/'+ID, 1)], 0, phImage, None)) 
           match = re.findall('pnum=6.*?href="(.*?)"', data, re.S)
           if match:
              phUrl = decodeHtml(match[0])
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, ['http://search.el-ladies.com/'+phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'EL-LADIES-new' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('CDATA\[(.*?)\].*?src="(.*?)".*?<link>(.*?)</link>', data, re.S) 
           if phMovies:
              for (phTitle, phImage, phUrl) in phMovies:
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab

        if 'EXTREMETUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.extremetube.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('class="title-general">\s{0,1}Categories</h1>(.*?)footer', data, re.S)   
           if parse:
              phCats = re.findall('href="(.*?)".*?src="(.*?)".*?title="(.*?)"', parse.group(1), re.S) 
              if phCats:
                 for (phUrl, phImage, phTitle) in phCats: 
                    if phTitle != "High Definition Videos":
                       phUrl = phUrl.replace('?fromPage=categories', '') + '?page='
                       printDBG( 'Host listsItems phImage: '  +phImage )
                       printDBG( 'Host listsItems phTitle: '+phTitle )
                       printDBG( 'Host listsItems phUrl: '  +phUrl )
                       valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'EXTREMETUBE-clips', phImage, None)) 
                       valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'EXTREMETUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('data-srcmedium="(.*?)".*?title="(.*?)".*?href="(.*?)".*?id="duration.*?>(.*?)<', data, re.S) 
           if phMovies:
              for ( phImage, phTitle, phUrl, Runtime) in phMovies:
                  if phImage.startswith('//'): phImage = 'http:' + phImage
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,'['+Runtime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<link rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = decodeHtml(match[0])
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'XXXLIST' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'xxxlist.txt' 
           URLLIST_FILE    = 'xxxlist.txt'
           self.filespath = config.plugins.iptvplayer.xxxlist.value
           self.sortList = config.plugins.iptvplayer.xxxsortuj.value
           self.currFileHost = IPTVFileHost() 
           self.currFileHost.addFile(self.filespath + URLLIST_FILE, encoding='utf-8')
           tmpList = self.currFileHost.getGroups(self.sortList)
           for item in tmpList:
               if '' == item: title = (_("Other"))
               else:          title = item
               valTab.append(CDisplayListItem(title,title,CDisplayListItem.TYPE_CATEGORY, [title],'XXXLIST-clips', '', None)) 
           return valTab
        if 'XXXLIST-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           desc = ''
           icon = ''
           tmpList = self.currFileHost.getAllItems(self.sortList)
           for item in tmpList:
               if item['group'] == url:
                   Title = item['title_in_group']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   printDBG( 'Host listsItems Title:'+Title )
                   printDBG( 'Host listsItems Url:'+Url )
                   printDBG( 'Host listsItems icon:'+icon )
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
               elif url == (_("Other")) and item['group'] == '':
                   Title = item['full_title']
                   Url = item['url']
                   if item.get('icon', '') != '':
                      icon = item.get('icon', '')
                   if item.get('desc', '') != '':
                      desc = item['desc']
                   printDBG( 'Host listsItems Title:'+Title )
                   printDBG( 'Host listsItems Url:'+Url )
                   if Url.endswith('.mjpg') or Url.endswith('.cgi'):
                      valTab.append(CDisplayListItem(Title, Url,CDisplayListItem.TYPE_PICTURE, [CUrlItem('', Url, 1)], 0, '', None)) 
                   else:
                      valTab.append(CDisplayListItem(Title, desc,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 1)], 0, icon, None)) 
           return valTab

        if 'RAMPANT' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.rampant.tv' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'rampant.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host1 getResolvedURL data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'channel title=', '</channel>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              try:
                 phTitle = self.cm.ph.getSearchGroups(item, '''title="([^"]+?)"''', 1, True)[0] 
                 serwery = self.cm.ph.getSearchGroups(item, '''servers="([^"]+?)"''', 1, True)[0] 
                 appli = self.cm.ph.getSearchGroups(item, '''application="([^"]+?)"''', 1, True)[0] 
                 Stremname = self.cm.ph.getSearchGroups(item, '''streamName="([^"]+?)"''', 1, True)[0] 
                 mbr = self.cm.ph.getSearchGroups(item, '''mbr="([^"]+?)"''', 1, True)[0] 
                 phImage = self.cm.ph.getSearchGroups(item, '''logo="([^"]+?)"''', 1, True)[0].replace('{SIZE}', '80x65')
                 live = self.cm.ph.getSearchGroups(item, '''live="([^"]+?)"''', 1, True)[0] 
                 uri = serwery.split(',')[0]
                 if mbr<>'0': Stremname=Stremname+mbr
                 if appli <> 'leah' and  appli <> 'null' and  appli <> 'iframe' and  live <> '0':
                    printDBG( 'Host listsItems phTitle: '  +phTitle )
                    printDBG( 'Host listsItems serwery: '  +serwery )
                    printDBG( 'Host listsItems appli: '  +appli )
                    printDBG( 'Host listsItems Stremname: '  +Stremname )
                    printDBG( 'Host listsItems mbr: '  +mbr )
                    printDBG( 'Host listsItems phImage: '  +phImage )
                    printDBG( 'Host listsItems uri: '  +uri )
                    printDBG( 'Host listsItems live: '  +live )
                    Url = 'rtmp://%s/%s/ playpath=%s swfUrl=https://static.rampant.tv/swf/player.swf pageUrl=https://www.rampant.tv/channels live=1 ' % (uri, appli, Stremname)+ 'flashVer=WIN 12,0,0,44 '
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', Url, 0)], 0, phImage, None)) 
              except: pass
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'BONGACAMS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://pl.bongacams.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           valTab.insert(0,CDisplayListItem("--- Couples ---",       "Pary",       CDisplayListItem.TYPE_CATEGORY,["https://pl.bongacams.com/couples"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Male ---",       "Mężczyźni",       CDisplayListItem.TYPE_CATEGORY,["https://pl.bongacams.com/male"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Transsexual ---",       "Transseksualiści",       CDisplayListItem.TYPE_CATEGORY,["https://pl.bongacams.com/transsexual"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- New ---",       "Nowe",       CDisplayListItem.TYPE_CATEGORY,["https://pl.bongacams.com/new-models"], 'BONGACAMS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Female ---",       "Kobiety",       CDisplayListItem.TYPE_CATEGORY,["https://pl.bongacams.com"], 'BONGACAMS-clips', '',None))

           printDBG( 'Host listsItems end' )
           return valTab 

        if 'BONGACAMS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host query error url: '+url )
              return ''
           #printDBG( 'Host data: '+data )
           swfUrl = self.cm.ph.getSearchGroups(data, '''(/swf/chat/BCamChat[^"^']+?)['"]''', 1, True)[0] 
           if swfUrl: swfUrl = self.MAIN_URL+swfUrl
           printDBG( 'Host listsItems swfurl: '+swfUrl )
           parse = re.search('"models.":(.*?),."online_count', data, re.S)
           if not parse: return valTab
           printDBG( 'Host listsItems parse.group(1): '+parse.group(1) )
           data = parse.group(1).replace('\\','')
           result = simplejson.loads(data)
           if result:
              for item in result:
                 vsid = str(item["vsid"])  
                 phTitle = str(item["username"]) 
                 phTitle2 = str(item["display_name"]) 
                 phImage = str(item["live_image"]) 
                 if phImage.startswith('//'): phImage = 'http:' + phImage
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems phUrl: '  +vsid )
                 printDBG( 'Host listsItems phImage: '+phImage )
                 phUrl = 'rtmp://dedNUMER_SERWERA-edge%s.bongacams.com:1935/bongacams playpath=stream_%s?uid=SKROT_MD5 swfUrl=%s pageUrl=https://pl.bongacams.com/ ' % (vsid, phTitle, swfUrl)
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab 

        if 'RUSPORN' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://rusporn.tv' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('cats(.*?)<!--/noindex-->', data, re.S)
           if parse:
              printDBG( 'Host listsItems data: '+parse.group(1) )
              phCats = re.findall('a href="(.*?)"', parse.group(1), re.S)
              if phCats:
                 for (phUrl) in phCats:
                    phTitle = re.search('/(.*?)_', phUrl, re.S)
                    if phTitle: 
                       phTitle = phTitle.group(1)
                       printDBG( 'Host listsItems phUrl: '  +phUrl )
                       printDBG( 'Host listsItems phTitle: '+phTitle )
                       valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'RUSPORN-clips', '', phUrl)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'RUSPORN-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('RPThumbs(.*?)PagesLoader', data, re.S) 
           if parse:
              Movies = re.findall('a href="(.*?)".*?src="(.*?)".*?"rdur">(.*?)<', parse.group(1), re.S) 
              if Movies:
                 for (phUrl, phImage, Time) in Movies:
                    phTitle = re.search('.*?_.*?_(.*?).html', phUrl, re.S)
                    if phTitle:
                       phTitle = phTitle.group(1)
                       phUrl = 'http:'+phUrl
                       printDBG( 'Host listsItems phUrl: '  +phUrl )
                       printDBG( 'Host listsItems phTitle: '+phTitle )
                       printDBG( 'Host listsItems Time: '+Time ) 
                       valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phUrl),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 match = re.search('RPTabPages.*?class="active".*?href="(.*?)"', data, re.S)
                 if match:
                    phUrl = match.group(1)
                    valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORN720' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://porn720.net' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('id="menu-menu2"(.*?)class="sub-header"', data, re.S)
           if parse:
              phCats = re.findall('a href="(.*?)"', parse.group(1), re.S)
              if phCats:
                 for (phUrl) in phCats:
                     phTitle = phUrl.replace('http://porn720.net/tag/','')
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     valTab.append(CDisplayListItem(phTitle,phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORN720-clips', '', phUrl)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORN720-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('main class="content"(.*?)footer', data, re.S)
           if parse:
              Movies = re.findall('href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?fa-clock-o"></i>(.*?)</div>.*?href=', parse.group(1), re.S) 
              if Movies:
                 for (phUrl, phTitle, phImage, Time) in Movies:
                     Time = Time.strip()
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     printDBG( 'Host listsItems Time: '+Time ) 
                     valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phUrl),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                 match = re.search('rel="next".*?href="(.*?)"', data, re.S)
                 if match:
                    phUrl = match.group(1)
                    valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORNTREX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.porntrex.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="item"', 'class="rating')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNTREX-clips', phImage, phUrl)) 
           valTab.sort(key=lambda poz: poz.name)
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNTREX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="video-item', '</ul>')
           #printDBG( 'Host2 getResolvedURL data: '+str(data) )
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''data-original=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''fa-clock-o"></i>([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           return valTab

        if 'PORNDOE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://porndoe.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('categories-list(.*?)</header>', data, re.S)
           if parse:
              #printDBG( 'Host listsItems data2: '+parse.group(1) )
              phCats = re.findall('="(/category/.*?)".*?">(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     valTab.append(CDisplayListItem(decodeHtml(phTitle),self.MAIN_URL+phUrl,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'PORNDOE-clips', '', phUrl)) 
           self.SEARCH_proc='porndoe-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'porndoe-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://porndoe.com/search?keywords=%s' % url, 'PORNDOE-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNDOE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('video-item-thumb.*?href="(.*?)".*?image="(.*?)".*?alt="(.*?)".*?duration">.*?>(.*?)<', data, re.S) 
           if Movies:
              for (phUrl, phImage, phTitle, Time) in Movies:
                 Time = Time.strip()
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems Time: '+Time ) 
                 valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.search('page next"><a href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1).replace('amp;','')
              printDBG( 'Host listsItems Next: '+phUrl ) 
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORNFROMCZECH' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.pornfromczech.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('id="categories-2"(.*?)id="text-6"', data, re.S)
           if parse:
              phCats = re.findall('<a href="(.*?)".*?(>.*?)</a>', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     phTitle = phTitle.replace('>','')
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNFROMCZECH-clips', '', phUrl)) 
           self.SEARCH_proc='PORNFROMCZECH-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNFROMCZECH-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://pornfromczech.com/?s=%s&x=0&y=0' % url, 'PORNFROMCZECH-clips')
           printDBG( 'Host listsItems end' )
           return valTab              
        if 'PORNFROMCZECH-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('<div\sclass="thumb">.*?<a\shref="(.*?)".*?title="(.*?)">.*?<img\ssrc="(.*?)".*?<p class="duration">(.*?)</p>', data, re.S) 
           if Movies:
              for (phUrl, phTitle, phImage, Time) in Movies:
                  Time = Time.strip()
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems Time: '+Time ) 
                  #valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
                  valTab.append(CDisplayListItem(decodeHtml(phTitle), '['+Time+']    '+decodeHtml(phTitle), CDisplayListItem.TYPE_CATEGORY, [phUrl], 'PORNFROMCZECH-serwer', phImage, catUrl))                
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', catUrl))                
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNFROMCZECH-serwer' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('<iframe src="(.*?)"', data, re.S) 
           if Movies:
              for (phUrl) in Movies:
                 valTab.append(CDisplayListItem(phUrl,phUrl,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, '', None)) 
           return valTab

        if 'FILMYPORNO' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.filmyporno.tv' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('HEADER UP END(.*?)FOOTER DOWN END', data, re.S)
           if parse:
              phCats = re.findall('<a href="(.*?)".*?src="(.*?)".*?"title">(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phImage, phTitle) in phCats:
                     #phUrl = phUrl + 'page/'
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phImage: '  +phImage )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'FILMYPORNO-clips', phImage, phUrl)) 
           valTab.insert(0,CDisplayListItem("--- NAJDŁUŻSZE ---",       "NAJDŁUŻSZE",                    CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/longest/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJCZĘŚCIEJ DYSKUTOWANE ---","NAJCZĘŚCIEJ DYSKUTOWANE", CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-discussed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJLEPIEJ OCENIONE ---",     "NAJLEPIEJ OCENIONE",      CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/top-rated/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NAJPOPULARNIEJSZE ---",      "NAJPOPULARNIEJSZE",       CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/most-viewed/"], 'FILMYPORNO-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- NOWE FILMY ---",             "NOWE FILMY",              CDisplayListItem.TYPE_CATEGORY,["http://www.filmyporno.tv/videos/"], 'FILMYPORNO-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'FILMYPORNO-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('HEADER UP END(.*?)FOOTER DOWN END', data, re.S)
           if parse:
              Movies = re.findall('<a\shref="(.*?)".*?src="(.*?)".*?lt="(.*?)".*?"time">(.*?)<.*?item\sEND', parse.group(1), re.S) 
              if Movies:
                 for (phUrl, phImage, phTitle, Time) in Movies:
                    Time = Time.strip()
                    printDBG( 'Host listsItems phUrl: '  +phUrl )
                    printDBG( 'Host listsItems phTitle: '+phTitle )
                    printDBG( 'Host listsItems Time: '+Time ) 
                    valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              url = re.sub('page.+', '', url)
              valTab.append(CDisplayListItem('Next ', 'Page: '+url+phUrl, CDisplayListItem.TYPE_CATEGORY, [url+phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'CLIPHUNTER' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.cliphunter.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('id="submenu-categories">(.*?)</div>', data, re.S)
           if parse:
              phCats = re.findall('href="(/categories/.*?)".*?>(.*?)<', parse.group(1), re.S)
              if phCats:
                 for (phUrl, phTitle) in phCats:
                     phUrl = 'http://www.cliphunter.com%s/' % phUrl.replace(' ','%20')
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     #if not phTitle == "All" and not phTitle == "More ...  ": 
                     if phTitle <> "More ... ": 
                        valTab.append(CDisplayListItem(decodeHtml(phTitle),phUrl,CDisplayListItem.TYPE_CATEGORY, [phUrl],'CLIPHUNTER-clips', '', phUrl)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'CLIPHUNTER-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Movies = re.findall('class="t"\shref="(.*?)".*?class="i"\ssrc="(.*?)".*?class="tr">(.*?)</div>.*?class="vttl.*?">(.*?)</a>', data, re.S) 
           if Movies:
              for (phUrl, phImage, Time, phTitle) in Movies:
                 Time = Time.strip()
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems Time: '+Time )
                 if Time[:2]<>'00': 
                    valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']    '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           match = re.search('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match.group(1)
              valTab.append(CDisplayListItem('Next ', 'Page: '+self.MAIN_URL+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))                
           printDBG( 'Host listsItems end' )
           return valTab

        if 'EMPFLIX' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.empflix.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           genre = re.findall('"thumb"\shref="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S) 
           if genre:
              for (phUrl, phImage, phTitle) in genre:
                 phTitle = decodeHtml(phTitle)
                 phImage = 'http:'+phImage
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 printDBG( 'Host listsItems phImage: '+phImage )
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'EMPFLIX-clips', phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'EMPFLIX-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall("data-vid='.*?data-name='(.*?)'.*?href='(.*?)'.*?data-original='(.*?)'.*?videoDuration\'>(.*?)<", data, re.S)  
           if phMovies:
              for ( phTitle, phUrl, phImage, phRuntime) in phMovies:
                  if phUrl[:2] == "//":
                     phUrl = "http:" + phUrl
                  else:
                     phUrl = self.MAIN_URL + phUrl
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('<a class="llNav".*?href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORNOHUB' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornohub.su' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('<a href="#">Categories<(.*?)pornohub.su/my-list/', data, re.S)
           if parse:
              phCats = re.findall('href="(.*?)"', parse.group(1), re.S) 
              if phCats:
                 for (phUrl) in phCats:
                    phTitle = decodeHtml(phUrl).replace ('https://pornohub.su/porn/','').replace('/','')
                    printDBG( 'Host listsItems phUrl: '  +phUrl )
                    printDBG( 'Host listsItems phTitle: '+phTitle )
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOHUB-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- PORNSTARS ---",      "PORNSTARS", CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/pornstars/"], 'PORNOHUB-pornstars', '',None))
           valTab.insert(0,CDisplayListItem("--- PREMIUM SELECTION ---",     "PREMIUM SELECTION",      CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/premium-selection/"], 'PORNOHUB-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- MOFOS HD 720 ---","MOFOS HD 720", CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/mofos/"], 'PORNOHUB-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- BRAZZERS ---",       "BRAZZERS",  CDisplayListItem.TYPE_CATEGORY,["http://pornohub.su/porn/brazzers/"], 'PORNOHUB-clips', '',None))
           self.SEARCH_proc='PORNOHUB-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOHUB-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://pornohub.su/?s=%s' % url, 'PORNOHUB-pornstars-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOHUB-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('<div class="td-category-grid">(.*?)page-nav', data, re.S)
           if parse:
              #printDBG( 'Host listsItems parse: '+parse.group(1) )
              if not '/page/' in url:
                 hot5 = re.search('<div class="td-container">(.*?)"entry-thumb99">', parse.group(1), re.S)
                 phMovies = re.findall('thumb"><a href="(.*?)".*?title="(.*?)".*?src="(.*?)"', hot5.group(1), re.S)  
                 if phMovies:
                    for ( phUrl, phTitle, phImage) in phMovies:
                        phTitle = decodeHtml(phTitle)
                        phRuntime = '-'
                        printDBG( 'Host listsItems phUrl: '  +phUrl )
                        printDBG( 'Host listsItems phImage: '+phImage )
                        printDBG( 'Host listsItems phTitle: '+phTitle )
                        printDBG( 'Host listsItems phRuntime: '+phRuntime )
                        valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
              phMovies = re.findall('"entry-thumb99">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?"time">(.*?)</div>', parse.group(1), re.S)  
              if phMovies:
                 for ( phUrl, phTitle, phImage, phRuntime) in phMovies:
                     phTitle = decodeHtml(phTitle)
                     printDBG( 'Host listsItems phUrl: '  +phUrl )
                     printDBG( 'Host listsItems phImage: '+phImage )
                     printDBG( 'Host listsItems phTitle: '+phTitle )
                     printDBG( 'Host listsItems phRuntime: '+phRuntime )
                     valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('</a><a href="(.*?)"', data, re.S)
           if match:
              phUrl = match[-1]
              if '#' in phUrl: phUrl = match[-2]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOHUB-pornstars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('"td-module-image44">.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)".*?camera"></i>(.*?)</div>', data, re.S)  
           if phMovies:
              for ( phUrl, phTitle, phImage, phRuntime) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle, 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl+'#videos'], 'PORNOHUB-pornstars-clips', phImage, None))
                  #valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('</a><a href="(.*?)"', data, re.S)
           if match:
              phUrl = match[-1]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOHUB-pornstars-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('td-block-span.*?"time">(.*?)<.*?href="(.*?)".*?title="(.*?)".*?src="(.*?)"', data, re.S)  
           if phMovies:
              for ( phRuntime, phUrl, phTitle, phImage) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           phMovies = re.findall('WPcommentSearch.*?href="(.*?)".*?src="(.*?)".*?alt="(.*?)"', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle ) in phMovies:
                  phTitle = decodeHtml(phTitle)
                  phRuntime = '-'
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab

        if 'THUMBZILLA' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.thumbzilla.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Cats = re.findall('href="(/categories/.*?)".*?click\',\s\'(.*?)\'', data, re.S) 
           if Cats:
              for (phUrl, phTitle) in Cats:
                 phTitle = decodeHtml(phTitle)
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 if not phTitle == "All": 
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'THUMBZILLA-clips', '', None)) 
           valTab.insert(0,CDisplayListItem("--- Homemade ---",     "Homemade",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/homemade"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- HD Videos ---","HD Videos", CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/hd"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular Videos ---",     "Popular Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/popular"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top Videos ---",     "Top Videos",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/top"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Trending ---",     "Trending",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/trending"], 'THUMBZILLA-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---",     "Newest",      CDisplayListItem.TYPE_CATEGORY,[self.MAIN_URL+"/newest"], 'THUMBZILLA-clips', '',None))
           self.SEARCH_proc='THUMBZILLA-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'THUMBZILLA-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.thumbzilla.com/tags/%s' % url, 'THUMBZILLA-clips')
           printDBG( 'Host listsItems end' )
           return valTab          
        if 'THUMBZILLA-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           phMovies = re.findall('href="(/video/.*?)".*?src="(.*?)".*?"title">(.*?)<.*?"duration">(.*?)<', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle, phRuntime) in phMovies:
                  if phUrl[:2] == "//":
                     phUrl = "http:" + phUrl
                  else:
                     phUrl = self.MAIN_URL + phUrl
                  if phImage[:2] == "//":
                     phImage = "http:" + phImage
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  printDBG( 'Host listsItems phRuntime: '+phRuntime )
                  valTab.append(CDisplayListItem(phTitle,'['+phRuntime+'] '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('"next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'ADULT' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://adult-channels.com' 
           COOKIEFILE = os_path.join(GetCookieDir(), 'adult.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host listsItems query error cookie' )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           Cats = re.findall('class="clip-link".*?title="(.*?)".*?img src="(.*?)".*?href="(.*?)"', data, re.S) 
           if Cats:
              for ( phTitle, phImage, phUrl) in Cats:
                 phTitle = decodeHtml(phTitle)
                 printDBG( 'Host listsItems phUrl: '  +phUrl )
                 printDBG( 'Host listsItems phTitle: '+phTitle )
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           match = re.findall('rel="next" href="(.*?)"', data, re.S)
           if match:
              phUrl = match[0]
              printDBG( 'Host listsItems page phUrl: '+phUrl )
              valTab.append(CDisplayListItem('Next', 'Page: '+phUrl, CDisplayListItem.TYPE_CATEGORY, [phUrl], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'YUVUTU' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.yuvutu.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page = 1
           parse = re.search('Categories</h1>(.*?)footer-pub-centered', data, re.S) 
           if parse:
              genre = re.findall('href="(.*?)".*?src="(.*?)".*?title="(.*?)".*?videos</span>', parse.group(1), re.S) 
              if genre:
                 for (phUrl, phImage, phTitle) in genre:
                    phTitle = decodeHtml(phTitle)
                    phTitle = re.sub(' - .+', '', phTitle)
                    printDBG( 'Host listsItems phUrl: '  +phUrl )
                    printDBG( 'Host listsItems phImage: '+phImage )
                    printDBG( 'Host listsItems phTitle: '+phTitle )
                    valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [self.MAIN_URL+phUrl],'YUVUTU-clips', phImage, None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'YUVUTU-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           self.page += 1
           phMovies = re.findall('class="thumb-image">.*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"', data, re.S)  
           if phMovies:
              for ( phUrl, phImage, phTitle ) in phMovies:
                  phTitle = phTitle.replace(' - ','')
                  printDBG( 'Host listsItems phUrl: '  +phUrl )
                  printDBG( 'Host listsItems phImage: '+phImage )
                  printDBG( 'Host listsItems phTitle: '+phTitle )
                  valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           url = re.sub('page.+', '', url)
           valTab.append(CDisplayListItem('Next', 'Page: '+str(self.page), CDisplayListItem.TYPE_CATEGORY, [url+'page/'+str(self.page)+'/'], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'X3XTUBE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.x3xtube.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<option', '/option>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''>([^"^']+?)<''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''value=['"]([^"^']+?)['"]''', 1, True)[0] 
              phUrl = 'http://www.x3xtube.com/index.php?go=channel&nid=%s' % phUrl
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              if phTitle<>'All Channels':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'X3XTUBE-clips', '', None))
           valTab.insert(0,CDisplayListItem("--- Most Viewed ---", "Most Viewed", CDisplayListItem.TYPE_CATEGORY,['http://www.x3xtube.com/index.php?go=mv'], 'X3XTUBE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Recent ---", "Most Recent", CDisplayListItem.TYPE_CATEGORY,['http://www.x3xtube.com/index.php?go=mr'], 'X3XTUBE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Most Discussed ---", "Most Discussed", CDisplayListItem.TYPE_CATEGORY,['http://www.x3xtube.com/index.php?go=md'], 'X3XTUBE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Best Rated ---", "Best Rated", CDisplayListItem.TYPE_CATEGORY,['http://www.x3xtube.com/index.php?go=br'], 'X3XTUBE-clips', '',None))
           self.SEARCH_proc='x3xtube-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'x3xtube-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.x3xtube.com/search.php?q=%s' % url, 'X3XTUBE-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'X3XTUBE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           catUrl = self.currList[Index].possibleTypesOfSearch
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = ''
           next = self.cm.ph.getDataBeetwenMarkers(data, 'Found:', 'NEXT', False)[1]
           next = self.cm.ph.getAllItemsBeetwenMarkers(next, '<a', '<font')
           for item in next:
              next_page = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
           data = self.cm.ph.getDataBeetwenMarkers(data, 'START THUMBS', 'START TRADE THUMBS', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<td width=', '</table>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''<td><font size='1'>([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', self.MAIN_URL+phUrl, 1)], 0, phImage, None)) 
           if next_page:
              valTab.append(CDisplayListItem('Next', next_page, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORNICOM' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://pornicom.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="item">', '<div class="info">')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNICOM-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Most popular ---", "Most popular", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/most-popular/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Latest updates ---", "Latest updates", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/latest-updates/'], 'PORNICOM-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top rated ---", "Top rated", CDisplayListItem.TYPE_CATEGORY,['http://www.pornicom.com/top-rated/'], 'PORNICOM-clips', '',None))
           self.SEARCH_proc='pornicom-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'pornicom-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.pornicom.com/search/?q=%s' % url, 'PORNICOM-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNICOM-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'pagination', '</div>', False)[1]
           #printDBG( 'Host listsItems next_page: '+next_page )
           next_page = self.cm.ph.getDataBeetwenMarkers(next_page, '</span>', 'Page', False)[1]
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           #printDBG( 'Host listsItems next_page: '+next_page )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="image" >', '<div class="g_clear">')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''class="length">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              printDBG( 'Host listsItems next_page: '  +next_page )
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'HDZOG' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hdzog.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-categories">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''"title">([^"^']+?)<''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phImage: '+phImage )
              valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HDZOG-clips', phImage, None))
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/longest/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---", "Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/popular/'], 'HDZOG-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---", "Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.hdzog.com/new/'], 'HDZOG-clips', '',None))
           self.SEARCH_proc='hdzog-search'
           valTab.insert(0,CDisplayListItem('Historia wyszukiwania', 'Historia wyszukiwania', CDisplayListItem.TYPE_CATEGORY, [''], 'HISTORY', '', None)) 
           valTab.insert(0,CDisplayListItem('Szukaj',  'Szukaj filmów',                       CDisplayListItem.TYPE_SEARCH,   [''], '',        '', None)) 
           printDBG( 'Host listsItems end' )
           return valTab
        if 'hdzog-search' == name:
           printDBG( 'Host listsItems begin name='+name )
           valTab = self.listsItems(-1, 'http://www.hdzog.com/search/?q=%s' % url, 'HDZOG-clips')
           printDBG( 'Host listsItems end' )
           return valTab
        if 'HDZOG-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next">', '</li>', False)[1]
           #printDBG( 'Host listsItems next_page: '+next_page )
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           #printDBG( 'Host listsItems next_page: '+next_page )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumbs-videos">', 'video thumbs list', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''title=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''class="time">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              printDBG( 'Host listsItems next_page: '  +next_page )
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'HCLIPS' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'http://www.hclips.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'list list_cols">', 'gay-panel', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''<strong>([^"^']+?)</strong>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              if phTitle<>'':
                 valTab.append(CDisplayListItem(phTitle,phTitle,CDisplayListItem.TYPE_CATEGORY, [phUrl],'HCLIPS-clips', '', None))
           valTab.insert(0,CDisplayListItem("--- Longest ---", "Longest", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/longest/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Popular ---", "Popular", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/most-popular/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Top ---", "Top", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/top-rated/'], 'HCLIPS-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Newest ---", "Newest", CDisplayListItem.TYPE_CATEGORY,['http://www.hclips.com/latest-updates/'], 'HCLIPS-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'HCLIPS-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           #printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'class="next">', 'Next', False)[1]
           #printDBG( 'Host listsItems next_page: '+next_page )
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           #printDBG( 'Host listsItems next_page: '+next_page )
           data = self.cm.ph.getDataBeetwenMarkers(data, 'class="thumb_holder">', 'js-pagination', False)[1]
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''"dur">([^"^']+?)<''', 1, True)[0] 
              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(phTitle,'['+Time+']   '+phTitle,CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-2]
              printDBG( 'Host listsItems next_page: '  +next_page )
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab

        if 'PORNOMENGE' == name:
           printDBG( 'Host listsItems begin name='+name )
           self.MAIN_URL = 'https://www.pornomenge.com' 
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url:'+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', '</h4>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''">([^"^']+?)</a>''', 1, True)[0]
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phTitle: '+phTitle )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           valTab.insert(0,CDisplayListItem("--- Kanale ---", "Kanale", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/websites/videos/'], 'PORNOMENGE-clips', '',None))
           valTab.insert(0,CDisplayListItem("--- Pornostars ---", "Pornostars", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/pornostars/'], 'PORNOMENGE-Pornostars', '',None))
           valTab.insert(0,CDisplayListItem("--- Beste Videos ---", "Beste Videos", CDisplayListItem.TYPE_CATEGORY,['https://www.pornomenge.com/am-meisten-gestimmt/m/'], 'PORNOMENGE-clips', '',None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOMENGE-clips' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           #printDBG( 'Host listsItems next_page: '+next_page )
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           #printDBG( 'Host listsItems next_page: '+next_page )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-escena">', 'class="votar-escena')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage

              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),'['+Time+']   '+decodeHtml(phTitle),CDisplayListItem.TYPE_VIDEO, [CUrlItem('', phUrl, 1)], 0, phImage, None)) 
           if next_page: 
              numer = next_page.split('/')[-1]
              printDBG( 'Host listsItems next_page: '  +next_page )
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab
        if 'PORNOMENGE-Pornostars' == name:
           printDBG( 'Host listsItems begin name='+name )
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error url: '+url )
              return valTab
           printDBG( 'Host listsItems data: '+data )
           next_page = self.cm.ph.getDataBeetwenMarkers(data, 'rel="next"', '/>', False)[1]
           #printDBG( 'Host listsItems next_page: '+next_page )
           next_page = self.cm.ph.getSearchGroups(next_page, '''href=['"]([^"^']+?)['"]''')[0] 
           if next_page.startswith('/'): next_page = self.MAIN_URL + next_page
           #printDBG( 'Host listsItems next_page: '+next_page )
           data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'class="wrap-box-chica">', 'class="clear"></div>')
           for item in data:
              phTitle = self.cm.ph.getSearchGroups(item, '''alt=['"]([^"^']+?)['"]''', 1, True)[0].strip() 
              phUrl = self.cm.ph.getSearchGroups(item, '''href=['"]([^"^']+?)['"]''', 1, True)[0] 
              phImage = self.cm.ph.getSearchGroups(item, '''src=['"]([^"^']+?)['"]''', 1, True)[0] 
              Time = self.cm.ph.getSearchGroups(item, '''duracion">([^"^']+?)<''', 1, True)[0] 
              if phUrl.startswith('/'): phUrl = self.MAIN_URL + phUrl
              if phImage.startswith('//'): phImage = 'http:' + phImage

              printDBG( 'Host listsItems phTitle: '+phTitle )
              printDBG( 'Host listsItems phUrl: '  +phUrl )
              printDBG( 'Host listsItems phImage: '+phImage )
              printDBG( 'Host listsItems Time: '+Time )
              valTab.append(CDisplayListItem(decodeHtml(phTitle),decodeHtml(phTitle),CDisplayListItem.TYPE_CATEGORY, [phUrl],'PORNOMENGE-clips', '', None))
           if next_page: 
              numer = next_page.split('/')[-1]
              printDBG( 'Host listsItems next_page: '  +next_page )
              valTab.append(CDisplayListItem('Next', 'Next '+numer, CDisplayListItem.TYPE_CATEGORY, [next_page], name, '', None))
           printDBG( 'Host listsItems end' )
           return valTab
        return valTab


    def getLinksForVideo(self, url):
        printDBG("Urllist.getLinksForVideo url[%s]" % url)
        videoUrls = []
        uri, params   = DMHelper.getDownloaderParamFromUrl(url)
        printDBG(params)
        uri = urlparser.decorateUrl(uri, params)
       
        urlSupport = self.up.checkHostSupport( uri )
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt( uri )
            videoUrls.extend(retTab)
            printDBG("Video url[%s]" % videoUrls)
            return videoUrls

    def getParser(self, url):
        printDBG( 'Host getParser begin' )
        printDBG( 'Host getParser mainurl: '+self.MAIN_URL )
        printDBG( 'Host getParser url    : '+url )
        if self.MAIN_URL == 'https://www.pornomenge.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://www.yuvutu.com':         return self.MAIN_URL
        if self.MAIN_URL == 'https://www.camsoda.com/':      return self.MAIN_URL
        if self.MAIN_URL == 'http://adult-channels.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.thumbzilla.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://pornohub.su':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.cliphunter.com':     return self.MAIN_URL
        if url.startswith('http://www.slutsxmovies.com/embed/'): return 'http://www.nuvid.com'
        if url.startswith('http://www.cumyvideos.com/embed/'):   return 'http://www.nuvid.com'
        if self.MAIN_URL == 'http://www.filmyporno.tv':      return self.MAIN_URL
        if self.MAIN_URL == 'http://porndoe.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.porntrex.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://porn720.net':            return self.MAIN_URL
        if self.MAIN_URL == 'http://rusporn.tv':             return self.MAIN_URL
        if self.MAIN_URL == 'http://www.extremetube.com':    return self.MAIN_URL
        if self.MAIN_URL == 'http://search.el-ladies.com':   return self.MAIN_URL
        if self.MAIN_URL == 'http://new.livejasmin.com':     return self.MAIN_URL
        if self.MAIN_URL == 'https://pl.bongacams.com':      return self.MAIN_URL
        if self.MAIN_URL == 'https://www.tnaflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'https://www.empflix.com':       return self.MAIN_URL
        if self.MAIN_URL == 'http://www.myfreecams.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://www.drtuber.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.dachix.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.youjizz.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.cam4.pl':            return self.MAIN_URL
        if self.MAIN_URL == 'http://www.amateurporn.net':    return self.MAIN_URL
        if self.MAIN_URL == 'https://chaturbate.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.ah-me.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornhd.com':         return self.MAIN_URL
        if self.MAIN_URL == 'http://www.pornrabbit.com':     return self.MAIN_URL
        if url.startswith('http://www.pornrabbit.com'):      return 'http://www.pornrabbit.com'
        if self.MAIN_URL == 'http://beeg.com':               return self.MAIN_URL
        if url.startswith('http://www.tube8.com/embed/'):    return 'http://www.tube8.com/embed/'
        if url.startswith('http://www.tube8.com'):           return 'http://www.tube8.com'
        if self.MAIN_URL == 'http://www.tube8.com':          return self.MAIN_URL
        if url.startswith('http://embed.redtube.com'):       return 'http://embed.redtube.com'
        if url.startswith('http://www.redtube.com'):         return 'http://www.redtube.com'
        if self.MAIN_URL == 'http://www.redtube.com':        return self.MAIN_URL
        if url.startswith('http://www.youporn.com/embed/'):  return 'http://www.youporn.com/embed/'
        if url.startswith('http://www.youporn.com'):         return 'http://www.youporn.com'
        if self.MAIN_URL == 'http://www.youporn.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://showup.tv':              return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xnxx.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.xvideos.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://hentaigasm.com':         return 'file: '
        if self.MAIN_URL =='http://xhamsterlive.com':        return 'http://xhamster.com/cams'
        if self.MAIN_URL == 'http://xhamster.com':           return self.MAIN_URL
        if self.MAIN_URL == 'http://www.eporner.com':        return self.MAIN_URL
        if url.startswith('http://www.pornhub.com/embed/'):  return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com/embed/'):   return 'http://www.pornhub.com/embed/'
        if url.startswith('http://pl.pornhub.com'):          return 'http://www.pornhub.com'
        if url.startswith('http://www.pornhub.com'):         return 'http://www.pornhub.com'
        if self.MAIN_URL == 'http://www.pornhub.com':        return self.MAIN_URL
        if self.MAIN_URL == 'http://www.4tube.com':          return self.MAIN_URL
        if self.MAIN_URL == 'http://www.hdporn.net':         return self.MAIN_URL
        if self.MAIN_URL == 'http://m.tube8.com':            return self.MAIN_URL
        if self.MAIN_URL == 'http://mobile.youporn.com':     return self.MAIN_URL
        if self.MAIN_URL == 'http://m.pornhub.com':          return self.MAIN_URL
        if url.startswith('http://www.xnxx.com'):            return 'http://www.xnxx.com'
        if url.startswith('http://www.xvideos.com'):         return 'http://www.xvideos.com'
        if url.startswith('http://hentaigasm.com'):          return 'http://hentaigasm.com'
        if url.startswith('http://xhamster.com'):            return 'http://xhamster.com'
        if url.startswith('https://xhamster.com'):           return 'http://xhamster.com'
        if url.startswith('http://www.eporner.com'):         return 'http://www.eporner.com'
        if url.startswith('http://www.4tube.com'):           return 'http://www.4tube.com'
        if url.startswith('http://www.hdporn.net'):          return 'http://www.hdporn.net'
        if url.startswith('http://m.tube8.com'):             return 'http://m.tube8.com'
        if url.startswith('http://mobile.youporn.com'):      return 'http://mobile.youporn.com'
        if url.startswith('http://m.pornhub.com'):           return 'http://m.pornhub.com'
        if url.startswith('http://www.katestube.com'):       return 'file: '
        if url.startswith('http://www.x3xtube.com'):         return 'file: '
        if url.startswith('http://www.nuvid.com'):           return 'http://www.nuvid.com'
        if url.startswith('http://www.wankoz.com'):          return 'file: '
        if url.startswith('http://hornygorilla.com'):        return 'file: '
        if url.startswith('http://www.vikiporn.com'):        return '1file: "'
        if url.startswith('http://www.fetishshrine.com'):    return 'file: '
        if url.startswith('http://www.hdzog.com'):           return "file': '"
        if url.startswith('http://www.sunporno.com'):        return 'http://www.sunporno.com'
        if url.startswith('http://www.befuck.com'):          return "video_url: '"
        if url.startswith('http://www.drtuber.com'):         return 'http://www.drtuber.com'
        if url.startswith('http://www.pornoxo.com'):         return 'http://www.pornoxo.com'
        if url.startswith('http://theclassicporn.com'):      return "video_url: '"
        if url.startswith('http://www.tnaflix.com'):         return 'https://www.tnaflix.com'
        if url.startswith('https://alpha.tnaflix.com'):      return 'https://alpha.tnaflix.com'
        if url.startswith('http://www.faphub.xxx'):          return 'http://www.faphub.xxx'
        if url.startswith('http://www.sleazyneasy.com'):     return 'file: '
        if url.startswith('http://www.proporn.com'):         return 'http://www.proporn.com'
        if url.startswith('http://www.tryboobs.com'):        return "video_url: '"
        if url.startswith('http://www.empflix.com'):         return "video_url: '"
        if url.startswith('http://www.viptube.com'):         return 'http://www.nuvid.com'
        if url.startswith('http://pervclips.com'):           return 'http://www.wankoz.com'
        if url.startswith('http://www.jizz.us'):             return 'http://www.x3xtube.com'
        if url.startswith('http://www.pornstep.com'):        return 'videoFile="'
        if url.startswith('http://www.azzzian.com'):         return "video_url: '"
        if url.startswith('https://openload.co'):            return 'xxxlist.txt'
        if url.startswith('http://openload.co'):             return 'xxxlist.txt'
        if url.startswith('https://oload.tv'):               return 'xxxlist.txt'
        if url.startswith('http://www.cda.pl'):              return 'xxxlist.txt'
        if url.startswith('https://vidlox.tv'):              return 'https://vidlox.tv'
        if url.startswith('http://hqq.tv'):                  return 'xxxlist.txt'
        if url.startswith('https://hqq.tv'):                  return 'xxxlist.txt'
        if url.startswith('https://www.rapidvideo.com'):     return 'xxxlist.txt'
        if url.startswith('http://videomega.tv'):            return 'xxxlist.txt'
        if url.startswith('http://www.flashx.tv'):           return 'xxxlist.txt'
        if url.startswith('http://www.porndreamer.com'):     return 'http://www.x3xtube.com'
        if url.startswith('http://pornicom.com'):            return 'http://pornicom.com'
        if url.startswith('https://pornicom.com'):            return 'http://pornicom.com'
        if url.startswith('http://www.pornicom.com'):        return 'http://pornicom.com'
        if url.startswith('http://www.tubeon.com'):          return 'http://www.tubeon.com'
        if url.startswith('http://www.finevids.xxx'):        return "video_url: '"
        if url.startswith('http://www.pornwhite.com'):       return 'file: '
        if url.startswith('http://www.hotshame.com'):        return "video_url: '"
        if url.startswith('http://www.xfig.net'):            return 'videoFile="'
        if url.startswith('http://www.pornoid.com'):         return "video_url: '"
        if url.startswith('http://www.thenewporn.com'):      return "video_url: '"
        if url.startswith('http://tubeq.xxx'):               return 'http://www.faphub.xxx'
        if url.startswith('http://www.wetplace.com'):        return "video_url: '"
        if url.startswith('http://www.pinkrod.com'):         return "video_url: '"
        if url.startswith('http://sexylies.com'):            return 'http://sexylies.com'
        if url.startswith('http://www.eskimotube.com'):      return 'http://www.eskimotube.com'
        if url.startswith('http://www.pornalized.com'):      return "video_url: '"
        if url.startswith('http://www.porn5.com'):           return 'http://www.porn5.com'
        if url.startswith('http://www.pornyeah.com'):        return 'http://www.pornyeah.com'
        if url.startswith('http://www.porn.com'):            return 'http://www.porn5.com'
        if url.endswith('.mjpg'):                            return 'mjpg_stream'
        if url.endswith('.cgi'):                             return 'mjpg_stream'
        if url.startswith('http://porndoe.com'):             return 'http://porndoe.com'
        if url.startswith('http://www.yeptube.com'):         return 'http://www.yeptube.com'
        if url.startswith('http://www.upornia.com'):         return "video_url: '"
        if url.startswith('http://www.pornpillow.com'):      return 'http://www.pornpillow.com'
        if url.startswith('http://porneo.com'):              return 'http://www.nuvid.com'
        if self.MAIN_URL == 'http://www.pornfromczech.com':  return self.MAIN_URL
        if url.startswith('http://www.5fing.com'):           return 'file: '
        if url.startswith('http://www.pornroxxx.com'):       return "0p'  : '"
        if url.startswith('http://www.hd21.com'):            return "0p'  : '"
        if url.startswith('http://www.txxx.com'):            return "file': '"
        if url.startswith('http://www.pornrox.com'):         return "0p'  : '"
        if url.startswith('http://www.flyflv.com'):          return 'http://www.flyflv.com'
        if url.startswith('http://www.pornerbros.com'):      return 'http://www.pornerbros.com'
        if url.startswith('http://www.xtube.com'):           return 'https://vidlox.tv'
        if url.startswith('http://xxxkingtube.com'):         return 'http://xxxkingtube.com'
        if url.startswith('http://www.boyfriendtv.com'):     return 'source src="'
        if url.startswith('http://pornxs.com'):              return 'http://pornxs.com'
        if url.startswith('http://www.hclips.com'):          return "file': '"
        if url.startswith('http://www.ashemaletube.com'):    return 'source src="'
        if url.startswith('http://pornsharing.com'):         return 'http://pornsharing.com'
        if url.startswith('http://www.xerotica.com'):        return 'http://pornohub.su'
        if url.startswith('http://www.updatetube.com'):      return "video_url: '"
        if url.startswith('http://www.vivatube.com'):        return 'http://vivatube.com'
        if url.startswith('http://www.clipcake.com'):        return 'videoFile="'
        if url.startswith('http://www.cliplips.com'):        return 'videoFile="'
        if url.startswith('http://www.sheshaft.com'):        return 'file: '
        if url.startswith('http://www.vid2c.com'):           return 'videoFile="'
        if url.startswith('http://www.bonertube.com'):       return 'videoFile="'

        return ''

    def getResolvedURL(self, url):
        printDBG( 'Host getResolvedURL begin' )
        printDBG( 'Host getResolvedURL url: '+url )
        videoUrl = ''
        parser = self.getParser(url)
        printDBG( 'Host getResolvedURL parser: '+parser )
        if parser == '': return url

        if parser == 'mjpg_stream':
           stream=urllib.urlopen(url)
           bytes=''
           while True:
              bytes+=stream.read(1024)
              a = bytes.find('\xff\xd8')
              b = bytes.find('\xff\xd9')
              if a!=-1 and b!=-1:
                 jpg = bytes[a:b+2]
                 bytes= bytes[b+2:]
                 with open('/tmp/obraz.jpg', 'w') as titleFile:  
                    titleFile.write(jpg) 
                    return 'file:///tmp/obraz.jpg'
           return ''

        if parser == 'http://www.porntrex.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'porntrex.cookie')
           self.defaultParams = {'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': COOKIEFILE}
           sts, data = self.getPage(url, 'porntrex.cookie', 'porntrex.com', self.defaultParams)
           if not sts: return ''
           #printDBG( 'Host listsItems data: '+str(data) )
           if 'video is a private' in data:
              SetIPTVPlayerLastHostError(_(' This video is a private.'))
              return []
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url2: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url2 High: '+videoPage )
              return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''video_alt_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_alt_url Medium: '+videoPage )
              return videoPage
           videoPage = self.cm.ph.getSearchGroups(data, '''video_url: ['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              printDBG( 'Host videoPage video_url Low: '+videoPage )
              return videoPage
           return ''

        if parser == 'http://beeg.com':
           printDBG( 'self.beeg_version: '+self.beeg_version)
           urljs = 'http://static.beeg.com/cpl/%s.js' % self.beeg_version
           query_data = {'url': urljs, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
           try:
              data = self.cm.getURLRequestData(query_data)
              #printDBG( 'Host getResolvedURL data: '+data )
           except:
              printDBG( 'Host getResolvedURL query error' )
           parse = re.search('beeg_salt="(.*?)"', data, re.S)
           if parse: a = parse.group(1)

           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'second beeg-clips data: '+data )
           bestUrl = re.findall('0p":"(.*?)"', data, re.S)
           if bestUrl:
              phUrl = 'http:%s' % bestUrl[-1]
              phUrl = phUrl.replace('{DATA_MARKERS}','data=pc.DE')
              key = re.search(r'/key=(.*?)%2Cend=', phUrl, 0) 
              key = key.group(1)
              printDBG( 'key encrypt : '+key )
              key = decrypt_key(key, a)	
              printDBG( 'key decrypt: '+key )
              videoUrl = re.sub(r'/key=(.*?)%2Cend=', '/key='+key+',end=', phUrl)
              return videoUrl
           else: return ''
  
        if parser == 'http://showup.tv':
           COOKIEFILE = os_path.join(GetCookieDir(), 'showup.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           parse = re.search("var srvE = '(.*?)'", data, re.S)
           if parse:
              printDBG( 'Host Url: '+url)
              printDBG( 'Host rtmp: '+ parse.group(1))
              rtmp = parse.group(1)
           startChildBug = re.search("startChildBug\(user\.uid, '', '([\s\S]+?)'", data, re.I);
           if startChildBug:
              s = startChildBug.group(1)
              printDBG( 'Host startChildBug: '+ s)
              ip = ''
              t = re.search(r"(.*?):(.*?)", s, re.I)
              if t.group(1) == 'j12.showup.tv': ip = '94.23.171.122'
              if t.group(1) == 'j13.showup.tv': ip = '94.23.171.121'
              if t.group(1) == 'j11.showup.tv': ip = '94.23.171.115'
              if t.group(1) == 'j14.showup.tv': ip = '94.23.171.120'
              printDBG( 'Host IP: '+ip)
              port = s.replace(t.group(1)+':', '')
              printDBG( 'Host Port: '+port)
              modelName = url.replace('http://showup.tv/','')
              printDBG( 'Host modelName: '+modelName)

              libsPath = GetPluginDir('libs/')
              import sys
              sys.path.insert(1, libsPath)
              import websocket 
              wsURL1 = 'ws://'+s
              wsURL2 = 'ws://'+ip+':'+port
              printDBG( 'Host wsURL1: '+wsURL1)
              printDBG( 'Host wsURL2: '+wsURL2)
              ws = websocket.create_connection(wsURL2)

              zapytanie = '{ "id": 0, "value": ["", ""]}'
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result: '+result)

              zapytanie = '{ "id": 2, "value": ["%s"]}' % modelName
              zapytanie = zapytanie.decode("utf-8")
              printDBG( 'Host zapytanie: '+zapytanie)
              ws.send(zapytanie) 
              result = ws.recv()
              printDBG( 'Host result: '+result)
              ws.close() 

              playpath = re.search('value":\["(.*?)"', result)
              if playpath:
                 Checksum =  playpath.group(1)  
                 if len(Checksum)<30: return ''
                 #videoUrl = rtmp+' playpath='+playpath.group(1)+' swfUrl=http://showup.tv/flash/suStreamer.swf?cache=20&autoReconnect=1&id='+playpath.group(1)+'&swfObjectID=video&sender=false&token=&address='+rtmp[7:-9]+'@liveedge live=1 pageUrl='+url+ ' conn=S:OK '
                 #videoUrl = rtmp+' playpath='+playpath.group(1)+' swfUrl=http://showup.tv/flash/suStreamer.swf?cache=1&thresholdCount=180&thresholdViewers=40&autoReconnect=1&id='+playpath.group(1)+'&swfObjectID=video&sender=false&token=&address='+rtmp[7:-9]+'@liveedge live=1 pageUrl='+url+ ' conn=S:OK'+ ' flashVer=WIN 12,0,0,44 '
                 videoUrl = rtmp+' playpath='+Checksum+' swfUrl=http://showup.tv/flash/suStreamer.swf?cache=1&thresholdCount=180&thresholdViewers=40&autoReconnect=1&id='+Checksum+'&swfObjectID=video&sender=false&token=&address='+rtmp[7:-9]+'@liveedge live=1 pageUrl='+url+' flashVer=WIN 12,0,0,44 '
                 return videoUrl

           return ''

        if parser == 'http://adult-channels.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'adult.cookie')
           host = "Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; androVM for VirtualBox ('Tablet' version with phone caps) Build/JRO03S) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30"
           header = {'Referer':'http://adult-channels.com', 'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}   
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoUrl = re.search('<iframe.*?src="(.*?)"', data, re.S)
           if videoUrl:
              link = ''
              if videoUrl.group(1).startswith('/'): link = 'http://adult-channels.com' 
              xml = link+videoUrl.group(1)
              try: data = self.cm.getURLRequestData({ 'url': xml, 'header': header, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
              except:
                 printDBG( 'Host getResolvedURL query error xml: '+xml )
                 return ''
              #printDBG( 'Host getResolvedURL data: '+data )
              videoPage = re.search('file:"(.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('<source.*?src="(.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('<source src="(.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search("'file': '(.*?)'", data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('Uppod.*?file: "#(.*?)"', data, re.S)   
              if videoPage: return ''
              videoPage = re.search(';src=(.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.myfreecams.com':
           videoUrl = myfreecam_start(url)
           if videoUrl: return videoUrl
           return ''

        def _get_stream_uid(username):
           m = hashlib.md5(username.encode('utf-8') + str(time_time()).encode('utf-8'))
           return m.hexdigest()

        if parser == 'https://pl.bongacams.com':
           printDBG( 'Host url:  '+url )
           username = self.cm.ph.getSearchGroups(url, '''playpath=stream_([^"^']+?)[?]''')[0] 
           printDBG( 'Host username:  '+username )
           serwer = [
           6026,6027,6047,6098,6099,6147,6185,6191,6194,6239,6241,6242,6247,6358,6382,6385,6386,6443,6447,6548,6559,6561,6562,6573,
           6575,6678,6680,6681,6685,6686,6739,6740,6741,
           5109,5112,5281,5355,5478,5480,5481,5489,5491,
           3083,3885,
           1113,1143,1650,1781,1782,1788,1789,
           ]
           printDBG( 'Host len(serwer):  '+str(len(serwer)) )
           printDBG( 'Host serwer[1]:  '+str(serwer[1]) )
           url = url.replace('rtmp://dedNUMER_SERWERA','')

           for i in range(0, len(serwer)):
              md5 = _get_stream_uid(username)
              url = url.replace('SKROT_MD5',md5)
              url = 'rtmp://ded'+str(serwer[i])+url
              printDBG( 'Host newurl:  '+url )
              cmd = '/usr/bin/rtmpdump -r "%s"' % url
              try:
                  import commands
                  wow = commands.getoutput(cmd)
                  if 'Connected' in wow:
                     printDBG( 'HostXXX rtmpdump > '+ wow )
                     return url.replace(md5,_get_stream_uid(username)) + 'flashVer=WIN 2024,0,0,186 '
                     break
                  printDBG( 'HostXXX GUZIK ' )
              except:
                  printDBG( 'HostXXX error commands.getoutput ' )
              url = url.replace('rtmp://ded'+str(serwer[i]),'')
              url = url.replace(md5,'SKROT_MD5')
           return ''       # KONIEC

           printDBG( 'Serwer skanowanie' )
           for serwer in range(5000, 7000): 
              md5 = _get_stream_uid(username)
              url = url.replace('SKROT_MD5',md5)
              url = 'rtmp://ded'+str(serwer)+url
              printDBG( 'Host newurl:  '+url )
              cmd = '/usr/bin/rtmpdump -r "%s"' % url
              try:
                  import commands
                  wow = commands.getoutput(cmd)
                  if 'Connected' in wow:
                     printDBG( 'HostXXX katalog list > '+ wow )
                     return url.replace(md5,_get_stream_uid(username)) + 'flashVer=WIN 2024,0,0,186 '
                     break
                  printDBG( 'HostXXX GUZIK2 ' )
              except:
                  printDBG( 'HostXXX error commands.getoutput ' )
              url = url.replace('rtmp://ded'+str(serwer),'')
              url = url.replace(md5,'SKROT_MD5')

           return ''

        if parser == 'http://new.livejasmin.com':
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error' )
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoPage = re.search('performerid":"(.*?)".*?proxyip":"(.*?)"', data, re.S) 
           if videoPage.group(1) and videoPage.group(2):
              printDBG( 'Host listsItems videoPage.group(2): '+videoPage.group(2) )
              printDBG( 'Host listsItems videoPage.group(1): '+videoPage.group(1) )
              return (videoPage.group(2)+'/'+videoPage.group(1)) 
           return ''

        if parser == 'http://www.cam4.pl':
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           parse = re.search('"playerUrl":"(.*?)"', data, re.S) 
           if parse:
              swfUrl = parse.group(1)
              parse = re.search('"videoPlayUrl":"(.*?)"', data, re.S) 
              if parse:
                 videoPlayUrl = parse.group(1)
                 parse = re.search('"videoAppUrl":"(.*?)"', data, re.S) 
                 if parse:
                    videoAppUrl = parse.group(1)
                    printDBG( 'Host swfUrl: '  +swfUrl )
                    printDBG( 'Host videoPlayUrl: '  +videoPlayUrl )
                    printDBG( 'Host videoAppUrl: '  +videoAppUrl )
                    if len(videoPlayUrl)<20: return ''
                    if len(videoAppUrl)<20: return ''
                    Url = '%s playpath=%s?playToken=null swfUrl=%s conn=S:OK live=1 pageUrl=%s' % (videoAppUrl, videoPlayUrl, swfUrl, url)
                    return Url
           return ''

        if parser == 'https://www.camsoda.com/':
           if 'rtmp' in url:
              rtmp = 1
           else:
              rtmp = 0
           url = url.replace('rtmp','')
           query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           dane = '['+data+']'
           printDBG( 'Host listsItems json: '+dane )
           result = simplejson.loads(dane)
           if result:
              for item in result:
                 token = str(item["token"])
                 app = str(item["app"])
                 serwer = str(item["edge_servers"][0])
                 #edge_servers2 = str(item["edge_servers"][1])
                 stream_name = str(item["stream_name"])
                 printDBG( 'Host listsItems token: '+token )
                 printDBG( 'Host listsItems app: '+app )
                 printDBG( 'Host listsItems edge_servers1: '+serwer )
                 #printDBG( 'Host listsItems edge_servers2: '+edge_servers2 )
                 printDBG( 'Host listsItems stream_name: '+stream_name )
                 name = re.sub('-enc.+', '', stream_name)
                 if rtmp == 0:
                    Url = 'https://%s/%s/mp4:%s_mjpeg/playlist.m3u8?token=%s' % (serwer, app, stream_name, token )
                    return Url
                 else:
                    Url = 'rtmp://%s:1935/%s?token=%s/ playpath=?mp4:%s swfUrl=https://www.camsoda.com/lib/video-js/video-js.swf live=1 pageUrl=https://www.camsoda.com/%s' % (serwer, app, token, stream_name, name)
                    return Url
           return ''

        if parser == 'xxxlist.txt':
           videoUrls = self.getLinksForVideo(url)
           if videoUrls:
              for item in videoUrls:
                 Url = item['url']
                 Name = item['name']
                 printDBG( 'Host url:  '+Url )
                 return Url
           if url.startswith('http://tvtoya.pl'):
              query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
              try:
                 data = self.cm.getURLRequestData(query_data)
                 #printDBG( 'Host getResolvedURL data: '+data )
              except:
                 printDBG( 'Host getResolvedURL query error' )
              videoUrl = re.search('data-stream="(.*?)"', data, re.S)
              return videoUrl.group(1).replace("index","03")
           if url.startswith('http://polskikarting.pl'):
              query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
              try:
                 data = self.cm.getURLRequestData(query_data)
                 #printDBG( 'Host getResolvedURL data: '+data )
              except:
                 printDBG( 'Host getResolvedURL query error' )
              videoUrl = re.findall("file: '(.*?)'", data, re.S)
              return videoUrl[0] # or videoUrl[1]
           return ''

        if parser == 'http://xhamster.com/cams':
           config='http://xhamsterlive.com/api/front/config'
           query_data = { 'url': config, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error' )
              printDBG( 'Host listsItems query error url: '+url )
              return ''
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"sessionHash":"(.*?)"', data, re.S) 
           if not parse: return ''
           sessionHash = parse.group(1) 
           printDBG( 'Host sessionHash: '+sessionHash )

           models='http://xhamsterlive.com/api/front/models'
           query_data = { 'url': models, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try: data = self.cm.getURLRequestData(query_data)
           except:
              printDBG( 'Host listsItems query error models: '+models )
              return ''
           #printDBG( 'Host listsItems data: '+data )
           parse = re.search('"models":(.*?),"ttl":', data, re.S) 
           if not parse: return ''
           result = simplejson.loads(parse.group(1))
           if result:
              for item in result:
                 ID = str(item["id"]) 
                 Name = item["username"]
                 BroadcastServer = item["broadcastServer"]
                 swf_url = 'http://xhamsterlive.com/assets/cams/components/ui/Player/player.swf?bgColor=2829099&isModel=false&version=1.5.892&bufferTime=1&camFPS=30&camKeyframe=15&camQuality=85&camWidth=640&camHeight=480'
                 Url = 'rtmp://b-eu1.stripcdn.com:1935/%s?sessionHash=%s&domain=xhamsterlive.com playpath=%s swfUrl=%s pageUrl=http://xhamsterlive.com/cams/%s live=1 ' % (BroadcastServer, sessionHash, ID, swf_url, Name) 
                 if ID == url: 
                    return Url
           return ''

        if parser == 'http://www.cliphunter.com':
           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Host listsItems data: '+data )
           url = re.findall('"url":"(.*?)"}', data, re.S)
           if url:
              url = url[-1]
              url = url.replace('\u0026', '.')
              translation_table = {
                 'm': 'a', 'b': 'b', 'c': 'c', 'i': 'd', 'd': 'e', 'g': 'f', 'a': 'h',
                 'z': 'i', 'y': 'l', 'n': 'm', 'l': 'n', 'f': 'o', 'v': 'p', 'x': 'r',
                 'r': 's', 'q': 't', 'p': 'u', 'e': 'v',
                 '$': ':', '&': '.', '(': '=', '^': '&', '=': '/',
              }
              url = ''.join(translation_table.get(c, c) for c in url) 
              return url
           else: return ''

        if parser == 'http://www.pornerbros.com':
           host = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
           header = {'User-Agent': host, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Host listsItems pornerbros: '+data )
           videoPage = re.findall('itemprop="embedUrl" content="(.*?)"', data, re.S)
           if not videoPage: return ''
           xml = videoPage[0]
           printDBG( 'Host getResolvedURL xml: '+xml )
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoPage = re.findall('defaultVideo:(.*?);', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://www.redtube.com':
           host = 'Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
           header = {'User-Agent': host, 'Accept':'application/json', 'Accept-Language':'de,en-US;q=0.7,en;q=0.3', 'X-Requested-With':'XMLHttpRequest', 'Content-Type':'application/x-www-form-urlencoded'} 
           query_data = { 'url': url, 'header': header, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
           try:
              data = self.cm.getURLRequestData(query_data)
           except:
              return ''
           #printDBG( 'Host listsItems data: '+data )
           videoPage = re.search('sources.*?"\d+":"(.*?)"', data, re.S)
           if videoPage:
              videos = videoPage.group(1)
              videos = videos.replace(r"\/",r"/")
              if videos[:2] == "//":
                 videos = "http:" + videos
              videos = videos.replace('&amp;','&')
              printDBG( 'Host listsItems first' )
              return videos
           videoPage = re.search('<source\ssrc="(.*?)"\stype="video/mp4">', data, re.S)
           if videoPage:
              videos = urllib.unquote(videoPage.group(1))
              videos = videos.replace(r"\/",r"/")
              if videos[:2] == "//":
                 videos = "http:" + videos
              videos = videos.replace('&amp;','&')
              printDBG( 'Host listsItems second' )
              return videos
           return ''

        if parser == 'http://www.tube8.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r""))
        
        if parser == 'http://www.youporn.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r"watch/"))

        if parser == 'http://www.pornhub.com/embed/':
           return self.getResolvedURL(url.replace(r"embed/",r"view_video.php?viewkey="))

        if parser == 'http://www.tube8.com':
           COOKIEFILE = os_path.join(GetCookieDir(), 'tube8.cookie')
           try: data = self.cm.getURLRequestData({ 'url': url, 'header': {'Origin':'http://www.tube8.com'}, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': COOKIEFILE, 'use_post': False, 'return_data': True })
           except:
              printDBG( 'Host getResolvedURL query error url: '+url )
              return ''
           #printDBG( 'Host getResolvedURL data: '+data )
           videoPage = self.cm.ph.getSearchGroups(data, '''quality_720p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return videoPage.replace(r"\/",r"/")
           videoPage = self.cm.ph.getSearchGroups(data, '''quality_480p['"]:['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return videoPage.replace(r"\/",r"/")
           return ''

##########################################################################################################################
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True}
        try:
           data = self.cm.getURLRequestData(query_data)
           printDBG( 'Host getResolvedURL data: '+data )
        except:
           printDBG( 'Host getResolvedURL query error' )
           return videoUrl

        if parser == 'file: ':
           return self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 

        if parser == '1file: "':
           videoPage = re.findall('file: "(.*?)"', data, re.S)   
           if videoPage:
              return videoPage[1]
           return ''

        if parser == "file': '":
           videoPage = re.findall("file': '(.*?)'", data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == "0p'  : '":
           videoPage = re.findall("0p'  : '(http.*?)'", data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'source src="':
           videoPage = re.findall('source src="(http.*?)"', data, re.S)   
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == "video_url: '":
           videoPage = re.findall("video_url: '(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'videoFile="':
           videoPage = re.findall('videoFile="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.pornrabbit.com':
           videoPage = re.findall("file: '(.*?)'", data, re.S)
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.pornhd.com':
           videoPage = re.findall("'1080p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]
           videoPage = re.findall("'720p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]
           videoPage = re.findall("'480p' : '(.*?)'", data, re.S)
           if videoPage:
              printDBG( 'Host pornhd videoPage:'+videoPage[0])
              if len(videoPage[0])>10: return videoPage[0]
           return ''

        if parser == 'http://www.ah-me.com':
           videoPage = re.findall('<video\ssrc="(.*?)"', data, re.S) 
           if videoPage:
              printDBG( 'Host ah-me videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'https://chaturbate.com':
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return urllib2.unquote(videoPage.replace('&amp;','&'))
           return ''

        if parser == 'http://www.amateurporn.net':
           videoPage = re.findall('<param\sname="flashvars"\svalue="file=(.*?)&provider=', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.nuvid.com':
           videoUrl = re.search("http://www.nuvid.com/video/(.*?)/.+", url, re.S)
           if videoUrl:
              xml = 'http://m.nuvid.com/video/%s' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.findall('source src="(.*?)"', data, re.S)   
              if videoPage:
                 return videoPage[0]
           return ''

        if parser == 'http://www.wankoz.com':
           videoPage = re.findall("'video_html5_url']='(.*?).'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.sunporno.com':
           videoPage = re.findall('video src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'http://www.pornoxo.com':
           videoPage = re.findall('source src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''

        if parser == 'https://alpha.tnaflix.com':
           videoPage = re.findall('"embedUrl" content="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return 'http:'+videoPage[0]
           return ''

        if parser == 'http://www.faphub.xxx':
           videoPage = re.findall("url: '(.*?)'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.proporn.com':
           videoPage = re.findall('source src="(.*?)"', data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.empflix.com':
           videoPage = re.findall("video_url: '(.*?)'", data, re.S)   
           if videoPage:
              printDBG( 'Host videoPage:'+videoPage[0])
              return videoPage[0]
           return ''
   
        if parser == 'http://www.xnxx.com':
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://www.xvideos.com':
           videoUrl = re.search("setVideoUrlHigh\('(.*?)'", data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           videoUrl = re.search('flv_url=(.*?)&', data, re.S)
           if videoUrl: return decodeUrl(videoUrl.group(1))
           return ''

        if parser == 'http://www.youporn.com':
           match = re.findall(r'encryptedQuality720URL\s=\s\'([a-zA-Z0-9+/]+={0,2})\',', data)
           if match:
              fetchurl = urllib2.unquote(match[0])
              printDBG( 'Host getResolvedURL fetchurl: '+fetchurl )
              match = re.compile("video_title = '(.*?)'").findall(data)
              if match:
                 title = urllib.unquote_plus(match[0])
                 #title = '%s_720p' % title
                 printDBG( 'Host getResolvedURL title: '+title )
                 printDBG( 'Host getResolvedURL decrypt begin ' )
                 phStream = decrypt(fetchurl, title, 32)
                 if phStream: 
                    printDBG( 'Host getResolvedURL decrypted url: '+phStream )
                    return phStream
           videoUrl = self.cm.ph.getSearchGroups(data, '''1080:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''720:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''480:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           videoUrl = self.cm.ph.getSearchGroups(data, '''240:[ ]['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&')
           return ''

        if parser == 'http://embed.redtube.com':
           videoPage = re.findall('sources:.*?":"(.*?)"', data, re.S)
           if videoPage:
              link = videoPage[-1].replace(r"\/",r"/")
              if link.startswith('//'): link = 'http:' + link 
              return link
           return ''

        if parser == 'http://www.redtube.com':
           videoPage = re.search('<source\ssrc="(.*?)"\stype="video/mp4">', data, re.S)
           if videoPage:
              videos = urllib.unquote(videoPage.group(1))
              videos = videos.replace(r"\/",r"/")
              if videos[:2] == "//":
                 videos = "http:" + videos
              return videos
           return ''

        if parser == 'http://xhamster.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''720p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           videoUrl = self.cm.ph.getSearchGroups(data, '''480p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           videoUrl = self.cm.ph.getSearchGroups(data, '''240p['"]:['"]([^'"]+?)['"]''')[0]
           if videoUrl: return videoUrl.replace('&amp;','&').replace(r"\/",r"/")
           xhFile = re.findall('"file":"(.*?)"', data)
           if xhFile: return xhFile[0].replace(r"\/",r"/")
           else: 
              xhFile = re.findall("file: '(.*?)'", data)
              if xhFile: return xhFile[0].replace(r"\/",r"/")
           return ''
        
        if parser == 'http://www.eporner.com':
           videoID = re.search("http://www.eporner.com/hd-porn/(.*?)/.+", url)
           if not videoID: return ''
           parse = re.findall("hash: '(.*?)'", data, re.S)
           hash =  urllib.unquote_plus(parse[0]).decode("utf-8")
           x = calc_hash(hash)
           printDBG( 'Host getResolvedURL hash: '+parse[0]+' calc_hash:'+x)
           xml = 'http://www.eporner.com/xhr/video/%s?device=generic&domain=www.eporner.com&hash=%s&fallback=false' % (videoID.group(1), x)
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return ''
           #printDBG( 'Host data json: '+data )
           videoPage = re.findall('src": "(.*?)"', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://www.pornhub.com/embed/':
           match = re.findall("container.*?src.*?'(.*?)'", data, re.S)
           if match: return match[0]
           return ''
        
        if parser == 'http://www.pornhub.com':
           try:
              js = re.findall('(var flashvars_(?:\d+).*?)loadScriptUniqueId', data, re.S)
              #js = self.cm.ph.getDataBeetwenMarkers(data, 'var flashvars_', 'loadScriptUniqueId', False)[1]
              if js:
                 urls = iptv_js_execute( js[0]+ '\nfor (n in this){print(n+"="+this[n]+";");}')
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_720p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_480p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
                 videoPage = self.cm.ph.getSearchGroups(urls['data'], '''quality_240p=([^"^']+?);''')[0] 
                 if videoPage: return videoPage
           except:
              embed = re.search('"embedCode":"<iframe src=."(.*?)"', data, re.S)
              if embed:
                 url = embed.group(1).replace('\/','/').replace('\\','')
                 try:    data = self.cm.getURLRequestData({'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 except: 
                    printDBG( 'Host getResolvedURL query error xml' )
                    return ''
                 #printDBG( 'Host data embed: '+data )
                 videoPage = re.findall('quality_720p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
                 videoPage = re.findall('quality_480p":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[0].replace('\/','/')
           return ''

        if parser == 'http://www.4tube.com':
           #printDBG( 'Host getResolvedURL data: '+data )
           videoID = re.findall('data-id="(\d+)".*?data-quality="(\d+)"', data, re.S)
           if videoID:
              res = ''
              for x in videoID:
                  res += x[1] + "+"
              res.strip('+')
              posturl = "%s/%s/desktop/%s" % (parser.replace('www','tkn'), videoID[-1][0], res)
              printDBG( 'Host getResolvedURL posturl: '+posturl )
              try:
                 data = self.cm.getURLRequestData({'url': posturl, 'header': {'Origin':'http://www.4tube.com'},'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True},{})
              except:
                 printDBG( 'Host getResolvedURL query error posturl' )
                 return ''
              #printDBG( 'Host getResolvedURL posturl data: '+data )
              videoUrl = re.findall('token":"(.*?)"', data, re.S)
              if videoUrl: return videoUrl[-1]                 
              else: return ''
           else: return ''
        
        if parser == 'http://www.hdporn.net':
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://m.tube8.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://mobile.youporn.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://m.pornhub.com':
           match = re.compile('<div class="play_video.+?<a href="(.+?)"', re.DOTALL).findall(data)
           return match[0]

        if parser == 'http://www.youjizz.com':
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              if videoPage.startswith('//'): videoPage = 'http:' + videoPage
              return decodeUrl(videoPage).replace("&amp;","&") 
           return ''

        if parser == 'http://www.dachix.com':
           videoPage = self.cm.ph.getSearchGroups(data, '''<source src=['"]([^"^']+?)['"]''')[0] 
           if videoPage:
              return urllib2.unquote(videoPage) 
           return ''

        if parser == 'http://www.drtuber.com':
           params = re.findall('params\s\+=\s\'h=(.*?)\'.*?params\s\+=\s\'%26t=(.*?)\'.*?params\s\+=\s\'%26vkey=\'\s\+\s\'(.*?)\'', data, re.S)
           if params:
              for (param1, param2, param3) in params:
                 hash = hashlib.md5(param3 + base64.b64decode('UFQ2bDEzdW1xVjhLODI3')).hexdigest()
                 url = '%s/player_config/?h=%s&t=%s&vkey=%s&pkey=%s&aid=' % ("http://www.drtuber.com", param1, param2, param3, hash)
                 query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
                 try:
                    data = self.cm.getURLRequestData(query_data)
                 except:
                    printDBG( 'Host listsItems query error' )
                    printDBG( 'Host listsItems query error url: '+url )
                 #printDBG( 'Host listsItems data: '+data )
                 url = re.findall('video_file>.*?(http.*?)\]\]><\/video_file>', data, re.S)
                 if url:
                    url = str(url[0])
                    url = url.replace("&amp;","&")
                    printDBG( 'Host listsItems data: '+url )
                    return url
           return ''

        if parser == 'https://www.tnaflix.com':
           link = re.search("data-vid='(.*?)'\sdata-nk='(.*?)'\sdata-vk='(.*?)'", data, re.S) 
           if link:
              vid = link.group(1)
              nk =  link.group(2)
              vk =  link.group(3)
              xml = 'https://cdn-fck.tnaflix.com/tnaflix/%s.fid?key=%s&VID=%s&nomp4=1&catID=0&rollover=1&startThumb=31&embed=0&utm_source=0&multiview=0&premium=1&country=0user=0&vip=1&cd=0&ref=0&alpha' % (vk, nk, vid) 
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return videoUrl
           videoPage = re.findall('<videoLink>.*?//(.*?)(?:]]>|</videoLink>)', data, re.S)
           if videoPage: return 'http://' + videoPage[-1]
           return ''

        if parser == 'https://www.empflix.com':
           videoPage = re.search('"contentUrl" content="(.*?)"', data, re.S)  
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://search.el-ladies.com':
           videoPage = re.findall(',file:\'(.*?)\'', data, re.S)  
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.extremetube.com':
           videoPage = re.findall('"quality_\d+p":"(.*?)"', data, re.S) 
           if videoPage:
              url = videoPage[-1] 
              url = url.replace('\/','/') 
              return url
           return ''

        if parser == 'http://pornicom.com':
           #videoPage = re.search('download-link.*?href="(.*?)"', data, re.S) 
           #videoPage = re.search('file: "(.*?)"', data, re.S) 
           #videoPage = re.search('{ file: "(.*?)"', data, re.S)
           return self.cm.ph.getSearchGroups(data, '''file: ['"]([^"^']+?)['"]''')[0] 

        if parser == 'http://sexylies.com':
           videoPage = re.search('source\stype="video/mp4"\ssrc="(.*?)"', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.eskimotube.com':
           videoPage = re.search('color=black.*?href=(.*?)>', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://www.porn5.com':
           videoPage = re.findall('p",url:"(.*?)"', data, re.S) 
           if videoPage:
              return videoPage[-1]
           return ''

        if parser == 'http://www.pornyeah.com':
           videoPage = re.findall('settings=(.*?)"', data, re.S)
           if not videoPage: return ''
           xml = videoPage[0]
           printDBG( 'Host getResolvedURL xml: '+xml )
           try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
           except: 
                   printDBG( 'Host getResolvedURL query error xml' )
                   return videoUrl
           videoPage = re.findall('defaultVideo:(.*?);', data, re.S)
           if videoPage: return videoPage[0]
           return ''

        if parser == 'http://rusporn.tv':
           VideoID = re.search("var videoId = '(.*?)'", data, re.S)
           if VideoID:
              VideoID = VideoID.group(1)
              videoPage = re.findall('"file": "(.*?)"', data, re.S) 
              if videoPage:
                 return videoPage[-1]+VideoID+"&hq=high&ex=mp4"
           return ''

        if parser == 'http://porn720.net':
           videoPage = re.search('720p":"(.*?)"', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           videoPage = re.search('480p":"(.*?)"', data, re.S) 
           if videoPage:
              return videoPage.group(1)
           return ''

        if parser == 'http://porndoe.com':
           parse = re.search('sources:(.*?)width', data, re.S) 
           if parse:
              videoPage = re.findall('file:\s"(.*?)".*?label:"(.*?)"', parse.group(1), re.S)  
              if videoPage:
                 for (link, default) in videoPage:
                    printDBG( 'Host listsItems link: '  +link )
                    printDBG( 'Host listsItems default: '+default )
                 return link
           return ''

        if parser == 'http://www.pornpillow.com':
           videoPage = re.findall("'file': '(.*?)'", data, re.S)   
           if videoPage:
              return videoPage[0]
           return ''

        if parser == 'http://www.pornfromczech.com':
           try:
              link = re.search('src="(https://www.rapidvideo.com.*?)"', data, re.S) 
              if link:
                 rapid = link.group(1).replace(r'embed/',r'?v=')
                 printDBG( 'Host listsItems test1: '  +rapid )
                 data = self.cm.getURLRequestData({'url': rapid, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 #printDBG( 'Host listsItems test1 data: '  +data )
                 videoPage = re.findall('"file":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[-1].replace('\/','/')
           except: pass
           try:
              link = re.search('src="(https://www.bitporno.sx.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test2: '  +link.group(1) )
                 data = self.cm.getURLRequestData({'url': link.group(1).replace('embed/','?v='), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 #printDBG( 'Host getResolvedURL data: '+data )
                 videoPage = re.findall('"file":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[-1].replace('\/','/')
           except: pass
           try:
              link = re.search('src="(https://openload.co.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test3: '  +link.group(1) )
                 return self.getResolvedURL(link.group(1))
           except: pass
           try:
              link = re.search('src="(http://www.flashx.tv.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test4: '  +link.group(1) )
                 return self.getResolvedURL(link.group(1))
           except: pass
           try:
              link = re.search('src="(http://videomega.tv.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test5: '  +link.group(1) )
                 return self.getResolvedURL(link.group(1))
           except: pass
           try:
              link = re.search('src="(https://player.tnaflix.com.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test6: '  +link.group(1) )
                 data = self.cm.getURLRequestData({'url': link.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 #printDBG( 'Host getResolvedURL data: '+data )
                 videoPage = re.search('(//www.tnaflix.com.*?)"', data, re.S)
                 if videoPage: return self.getResolvedURL('http:'+videoPage.group(1))
           except: pass
           try:
              link = re.search('="(http://vidlox.tv.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test7: '  +link.group(1) )
                 data = self.cm.getURLRequestData({'url': link.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 #printDBG( 'Host getResolvedURL data: '+data )
                 videoPage = re.search('file:"(.*?)"', data, re.S)
                 if videoPage: return videoPage.group(1)
           except: pass
           try:
              link = re.search('src="(https://www.bitporno.com/embed/.*?)"', data, re.S) 
              if link:
                 printDBG( 'Host listsItems test2: '  +link.group(1) )
                 data = self.cm.getURLRequestData({'url': link.group(1).replace('embed/','?v='), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
                 #printDBG( 'Host getResolvedURL data: '+data )
                 videoPage = re.findall('"file":"(.*?)"', data, re.S)
                 if videoPage: return videoPage[-1].replace('\/','/')
           except: pass
           return ''

        if parser == 'http://www.filmyporno.tv':
           match = re.findall('source src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://pornohub.su':
           match = re.findall('video/mp4.*?src="(.*?)"', data, re.S)
           if match: return match[0]
           else: return ''

        if parser == 'http://www.thumbzilla.com':
           match = re.findall('data-quality="(.*?)"', data)
           if match:
              fetchurl = urllib2.unquote(match[-1])
              fetchurl = fetchurl.replace(r"\/",r"/")
              if fetchurl.startswith('//'): fetchurl = 'http:' + fetchurl
              return fetchurl 
           return ''

        if parser == 'https://vidlox.tv':
           parse = re.search('sources.*?"(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://xxxkingtube.com':
           parse = re.search("File = '(http.*?)'", data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornsharing.com':
           parse = re.search('btoa\("(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://pornxs.com':
           parse = re.search('config-final-url="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.flyflv.com':
           parse = re.search('fileUrl="(http.*?)"', data, re.S) 
           if parse: return parse.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yeptube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.yeptube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://vivatube.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://vivatube.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.tubeon.com':
           videoUrl = re.search('video_id = "(.*?)"', data, re.S)
           if videoUrl:
              xml = 'http://www.tubeon.com/player_config_json/?vid=%s&aid=0&domain_id=0&embed=0&ref=&check_speed=0' % videoUrl.group(1)
              try:    data = self.cm.getURLRequestData({'url': xml, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True})
              except: 
                 printDBG( 'Host getResolvedURL query error xml' )
                 return ''
              #printDBG( 'Host data json: '+data )
              videoPage = re.search('"hq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
              videoPage = re.search('"lq":"(http.*?)"', data, re.S)   
              if videoPage: return videoPage.group(1).replace('\/','/')
           return ''

        if parser == 'http://www.yuvutu.com':
           match = re.findall('iframe src="(.*?)"', data, re.S)
           if match: 
              url = 'http://www.yuvutu.com'+match[0]
              query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
              try:
                 data = self.cm.getURLRequestData(query_data)
              except:
                 printDBG( 'Host listsItems query error url: '+url )
              printDBG( 'Host listsItems data: '+data )
              url = re.findall('file: "(.*?)"', data, re.S)
              if url: 
                 videoUrl = url[-1]
                 return videoUrl
           return ''

        if parser == 'https://www.pornomenge.com':
           videoUrl = self.cm.ph.getSearchGroups(data, '''<source\ssrc=['"]([^"^']+?)['"]''')[0] 
           if videoUrl.startswith('//'): videoUrl = 'http:' + videoUrl
           return videoUrl

        printDBG( 'Host getResolvedURL end' )
        return videoUrl




############################################
# functions for host
############################################
def decodeUrl(text):
	text = text.replace('%20',' ')
	text = text.replace('%21','!')
	text = text.replace('%22','"')
	text = text.replace('%23','&')
	text = text.replace('%24','$')
	text = text.replace('%25','%')
	text = text.replace('%26','&')
	text = text.replace('%2F','/')
	text = text.replace('%3A',':')
	text = text.replace('%3B',';')
	text = text.replace('%3D','=')
	text = text.replace('%3F','?')
	text = text.replace('%40','@')
	return text

def decodeHtml(text):
	text = text.replace('&auml;','ä')
	text = text.replace('\u00e4','ä')
	text = text.replace('&#228;','ä')

	text = text.replace('&Auml;','Ä')
	text = text.replace('\u00c4','Ä')
	text = text.replace('&#196;','Ä')
	
	text = text.replace('&ouml;','ö')
	text = text.replace('\u00f6','ö')
	text = text.replace('&#246;','ö')
	
	text = text.replace('&ouml;','Ö')
	text = text.replace('\u00d6','Ö')
	text = text.replace('&#214;','Ö')
	
	text = text.replace('&uuml;','ü')
	text = text.replace('\u00fc','ü')
	text = text.replace('&#252;','ü')
	
	text = text.replace('&Uuml;','Ü')
	text = text.replace('\u00dc','Ü')
	text = text.replace('&#220;','Ü')
	
	text = text.replace('&szlig;','ß')
	text = text.replace('\u00df','ß')
	text = text.replace('&#223;','ß')
	
	text = text.replace('&amp;','&')
	text = text.replace('&quot;','\"')
	text = text.replace('&gt;','>')
	text = text.replace('&apos;',"'")
	text = text.replace('&acute;','\'')
	text = text.replace('&ndash;','-')
	text = text.replace('&bdquo;','"')
	text = text.replace('&rdquo;','"')
	text = text.replace('&ldquo;','"')
	text = text.replace('&lsquo;','\'')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&#034;','\'')
	text = text.replace('&#038;','&')
	text = text.replace('&#039;','\'')
	text = text.replace('&#160;',' ')
	text = text.replace('\u00a0',' ')
	text = text.replace('&#174;','')
	text = text.replace('&#225;','a')
	text = text.replace('&#233;','e')
	text = text.replace('&#243;','o')
	text = text.replace('&#8211;',"-")
	text = text.replace('\u2013',"-")
	text = text.replace('&#8216;',"'")
	text = text.replace('&#8217;',"'")
	text = text.replace('#8217;',"'")
	text = text.replace('&#8220;',"'")
	text = text.replace('&#8221;','"')
	text = text.replace('&#8222;',',')
	text = text.replace('&#x27;',"'")
	text = text.replace('&#8230;','...')
	text = text.replace('\u2026','...')
	text = text.replace('&#41;',')')
	return text	

############################################
# functions for pornhub
############################################
def decrypt(ciphertext, password, nBits):
    printDBG( 'decrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
    ciphertext = base64.b64decode(ciphertext)
#    password = password.encode("utf-8")

    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    ctrTxt = ciphertext[:8]
    for i in range(8): counterBlock[i] = ord(ctrTxt[i])

    keySchedule = KeyExpansion(key)

    nBlocks = int( math.ceil( float(len(ciphertext)-8) / float(blockSize) ) )
    ct = [0] * nBlocks
    for b in range(nBlocks):
        ct[b] = ciphertext[8+b*blockSize : 8+b*blockSize+blockSize]
    ciphertext = ct

    plaintxt = [0] * len(ciphertext)

    for b in range(nBlocks):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs( int( float(b+1)/0x100000000-1 ), c*8) & 0xff

        cipherCntr = Cipher(counterBlock, keySchedule)

        plaintxtByte = [0] * len(ciphertext[b])
        for i in range(len(ciphertext[b])):
            plaintxtByte[i] = cipherCntr[i] ^ ord(ciphertext[b][i])
            plaintxtByte[i] = chr(plaintxtByte[i])
        plaintxt[b] = "".join(plaintxtByte)

    plaintext = "".join(plaintxt)
 #   plaintext = plaintext.decode("utf-8")
    return plaintext

Sbox = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

Rcon = [
    [0x00, 0x00, 0x00, 0x00],
    [0x01, 0x00, 0x00, 0x00],
    [0x02, 0x00, 0x00, 0x00],
    [0x04, 0x00, 0x00, 0x00],
    [0x08, 0x00, 0x00, 0x00],
    [0x10, 0x00, 0x00, 0x00],
    [0x20, 0x00, 0x00, 0x00],
    [0x40, 0x00, 0x00, 0x00],
    [0x80, 0x00, 0x00, 0x00],
    [0x1b, 0x00, 0x00, 0x00],
    [0x36, 0x00, 0x00, 0x00]
]

def Cipher(input, w):
    printDBG( 'cipher begin ' )
    Nb = 4
    Nr = len(w)/Nb - 1

    state = [ [0] * Nb, [0] * Nb, [0] * Nb, [0] * Nb ]
    for i in range(0, 4*Nb): state[i%4][i//4] = input[i]

    state = AddRoundKey(state, w, 0, Nb)

    for round in range(1, Nr):
        state = SubBytes(state, Nb)
        state = ShiftRows(state, Nb)
        state = MixColumns(state, Nb)
        state = AddRoundKey(state, w, round, Nb)

    state = SubBytes(state, Nb)
    state = ShiftRows(state, Nb)
    state = AddRoundKey(state, w, Nr, Nb)

    output = [0] * 4*Nb
    for i in range(4*Nb): output[i] = state[i%4][i//4]
    return output

def SubBytes(s, Nb):
    printDBG( 'subbytes begin ' )
    for r in range(4):
        for c in range(Nb):
            s[r][c] = Sbox[s[r][c]]
    return s

def ShiftRows(s, Nb):
    printDBG( 'shiftrows begin ' )
    t = [0] * 4
    for r in range (1,4):
        for c in range(4): t[c] = s[r][(c+r)%Nb]
        for c in range(4): s[r][c] = t[c]
    return s

def MixColumns(s, Nb):
    printDBG( 'mixcolumns begin ' )
    for c in range(4):
        a = [0] * 4
        b = [0] * 4
        for i in range(4):
            a[i] = s[i][c]
            b[i] = s[i][c]<<1 ^ 0x011b if s[i][c]&0x80 else s[i][c]<<1
        s[0][c] = b[0] ^ a[1] ^ b[1] ^ a[2] ^ a[3]
        s[1][c] = a[0] ^ b[1] ^ a[2] ^ b[2] ^ a[3]
        s[2][c] = a[0] ^ a[1] ^ b[2] ^ a[3] ^ b[3]
        s[3][c] = a[0] ^ b[0] ^ a[1] ^ a[2] ^ b[3]
    return s

def AddRoundKey(state, w, rnd, Nb):
    printDBG( 'addroundkey begin ' )
    for r in range(4):
        for c in range(Nb):
            state[r][c] ^= w[rnd*4+c][r]
    return state

def KeyExpansion(key):
    printDBG( 'keyexpansion begin ' )
    Nb = 4
    Nk = len(key)/4
    Nr = Nk + 6

    w = [0] * Nb*(Nr+1)
    temp = [0] * 4

    for i in range(Nk):
        r = [key[4*i], key[4*i+1], key[4*i+2], key[4*i+3]]
        w[i] = r

    for i in range(Nk, Nb*(Nr+1)):
        w[i] = [0] * 4
        for t in range(4): temp[t] = w[i-1][t]
        if i%Nk == 0:
            temp = SubWord(RotWord(temp))
            for t in range(4): temp[t] ^= Rcon[i/Nk][t]
        elif Nk>6 and i%Nk == 4:
            temp = SubWord(temp)
        for t in range(4): w[i][t] = w[i-Nk][t] ^ temp[t]
    return w

def SubWord(w):
    printDBG( 'subword begin ' )
    for i in range(4): w[i] = Sbox[w[i]]
    return w

def RotWord(w):
    printDBG( 'rotword begin ' )
    tmp = w[0]
    for i in range(3): w[i] = w[i+1]
    w[3] = tmp
    return w

def encrypt(plaintext, password, nBits):
    printDBG( 'encrypt begin ' )
    blockSize = 16
    if not nBits in (128, 192, 256): return ""
#    plaintext = plaintext.encode("utf-8")
#    password  = password.encode("utf-8")
    nBytes = nBits//8
    pwBytes = [0] * nBytes
    for i in range(nBytes): pwBytes[i] = 0 if i>=len(password) else ord(password[i])
    key = Cipher(pwBytes, KeyExpansion(pwBytes))
    key += key[:nBytes-16]

    counterBlock = [0] * blockSize
    now = datetime.datetime.now()
    nonce = time.mktime( now.timetuple() )*1000 + now.microsecond//1000
    nonceSec = int(nonce // 1000)
    nonceMs  = int(nonce % 1000)

    for i in range(4): counterBlock[i] = urs(nonceSec, i*8) & 0xff
    for i in range(4): counterBlock[i+4] = nonceMs & 0xff

    ctrTxt = ""
    for i in range(8): ctrTxt += chr(counterBlock[i])

    keySchedule = KeyExpansion(key)

    blockCount = int(math.ceil(float(len(plaintext))/float(blockSize)))
    ciphertxt = [0] * blockCount

    for b in range(blockCount):
        for c in range(4): counterBlock[15-c] = urs(b, c*8) & 0xff
        for c in range(4): counterBlock[15-c-4] = urs(b/0x100000000, c*8)

        cipherCntr = Cipher(counterBlock, keySchedule)

        blockLength = blockSize if b<blockCount-1 else (len(plaintext)-1)%blockSize+1
        cipherChar = [0] * blockLength

        for i in range(blockLength):
            cipherChar[i] = cipherCntr[i] ^ ord(plaintext[b*blockSize+i])
            cipherChar[i] = chr( cipherChar[i] )
        ciphertxt[b] = ''.join(cipherChar)

    ciphertext = ctrTxt + ''.join(ciphertxt)
    ciphertext = base64.b64encode(ciphertext)

    return ciphertext

def urs(a, b):
    printDBG( 'urs begin ' )
    a &= 0xffffffff
    b &= 0x1f
    if a&0x80000000 and b>0:
        a = (a>>1) & 0x7fffffff
        a = a >> (b-1)
    else:
        a = (a >> b)
    return a

############################################
# functions for beeg.com
############################################
def decrypt_key(key, a):
    printDBG( 'beeg_salt= '+a)
    e = urllib.unquote_plus(key).decode("utf-8")
    o = ''.join([
        chr(ord(e[n]) - ord(a[n % len(a)]) % 21)
        for n in range(len(e))])
    return ''.join(split(o, 3)[::-1])
	
def split(o, e):
    def cut(s, x):
        n.append(s[:x])
        return s[x:]
    n = []
    r = len(o) % e
    if r > 0:
        o = cut(o, r)
    while len(o) > e:
        o = cut(o, e)
    n.append(o)
    return n
############################################
# functions for eporner
############################################
def calc_hash(s):
    return ''.join((encode_base_n(int(s[lb:lb + 8], 16), 36) for lb in range(0, 32, 8)))

def encode_base_n(num, n, table=None):
    FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if not table:
        table = FULL_TABLE[:n]

    if n > len(table):
        raise ValueError('base %d exceeds table length %d' % (n, len(table)))

    if num == 0:
        return table[0]

    ret = ''
    while num:
        ret = table[num % n] + ret
        num = num // n
    return ret
############################################
# functions for myfreecam
############################################
vs_str={}
vs_str[0]="PUBLIC"
vs_str[2]="AWAY"
vs_str[12]="PVT"
vs_str[13]="GROUP"
vs_str[90]="CAM OFF"
vs_str[127]="OFFLINE"
vs_str[128]="TRUEPVT"

def fc_decode_json(m):
	try:
		m = m.replace('\r', '\\r').replace('\n', '\\n')
		return simplejson.loads(m[m.find("{"):].decode("utf-8","ignore"))
	except:
		return simplejson.loads("{\"lv\":0}")

def read_model_data(m):
	global CAMGIRLSERVER
	global CAMGIRLCHANID
	global CAMGIRLUID
	usr = ''
	msg = fc_decode_json(m)
	try:
		sid=msg['sid']
		level  = msg['lv']
	except:
		printDBG ("errr reply ... We're fucked ..")
		return

	vs     = msg['vs']

	if vs == 127:
		printDBG ("%s is %s" % (usr, vs_str[vs]))
		return

	usr    = msg['nm']
	CAMGIRLUID    = msg['uid']
	CAMGIRLCHANID = msg['uid'] + 100000000
	camgirlinfo=msg['m']
	flags  = camgirlinfo['flags']
	u_info=msg['u']

	try:
		CAMGIRLSERVER = u_info['camserv']
		if CAMGIRLSERVER >= 500:
			CAMGIRLSERVER = CAMGIRLSERVER - 500
		if vs != 0:
			CAMGIRLSERVER = 0
	except KeyError:
		CAMGIRLSERVER=0

	truepvt = ((flags & 8) == 8)

	buf=usr+" =>"
	try:
		if truepvt == 1:
			buf+=" (TRUEPVT)"
		else:
			buf+=" ("+vs_str[vs]+")"
	except KeyError:
		pass
	printDBG ("%s  Video Server : %d Channel Id : %d  Model id : %d " 
		%(buf, CAMGIRLSERVER, CAMGIRLCHANID, CAMGIRLUID))


def myfreecam_start(url):
	global CAMGIRL
	global CAMGIRLSERVER
	global CAMGIRLUID
	global CAMGIRLCHANID
	CAMGIRL= url
	CAMGIRLSERVER = 0
	libsPath = GetPluginDir('libs/')
	import sys
	sys.path.insert(1, libsPath)
	import websocket
	printDBG("Connecting to Chat Server...")
	try:
		xchat=[ 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
			20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 
			33, 34, 35, 36, 39, 40, 41, 42, 43, 44, 45, 46, 
			47, 48, 49, 56, 57, 58, 59, 60, 61
		      ]
		host = "ws://xchat"+str(random.choice(xchat))+".myfreecams.com:8080/fcsl"
		printDBG("Chat Server..."+host)
		ws = websocket.create_connection(host)
		ws.send("hello fcserver\n\0")
		ws.send("1 0 0 20071025 0 guest:guest\n\0")
	except:
		printDBG ("We're fucked ...")
		return ''
	rembuf=""
	quitting = 0
	while quitting == 0:
		sock_buf =  ws.recv()
		sock_buf=rembuf+sock_buf
		rembuf=""
		while True:
			hdr=re.search (r"(\w+) (\w+) (\w+) (\w+) (\w+)", sock_buf)
			if bool(hdr) == 0:
				break

			fc = hdr.group(1)

			mlen   = int(fc[0:4])
			fc_type = int(fc[4:])

			msg=sock_buf[4:4+mlen]

			if len(msg) < mlen:
				rembuf=''.join(sock_buf)
				break

			msg=urllib.unquote(msg)

			if fc_type == 1:
				ws.send("10 0 0 20 0 %s\n\0" % CAMGIRL)
			elif fc_type == 10:
				read_model_data(msg)
				quitting=1

			sock_buf=sock_buf[4+mlen:]

			if len(sock_buf) == 0:
				break
	ws.close()
	if CAMGIRLSERVER != 0:
		Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/ngrp:mfc_"+\
			str(CAMGIRLCHANID)+".f4v_mobile/playlist.m3u8" #better resolution
		#Url="http://video"+str(CAMGIRLSERVER)+".myfreecams.com:1935/NxServer/mfc_"+str(CAMGIRLCHANID)+".f4v_aac/playlist.m3u8" #320x240
		printDBG("Camgirl - "+CAMGIRL)
		printDBG("Url  - "+Url)
		return Url
	else:
		printDBG ("No video server ... _|_ ")
