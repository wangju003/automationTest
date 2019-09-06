import logging
import os
import json
import requests
import re
import urllib3
import datetime,time
#发邮件模块
import smtplib #发送邮件模块
from email.mime.text import   MIMEText #定义邮件内容
from email.mime.multipart import MIMEMultipart
from email.header import Header #定义邮件标题


from model import TestAccounts,TestCase,EnvConfig,ResponseTime
from getConnection import GetConnection

from conf import config as conf#自定义测试环境
print("当前测试host是:",conf.HOST)


session = GetConnection.session


time_str = '%Y-%m-%d %H:%M:%S'
# 初始化超时接口数据集合
num_record = []
api_purpose_record = []
request_url_record = []
run_time_record = []
res_time_record = []




#生成运行日志
##注意程序要能在Linux环境下跑通，getcwd是在win下的命令，在Linux环境获得的不是当前路径的
def createLog():
    dirname,filename = os.path.split(os.path.abspath(__file__))
    log_path = os.path.join(dirname,"log/liveapi.log")
    log_format = "[%(asctime)s][%(levelname)s] %(message)s"
    logging.basicConfig(format=log_format,filename=log_path,filemode="w",level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    return log_path

#以字典形式返回数据库中记录的uid 及 token值 {uid:token}
def getUidToken():
    uid_token = {}
    for i in session.query(TestAccounts).order_by(TestAccounts.id):
        uid_token[i.uid] = i.token

    return uid_token

def int_to_time(seconds):
    minutes,second = divmod(seconds,60)
    hour,minute= divmod(minutes,60)
    return hour,minute,second


#统计测试用例执行
def countRun(func):
    def wrapper(*args,**kwargs):
        run_data={}
        #记录当前时间  开始时间
        stime=datetime.datetime.now()
        run_data["stime"]=stime.strftime("%Y-%m-%d %H:%M:%S")
        #调用runTest()函数，通过len(errorCase) 获得 执行fail的case数量
        errorTest = func(*args,**kwargs)
        fail_case = len(errorTest)
        run_data["fail_case"]=fail_case
        #记录当前时间  结束时间
        etime=datetime.datetime.now()
        run_data["etime"]=etime.strftime("%Y-%m-%d %H:%M:%S")
        #计算时间差  所有Case的执行时间
        stime = int(time.mktime(stime.timetuple()))
        etime = int(time.mktime(etime.timetuple()))
        time_diff = etime - stime
        h,m,s= int_to_time(time_diff)

        time_diff = "%.2d时%.2d分%.2d秒"% (h, m, s)
        run_data["time_diff"]=time_diff

        # 读excel 计算全部case数，跳过case数
        testcase = session.query(TestCase).all()
        #计算全部case数
        all_case=len(testcase)
        run_data["all_case"]=all_case
        jump_case=0
        run_case = 0
        for i in testcase:
            if i.active.replace("\r","").replace("\n","") !="Yes":
                jump_case = jump_case+1
            else:
                run_case =run_case+1
        run_data["jump_case"]=jump_case
        run_data["run_case"]=run_case
        #成功case数=table.nrows-未验证case数-执行失败的case数
        pass_case = all_case - jump_case-fail_case
        run_data["pass_case"]=pass_case
        return {"errorTest":errorTest,"run_data":run_data}
    return wrapper

#执行测试用例
@countRun
def runTest(testcase):
    errorCase =[]
    correlationDict = {}
    #读取数据库中的case
    for i in testcase:
        if i.active.replace("\n", "").replace("\r", "") != "Yes":
            continue
        num = str(i.id)
        api_purpose = i.api_purpose.replace("\n", "").replace("\r", "")
        # api_host =session.query(EnvConfig).filter_by(id=1).first().host #获得全局配置的host
        request_url = i.request_url.replace("\n", "").replace("\r", "")
        request_method = i.request_method.replace("\n", "").replace("\r", "")
        request_data_type = i.request_data_type.replace("\n", "").replace("\r", "")
        request_data = i.request_data.replace("\n", "").replace("\r", "").replace("'", '"')
        check_point = i.check_point
        correlation = i.correlation.replace("\n", "").replace("\r", "").split(";")
        creater =i.creater
        project = i.project
        api_host = session.query(EnvConfig).all()
        gw_host = conf.HOST
        hw_host = api_host[1].host

        #根据不同项目，匹配不同的host
        if project == "gw":
            api_host = gw_host
        elif project == "hw":
            api_host = hw_host

            #检查correlationDict是否包含 入参中需要使用的变量,如果有,使用correlationDict中保存的值
        for keyword in correlationDict:
            if request_data.find(keyword) > 0:
                request_data = request_data.replace(keyword, str(correlationDict[keyword]))

        status,resp = interfaceTest(num,api_purpose,api_host,request_url,request_data,
                                    check_point,request_method)
        # print(resp)
        #记录响应状态不等200的接口
        if status !=200:
            if project == "hw":
                request_url = "http://" + api_host + request_url
            elif project == "gw":
                request_url = "https://" + api_host + request_url

            errorCase.append((num + " " + api_purpose, str(status), request_url, resp[:40], creater))
            continue
        #检查是否有关联参数,如果有将关联参数保存到correlationDict
        for j in range(len(correlation)):
            param = correlation[j].split("=")
            if len(param)==2:
                if param[1] == "" or not re.search(r'^\[',param[1]) or not re.search(r'\]',param[1]):
                    logging.error(num+" "+api_purpose+"关联参数设置有误，请检查[Correlation]字段参数格式是否正确！！！")
                    continue
                value = json.loads(resp)

                for key in param[1][1:-1].split("]["):
                    try:
                        temp = value[int(key)]
                    except:
                        try:
                            temp = value[key]
                        except:
                            break
                    value = temp
                correlationDict[param[0]] = value
    return errorCase

#执行接口测试
def interfaceTest(num,api_purpose,api_host,request_url,request_data,check_point,request_method):

    try:
        request_data = request_data.encode("utf-8")
        request_data = json.loads(request_data)
    except Exception as e:
        logging.error(num + ' ' + api_purpose + ' 请求的数据有误，请检查[Request Data]字段是否是标准的json格式字符串！')
        return 400, ' 请求的数据有误，请检查[Request Data]字段是否是标准的json格式字符串！'
    #使用指定账号进行测试
    headers = {}

    uid_token = getUidToken()
    idlist= ["uid","userId","userID","userid"]
    for uid in idlist:
        if uid in request_data:
            uid = request_data[uid]
            if isinstance(uid, int):
                uid = str(uid)
            if uid not in uid_token:
                logging.error(num + ' ' + api_purpose + ' 查无此uid,请去test_account表中录入测试账号信息!')
                return 400, ' 查无此uid,请去test_account表中录入测试账号信息!'
            else:
                headers["token"] = uid_token[uid]

    #匹配拼接不同项目的url地址
    if "overseas" in api_host:
        request_url = "http://" + api_host + request_url
    elif "appapi" in api_host:
        request_url = "https://" + api_host + request_url
    elif "appts" in api_host:
        request_url = "https://" + api_host + request_url

    if request_method == "POST":
        r=requests.post(request_url,request_data,headers=headers,verify=False) #是否验证服务器的SSL证书

        #此处不合理，必须优化
        run_time = datetime.datetime.now().strftime(time_str)  # 统计运行时间
        res_time = round(r.elapsed.total_seconds(), 2)  # 计算接口的响应时间,保留2位小数,傻了吧，我其实只需要一个全局变量，就是运行时间，我就可用装饰器运行这个函数了
        if res_time > 1.0:
            # 收集 response_time表数据
            num_record.append(num)
            api_purpose_record.append(api_purpose)
            request_url_record.append(request_url)
            run_time_record.append(run_time)
            res_time_record.append(res_time)

    elif request_method == "GET":
        r=requests.post(request_url,request_data,headers = headers)
    else:
        logging.error(num+" "+ api_purpose + "HTTP请求方法错误，请确认[Request Method]字段是否正确！！！")
        return 400,request_method
    status = r.status_code
    resp = r.text
    if  status == 200:
        if re.search(check_point,resp):
            logging.info(num+" "+api_purpose + "成功"+str(status) +", "+resp)
            return status,resp
        else:
            logging.error(num+" "+api_purpose+" 失败！！！,["+str(status)+"],"+resp)
            return 2001, resp
    else:
        logging.error(num+" "+api_purpose+"失败！！！,["+str(status)+"],"+resp)
        return status, resp

#查询海外 或 官网测试用例
def runProject(project_name="all"):
    if project_name == "all":
        testcase = session.query(TestCase).all()
    elif project_name == "gw":
        testcase = session.query(TestCase).filter_by(project = "gw").all()
    elif project_name == "hw":
        testcase = session.query(TestCase).filter_by(project = "hw").all()

    return testcase


#发送通知邮件
def sendMail(text,mail_to,testCase):
    smtpserver = "smtp.126.com"
    user = "wangju003@126.com"
    mail_pass = "123456q"
    sender = "wangju003@126.com"
    # receive = "wangju003@126.com"

    msg = MIMEMultipart()
    subject = "[AutomationTest]接口自动化测试报告通知"
    msg["subject"] = Header(subject, "utf-8")
    # msg["From"] = "on-line@5i5j.com"
    msg["From"] = "wangju003@126.com"
    msg["To"] = ",".join(mail_to)

    msg.attach(MIMEText(text,"html","utf-8"))

    #构造日志附件
    log_attach = MIMEText(open(createLog(),"rb").read(),"base64","utf-8")
    log_attach["Content-Type"] = 'application/octet-stream'
    log_attach["Content-Disposition"]="attachment;filename=liveapi.log"
    msg.attach(log_attach)

    #构造测试用例附件
    case_attach = MIMEText(open(testCase,"rb").read(),"base64","utf-8")
    case_attach ["Content-Type"] ='application/octet-stream'
    case_attach["Content-Disposition"]='attachment; filename="TestCase.xlsx"'
    msg.attach(case_attach)

    smtp = smtplib.SMTP_SSL(smtpserver, 465)

    smtp.helo(smtpserver)
    smtp.ehlo(smtpserver)
    smtp.login(user, mail_pass)

    try:
        print("Start send Email....")
        smtp.sendmail(sender, msg["To"].split(","), msg.as_string())
        print("Send Email end!")
    except smtplib.SMTPException:
        print("Error: Email send fail!")
    finally:
        smtp.quit()

# 这样写是不合理的，后期要改
 # 组装接口时间数据
def tempInsertDB():
    data = {}
    data["num"] = num_record
    data["api_purpose"] = api_purpose_record
    data["request_url"] = request_url_record
    data["run_time"] = run_time_record
    data["res_time"] = res_time_record

    # 插入数据 data->table
    from crubDB import insertDB
     # 插入数据
    insertDB("response_time", data)


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    file_path = os.path.join(os.path.abspath("."), "db.ini")
    session = GetConnection.session

    # testcase = session.query(TestCase).filter_by(project="gw").all()[:2]
    testcase = session.query(TestCase).filter_by(id=4185)
    print(testcase)
    res = runTest(testcase)
    print(res)

