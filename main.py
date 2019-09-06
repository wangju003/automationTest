# -*- coding: UTF-8 -*-
import urllib3
from getConnection import GetConnection #连接数据库

from common import runTest,sendMail,runProject,tempInsertDB

from  exportExcel import exportExcel
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 将数据库中的case文件生成excel文件，并保存到当前文件夹
case_path=exportExcel()
#测试发邮件
session = GetConnection.session
testcase = runProject("gw")
print("开始执行测试用例")
result = runTest(testcase)
print("测试用例执行完成")
tempInsertDB()#将接口超时数据插入数据库
errorTest = result["errorTest"]
# 运行海外＋官网case；支持官网联调环境执行case

errorTest.sort()
run_data = result["run_data"]
# if len(errorTest)>0:  失败时才发送邮件
html = '接口自动化定期扫描，共有 <b>' + str(len(errorTest)) + ' </b>个异常接口:' + ''
html = html + ' <ul><li>开始时间：' + str(run_data["stime"]) + '</li><li>结束时间：' + str(
    run_data["etime"]) + '</li><li>测试用时：' + run_data["time_diff"] + '</li></ul>' + " "
html = html + '<table border="1" ><td bgcolor="#6495ed">全部（' + str(
    run_data["all_case"]) + '）</td><td bgcolor="#7fff00">成功（' + str(
    run_data["pass_case"]) + '）</td><td bgcolor="yellow">失败（' + str(
    run_data["fail_case"]) + '）</td> <td bgcolor="#e0ffff">未验证（' + str(
    run_data["jump_case"]) + '）</td></table>' + " "
html = html + '列表如下：<table><tbody><tr><th style="width:90px;">接口</th><th style="width:150px;">状态</th><th style="width:300px;">接口地址</th><th style="width:200px;">接口返回值</th><th style="width:200px;">创建者</th></tr></tbody></table>'
for test in errorTest:
    html = html + ' '
    html = html + '<table><tbody><tr><td style="width:150px;">' + test[0] + '</td><td style="width:50px;">' + test[
        1] + '</td><td style="width:300px;">' + test[2] + '</td><td style="width:600px;">&nbsp;&nbsp;&nbsp;' + test[
               3] + '</td><td style="width:600px;">&nbsp;&nbsp;' + test[4] + '</td></tr></tbody></table>'

mail_to=["wangju003@126.com",
             'zhangxuwei@5i5j.com',
             'yangmengyao@5i5j.com',
             'yong.chen17@pactera.com',
             'mingjie.gao@pactera.com',
             'zhenzhen.yang@pactera.com',
             'buhuangling@5i5j.com',
             'ouyangguowen@5i5j.com',
            'wenzg@visionet.com.cn',
           '13693546022@163.com',
         'on-line@5i5j.com'
         ]
#测试
# mail_to = ["wangju003@126.com",'13693546022@163.com',
#             'wenzg@visionet.com.cn','buhuangling@5i5j.com','on-line@5i5j.com']

# mail_to = ["wangju003@126.com"]
sendMail(html, mail_to, case_path)

