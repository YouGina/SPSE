from bs4 import BeautifulSoup
import urllib
import urlparse
import os
import sys
import Queue
import threading
#~ from __future__ import print_function

image_list = []
path = "images/"

download_counter = 0

class DownloadFiles(threading.Thread):
	def __init__(self, queue, count):
		threading.Thread.__init__(self)
		self.queue = queue
		self.count = count
		print "Downloader thread #%d started" %count
		
	def run(self):
		global path, download_counter
		total_files = 0
		while True:
			try:
				file = self.queue.get(timeout=1)
			except Queue.Empty:
				print "[+] Downloader #%d finished. Downloaded %d files..." % (self.count, total_files)
				return
			urllib.urlretrieve(file, os.path.join(path, file.split("/")[-1]))
			
			download_counter+=1
			sys.stdout.write("\rDownloaded file: %d" %download_counter)
			self.queue.task_done()
			total_files += 1

def main(url):
	global image_list
	httpResponse = urllib.urlopen(url)
	html = httpResponse.read()

	bs = BeautifulSoup(html)
	parsed = list(urlparse.urlparse(url))
	count = 0
	for link in bs.findAll("a"):
		if count == 0 or link["href"] == url:
			count = 1
			continue
		filename = link["href"].split("/")[-1]
		parsed[3] = link["href"]
		
	
		if ".jpg" in link["href"]:
			#~ print "[+] appending url to image: %s%s" % (url, parsed[3])
			#urllib.urlretrieve(urlparse.urlunparse(parsed).replace(";", ""), outpath)
			image_list.append(urlparse.urlunparse(parsed).replace(";", ""))
		else:
			if "." not in parsed[3] and parsed[3] != "/":
				#print parsed[3]
				main(urlparse.urlunparse(parsed).replace(";", ""))


def _usage():
	print "usage: python download.py http://example.com [outpath]"

url = sys.argv[-1]

if not url.lower().startswith("http"):
	
		path = sys.argv[-1]
		try: 
			url = sys.argv[-2]
		except:
			_usage()
			sys.exit(-1)
		if not url.lower().startswith("http"):
			_usage()
			sys.exit(-1)
				
print "[+] Start fetching webpage"
main(url)

queue = Queue.Queue()

threads = []

for i in range(1, 10):
	print "Creating DownloadThread: %d"%i
	worker = DownloadFiles(queue, i)
	worker.setDaemon(True)
	worker.start()
	threads.append(worker)


for thread in image_list:
	queue.put(thread)

queue.join()

for item in threads: 
	item.join()
	
print "Downloads complete!"

		