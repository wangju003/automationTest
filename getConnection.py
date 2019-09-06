import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

#结构不合理，待项目稳定时需要调整结构
# 此处写类是为了利用类的的我特性方便方便获取engine和session的值
class GetConnection:
    dirname, filename = os.path.split(os.path.abspath(__file__))
    db_path = os.path.join(dirname, "db.ini")

    # 获取数据库连接
    config = configparser.RawConfigParser()
    config.read(db_path)
    confset = {}
    confset["username"] = config.get("database", "username")
    confset["password"] = config.get("database", "password")
    confset["url"] = config.get("database", "url")
    confset["port"] = config.get("database", "port")
    confset["dbname"] = config.get("database", "dbname")
    confset["charset"] = config.get("database", "charset")
    connStr = "mysql+mysqlconnector://{username}:{password}@{url}:{port}/{dbname}?charset={charset}".format(
        username=confset["username"],
        password=confset["password"],
        url=confset["url"],
        port=confset["port"],
        dbname=confset["dbname"],
        charset=confset["charset"]
    )
    engine = create_engine(connStr)
    DBsession = sessionmaker(bind=engine)  # 创建DBsession类
    session = DBsession()  # 创建session对象


#读取ini配置文件
def readIni(db_path):
    config=configparser.RawConfigParser()
    config.read(db_path)
    confset={}
    confset["username"]= config.get("database","username")
    confset["password"]= config.get("database","password")
    confset["url"]= config.get("database","url")
    confset["port"]=config.get("database","port")
    confset["dbname"]= config.get("database","dbname")
    confset["charset"]=config.get("database","charset")
    return  confset



# 获取数据库连接
def getConnMysql(db_path):
    confset = readIni(db_path)
    connStr="mysql+mysqlconnector://{username}:{password}@{url}:{port}/{dbname}?charset={charset}".format(
        username=confset["username"],
        password=confset["password"],
        url = confset["url"],
        port= confset["port"],
        dbname=confset["dbname"],
        charset=confset["charset"]
    )
    engine=create_engine(connStr)
    DBsession = sessionmaker(bind=engine)  # 创建DBsession类
    session= DBsession()  # 创建session对象

    return session


if __name__ =="__main__":
    from model import TestCase

    dirname, filename = os.path.split(os.path.abspath(__file__))
    db_path = os.path.join(dirname, "db.ini")
    print(db_path)

    session=getConnMysql(db_path)
    # testcase=session.query(TestCase).filter_by(id=232).first().creater #获取1个记录的某1个字段
    # testcase=session.query(TestCase).filter_by(id=232).all() #获取符合记录的所有对象，返回一个对象列表
    testcase = session.query(TestCase).all()#不带查询条件?
    print(testcase[:3])
