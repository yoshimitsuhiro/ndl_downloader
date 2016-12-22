#!/usr/bin/python3

from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader
import requests, time, os, regex#, sys, codecs#, re

def main():
	scale = 1  #scale of images (1 = 100%, 2 = 50%, 4 = 25%, 8 = 12.5%, 16 = 6.25%, 32 = 3.125%)
	waittime = 30 #wait interval between downloads (must be set to at least 30 or IP will be blocked temporarily as of 2016.01)
	jpglimit = 1 #number of simultaneous jpg downloads (currently can't go higher than 1 as of 2016.01)
	pdflimit = 50 #number of simultaneous pdf page downloads (currently can't go higher than 50 as of 2016.01)
	#the three commands below only make a difference in single volume mode
	firstpage = 1 #starting page (should be set to 1 unless starting midway)
	lastpage = 0 #set last page manually here (set to 0 to find last page automatically or if downloading individual pages)
	pages = [0,0] #insert pages numbers separated by comma for manual download of individual pages (set to 0 to download all pages)
	book_ids = []
	if pages[0] != 0:
		firstpage = pages[0]
		lastpage = pages[1]
	print(u"Choose one of the following options:")
	print(u"1. Download a single volume book or a single volume of a book.\n2. Download all volumes of a multi volume book.")
	while True:
		multi_vol = input()
		if multi_vol == "1": break
		elif multi_vol == "2": break
		else: print(u"Invalid input! Input 1 or 2.")
	if multi_vol == "1": print(u"Enter the URL of the book you wish to download:")
	elif multi_vol == "2": print(u"Enter the URL of the first volume of the book you wish to download:")
	while True:
		url = input("") #get URL of book
		if url[:35] == "http://dl.ndl.go.jp/info:ndljp/pid/": break
		else: print(u"Invalid input! Be sure to enter the full URL including http://.")
	book_id = int(url.split("/")[-1]) #get book id
	book_ids.append(book_id)
	soup = BeautifulSoup(requests.get(url).text) #get soup of URL
	title, volume, fulltitle = gettitle(soup) #get title
	if lastpage == 0: lastpage = getpages(soup) #get last page automatically if not specified
	if multi_vol == "2": #check to see if multiple volumes exist or not in multi_vol mode
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
	if estimate(book_ids, title, fulltitle, firstpage, lastpage, waittime, downloadmode, downloadlimit, multi_vol): #estimate download time and confirm download
		for i in book_ids:
			url = "http://dl.ndl.go.jp/info:ndljp/pid/{}".format(i)
			soup = BeautifulSoup(requests.get(url).text)
			title, volume, fulltitle = gettitle(soup)
			if lastpage == 0: lastpage = getpages(soup) #get last page automatically if not specified
			#make directory to store files in
			try:
				os.makedirs(fulltitle, exist_ok=False)
			except OSError:
				print("Directory \"{0}\" already exists.\nProceed anyway and overwrite contents?".format(fulltitle))
				while True:
					choice = input()
					if choice == "y" or choice == "Y" or choice == "yes" or choice == "YES": break
					elif choice == "n" or choice == "N" or choice == "no" or choice == "NO": return
					else: print(u"Invalid input! Input yes or no.")
			os.chdir(fulltitle)
			#download files
			if downloadmode == "1":	getjpgs(fulltitle, firstpage, lastpage, i, scale, waittime, downloadlimit) #download volume as jpgs
			elif downloadmode == "2": getpdfs(fulltitle, firstpage, lastpage, i, scale, waittime, downloadlimit) #download volume as pdf
			os.chdir("..")
			lastpage = 0

def gettitle(soup): #get title and volume of book
	if soup.find("dt",text=u"タイトル (title)"):#get title
		title = soup.find("dt",text=u"タイトル (title)").findNext("dd").contents[0].lstrip()
		title = replacebadchars(title) #only needed in Windows
	else:
		title = "No.Title"
	if soup.find("dt",text=u"著者 (creator)"):#get author
		author = soup.find("dt",text=u"著者 (creator)").findNext("dd").contents[0].lstrip()
		author = regex.sub(r"\s+", "", author)
		if author[-1:] == "著": author = author[:-1]
		author = replacebadchars(author) #only needed in Windows
	else:
		author = "Unknown"
	if soup.find("dt",text=u"出版年月日(W3CDTF形式) (issued:W3CDTF)"):#get date of publication
		date = soup.find("dt",text=u"出版年月日(W3CDTF形式) (issued:W3CDTF)").findNext("dd").contents[0].lstrip()
		date = replacebadchars(date) #only needed in Windows
	else:
		date = "Undated"	
	if soup.find("dt",text=u"巻次、部編番号 (volume)"):#get name of volume (if applicable)
		volume = soup.find("dt",text=u"巻次、部編番号 (volume)").findNext("dd").contents[0].lstrip()
		volume = replacebadchars(volume) #only needed in Windows
		fulltitle = "{0} ({1}) {2}, {3}".format(author, date, title, volume) #format of fulltitle with volume information
	else:
		volume = ""
		fulltitle = "{0} ({1}) {2}".format(author, date, title) #format of fulltitle without volume information
	return(title, volume, fulltitle)
	
