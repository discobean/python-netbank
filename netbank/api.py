import re
import mechanize
import cookielib
import json
from bs4 import BeautifulSoup
from html2text import html2text

class Netbank(object):

	def __init__(self):
		self.base_url = 'https://www.my.commbank.com.au/'
		self.login_url = 'netbank/Logon/Logon.aspx'
		self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36'
		self.br = mechanize.Browser()
		self.br.set_handle_robots(False)
		self.br.set_handle_refresh(False)
		self.br.set_handle_equiv(True)
		self.br.set_handle_gzip(True)
		self.br.set_handle_redirect(True)
		self.br.set_handle_referer(True)
		self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
		self.br.addheaders = [('User-agent', self.user_agent)]
		self.br.set_cookiejar(cookielib.LWPCookieJar())

	def login(self, username, password):
		br = self.br

		br.open("%s%s" % (self.base_url, self.login_url))

		br.select_form(name="form1")
		for control in br.form.controls:
			control.disabled = False

		br.form.set_all_readonly(False)
		br['txtMyClientNumber$field'] = username
		br['txtMyPassword$field'] = password
		br['JS'] = 'E'
		response = br.submit()

		soup = BeautifulSoup(response.read(), 'html5lib')

		account_list = []
		for row in soup.select(".main_group_account_row"):
			nickname = row.select(".NicknameField a")[0]
			bsb = row.select(".BSBField .field")[0]
			account_number = row.select(".AccountNumberField .field")[0]
			try:
				balance = row.select("td.AccountBalanceField span.Currency")[0]
				balance = balance.text
			except IndexError:
				balance = 0
			try:
				available = row.select("td.AvailableFundsField span.Currency")[0]
				available = available.text
			except IndexError:
				available = 0

			account_list.append({
				"nickname": nickname.text,
				"url": nickname.get('href'),
				"bsb": bsb.text,
				"account_num": account_number.text,
				"balance": balance,
				"available": available
			})

		return account_list

	def get_transactions(self, account, from_date=None, to_date=None):
		br = self.br

		response = br.open("%s%s" % (self.base_url, account['url']))
		soup = BeautifulSoup(response.read(), 'html5lib')

		try:
			br.select_form(name="aspnetForm")
		except mechanize._mechanize.FormNotFoundError:
			return []

		br.form.set_all_readonly(False)
		br['__EVENTTARGET'] = 'ctl00$BodyPlaceHolder$lbSearch'
		br['__EVENTARGUMENT'] = ''
		br['ctl00$BodyPlaceHolder$searchTypeField'] = '1'
		br['ctl00$BodyPlaceHolder$radioSwitchDateRange$field$'] = ['ChooseDates',]
		br['ctl00$BodyPlaceHolder$dateRangeField'] = 'ChooseDates'
		br['ctl00$BodyPlaceHolder$fromCalTxtBox$field'] = from_date
		br['ctl00$BodyPlaceHolder$radioSwitchSearchType$field$'] = ['AllTransactions',]

		br.form.new_control('text','ctl00$ctl00',{'value':''})
		br.form.fixup()

		br['ctl00$ctl00'] = 'ctl00$BodyPlaceHolder$updatePanelSearch|ctl00$BodyPlaceHolder$lbSearch'

		response = br.submit().read()
		pattern = "registerStartupFunction\('loadInitial',(.*\})"
		responses = re.findall(pattern, response)

		transactions = json.loads(responses[0])
		return transactions["Transactions"]
