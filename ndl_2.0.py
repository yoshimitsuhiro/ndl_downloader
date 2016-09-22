#!/usr/bin/python3

from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader
import requests, time, os#, sys, codecs#, re

def main():
	scale = 1  #scale of images (1 = 100%, 2 = 50%, 4 = 25%, 8 = 12.5%, 16 = 6.25%, 32 = 3.125%)
	waittime = 30 #wait interval between downloads (must be set to at least 30 or IP will be blocked temporarily as of 2016.01)
	jpglimit = 1 #number of simultaneous jpg downloads (currently can't go higher than 1 as of 2016.01)
	pdflimit = 50 #number of simultaneous pdf page downloads (currently can't go higher than 50 as of 2016.01)
	#the three commands below only make a difference in single volume mode
	firstpage = 1 #starting page (should be set to 1 unless starting midway)
	lastpage = 0 #set last page manually here (set to 0 to find last page automatically or if downloading individual pages)
	pages = [0]	#insert pages numbers separated by comma for manual download of individual pages (set to 0 to download all pages)
	if pages[0] != 0:
		firstpage = pages[0]
		lastpage = pages[1]
	print(u"Choose one of the following options:")
	print(u"1. Download a single volume book or a single volume of a book.\n2. Download a multi volume book.")
	while True:
		multi_vol = input()
		if multi_vol == "1": break
		elif multi_vol == "2": break
		else: print(u"Invalid input! Input 1 or 2.")
	print(u"Enter the URL of the book you wish to download:")
	while True:
		book_url = input("") #get URL of book
		if book_url[:35] == "http://dl.ndl.go.jp/info:ndljp/pid/": break
		else: print(u"Invalid input! Be sure to enter the full URL including http://.")
	book_id = int(book_url.split("/")[-1]) #get book id
	soup = BeautifulSoup(requests.get(book_url).text) #soup of book URL
	title, volume, fulltitle = gettitle(soup) #get title and volume of book
	if lastpage == 0: lastpage = getpages(soup) #get last page of volume
	if multi_vol == "2":
		next_id = book_id + 1
		next_url = "http://dl.ndl.go.jp/info:ndljp/pid/{}".format(next_id)
		next_soup = BeautifulSoup(requests.get(next_url).text)
		next_title, next_volume, next_fulltitle = gettitle(next_soup)
		if title != next_title:
			print(u"Only one volume found. Do you wish to download anyway?\n(y/n?):")
			while True:
				choice = input()
				if choice == "y" or choice == "Y" or choice == "yes" or choice == "YES":
					multi_vol = "1"
					break
				elif choice == "n" or choice == "N" or choice == "no" or choice == "NO":
					choice == "n"
					return
				else: print(u"Invalid input! Input yes or no.")
	print(u"Choose one of the following options:")
	print(u"1. Download as jpgs (better quality but much longer download time).\n2. Download as pdf (lower quality but much shorter download time).")
	while True:
		downloadmode = input()
		if downloadmode == "1": break
		elif downloadmode == "2": break
		else: print(u"Invalid input! Input 1 or 2.")
	if downloadmode == "1": downloadlimit = jpglimit
	elif downloadmode == "2": downloadlimit = pdflimit
	if estimate(book_id, title, fulltitle, firstpage, lastpage, waittime, downloadlimit, multi_vol): #estimate time to download
		if downloadmode == "1":	getjpgs(fulltitle, firstpage, lastpage, book_id, scale, waittime, downloadlimit) #download book as jpgs
		elif downloadmode == "2": getpdfs(fulltitle, firstpage, lastpage, book_id, scale, waittime, downloadlimit) #download book as pdf			   
		if multi_vol == "2":
			next_id = book_id + 1
			while True:
				next_url = "http://dl.ndl.go.jp/info:ndljp/pid/{}".format(next_id)
				next_soup = BeautifulSoup(requests.get(next_url).text)
				next_title, next_volume, next_fulltitle = gettitle(next_soup)
				next_firstpage = 1
				next_lastpage = getpages(next_soup)
				if first_title == next_title:
					if downloadmode == "1":	getjpgs(next_fulltitle, next_firstpage, next_lastpage, next_id, scale, waittime, downloadlimit) #download volume as jpgs
					if downloadmode == "2":	getpdfs(next_fulltitle, next_firstpage, next_lastpage, next_id, scale, waittime, downloadlimit) #download volume as pdf
					next_id = next_id + 1
				else: break

