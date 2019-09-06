from getConnection import GetConnection
from sqlalchemy.engine import reflection
from model import TestCase,EnvConfig
import xlsxwriter
import os


def exportExcel():
    session = GetConnection.session
    engine = GetConnection.engine
    # print(session)

    # 获取testcase表字段名
    insp = reflection.Inspector.from_engine(engine)
    colums = insp.get_columns("testcase")  # 这里写表名
    headings = []
    for i in colums:
        headings.append(i["name"])
    headings.insert(2, "host")

    # 获取数数据库testcase表每行记录
    results = session.query(TestCase).all()
    # print(results)
    datas = []
    for record in results:
        # print(record)
        num = str(record.id)
        api_purpose = record.api_purpose.replace("\n", "").replace("\r", "")
        api_host = session.query(EnvConfig).filter_by(id=1).first().host  # 获得全局配置的host
        request_url = record.request_url.replace("\n", "").replace("\r", "")
        request_method = record.request_method.replace("\n", "").replace("\r", "")
        request_data_type = record.request_data_type.replace("\n", "").replace("\r", "")
        request_data = record.request_data.replace("\n", "").replace("\r", "").replace("'", '"')
        assert_method = record.assert_method
        check_point = record.check_point.replace("\n", "").replace("\r", "")
        try:
            correlation = str(record.correlation.replace("\n", "").replace("\r", "").split(";"))
        except AttributeError:
            print('请检查测试用例id:%s的correlation列的值是否为Null!'%num)

        active = record.active
        creater = record.creater
        datas.append(
            [num, api_purpose, api_host, request_url, request_method, request_data_type, request_data, assert_method,
             check_point, correlation, active, creater])
    # print(datas)
    # 新建并打开一个excel
    dirname, filename = os.path.split(os.path.abspath(__file__))
    case_path = os.path.join(dirname, "TestCase.xlsx")
    workbook = xlsxwriter.Workbook(case_path)
    worksheet = workbook.add_worksheet()

    # 配置表头样式
    head_style = workbook.add_format({"bold": True, "bg_color": "yellow", "align": "center", "font": 13})
    # 将获取的字段名作为表头写入excel
    worksheet.write_row("A1", headings, head_style)
    # 逐行填写数据库记录至excel
    for i in range(0, len(datas)):
        worksheet.write_row("A{}".format(i + 2), datas[i])
    workbook.close()


    return case_path

if __name__ =="__main__":
    case_path=exportExcel()
    print(case_path)