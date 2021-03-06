#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import urllib2
import urllib
import re
import shutil
import time
import thread
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2

class Account:
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0'}
        self.ip_h = self.get_ip_h()
        self.remixsid = self.get_remixsid()
        self.cookies = self.get_cookies()
        if self.cookies is not None:
            self.headers.update(Cookie=self.cookies)
            self.isvalid = True
        else:
            self.isvalid = False

    def get_ip_h(self):
        request = urllib2.Request('http://vk.com/', None, self.headers)
        try:
            response = urllib2.urlopen(request)
            ip_h = re.findall(r'value="[a-z 0-9]{18}"', response.read())[0]            
        except:
            print('Internet connection problems')
            ip_h = None
        finally:
            return ip_h

    def get_remixsid(self):
        values = {'act': 'login',
                  'q': '1',
                  'al_frame': '1',
                  'expire': '',
                  'captcha_sid': '',
                  'captcha_key': '',
                  'from_host': 'vk.com',
                  'from_protocol': 'http',
                  'ip_h': self.ip_h,
                  'email': self.email,
                  'pass': self.password} 
        data = urllib.urlencode(values)   
        request = urllib2.Request('https://login.vk.com/?act=login', data, self.headers)
        try:
            response = urllib2.urlopen(request)
            remixsid = re.findall(r"remixsid=([a-z 0-9]*);", response.headers['Set-Cookie'])[0]            
        except:
            print('Internet connection problems')
            remixsid = None
        finally:
            return remixsid

    def get_cookies(self):        
        if self.remixsid is not "" and self.remixsid is not None:
            list_cookies = ['remixlang=0;',
                            'remixchk=5;',
                            'remixdt=0;', 
                            'audio_vol=100;',
                            'remixflash=11.2.202;',
                            'remixseenads=2;'
                            'remixsid=' + self.remixsid + ';',
                            'remixreg_sid=;',
                            'remixrec_sid=']            
            return  " ".join(list_cookies)
        else:
            print('Incorrect account data')
            return None

    def _get_page(self, url): 
        headers = self.headers
        headers.update(Cookie=self.cookies)        
        try:
            request = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(request)
            print(dir(response))
            return response.read()
        except:
            print('Internet connection problems')
            return None

class Folders:
    def __init__(self, temp='temp/', save_to='saved/'):
            if not os.path.exists(temp):
                try:
                    os.makedirs(temp)
                except:
                    print('Failed to create a folder')
                    self.temp = 'temp/'
                else:
                    self.temp = temp
            else:
                self.temp = temp
            if not os.path.exists(save_to):
                try:
                    os.makedirs(save_to)
                except:
                    print('Failed to create a folder ')
                    self.save_to = 'saved/'
                else:
                    self.save_to = save_to
            else:
                self.save_to = save_to

class Track:
    def __init__(self, account, keywords, folders):
        if account.isvalid:
            print "\nAccount is valid, searching for:", keywords, "..."
            self.account = account
        else:
            print('Incorrect account data, use valid account')
            return None
        self.keywords = keywords
        self.folders = folders         
        self.link = self.get_audio_link(keywords)        
        if not self.link:
            print('Sorry, this track is not found')
            return None
    def further(self):
        print 'Track is found'
        print 'URL:', self.link               
        self.tempname = self.folders.temp + self.link.split('/')[-1]
        print 'Downloading...'      
        print 'Saving path: \'{0}\''.format(self.folders.save_to)
        self.isdownloaded = None
        self.isdownloaded = self.download()        
        if self.isdownloaded:
            self.tags = self.get_audio_tags(self.tempname)                    
            self.filename = self.get_audio_name_by_tags(self.tags)
            shutil.move(self.tempname, self.filename)
            try:
                print '\nFile \'{0}\' has been saved!'.format(self.filename.encode('utf8'))
            except:
                print '\nFile \'{0}\' has been saved!'.format(self.filename)
        else:
            print("Tags not found")
            self.tags = None
            self.filename = None        
    
    def get_audio_link(self, keywords, number=0):
        values = {'act' : 'search',
                  'al' : 1,
                  'gid' : 0,
                  'id' : 0,
                  'offset' : 0,
                  'performer' : 0,
                  'q' : keywords,
                  'sort' : 0}       
        data = urllib.urlencode(values)
        request = urllib2.Request('http://vk.com/audio', data, self.account.headers)
        response = urllib2.urlopen(request)
        html = response.read()
        links = re.findall('(http://.*.mp3),', html)
        if len(links) != 0:
            return links[number]
        else:
            return None
    
    def get_audio_tags(self, filename):
        try:
            tags = MP3(filename)           
        except:
            print('Tags not found')
            return None
        else:
            if tags.has_key('TPE1') and tags.has_key('TIT2'):                
                return tags
            else:               
                tags = ID3()                
                return tags
    
    def get_audio_name_by_tags(self, tags, format=''):        
        try:
            artist = tags['TPE1'].text[0].encode('latin1').decode('cp1251')
            song = tags['TIT2'].text[0].encode('latin1').decode('cp1251')                   
        except:
            try:
                artist = tags['TPE1'].text[0].encode('utf8')
                song = tags['TIT2'].text[0].encode('utf8')
            except:
                print('Incorrect tags encoding')
                artist = 'Search result'
                song = self.keywords

        result_name = self.folders.save_to + artist + ' - ' + song + '.mp3'
        return result_name

    def download(self):        
        try:
            request = urllib2.Request(self.link)
            self.response = urllib2.urlopen(request)
            open(self.tempname, 'w').close()
            s = re.findall(r'Content-Length: [0-9]+', str(self.response.headers.headers))
            self.length = int(s[0].split(':')[-1][1:])                     
            self._ok = False
            thread.start_new_thread(self.progress_bar, ())       
            thread.start_new_thread(self._r, ())
            
            while not self._ok:
                time.sleep(1)                        
        except:
            print('Downloading error')
            return False
        else:
            return True

    def _r(self):
        urllib.urlretrieve(self.link, self.tempname)
        self._ok = True      
   
    def progress_bar(self):               
        while not self._ok and int(os.stat(self.tempname).st_size) != int(self.length):
            s ='\r ' + str(int(os.stat(self.tempname).st_size)) + ' of ' + str(self.length) + ' bytes'
            sys.stdout.write(s)
            sys.stdout.flush()
            time.sleep(1)
        
        sys.stdout.write('\r ' + str(self.length) + ' of ' + str(self.length) + ' bytes')
        sys.stdout.write('\nDone\n')
        sys.stdout.flush()  
      
    def play(self):
        pass

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) != 7:
        print "Use format: $ ./vkaudio.py -u \'user@mail.com:password\' -q \'query\' -o \'path/to/output/folder/\'"
        exit(1)

    params = {'-u': 'userdata', '-q': 'query', '-o': 'output'}
    for param in sys.argv:
        for key in params.keys():
            if param == key:
                try:
                    exec(params[key] + '=' + 'sys.argv[sys.argv.index(param)+1]')                    
                except:
                    print 'Incorrect params'                          
                    exit(1)
                else:
                    break    
    
    try:
        account = Account(userdata.split(':')[0], ''.join(userdata.split(':')[1:]))       
        folders = Folders('temp/', output)        
        track = Track(account, query, folders)
        if len(track.link) != 0:
            track.further()
    except:
        print('Something goes wrong, completion')
        exit(1)
    else:        
        print('Goodbye!')
        exit(0)     
