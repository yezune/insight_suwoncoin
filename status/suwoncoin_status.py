#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#// block 

#http://insight.suwoncoin.org:3000/api/blocks?blockDate=2015-01-20&startTimestamp=1422944374&limit=200
#response.read()

import json, urllib2, sys, datetime



BLOCKS_API = "http://insight.suwoncoin.org:3000/api/blocks"
BLOCK_API = "http://insight.suwoncoin.org:3000/api/block/"
TX_API = "http://insight.suwoncoin.org:3000/api/tx/"

def GetBlocks(date=None, startTimestamp=None, limit=200):
	params =  u"?limit=%d" % limit

	if date:
		params = params + u"&blockDate=%s" % date

	if startTimestamp:
		params = params +  u"&startTimestamp=%s" % startTimestamp
	
	response = urllib2.urlopen(BLOCKS_API+params)

	return  json.loads( response.read() )

def GetBlock(blockHash):
	response = urllib2.urlopen(BLOCK_API+blockHash)

	return  json.loads( response.read() )

def GetTx(txId):
	query = TX_API+txId
	#print query
	response = urllib2.urlopen(query)

	return  json.loads( response.read() )



# response = urllib2.urlopen(BLOCKS_API)

# data = json.loads( response.read() )

#data = GetBlocks()
	
#print data['length']

#pagination = data['pagination']

# print data['pagination']
# print data['pagination']['next']
# print data['pagination']['prev']
# print data['pagination']['current']
# print data['pagination']['currentTs']
# print data['pagination']['isToday']
# print data['pagination']['more']
# print data['pagination']['moreTs']

# for block in data['blocks']:
# 	print block

def dateFromYYYY_MM_DD(yyyy_mm_dd): # "format yyyy-mm-dd"
	yyyy,mm,dd = yyyy_mm_dd.split('-')
	return datetime.date(int(yyyy),int(mm),int(dd))		

def nextDay(someday):
	return someday + datetime.timedelta(days=1)

def GetTransaction(startDate, lastDate):

	trans = []

	blockDate = startDate
	moreTs = None
	pagination = {'next':'0000-00-00'}
	firstTime = True;
	count = 0
	tot = 0.0

	currentDay = dateFromYYYY_MM_DD(startDate)
	endDate = dateFromYYYY_MM_DD(lastDate)
	
	while currentDay < endDate:
		data = {}

		if firstTime:
			data = GetBlocks(blockDate)
			#print "# current %s" % data['pagination']['current']
			firstTime = False
		else:
			data = GetBlocks(blockDate, pagination['moreTs'])

		for block in data['blocks']:
			if block['txlength'] > 1:
				#print block['hash']
				bdata = GetBlock(block['hash'])
				txIds = bdata['tx']
				for txId in txIds:
					tx = GetTx(txId)
					if tx.has_key('isCoinBase') and tx['isCoinBase']:
						continue
					tot = tot + float(tx['vout'][0]['value'])
					count = count + 1
					#print '%s => %s + %s + fee(%f)' % (tx['vin'][0]['value'], tx['vout'][0]['value'], tx['vout'][1]['value'], tx['fees'])

		pagination = data['pagination']

		if not pagination.has_key('more'):	
			print u"%s,\t%3d,\t%10d" % (pagination['current'],count, tot)	

			trans.append((pagination['current'], count, tot,))		

			currentDay = dateFromYYYY_MM_DD(pagination['current'])
			blockDate = nextDay(currentDay).strftime("%Y-%m-%d")
			firstTime = True
			count = 0
			tot = 0

	return trans


def GetMonthlyTransaction(dailyData):
	monthlyData = []
	year, month = 0,0
	mCount, mTot = 0,0

	for day in dailyData:
		yyyy, mm, dd = day[0].split('-')
		if month != int(mm):
			
			if month != 0 : 
				monthlyData.append((year,month, mCount, mTot,))
			
			mCount, mTot = 0,0
			month = int(mm)
			year = int(yyyy)

		mCount = mCount + day[1]
		mTot = mTot + day[2]

	if month != 0 : 
		monthlyData.append((year,month, mCount, mTot,))



	return monthlyData

if __name__ == '__main__':

	startDate = '2014-09-14'
	endDate = datetime.date.today().strftime("%Y-%m-%d")
	
	if len(sys.argv) == 2:
		startDate = sys.argv[1]

	if len(sys.argv) == 3:
		startDate = sys.argv[1]
		endDate = sys.argv[2]

	print "기간: %s ~ %s" % (startDate, endDate)
	print "일단위 통계"
	
	dailyTrans = GetTransaction(startDate,endDate)
	monthlyTrans = GetMonthlyTransaction(dailyTrans)

	print "월단위 통계"
	for month in monthlyTrans:
		print "%d-%d, %d, %d" % month



