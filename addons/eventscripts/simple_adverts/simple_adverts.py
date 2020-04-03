import es
import random
import ConfigParser
import gamethread
import cfglib
import cmdlib

#AddonInfo:
info = es.AddonInfo() 
info.name     	= "Simple Adverts" 
info.basename 	= "simple_adverts"
info.version  	= "v1.0"
info.url      	= "www.NextGenerationGaming.de" 
info.description = "Displays adverts for your server. Easy to setup."
info.author   	= "Ruuubi"

#Classes:
class AdvertManager():
	def __init__(self):
		self.advertList = []
		self.colorDict = {}
		self.connectAdvert = es.ServerVar('advert_connect','','')
		self.roundAdvert = es.ServerVar('advert_round','','')
		self.spawnAdvert = es.ServerVar('advert_spawn','','')
		self.prefix = es.ServerVar('advert_prefix','#green[#defaultServer#green]','')
		self.mode = es.ServerVar('advert_mode',1,'')
		self.delay = es.ServerVar('advert_delay',30,'')
		self.index = 0
		self.importAdverts()
		self.importColors()
		cfglib.AddonCFG(PATH_ADDON+'/configs/config.cfg').execute()
		self.connectAdvert = str(self.connectAdvert)
		self.roundAdvert = str(self.roundAdvert)
		self.spawnAdvert = str(self.spawnAdvert)
		self.prefix = str(self.prefix)
		if self.prefix != '':
			if not self.prefix.startswith('#'): self.prefix = '#default'+self.prefix
			self.prefix = self.replaceColors(self.prefix)

	def importAdverts(self):
		file = open(PATH_ADDON+'/configs/adverts.txt','r')
		content = file.readlines()
		file.close()
		for x in content:
			if not x.startswith('//') and x != '\n': self.advertList.append(x.rstrip('\n'))

	def importColors(self):
		iniFile = ConfigParser.ConfigParser()
		iniFile.optionxform = str
		iniFile.read(PATH_ADDON+'/configs/colors.ini')
		for section in iniFile.sections():
			for color in iniFile.options(section):
				self.colorDict[color] = map(int,iniFile.get(section,color).split(','))

	def send(self,userid,text):
		es.tell(userid,'#multi','%s %s' % (self.prefix,self.replaceColors(text))) if self.prefix != '' else es.tell(userid,'#multi',self.replaceColors(text))

	def sendAll(self,text):
		es.msg('#multi','%s %s' % (self.prefix,self.replaceColors(text))) if self.prefix != '' else es.msg('#multi',self.replaceColors(text))

	def convertColor(self,(R,G,B)):
		return '\x07%02X%02X%02X' % (R,G,B)

	def replaceColors(self,text):
		for color in self.colorDict:
			text = text.replace('#%s' % color,self.convertColor(self.colorDict[color]))
		return text

	def endDelay(self):
		if self.mode == 1:
			self.sendAll(self.advertList[self.index])
			self.index +=1
			if self.index == len(self.advertList): self.index = 0
		elif self.mode == 2:
			self.sendAll(random.choice(self.advertList))
		gamethread.delayedname(self.delay,'advertDelay',self.endDelay)

	def dumpColors(self,args):
		es.msg('#multi','\x07FF8D00[\x0703B0FFSimple Adverts\x07FF8D00] Dumping colors..')
		iniFile = ConfigParser.ConfigParser()
		iniFile.optionxform = str
		iniFile.read(PATH_ADDON+'/configs/colors.ini')
		for section in iniFile.sections():
			dumpDict = {}
			dumpString = ''
			for color in iniFile.options(section):
				dumpString = dumpString+'%s%s ' % (self.replaceColors('#'+color),color)
			es.msg('#multi','\x07FF8D00[\x0703B0FF%s\x07FF8D00] %s' % (section,dumpString))
		es.msg('#multi','\x07FF8D00[\x0703B0FFSimple Adverts\x07FF8D00] Finished colordump!')

#Constants:
PATH_ADDON = es.getAddonPath("simple_adverts")

#Globals [Classes]:
advert = AdvertManager()

#Events:
def load():
	es.set('simple_adverts',info.version)
	es.makepublic('simple_adverts')
	gamethread.delayedname(advert.delay,'advertDelay',advert.endDelay)
	cmdlib.registerServerCommand('dump_colors',advert.dumpColors,'')
	es.msg('#multi','\x07FF8D00[\x0703B0FFSimple Adverts\x07FF8D00] \x0703B0FF%s \x07FF8D00successfully loaded!' % info.version)
	

def unload():
	gamethread.cancelDelayed('advertDelay')
	cmdlib.unregisterServerCommand('dump_colors')
	es.msg('#multi','\x07FF8D00[\x0703B0FFSimple Adverts\x07FF8D00] \x0703B0FF%s \x07FF8D00successfully unloaded!' % info.version)

def round_start(ev):
	if advert.roundAdvert != "": advert.sendAll(advert.roundAdvert)

def player_spawn(ev):
	if advert.spawnAdvert != "": advert.send(int(ev['userid']),advert.spawnAdvert)

def player_activate(ev):
	if advert.connectAdvert != "": advert.send(int(ev['userid']),advert.connectAdvert)
