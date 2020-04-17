#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author lixingmeng
# @date 2019-06-11
# @version V1.0.0
# @description 登录飞机票查验网站
import pymysql
import random
import time
import json
import configparser

config = configparser.ConfigParser()
config.read("../Configs/config.ini", encoding="utf-8")

def get_uuid():
    t = time.time()
    fileName = str(round(t))
    uuid = random.sample('abcdefghijlmnopqrstuvwxyz', 3)
    tmp_file_name = fileName.join(uuid)
    return tmp_file_name

#获取数据库连链接
def get_mysql_conn(ip,user_name,passwd,data_base):
    # 打开数据库连接
    db = pymysql.connect(ip, user_name,passwd ,data_base )

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    #返回游标地址
    return cursor


def insert_db(dic):
    # 打开数据库连接
   # print(dic['name'])
    db = pymysql.connect(
        host=config.get('mysql.conf','mysqlUrl'),
        port=3306,
        user=config.get('mysql.conf', 'mysqlUserName'),
        passwd=config.get('mysql.conf', 'mysqlPassWd'),
        db=config.get('mysql.conf', 'mysqlDataBase'),
        charset="utf8")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    uuid = get_uuid()
    sql_info = "INSERT INTO air_check.air_invoice_info(uuid,passenger_name,serial_number,id_no,fare,caac_development_fund," \
          "fuel_surcharge,total,e_ticket_no,ck,infomation,insurance,agent_code,issude_by,date_of_issue) VALUES ('{}','{}'," \
          "'{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(uuid),dic['passengerName'],dic['serialNumber'],
          dic['idNo'],dic['fare'],dic['caacDevelopmentFund'],dic['fuelSurcharge'],dic['total'],dic['eTicketNo'],dic['ck'],dic['infomation'],dic['insurance'],dic['agentCode'],dic['issudeBy'],dic['dateOfIssue'])

    #获取飞机票明细数据
    sql_detail = None
    flights = dic['flights']
    for i in range(len(flights)):
        dic = flights[i]
        sql_detail = sql_detail + \
          "INSERT INTO air_check.air_invoice_detail(uuid,info_id,flight_from,flight_to,flight,class,date,carrier,time,fare_basis,allow)" \
                     "VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(str(get_uuid()), str(uuid),
                                                                                             dic['from'], dic['to'],
                                                                                             dic['flight'],
                                                                                             dic['class'], dic['date'],
                                                                                             dic['carrier'],
                                                                                             dic['time'],
                                                                                             dic['fareBasis'],
                                                                                             dic['allow']) +";"

    # sql = "INSERT INTO air_check.air_invoice(uuid,name,serial_no,identity_card,carbon,start_city,end_city,carrier,flight,seat_class,date,fare_basis,allow,fare,caac_development_fund,fuel_surcharge,other_tax,total,e_ticket_no,ck,infomation,insurance,agent_code,issued_by,date_of_issue,is_check)" \
    #       " VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(get_uuid(),dic['name'],dic['serial_no'],dic['identity_card'],dic['carbon'],dic['start_city'],dic['end_city'],dic['carrier'],dic['flight'],dic['seat_class'],dic['date'],dic['fare_basis'],dic['allow']
    #  ,dic['fare'],dic['caac_development_fund'],dic['fuel_surcharge'],dic['other_tax'],dic['total'],dic['e_ticket_no'],dic['ck'],dic['infomation'],dic['insurance'],dic['agent_code'],dic['issued_by'],dic['date_of_issue'],dic['is_check'])
    #print('执行插入sql***'+sql)

    try:
        # 执行sql语句
        cursor.execute(sql_info)

        cursor.execute(sql_detail)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        print(e)
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()


def query_invoice(e_ticket_no,air_name):
    # 打开数据库连接
    db = pymysql.connect(
        host=config.get('mysql.conf','mysqlUrl'),
        port=3306,
        user=config.get('mysql.conf', 'mysqlUserName'),
        passwd=config.get('mysql.conf', 'mysqlPassWd'),
        db=config.get('mysql.conf', 'mysqlDataBase'),
        charset='utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # SQL 查询语句
    # sql = "SELECT * FROM EMPLOYEE \
    #        WHERE INCOME > '%d'" % (1000)
    sql = "SELECT * FROM air_invoice_info WHERE passenger_name= '%s' AND e_ticket_no= '%s'" % (air_name,e_ticket_no)
    print('执行查询sql***'+sql)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchone()
        if results != None:
            #有结果
            sql_detail = "SELECT * FROM air_invoice_detail WHERE info_id= '%s'" % (results['uuid'])
            cursor.execute(sql_detail)
            details = cursor.fetchall()
            detail = details[0]
            list = []
            detail.pop('uuid')
            detail.pop('info_id')
            detail['from'] = detail.pop('flight_from')
            detail['to'] = detail.pop('flight_to')
            #detail['fareBasis'] = detail.pop('fare_basis')
            results.pop('uuid')
            info = formatter(str(detail), '_')
            list.append(eval(info))
            res = {}
            return_state_info = {}
            return_state_info['returnCode'] = '8888'
            return_state_info['returnMessage'] = '查验成功'
            res['returnStateInfo'] = return_state_info
            #flights = {}
            results['flights'] = list
            #info['flights'] = flights
            res['data'] = eval(formatter(str(results), '_'))
            return str(res)
        return None
    except Exception as e:
        print(e)
        print("Error: unable to fetch data")
    # 关闭数据库连接
    db.close()
def convert(one_string,space_character):    #one_string:输入的字符串；space_character:字符串的间隔符，以其做为分隔标志
    string_list = str(one_string).split(space_character)    #将字符串转化为list
    first = string_list[0].lower()
    others = string_list[1:]
    others_capital = [word.capitalize() for word in others]      #str.capitalize():将字符串的首字母转化为大写
    others_capital[0:0] = [first]
    hump_string = ''.join(others_capital)     #将list组合成为字符串，中间无连接符。
    return hump_string
def formatter(src: str, firstUpper: bool = True):
    """
    将下划线分隔的名字,转换为驼峰模式
    :param src:
    :param firstUpper: 转换后的首字母是否指定大写(如
    :return:
    """
    arr = src.split('_')
    res = ''
    for i in arr:
        res = res + i[0].upper() + i[1:]

    if not firstUpper:
        res = res[0].lower() + res[1:]
    return res


if __name__ == '__main__':

   a = query_invoice('****','*(***')
   print(a)