def gettitle(soup): #get title and volume of book
	#title = soup.find("dt",text=re.compile("(title)")).findNext("dd").contents[0].lstrip()
	#if soup.find("dt",text=re.compile("(volume)")):
	#	volume = soup.find("dt",text=re.compile("(volume)")).findNext("dd").contents[0].lstrip()
	#	fulltitle = "{0}_{1}".format(title, volume)
	#if soup.find("dt",text=u"タイトル (title)"):
	#	title = soup.find("dt",text=u"タイトル (title)").findNext("dd").contents[0].lstrip()
	#else:
	#	title = ""
	#if soup.find("dt",text=u"巻次、部編番号 (volume)"):
	#	volume = soup.find("dt",text=u"巻次、部編番号 (volume)").findNext("dd").contents[0].lstrip()
	#	fulltitle = u"{0}_{1}".format(title, volume)
	#else:
	#	volume = ""
	#	fulltitle = title
	if soup.find("dt",text=u"タイトル (title)"):#get title
		title = soup.find("dt",text=u"タイトル (title)").findNext("dd").contents[0].lstrip()
	else:
		title = "No.Title"
	if soup.find("dt",text=u"著者標目 (creator)"):#get author
		author = soup.find("dt",text=u"著者標目 (creator)").findNext("dd").contents[0].lstrip()
	else:
		author = "Unknown"
	if soup.find("dt",text=u"出版年月日(W3CDTF形式) (issued:W3CDTF)"):#get date of publication
		date = soup.find("dt",text=u"出版年月日(W3CDTF形式) (issued:W3CDTF)").findNext("dd").contents[0].lstrip()
	else:
		date = "Undated"	
	if soup.find("dt",text=u"巻次、部編番号 (volume)"):#get name of volume (if applicable)
		volume = soup.find("dt",text=u"巻次、部編番号 (volume)").findNext("dd").contents[0].lstrip()
		fulltitle = "{0} ({1}) {2}, {3}".format(author, date, title, volume)
	else:
		volume = ""
		fulltitle = "{0} ({1}) {2}".format(author, date, title)
	#title = title.lstrip()
	#volume = volume.lstrip()
	#if not os.path.isdir(title_tag):
	#	os.mkdir(title_tag)
	#	os.chdir(title_tag)
	#else:
	#	os.chdir(title_tag)
	return(title, volume, fulltitle)

def getpages(soup): #get last page of volume
	if soup.find("input", {"name":"lastContentNo"}):
		lastpage = int(soup.find("input", {"name":"lastContentNo"})["value"]) #find last page automatically
	return(lastpage)

def getjpgs(fulltitle, firstpage, lastpage, book_id, scale, waittime, downloadlimit): #download book
	#pagefiller = 0
	#if pages[0] == 0:
	#	pages[0] = firstpage
	#	for p in range(firstpage + 1, lastpage + 1):
	#		pages.append(p)
	#		pagefiller += 1
	#for page in pages:
	page = firstpage
	while page <= lastpage:
		for i in range(0, downloadlimit):
			if page < 10:
				filename = u"{0}_000{1}.jpg".format(fulltitle, page)
			elif page < 100:
				filename = u"{0}_00{1}.jpg".format(fulltitle, page)
			else:
				filename = u"{0}_0{1}.jpg".format(fulltitle, page)
			print(u"Now downloading page {0} of {1} of {2}.".format(page, lastpage, fulltitle))
			#print(u"Now downloading page {0} of {1}.".format(page, lastpage)) #for shitty Windows console
			payload = {"itemId": "info:ndljp/pid/{}".format(book_id), "contentNo": page, "outputScale": scale}
			while True:
				try:
					r = requests.get("http://dl.ndl.go.jp/view/jpegOutput", params=payload)
					r.raise_for_status()
					break
				except requests.exceptions.HTTPError:
					print("Download error. Trying again...")
					time.sleep(waittime)
			with open(filename, "wb") as f:
				f.write(r.content)
				f.closed
			page += 1
		time.sleep(waittime)

