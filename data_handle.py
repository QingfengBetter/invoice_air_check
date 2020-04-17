#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# @Time : 2019/9/26 17:46
# @Author : bad_bad_boy
# @File : xintianyou.py
# @Software: PyCharm
import base64
import requests
from datetime import datetime
import urllib
import json
from get_child_image import get_child_pic
from lxml import etree
from util import random_code
from get_ip_port import get_proxy_ip
import re
import configparser
import os
config = configparser.ConfigParser()
config.read("../Configs/config.ini", encoding="utf-8")
def org_response(air_name,eticketNo):
    headers_sky= {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'no-cache',
    'Connection':'keep-alive',
    'Host':'www.travelsky.com',
    'Pragma':'no-cache',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    headers_cnzz = {
    'Accept':'image/webp,image/*,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'no-cache',
    'Connection':'keep-alive',
    'Host':'z11.cnzz.com',
    'Pragma':'no-cache',
    'Referer':'http://www.travelsky.com/tsky/validate.jsp',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
    }

    try:
        session = requests.session()
        #headers = str2obj(header, '\n', ': ')
        #同意会话处理请求
        print(headers_sky)
        resp_sky = session.get('http://www.travelsky.com/tsky/validate.jsp',headers = headers_sky )
        #resp_cnzz = session.get('http://z11.cnzz.com/stat.htm?id=1256052643&r=&lg=zh-cn&ntime=1571033723&cnzz_eid=1113947971-1569544814-&showp=1280x720&p=http://www.travelsky.com/tsky/validate.jsp&t=信天游 - 电子客票验真官网 航空公司官网机票价格总汇&umuuid=16d705c11f240d-0baf3841917e3d-4d045769-e1000-16d705c11f326c&h=1&rnd=15403298',headers = headers_sky)
        resp_cnzz  = session.get('http://z11.cnzz.com/stat.htm?id=1256052643&r=http://www.travelsky.com/tsky/validate&lg=zh-cn&ntime=1571033723&cnzz_eid=387322806-1570779741-http://www.travelsky.com/&showp=1280x720&p=http://www.travelsky.com/tsky/validate&t=%E4%BF%A1%E5%A4%A9%E6%B8%B8%20-%20%E7%94%B5%E5%AD%90%E5%AE%A2%E7%A5%A8%E9%AA%8C%E7%9C%9F%E5%AE%98%E7%BD%91%20%E8%88%AA%E7%A9%BA%E5%85%AC%E5%8F%B8%E5%AE%98%E7%BD%91%E6%9C%BA%E7%A5%A8%E4%BB%B7%E6%A0%BC%E6%80%BB%E6%B1%87&umuuid=16db9ee595620d-01e4a3f10f44-67e1b3f-e1000-16db9ee5957e9&h=1&rnd=135804725')
        print(resp_sky.headers['Set-Cookie'])
        GMT_FORMAT = '%a %d %b %Y %H:%M:%S GMT 0800 '
        url = 'http://www.travelsky.com/tsky/servlet/CallYanServlet?title=nohome&now='
        now = datetime.now().strftime(GMT_FORMAT)
        data = urllib.parse.quote(now+'(中国标准时间)')
        headers_sky['Cookie'] = resp_sky.headers['Set-Cookie']+' UM_distinctid=16d705c11f240d-0baf3841917e3d-4d045769-e1000-16d705c11f326c; CNZZDATA1256052643=1113947971-1569544814-%7C1569544814; '
        print(headers_sky['Cookie'] )
        resp = session.get(url+data,headers = headers_sky)
        imgdata = base64.b64decode(base64.b64encode(resp.content))

        # 获取随机数
        name = random_code()
        file = open('./img/'+name+'.gif','wb')
        file.write(imgdata)
        file.close()
        #识别处理后的图像
        get_child_pic(name)
        #handle_img(name)
        base64_data = '';
        with open('./img/'+name+'.png',"rb") as f:#转为二进制格式
            base64_data = base64.b64encode(f.read())#使用base64进行加密
           # print(base64_data)
        #删除对应文件
        os.remove('./img/'+name+'.gif')
        os.remove('./img/'+name+'.png')
        dict = {}
        dict["image"] = base64_data.decode('utf-8')
        #print(dict)
       # resp = requests.session().post('http://223.71.97.12:19000/captcha/v1',json=dict)
        resp = requests.session().post('http://127.0.0.1:19952/captcha/v1', json=dict,)
        #print(resp.content)
        resp = json.loads(resp.content)
        print(headers_sky)
        print(resp['message'])
        headers_sky['Referer'] = 'http://www.travelsky.com/tsky/validate'
        data = {'validateFlag': 0,
                'eticketNo': eticketNo,
                'invoiceNo': '',
                'imgSrc': '/tsky/images/loading.gif',
                'eticketNoORIn': eticketNo,
                'passengerName_src':air_name,
                'passengerName': urllib.parse.quote(air_name),
                'randCode': resp['message']
                }
        res = session.post('http://www.travelsky.com/tsky/validate', params=data, headers=headers_sky)
        print(res.text)
        content = etree.HTML(res.text)
        #获取print的值
        js = content.xpath('normalize-space(//script[@type="text/javascript"]/text())')
        print(content.xpath('//*[@id="validateForm"]/div[4]/div[2]/span/text()'))
        res = js.strip()
        str = re.sub("[A-Za-z0-9(){}= ''.#_:/""\!\%\[\]\,\。]", "", res)
        error = str.split(";")[0]
        print(error)
        if error != 'null' and error!= '':
            res = {}
            return_state_info = {}
            return_state_info['returnCode'] = '7777'
            return_state_info['returnMessage'] = error
            res['returnStateInfo'] = return_state_info
            return res
        error_web = content.xpath('normalize-space(//*[@id="content"]/div/text())')

        if error_web != 'null' and error_web != '':
            res = {}
            return_state_info = {}
            return_state_info['returnCode'] = '6666'
            return_state_info['returnMessage'] = error_web
            res['returnStateInfo'] = return_state_info
            return res
        name_error = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[2]/li/span[1]/text())').strip()
        if name_error == '输入姓名不正确':
            res = {}
            return_state_info = {}
            return_state_info['returnCode'] = '5555'
            return_state_info['returnMessage'] = error_web
            res['returnStateInfo'] = return_state_info
        #error
        print(content.xpath('normalize-space//*[@id="validateForm"]/div[4]/div[2]/span[1]/text()'))
    except Exception as e:
       print(e)
       res = {}
       return_state_info = {}
       return_state_info['returnCode'] = '9999'
       return_state_info['returnMessage'] = '处理失败'
       res['returnStateInfo'] = return_state_info
       return res
    #组织结构信息
    # 组织返回报文
    res = {}
    return_state_info = {}
    return_state_info['returnCode'] = '8888'
    return_state_info['returnMessage'] = '查验成功'
    res['returnStateInfo'] = return_state_info
    dic = {}
    flights = {}
    list = []
    #error_text = content.xpath('//*[@id="validateForm"]/div[4]/div[2]/span/text()')
    # if(error_text!=''):
    #     res = {}
    #     return_state_info = {}
    #     return_state_info['returnCode'] = '9999'
    #     return_state_info['returnMessage'] = '处理失败!'+str(error_text)
    #     res['returnStateInfo'] = return_state_info
    #     return res
    try:
        dic['passengerName'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[2]/li/span[1]/text())').strip()
        serialNo = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[1]/li/div/span[2]/text())').strip()
        dic['serialNumber'] = re.findall("\d+", serialNo)[0] + re.findall("\d+", serialNo)[1].strip()
        dic['idNo'] = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[2]/li/span[2]/text())').strip()
        fare = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[3]/li/span[1]/text())').strip()
        fare = re.search('\d+\.\d+', fare).group()
        dic['fare'] = fare
        caacDevelopmentFund = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[3]/li/span[2]/text())').strip()
        dic['caacDevelopmentFund'] = re.search('\d+\.\d+', caacDevelopmentFund).group()
        # useState = content.xpath('//div[@class="coln coln-fourth coln-green status_1"]/text()')[0]
        useState = content.xpath('normalize-space(//*[@id="content"]/div[2]/div[2]/div[1])').split(' ')
        dic['useState'] = useState[len(useState) - 1]
        fuelSurcharge = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[3]/li/span[3]/text())').strip()
        dic['fuelSurcharge'] = re.search('\d+\.\d+', fuelSurcharge).group()
        otherTaxes = content.xpath('//*[@id="popup_detail"]/div[1]/ul[3]/li/span[4]/text()')[0].strip()
        dic['otherTaxes'] = re.search('\d+\.\d+', otherTaxes).group()
        total = content.xpath('//*[@id="popup_detail"]/div[1]/ul[3]/li/span[5]/text()')[0].strip()
        dic['total'] = re.search('\d+\.\d+', total).group()  # total
        dic['eTicketNo'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[4]/li/span[1]/text())').strip()
        dic['ck'] = content.xpath('normalize-space(//*[@id="popup_detail"]/div[1]/ul[4]/li/span[2]/text())').strip()
        dic['infomation'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[4]/li/span[3]/text())').strip()
        dic['insurance'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[4]/li/span[4]/text())').strip()
        dic['agentCode'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[5]/li/span[1]/text())').strip()
        dic['issudeBy'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[5]/li/span[2]/text())').strip()
        dic['dateOfIssue'] = content.xpath(
            'normalize-space(//*[@id="popup_detail"]/div[1]/ul[5]/li/span[3]/text())').strip()
        trs = content.xpath('normalize-space(//*[@id="content"]/div[2]/div[2]/div[1])').split(' ')
        for index in range(len(trs) // 5):
            flights = {}
            flights['from'] = content.xpath('normalize-space(//*[@id="from"])').split(' ')[index].strip()
            flights['to'] = content.xpath('normalize-space(//*[@id="from"])').split(' ')[index + 1].strip()
            flights['flight'] = content.xpath('normalize-space(//*[@id="flight_no"])').split(' ')[2 * index].strip() \
                                + content.xpath('normalize-space(//*[@id="flight_no"])').split(' ')[2 * index + 1].strip()
            flights['class'] = content.xpath('normalize-space(//*[@id="class"])').split(' ')[index].strip()
            flights['date'] = content.xpath('normalize-space(//*[@id="date"])').split(' ')[index].strip()
            flights['carrier'] = content.xpath('normalize-space(//*[@id="flight"])').split(' ')[index].strip()
            flights['time'] = content.xpath('normalize-space(//*[@id="time"])').split(' ')[index].strip()
            flights['fareBasis'] = content.xpath('normalize-space(//*[@id="fare_basts"])').split(' ')[index].strip()
            flights['allow'] = content.xpath('normalize-space(//*[@id="allow"])').split(' ')[index].strip()
            flights['useState'] = trs[len(trs) * (index + 1) - 1]
            list.append(flights)
        dic['flights'] = list
        res['data'] = dic
        return res
    except Exception as e:
       print(e)
       res = {}
       return_state_info = {}
       return_state_info['returnCode'] = '9999'
       return_state_info['returnMessage'] = '处理失败'
       res['returnStateInfo'] = return_state_info
       return res
# s = requests.session()
# data = urllib.parse.quote(now+'(中国标准时间)')
#
# resp = session.get(url+data,headers =  str2obj(resp.headers, '\n', ': '))
#
# print(resp.headers)
