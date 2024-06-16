# -*- coding: utf-8 -*-

import os
import time
import hashlib
import datetime
import feedparser
import configparser

from pygtrans import Translate
from urllib import parse
from rfeed import *

def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()


def getTime(e):
    try:
        struct_time =e.published_parsed
    except:
        struct_time =time.localtime()
    return datetime.datetime(*struct_time[:6])
def getSubtitle(e):
    try:
        sub =e.subtitle
    except:
        sub =""
    return sub
class GoogleTran:
    def __init__(self, url,  source  = 'auto', target  = 'zh-CN'):
        self.url = url
        self.source= source
        self.target=target

        self.d = feedparser.parse(url)
        self.GT = Translate()
    
    def tr(self,content):
        if self.source=='proxy': # do not translate
            return content
        tt = self.GT.translate(content,target=self.target,source=self.source)
        try:
            return tt.translatedText
        except:
            return ""
    
    def get_newconent(self,max=2):
        item_list = []
        if len(self.d.entries) < max:
            max = len(self.d.entries)
        for entry in self.d.entries[:max]:
            title="【" + entry.title + "】"
            if self.source=='proxy':
                title="【" + entry.title + "】" + self.tr(entry.title)
            one = Item(
                title=title,
                link=entry.link,
                description=self.tr(entry.summary),
                guid=Guid(entry.link),
                pubDate=getTime(entry))
            item_list += [one]
        feed=self.d.feed
        print(feed)
        newfeed = Feed(
            title=self.tr(feed.title),
            link=feed.link,
            description=self.tr(getSubtitle(feed)),
            lastBuildDate=getTime(feed),
            items=item_list)
        return newfeed.rss()



with open('test.ini', mode = 'r') as f:
    ini_data = parse.unquote(f.read())
config = configparser.ConfigParser()
config.read_string(ini_data)
secs=config.sections()



def get_cfg(sec,name):
    return config.get(sec,name).strip('"')

def set_cfg(sec,name,value):
    config[sec][name]='"%s"'%value

def get_cfg_tra(sec):
    cc=config.get(sec,"action").strip('"')
    target=""
    source=""
    if cc == "auto":
        source  = 'auto'
        target  = 'zh-CN'
        
    elif cc == "proxy":
        source  = 'proxy'
        target  = 'proxy'
    else:
        source  = cc.split('->')[0]
        target  = cc.split('->')[1]
    return source,target


BASE=get_cfg("cfg",'base')
try:
    os.makedirs(BASE)
except:
    pass
links=[]
def tran(sec):
    out_dir= BASE + get_cfg(sec,'name')
    url=get_cfg(sec,'url')
    max_item=int(get_cfg(sec,'max'))
    old_md5=get_cfg(sec,'md5')
    source,target=get_cfg_tra(sec)
    global links

    links+=[" - %s [%s](%s) -> [%s](https://fastly.jsdelivr.net/gh/yeshan333/rss-translate@main/%s)\n"%(sec,url,(url),get_cfg(sec,'name'),parse.quote(out_dir))]    
    c = GoogleTran(url,target=target,source=source).get_newconent(max=max_item)
    with open(out_dir,'w',encoding='utf-8') as f:
        f.write(c)
    print("GT: "+ url +" > "+ out_dir)

for x in secs[1:]:
    tran(x)
    print(config.items(x))

with open('test.ini','w') as configfile:
    config.write(configfile)


def get_idx(l):
    for idx,line in enumerate(l):
        if "## rss translate links" in line:
            return idx+2
YML="README.md"

f = open(YML, "r+", encoding="UTF-8")
list1 = f.readlines()           
list1= list1[:get_idx(list1)] + links

f = open(YML, "w+", encoding="UTF-8")
f.writelines(list1)
f.close()
