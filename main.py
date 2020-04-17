import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.escape import json_encode
from login import check_ticket
import json
from data_handle import org_response
from data_base import insert_db
from data_base import query_invoice
import os
import re
def set_default_header(self):
    # 后面的*可以换成ip地址，意为允许访问的地址
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'x-requested-with')
    self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, DELETE')
def check_eticket_name(name,ticket_no):
    if str(ticket_no).replace("-", "").isdigit() == False:
        res_err = {}
        return_state_info = {}
        return_state_info['returnCode'] = '7777'
        return_state_info['returnMessage'] = '输入的电子票号应当都为数字！'
        res_err['returnStateInfo'] = return_state_info
        return False, res_err
    if name == '':
        res_err = {}
        return_state_info = {}
        return_state_info['returnCode'] = '7777'
        return_state_info['returnMessage'] = '请输入姓名！'
        res_err['returnStateInfo'] = return_state_info
        return False, res_err
    if ticket_no == '':
        res_err = {}
        return_state_info = {}
        return_state_info['returnCode'] = '7777'
        return_state_info['returnMessage'] = '请输入电子票号或行程单号！'
        res_err['returnStateInfo'] = return_state_info
        return False, res_err
    elif len(ticket_no) == 13 or len(ticket_no) == 14 or len(ticket_no) == 11:
        if str(ticket_no).rfind("-") != -1:
            ticket_no = ticket_no.replace("-", "");
        return True, ticket_no
    else:
        res_err = {}
        return_state_info = {}
        return_state_info['returnCode'] = '7777'
        return_state_info['returnMessage'] = '票号/行程单号位数不正确！'
        res_err['returnStateInfo'] = return_state_info
        return False, res_err


class check_air(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        try:
            set_default_header(self)
            data = json.loads(self.request.body)
            ticket_no = data['eticketNo']
            name = data['passengerName']
            #检测电子客票号/姓名的正确性
            info = check_eticket_name(name,ticket_no)
            if info[0] == False:
                return self.write(json_encode(eval(str(info[1]))))
            # trt_time = data['multiTry']
            # num = 1
            # if trt_time=='true':
            #     num = 3
            # #查询数据库是否存在
            res = query_invoice(ticket_no,name)
            if res != None:
                return self.write(json_encode(eval(res)))
            for i in range(0,1):
                ret_info = org_response(name,info[1])
                #if ret_info['returnStateInfo']['returnCode'] == '8888' and ret_info['data']['useState']=='客票已使用':
                    #记录数据库
                    #insert_db(ret_info['data'])
                    #break
                #else:
                    #continue
            print('*****'+json_encode(ret_info))
            return self.write(json_encode(ret_info))
        except Exception as e:
            print(e)
            res_err = {}
            return_state_info = {}
            return_state_info['returnCode'] = '9999'
            return_state_info['returnMessage'] = '处理失败,请检查报文是否正确'
            res_err['returnStateInfo'] = return_state_info
            return self.write(json_encode(res_err))

def make_app():
    return tornado.web.Application([
        (r"/check_air/v1", check_air),
    ])

if __name__ =="__main__":
    app = make_app()
    app.listen(8888)
    print("Start Server success...")
    tornado.ioloop.IOLoop.current().start()
