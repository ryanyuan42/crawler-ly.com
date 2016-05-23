#!/usr/bin/python
# Coder : Tianshu Yuan
# Date  : May 17, 2016

import requests
import re
import json
import sys

LOYAL_CRUISE_ID = {'海洋量子号':162, '海洋赞礼号':313, '海洋航行者号':46, '海洋水手号':44, '海洋神话号': 30, '全部':0}
GSD_CRUISE_ID = {'全部':0, '赛琳娜号':123, '大西洋号': 95, '维多利亚号':10, '幸运号':130, '旅行者号' : 287}

COMPANY_ID = {'皇家加勒比游轮': [LOYAL_CRUISE_ID, {'company_id': 2}],
			  '歌诗达邮轮': [GSD_CRUISE_ID, {'company_id': 3}]}


def get_lineMsg(pageNum, companyid = 2, cruiseid = 0):
	source_url = 'http://www.ly.com/youlun/AjaxcallTravel.aspx?Type=GetYoulunPage3&producttypeid=0&hxid=3&hxcid=0&companyid=' + str(companyid) + '&cruiseid=' + str(cruiseid) + '&harbourid=0&dateid=0&sortManyiType=0&sortPriceType=0&sortCmCountType=0&sortSailDateType=0&dayNum=0&themeId=0&pctabid=&tagNum=0&isTCSpecialLine=0&holidayId=0&dest=&pageNum=' + str(pageNum) + '&iid=0.07044001940118316'
	response = s.get(source_url, verify = r'C:\\Python35\\lib\\site-packages\\requests\\cacert.pem')
	content = response.content.decode('utf-8')
	lineMsg = json.loads(content)['LineMessageMod']

	CruiseName  = []
	ShipName = []
	CompanyName = []
	Route = []
	City = []
	Nights = []
	SailDate = []
	Price = []
	Rooms = []

	for details in lineMsg:
		CruiseName.append(details['CruiseName'])
		ShipName.append(re.findall(re.compile(r'-(.*?)】'), lineMsg[0]['MainTitle'])[0])
		CompanyName.append(re.findall(re.compile(r'^【(.*?)-'), lineMsg[0]['MainTitle'])[0])

		# info for how many nights staying
		info = re.findall(re.compile(r'】([\u3400-\u9FFF]+)(-)(.*?)(\s+)(.*)'), lineMsg[0]['MainTitle'])[0]
		city, route, nights = info[0], info[2], info[4]

		Route.append(route)
		City.append(city)
		Nights.append(nights)

		# acquiring cabins type
		sail_date = details['SailDateListModel']['SailDateList'][0]
		line_id = details['LineId']

		cabin_type_url ='http://www.ly.com/youlun/CruiseTours/CruiseToursAjax_book.aspx?Type=GetToursLineMessge&lineid=' + line_id + '&date=' + sail_date
		cabin_page = json.loads(s.get(cabin_type_url, verify = r'C:\\Python35\\lib\\site-packages\\requests\\cacert.pem').content.decode('utf-8'))
		cabin_info = cabin_page['CabinInfo']
		print(cabin_info)
		for cabin in cabin_info:
			if cabin['CruiseCabinName'] == '阳台房':
				room_info = cabin['RoomTypeInfo']
				rooms = [room['PriceName'] for room in room_info]
				price = [room['FrontShowPrice'] for room in room_info]
			else:
				rooms = []
				price = []
		SailDate.append(sail_date)
		Price.append(price)
		Rooms.append(rooms)

	Info = {}
	Info['CruiseName'] = CruiseName
	Info['ShipName'] = ShipName
	Info['CompanyName'] = CompanyName
	Info['Route'] = Route
	Info['City'] = City
	Info['Nights'] = Nights
	Info['SailDate'] = SailDate
	Info['Price'] = Price
	Info['Rooms'] = Rooms

	return Info

def run():
	# UI
	page = 1
	filename = input('请输入你想保存数据的文件名（example: xxx.csv）: ')
	sample = open(filename, 'w')

	data = 0
	# Uncomment the above when you know the company id
	company_name = input('请输入要抓取公司名: ')
	cruise_id = input('请输入要抓取的航线名字: ')
	amount_of_pages = int(input('请输入要抓取的页数: '))

	while page <= amount_of_pages:
		print('正在访问网站...')
		try:
			Info = get_lineMsg(page, companyid = COMPANY_ID[company_name][1]['company_id'], cruiseid = COMPANY_ID[company_name][0][cruise_id])
		except Exception as e:
			input('无法找到你查询的航线...')
			raise e
			break

		length = len(Info['City'])
		i = 0

		# warning: not really efficient
		# warning: strcture required O(n^2) time
		# suggestion: algorithm or structure change needed

		while i < length:
			msg = []
			msg_ = []
			for v in Info.values():
				if type(v[i]) is list:
					msg_.append(str(info) for info in v[i])
				else:
					msg.append(v[i])
			first = ','.join(msg)

			for rest in zip(msg_[0], msg_[1]):
				sample.write(first + ',' + ','.join(rest))
				sample.write('\n')
				data += 1
				print('已抓取{0}条数据'.format(data))
			i += 1
		page += 1

	sample.close()

if __name__ == '__main__':
	s = requests.session()
	run()
