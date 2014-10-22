# -*- coding: utf-8 -*-
import yaml
import urllib, urllib2
import re
import cookielib
from BeautifulSoup import BeautifulSoup 


class Marco:
	cj = cookielib.CookieJar()
	http = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	params = {}
	scrap = None
	
	def login(self, username, password):
		response = self.http.open('https://marco.ms.dendai.ac.jp/PTDU79130R/AX0101.aspx')
		html = response.read()
		soup = BeautifulSoup(html)
		input = soup.findAll('input')
		#print soup.find('input', {'name', '__VIEWSTATE'})

		for x in input:
			value = x.get('value')
			name = x.get('name')
			if value == None:
				value = ''
			if name != 'TextBox_UserID' and name != 'TextBox_Password':
				self.params[name] = value
			elif name == 'TextBox_UserID':
				self.params[u'TextBox_UserID'] = username.decode('utf-8')
			else:
				self.params[u'TextBox_Password'] = password.decode('utf-8')

		encoded_params = urllib.urlencode(self.params)

		url = 'https://marco.ms.dendai.ac.jp/PTDU79130R/AX0101.aspx'
		#print params
		req = self.http.open(url, encoded_params)
		soup =  BeautifulSoup(req.read())
		login_msg = soup.findAll('div', {'class': 'login_msg'})
		login_msg = unicode.join(u'\n',map(unicode, login_msg))
		#print login_msg
		if 'Please enter User ID / Password' in login_msg:
			print 'Login failure.'
		else:
			for x in soup.findAll('input'):
				name = x.get('name')
				value = x.get('value')
				self.params[name] = value
		
	
	def getreport(self):
		# Step 1
		response = self.http.open('https://marco.ms.dendai.ac.jp/PTDU79130R/AX1301.aspx?targeturl=https://marco.ms.dendai.ac.jp/ReportServer/Pages/ReportViewer.aspx?/PTDU79130R/report_GSY0205&params=USER_ID&rs:Command=Render&system=rs')
		html = response.read()
		soup = BeautifulSoup(html)
		url = soup.find('form').get('action')
		print 'URL: %s' % url
		
		# Step 2
		userparams = {}
		for x in soup.findAll('input'):
			name = x.get('name')
			if name == u'USER_ID':
				value = x.get('value')
				userparams[name] = value
		#print userparams
		
		# Step 3
		encoded_params = urllib.urlencode(userparams)
		req = self.http.open(url, encoded_params)
		soup = BeautifulSoup(req.read())
		viewstate = ''
		eventvalidation = ''
		#print soup
		for x in soup.findAll('input'):
		#	#print 'x: %s' % x
			name = x.get('name').decode('utf-8')
			value = x.get('value')
			if name == u'__VIEWSTATE':
				viewstate = value
			elif name == u'__EVENTVALIDATION':
				eventvalidation = value
		#		step5params[name] = ''
		#	else:
		#		step5params[name] = value.encode('utf_8')
		
		r = re.compile('SessionID=(.*?)"')
		m = r.search(str(soup))
		session_id = m.group(1)
		
		r = re.compile('ControlID=(.*?)&')
		m = r.search(str(soup))
		control_id = m.group(1)
		print 'ControlId: %s' % control_id
		
		# Step 4
		url = 'https://marco.ms.dendai.ac.jp/ReportServer/Reserved.ReportViewerWebControl.axd?OpType=SessionKeepAlive&ControlID=' + control_id
		response = self.http.open(url, session_id)
		if response.read() != u'OK':
			print 'ERROR'
			return None
		else:
			print 'OK'
		
		# Step 5
		# fuckin' quote_plus
		step5params = {}
		step5params[u'AjaxScriptManager'] = u'AjaxScriptManager|ReportViewerControl$ctl09$Reserved_AsyncLoadTarget'
		step5params[u'NavigationCorrector$NewViewState'] = u''
		step5params[u'NavigationCorrector$PageState'] = u''
		step5params[u'NavigationCorrector$ScrollPosition'] = u''
		step5params[u'NavigationCorrector$ViewState'] = u''
		step5params[u'ReportViewerControl$AsyncWait$HiddenCancelField'] = u'False'
		step5params[u'ReportViewerControl$ToggleParam$collapse'] = u'false'
		step5params[u'ReportViewerControl$ToggleParam$store'] = u''
		step5params[u'ReportViewerControl$ctl03$ctl00'] = u''
		step5params[u'ReportViewerControl$ctl03$ctl01'] = u''
		step5params[u'ReportViewerControl$ctl05$ctl00$CurrentPage'] = u''
		step5params[u'ReportViewerControl$ctl05$ctl03$ctl00'] = u''
		step5params[u'ReportViewerControl$ctl07$collapse'] = u'false'
		step5params[u'ReportViewerControl$ctl07$store'] = u''
		step5params[u'ReportViewerControl$ctl08$ClientClickedId'] = u''
		step5params[u'ReportViewerControl$ctl09$ReportControl$ctl02'] = u''
		step5params[u'ReportViewerControl$ctl09$ReportControl$ctl03'] = u''
		step5params[u'ReportViewerControl$ctl09$ReportControl$ctl04'] = u'100'
		step5params[u'ReportViewerControl$ctl09$ScrollPosition'] = u''
		step5params[u'ReportViewerControl$ctl09$VisibilityState$ctl00'] = u'None'
		step5params[u'ReportViewerControl$ctl10'] = u'ltr'
		step5params[u'ReportViewerControl$ctl11'] = u'quirks'
		step5params[u'__ASYNCPOST'] = u'true'
		step5params[u'__EVENTARGUMENT'] = u''
		step5params[u'__EVENTTARGET'] = u'ReportViewerControl$ctl09$Reserved_AsyncLoadTarget'
		step5params[u'__EVENTVALIDATION'] = eventvalidation
		step5params[u'__VIEWSTATE'] = viewstate
		step5params[u'__LASTFOCUS'] = u''
		step5params[u'ReportViewerControl%24ctl04%24ctl05%24txtValue'] = u'2014/10/21 0:00:00' # DateTime
		#step5param = ''
		#for key, val in step5params.iteritems():
		#	step5param = step5param + key + '=' + val + '&'
		
		
		step5params = urllib.urlencode(step5params)
		# ユーザーエージェントないとAUTO
		self.http.addheaders = [('Referer', 'https://marco.ms.dendai.ac.jp/ReportServer/Pages/ReportViewer.aspx?/PTDU79130R/report_GSY0205'), ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36')]
		response = self.http.open('https://marco.ms.dendai.ac.jp/ReportServer/Pages/ReportViewer.aspx?%2fPTDU79130R%2freport_GSY0205', step5params)
		html = response.read()
		soup = BeautifulSoup(html)
		self.scrap = soup.findAll("tr", valign="top")
		return html

	#scrapをごにょごにょしてデータをぶっこ抜くメソッド
	def datascrapper(self):
		
		for val in self.scrap[3].findAll("div"):
			if "館" in val.string:
				hex_num = val["class"]
				break

		for index,val in enumerate(self.scrap[3].findAll("div")):
			if val["class"] == hex_num:
				try:
					data = self.scrap[3].findAll("div")[index-2].string
					time = self.scrap[3].findAll("div")[index-1].string
					where = val.string
				except:
					data = "None"
					time = "None"
					where = "None"
				print "%s - %s - %s"%(data,time,where)
				print "-------------------"

if __name__ == '__main__':
	setting_txt = open('setting.yaml', 'r').read().decode('utf-8')
	setting = yaml.load(setting_txt)
	username = setting['username']
	password = setting['password']
	marco = Marco()
	marco.login(username, password)
	html = marco.getreport()
	marco.datascrapper() #データぶっこ抜き
	f = open('marco.txt', 'w')
	f.write(html)
	f.close()