def replacebadchars(string): #necessary if running in Windows
	#for s in string: print(s, s.encode("unicode_escape"))
	badchars = [r"\\", r"\/", r"\:", r"\*", r"\?", r"\"", r"\<", r"\>", r"\|"]
	goodchars = ["＼", "／", "：", "＊", "？", "”", "＜", "＞", "｜"]
	for bad in badchars:
		string = regex.sub(bad, goodchars[badchars.index(bad)], string)
	#replace fullwidth numbers and punctuation with halfwidth (comment out next 4 lines if not desired)
	fullnums = [r"１", r"２", r"３", r"４", r"５", r"６", r"７", r"８", r"９", r"０", u"\u2212", r"[．。]", r"[、，]", r"（", r"）", r"［", r"］"]
	halfnums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", ".", ",", "(", ")", r"[", r"]"]
	for num in fullnums:
		string = regex.sub(num, halfnums[fullnums.index(num)], string)
	#remove all whitespace (comment out next line if not desired)
	string = regex.sub(r"\s", "", string)
	#remove 著 after the author's name
	string = regex.sub(r"著", "", string)
	return(string)

def getpages(soup): #get last page of volume
	if soup.find("input", {"name":"lastContentNo"}):
		lastpage = int(soup.find("input", {"name":"lastContentNo"})["value"]) #find last page automatically
	return(lastpage)

def getjpgs(fulltitle, page, lastpage, book_id, scale, waittime, downloadlimit): #download book as jpgs
	while page <= lastpage:
		for i in range(0, downloadlimit):
			if page < 10:
				#filename = u"{0}_000{1}.jpg".format(fulltitle, page) #full filename
				filename = "000{}.jpg".format(page) #page number only
			elif page < 100:
				#filename = u"{0}_00{1}.jpg".format(fulltitle, page) #full filename
				filename = "00{}.jpg".format(page) #page number only
			else:
				#filename = u"{0}_0{1}.jpg".format(fulltitle, page) #full filename
				filename = "0{}.jpg".format(page) #page number only
			print(u"Now downloading page {0} of {1} of {2}.".format(page, lastpage, fulltitle))
			#print(u"Now downloading page {0} of {1}.".format(page, lastpage)) #for ascii Windows console
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
		time.sleep(waittime) #wait designated time in order to not overburden server (DO NOT REMOVE!!!)

def getpdfs(fulltitle, page, lastpage, book_id, scale, waittime, downloadlimit): #download book as pdfs
	filenames = []
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
		#print(u"Now downloading pages {0} to {1} of {2}.".format(page, lastpdfpage, lastpage)) #for ascii Windows console
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

def estimate(book_ids, title, fulltitle, firstpage, lastpage, waittime, downloadmode, downloadlimit, multi_vol): #estimate time to download:
	totalpages = lastpage - firstpage + 1
	print("Number of pages in {0} = {1}".format(fulltitle, lastpage))
	if multi_vol == "2":
		book_id = book_ids[0] + 1
		while True:
			next_url = "http://dl.ndl.go.jp/info:ndljp/pid/{}".format(book_id)
			next_soup = BeautifulSoup(requests.get(next_url).text)
			next_title, next_volume, next_fulltitle = gettitle(next_soup)
			if title != next_title: break
			else:
				book_ids.append(book_id)
				next_lastpage = getpages(next_soup)
				print("Number of pages in {0} = {1}".format(next_fulltitle, next_lastpage))
				#print(u"Number of pages = {0}".format(next_lastpage)) #for shitty Windows console
				totalpages += next_lastpage
				book_id += 1
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
	print(u"\nTotal number of volumes = {0}".format(len(book_ids)))
	print(u"Total number of pages = {0}.".format(totalpages))
	print(u"Total time to download = {0}\nContinue with download?\n(y/n):".format(totaltime))
	while True:
		choice = input()
		if choice == "y" or choice == "Y" or choice == "yes" or choice == "YES":
			return True
		elif choice == "n" or choice == "N" or choice == "no" or choice == "NO":
			return False
		else: print(u"Invalid input! Input yes or no.")

if __name__ == "__main__":
	main()
