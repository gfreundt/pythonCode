from datetime import datetime as dt
import csv, os, sys
import subprocess
import platform
import yfinance as yf
from openpyxl import Workbook
import threading
from tqdm import tqdm


class YahooFinance:

	def __init__(self):
		self.FILE_NAME = 'yf_tickers.xlsx'
		self.CHUNK_SIZE = 50
		self.TICKERS, self.FIELDS = self.load_parameters()
		self.TITLE = 'YF Tickers'
		self.DESCRIPTION = 'Yahoo Finance General Information for Specific Tickers and Fields'
		
	def load_parameters(self):
		with open('yf_tickers.txt', mode='r') as file: #TEST FILE: yf_t.txt
			tickers = [i.strip() for i in file.readlines()]
			# Break into chunks for threading
			tickers = [tickers[i:i + self.CHUNK_SIZE] for i in range(0, len(tickers), self.CHUNK_SIZE)]
		with open('yf_fields.txt', mode='r') as file:
			fields = [i.strip() for i in file.readlines()]
		return tickers, fields

	def main(self):
		self.compose = []
		all_threads = []
		for ticker_chunk in tqdm(self.TICKERS):
			for ticker in ticker_chunk:
				new_thread = threading.Thread(target=self.yf_api, args=[ticker])
				new_thread.start()
				all_threads.append(new_thread)
			# Join all threads and wait until they are done before moving on with next chunk
			_ = [i.join() for i in all_threads]
		write_xlsx(headers=self.FIELDS, data=self.compose, title=self.TITLE, filename=self.FILE_NAME)
		
	def yf_api(self, ticker):
		t = yf.Ticker(ticker)
		self.compose.append(self.select_data(t.info, self.FIELDS))

	def select_data(self, data, selected):
		result = []
		for field in selected:
			if field in data.keys():
				result.append(data[field])
			else:
				result.append(' ')
		return result


class Bvl:

	def __init__(self):
		self.FILE_NAME = 'bvl_cierre.xlsx'
		self.URL = 'https://www.bvl.com.pe/mercado/movimientos-diarios'
		self.FIELDS = ['symbol', 'price', 'date']
		self.TITLE = 'Cierre BVL'
		self.DESCRIPTION = 'Cierre de precios de acciones BVL día anterior'

	def main(self):
		raw = self.httrack(self.URL)
		prices = self.get_prices(raw)
		final = self.mix_and_match(prices)
		write_xlsx(headers=self.FIELDS, data=final, title=self.TITLE, filename=self.FILE_NAME)

	def httrack(self, url):
		os.chdir('webdata')
		subprocess.run('httrack --quiet --update --skeleton --display ' + url, shell=True)
		os.chdir('..')
		with open(os.path.join('webdata', 'www.bvl.com.pe', 'mercado', 'agentes', 'listado.html'), mode='r') as file:
			return file.read()

	def get_prices(self, raw):
		codes = self.get_codes(raw)
		extract=[]
		for code in codes:
			nidx = raw.find(">"+code+"<") + len(code) + 12
			e = self.get_string(raw, nidx).replace(',','')
			extract.append(float(e))
		return list(zip(codes, extract, [dt.strftime(dt.now(),'%d-%m-%Y')]*len(codes)))

	def get_codes(self, raw):
		idx = 0
		extract = []
		while True:
			nidx = raw.find('<dl><dt>', idx) + 8
			if nidx == 7:
				return sorted(extract)
			e = self.get_string(raw, nidx)
			if not ([i for i in e if i.islower()]):
				extract.append(e)
			idx = int(nidx)

	def get_string(self, raw, idx):
		r = ''
		while True:
			s = raw[idx:idx+1]
			if s=="<":
				return r.strip()
			else:
				r += s
				idx += 1
	
	def mix_and_match(self, prices):
		final = []
		with open('bvl_latest_temp.csv', mode='r', encoding= 'utf-8') as file:
			content = [i for i in csv.reader(file, delimiter=",")]
		# update all current codes with new information (if it exists) or copy current one
		for code in content[1:]:
			appending = [i for i in prices if i[0] == code[0]]
			if not appending:
				to_append = code[:]
			else:
				to_append = appending[0]
			final.append(to_append)
		# add new codes from new information not in current codes
		for code in prices:
			if code not in final:
				final.append(code)
		# rewrite latest file (for next time)
		with open('bvl_latest_temp.csv', mode='w', encoding='utf-8') as file:
			w = csv.writer(file, delimiter=",")
			for line in sorted(final, key=lambda i:i[0]):
				w.writerow(line)
		return final


def get_system():
	node = platform.node()
	if 'raspberrypi' in node:
		return '/home/pi/pythonCode/financials'
	else:
		return '/home/gabriel/pythonCode/financials'

def write_xlsx(headers, data, title, filename):
	workbook = Workbook()
	sheet = workbook.active
	sheet.title = title
	# Insert header row
	sheet.append(headers)
	# Insert data by rows
	for row in data:
		sheet.append(row)
	workbook.save(filename=filename)

def send_gmail(to_list, subject, body, attach):
	import ezgmail # Import close to sending to avoid 'Broken Pipe' error
	for to in to_list:
		ezgmail.send(to, subject, body, attach)


# Set-Up
os.chdir(get_system())
send_to_list = ['gfreundt@losportales.com.pe', 'jlcastanedaherrera@gmail.com']
files_to_send = []
text_to_send = ''

# Yahoo Finance
if 'YF' in sys.argv:
	y = YahooFinance()
	y.main()
	files_to_send.append(y.FILE_NAME)
	text_to_send += ('\n- ' + y.DESCRIPTION)

# Bolsa de Valores de Lima
if 'BVL' in sys.argv:
	b = Bvl()
	b.main()
	files_to_send.append(b.FILE_NAME)
	text_to_send += ('\n- ' + b.DESCRIPTION)

# Close with sending mail with attachments
if not 'NOEMAIL' in sys.argv:
	send_gmail(send_to_list, subject='Información Financiera del ' + dt.strftime(dt.now(), '%Y.%m.%d'), body='Contenido:' + text_to_send, attach=files_to_send)
