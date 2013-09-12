#-*-coding:utf-8-*-
import cookielib, urllib2
import re
import os
import random
import time
import base64
import socket
import struct
import sys,getopt
import cPickle
import platform

if platform.system() != 'Windows':
    import fcntl        #the package didn't contain in the python on windows platform

class HitszClient:
    '''
    This class is used to authenticate the network!
    '''
    def __init__(self,flag=False,nic='eth0'):
        '''
	    some parameters
	    '''
        if platform.system() == 'Windows':      #Judge the paltform to verify the network
            self.platform = 1
        else:
            self.platform = 0
        self.username = '111111111'
        self.passwd = '22222222222'

        self.testUrl = 'http://www.baidu.com'   #the test page
        self.testStr = 'Authentication is required.'
        self.defaultPage = 'http://219.223.254.55/portal/index_default.jsp'
        self.actionurl = 'http://219.223.254.55/portal/login.jsp'
        self.onlineurl = 'http://219.223.254.55/portal/online.jsp'
        self.postdata = 'userName=%s&index_password=%s&userPwd=%s&serviceType=&isQuickAuth=false&language=Chinese&userurl=&userip=null&basip='%(self.username,self.passwd,self.GetAuthStr())
        self.headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0",
                        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                        #'Accept-Encoding':'gzip, deflate',
                        'Accept-Encoding':'deflate',
                        'Connection':'keep-alive'
                        }
        self.serialNo = ''
        self.heartStr = 'http://219.223.254.55/portal/online_heartBeat.jsp'
        self.offline = 'http://portal.utsz.edu.cn/portal/logout.jsp?language=Chinese&userip=null'
        self.doheartBeat = 'http://219.223.254.55/portal/doHeartBeat.jsp'
        self.heartUrl = ''
        self.offstr = '下线成功'    #the str to detect the status
        self.onstr = '在线窗口'     #the str to detect the online status
        self.userip = 'null'
        if self.platform:
            self.filepath = 'C:\\windows\\temp\\hitsz.txt'
            if not flag:
                self.ip = self.get_ip_address_win()
        else:
            self.filepath = '/tmp/hitsz.txt'
            if not flag:
                self.ip = self.get_ip_address_lin(nic)
        #print self.ip

    def GetAuthPage(self):
        '''
        Get the Authentication Page
        '''
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        test = opener.open(self.testUrl)
        return test.read() #return the page data

    def JudgeTheStatus(self,data):
        '''
        to judge the status of the network.
        the data is the return page
        the testdata is the key word
        '''
        if self.testStr in data:
            return False
        else:
            return True

    def GetAuthStr(self):
        '''
        Get the authencation string!
        '''
        pwd64 = base64.encodestring(self.passwd).replace('=','%3D').strip()
        return pwd64

    def WriteSerialNoAndIp(self):
        '''
        write the serial No
        '''
        print 'save Serial Number!!\n'
        f = open(self.filepath,'wb')
        if f:
            cPickle.dump(self.serialNo,f)
            cPickle.dump(self.userip,f)
            f.flush()
            f.close()
            return 1
        else:
            print 'save failed!'
            f.close()
            return 0

    def ReadSerialNoAndIp(self):
        '''
        read the serilNo
        '''
        print 'Read Serial Number!!\n'
        f = open(self.filepath,'rb')
        if f:
            self.serialNo = cPickle.load(f)
            self.userip = cPickle.load(f)
            f.close()
        else:
            f.close()

    def SetAuthInfo(self):
        '''
        send the Info to authenticate the network
        '''
        kcj = cookielib.CookieJar()
        ce4 = urllib2.build_opener(urllib2.HTTPCookieProcessor(kcj))
        req = urllib2.Request(self.actionurl, self.postdata, headers=self.headers)
        data = ce4.open(req)
        #print data.read()
        u = data.read()
        self.serialNo = re.search(r'(?<=<input type="hidden" name="serialNo" value=").+(?=">)', u).group(0)
        self.userip = re.search(r'(?<=<input type="hidden" name="userip" value=").+(?=">)', u).group(0)
        print self.userip
        self.WriteSerialNoAndIp()

        #print self.serialNo

    def get_ip_address_lin(self,ifname):
        '''
        Get IP address!
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
                )[20:24])

    def get_ip_address_win(self):
        '''
        get the ip address in windows environment.
        '''
        myname = socket.getfqdn(socket.gethostname())
        return socket.gethostbyname(myname)

    def sendOnlinePacket(self,seriNo):
        '''
        sent the heart Packet
        '''
        self.Datastr = 'language=Chinese&heartbeatCyc=2400000&heartBeatTimeoutMaxTime=3&userDevPort=C0006-SR6602-vlan-00-0000%%40vlan&userStatus=99&userip=%s&serialNo=%s&basip='%(self.userip,seriNo)
        kcj = cookielib.CookieJar()
        ce4 = urllib2.build_opener(urllib2.HTTPCookieProcessor(kcj))
        req = urllib2.Request(self.onlineurl, self.Datastr, headers=self.headers)
        data = ce4.open(req)
        if self.onstr in data.read():
            print 'Login online succeed!\n'
        else:
            print 'Login online failed!\n'
        #print data.read()

    def offlineVerify(self):
        '''
        log out the network
        '''
        req = urllib2.Request(self.offline,headers=self.headers)
        u = urllib2.urlopen(req)
        if self.offstr in u.read():
            print 'Login off succeed!'
        else:
            print 'Login off failed!'
        #print u.read()

    def sendHeartPacketInit(self):
        '''
        get online heart packet.
        '''
        #self.serialNo = self.ReadSerialNo(self.serialNo)
        self.heartStr += ('?heartbeatCyc=2400000&heartBeatTimeoutMaxTime=3&language=Chinese&userDevPort=C0006-SR6602-vlan-00-0000@vlan&userStatus=99&userip=%s&basip=&serialNo=%s'%(self.userip,self.serialNo))
        req = urllib2.Request(self.heartStr,headers=self.headers)
        u = urllib2.urlopen(req)
        print 'get heart Packet from url!!'
        #print u.read()
        #self.WriteFile(u.read(),'123.html')
        print self.userip

    def sendHeartPacket(self):
        '''
        request the heart Packet!
        '''
        self.doheartBeat += ('?heartBeatTimeoutMaxTime=3&language=Chinese&userDevPort=C0006-SR6602-vlan-00-0000@vlan&userip=%s&serialNo=%s&basip=&userStatus=99'%(self.userip,self.serialNo))
        req = urllib2.Request(self.doheartBeat,headers=self.headers)
        u = urllib2.urlopen(req)
        print 'Do heart Beat!!\n'
        print u.read()

    def WriteFile(self,content,path):
        '''
        write the file
        '''
        c = open(path,'wb')
        c.write(content)
        c.flush()
        c.close()

if __name__ == '__main__':
    opts,args = getopt.getopt(sys.argv[1:],"hi:o")
    for op, value in opts:
        if op == '-i':
            nic = value
            hitsz = HitszClient(False,nic)
            content = hitsz.GetAuthPage()
            if not hitsz.JudgeTheStatus(content):
                hitsz.SetAuthInfo()
                hitsz.sendOnlinePacket(hitsz.serialNo)
                hitsz.sendHeartPacketInit()
                hitsz.sendHeartPacket()
            else:
                hitsz.ReadSerialNoAndIp()
                hitsz.sendHeartPacket()


        elif op == '-o':
            hitsz = HitszClient(True)
            hitsz.offlineVerify()
        elif op == '-h':
            print 'command format:\n'
            print 'python hitszNet.py -i eth0  #to login\n'
            print 'python hitszNet.py -o #login out\n'
            print 'python hitszNet.py -h #for help\n'

        else:
            print 'Error!!'
            sys.exit()