def getpdfs(fulltitle, firstpage, lastpage, book_id, scale, waittime, downloadlimit): #download book as pdfs (faster but poorer quality)
	filenames = []
	#pagefiller = 0
	#if pages[0] == 0:
	#	pages[0] = firstpage
	#	for p in range(firstpage + 1, lastpage + 1):
	#		pages.append(p)
	#		pagefiller += 1
	#for page in pages:
	page = firstpage
	while page <= lastpage:
		if lastpage < page + downloadlimit - 1:
			lastpdfpage = lastpage
		else:
			lastpdfpage = page + downloadlimit - 1
		if page < 10:
			if lastpdfpage < 10: filename = u"{0}_000{1}-000{2}.pdf".format(fulltitle, page, lastpdfpage)
			elif lastpdfpage < 100: filename = u"{0}_000{1}-00{2}.pdf".format(fulltitle, page, lastpdfpage)
			else: filename = u"{0}_000{1}-0{2}.pdf".format(fulltitle, page, lastpdfpage)
		elif page < 100:
			if lastpdfpage < 100: filename = u"{0}_00{1}-00{2}.pdf".format(fulltitle, page, lastpdfpage)
			else: filename = u"{0}_00{1}-0{2}.pdf".format(fulltitle, page, lastpdfpage)			
		else:
			filename = u"{0}_0{1}-0{2}.pdf".format(fulltitle, page, lastpdfpage)
		print(u"Now downloading pages {0} to {1} of {2} in {3}.".format(page, lastpdfpage, lastpage, fulltitle))
		#print(u"Now downloading pages {0} to {1} of {2}.".format(page, lastpdfpage, lastpage)) #for shitty Windows console
		payload = {"pdfOutputRangeType": "R", "pdfPageSize": "", "pdfOutputRanges": "{0}-{1}".format(page, lastpdfpage)}
		while True:
			try:
				r = requests.get("http://dl.ndl.go.jp/view/pdf/digidepo_{}.pdf".format(book_id), params=payload)
				r.raise_for_status()
				break
			except requests.exceptions.HTTPError:
				print("Download error. Trying again...")
				time.sleep(waittime)
		with open(filename, "wb") as f:
			f.write(r.content)
			f.closed
		page += downloadlimit
		filenames.append(filename)
		time.sleep(waittime)
	mergepdfs(fulltitle, filenames)

def mergepdfs(fulltitle, filenames):
	fullfilename = u"{}.pdf".format(fulltitle)
	merger = PdfFileMerger()
	for f in filenames:
		merger.append(PdfFileReader(open(f, "rb")))
	merger.write(fullfilename)
	for d in filenames:
		os.remove(d)

def estimate(book_id, title, fulltitle, firstpage, lastpage, waittime, downloadlimit, multi_vol): #estimate time to download:
	if multi_vol == "1":
		#if pages[0] == 0: totalpages = lastpage - firstpage + 1
		#else: totalpages = len(pages)
		totalpages = lastpage
	elif multi_vol == "2":
		print(u"Number of pages in {0} = {1}".format(fulltitle, lastpage))
		#print(u"Number of pages = {0}".format(lastpage)) #for shitty Windows console
		num_vols = 1
		totalpages = lastpage
		next_id = book_id + 1
		while True:
			next_url = "http://dl.ndl.go.jp/info:ndljp/pid/{}".format(next_id)
			next_soup = BeautifulSoup(requests.get(next_url).text)
			next_title, next_volume, next_fulltitle = gettitle(next_soup)
			next_lastpage = getpages(next_soup)
			if title == next_title:
				print(u"Number of pages in {0} = {1}".format(next_fulltitle, next_lastpage))
				#print(u"Number of pages = {0}".format(next_lastpage)) #for shitty Windows console
				num_vols += 1
				totalpages = totalpages + next_lastpage
				next_id += 1
			else: break
		print(u"Total number of volumes = {0}".format(num_vols))
	m, s = divmod((waittime/downloadlimit) * totalpages, 60)
	h, m = divmod(m, 60)
	h = int(h)
	m = int(m)
	s = int(s)
	if h == 1:
		hours = "1 hour"
		if m > 0 or s > 0: hours += ", "
	elif h > 1:
		hours = "{} hours".format(h)
		if m > 0 or s > 0: hours += ", "
	else: hours = ""
	if m == 1:
		minutes = "1 minute"
		if s > 0: minutes += ", "
	elif m > 1:
		minutes = "{} minutes".format(m)
		if s > 0: minutes += ", "
	else: minutes = ""
	if s == 1: seconds = "1 second"
	elif s > 1: seconds = "{} seconds".format(s)
	else: seconds = ""
	totaltime = "{0}{1}{2}.".format(hours, minutes, seconds)
	if multi_vol == "1": print(u"Total number of pages in {0} = {1}.".format(fulltitle, totalpages))
	#if multi_vol == "1": print(u"Total number of pages = {0}.".format(totalpages)) #for shitty Windows console
	elif multi_vol == "2": print(u"Total number of pages in {0} = {1}.".format(title, totalpages))
	#elif multi_vol == "2": print(u"Total number of pages = {0}.".format(totalpages)) #for shitty Windows console
	print(u"Total time to download = {2}\nContinue with download?\n(y/n):".format(title, totalpages, totaltime))
	while True:
		choice = input()
		if choice == "y" or choice == "Y" or choice == "yes" or choice == "YES":
			return True
		elif choice == "n" or choice == "N" or choice == "no" or choice == "NO":
			return False
		else: print(u"Invalid input! Input yes or no.")

if __name__ == "__main__":
	main()