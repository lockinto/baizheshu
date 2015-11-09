#-*-coding:utf8-*-
from lxml import etree
from multiprocessing.dummy import Pool as ThreadPool
import requests
import json
import sys
import re

reload(sys)

sys.setdefaultencoding('utf-8')

def nextpage(url):
	selector=selector_gen(url)
	name=selector.xpath('//*[@id="pagnNextLink"]/@href')
	if (name):
		url='http://www.amazon.cn%s'%(name[0])
	else:
		return 0
	return url

def requesthtml(url):
	try:
		html=requests.get(url)
		while (html.status_code != 200):
			print "request fail."
			html=requests.get(url)
		else:
			return html
	except requests.exceptions.RequestException,ex:
		print ex
		return 0


def selector_gen(url):
	html=requesthtml(url)
	if (html == 0):
		return 0
	selector=etree.HTML(html.text)
	return selector

def getinfo(fileobj,index):
	while(1):
		line=fileobj.readline()
		line=line.replace('\n','')
		if (line == ('%s'%(index))):
			name=fileobj.readline()
			name=name.replace('\n','')
			url=fileobj.readline()
			url=url.replace('\n','')
			url=url.replace('URL=','')
			return [name,url]
			break

def getbooks(fileobj,index,name,url):
	fileobj.write ('#分类编号:%d\n'%(index))
	fileobj.write ('#分类:%s\n'%(name))
	selector=selector_gen(url)
	while(selector==0):
		print "Exception error! Try again."
		selector=selector_gen(url)
	booknum=0
	while(1):
		
		bookurl_prev=selector.xpath('//*[@id="result_%d"]/div/div/div/div[2]/div[1]/a/@href'%(booknum))
		if (bookurl_prev):
			bookurl='%s'%(bookurl_prev[0])
		else:
			break
		img_prev=selector.xpath('//*[@id="result_%d"]/div/div/div/div[1]/div/div/a/img/@src'%(booknum))
		if (img_prev):
			img=('%s')%(img_prev[0])
		else:
			img=''
		bookhtml=requesthtml(bookurl)
		while(bookhtml==0):
			print "Exception error! Try again."
			bookhtml=requesthtml(bookurl)
		bookselector=etree.HTML(bookhtml.text)
		#bookname
		bookname_prev=bookselector.xpath('//*[@id="productTitle"]/text()')
		bookname=''
		if (bookname_prev):
			kindel=0
		else:
			bookname_prev=bookselector.xpath('//*[@id="btAsinTitle"]/span/text()')
			kindel=1
		if (bookname_prev):
			bookname='%s'%(bookname_prev[0])
		bookname=bookname.replace(' ','')
		bookname=bookname.replace('\n','')
		fileobj.write('$书名：%s\n'%(bookname))
		print ('书名：%s'%(bookname))
		if (kindel==1):
			author_prev=bookselector.xpath('//*[@id="divsinglecolumnminwidth"]/div[3]/span/a[1]/text()')
			if (author_prev):
				author_prev=bookselector.xpath('//*[@id="divsinglecolumnminwidth"]/div[3]/span/a/text()')
		else:
			author_prev=bookselector.xpath('//*[@id="byline"]/span[1]/a/text()')
			if (author_prev):
				author_prev=bookselector.xpath('//*[@id="byline"]/span/a/text()')
		if (author_prev):
			author=('%s'%(author_prev[0]))
		else:
			author=''
		author=author.replace(' ','')
		author=author.replace('\n','')
		fileobj.write('$作者：%s\n'%(author))
		#add pic
		fileobj.write('$PICURL=：%s\n'%(img))
		#add hot
		fileobj.write('$人气：%d\n'%(booknum+1))
		#other infomation
		content1=re.findall('<td class="bucket">(.*)SalesRank',bookhtml.text,re.S)
		if(content1):
			content2=re.findall('<li>(.*?)</li>',('%s'%(content1[0])),re.S)
		i=0
		while(content2):
			result=('%s')%(content2[i])
			result=result.replace(' ','')
			result=result.replace('\n','')
			result=result.replace('<b>','')
			result=result.replace('</b>','')
			if 'href' in result:
				i=i+1
				continue
			fileobj.write('$%s\n'%(result))
			if 'ASIN' in result:
				break
			else:
				i=i+1
		#add bookend
		fileobj.write('%\n')
		if ((booknum+1)%16==0):
			url=nextpage(url)

		if (url==0):
			break
		else:
			selector=selector_gen(url)
		#booknum++
		print '已经成功抓取第%d分类的第%d本书。。。'%(index,booknum+1)
		booknum=booknum+1




if __name__ == '__main__':
	#from 1 to 562
	begin=1
	end=110
	index=0
	name=''
	url=''
	catalog=open('catalog.txt','r')
	for index in range(begin,end+1):
		result=getinfo(catalog,index)
		name=result[0]
		url=result[1]
		bookfile=open('book%d'%(index),'w')
		getbooks(bookfile,index,name,url)
		bookfile.close()
	catalog.close()