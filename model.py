from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,Text,String,Enum
Base =declarative_base()



#测试账号表
class TestAccounts(Base):
    __tablename__="test_accounts"

    id =Column(Integer,primary_key=True)
    uid=Column(String(255),nullable=False)
    token=Column(Text,nullable=False)
    loginname=Column(String(255),nullable=False)
    password=Column(String(255),nullable=False)
    creater=Column(String(255))

    def __repr__(self):
        return "<TestAccounts(loginname=%s)>"%self.loginname

#测试用例表
class TestCase(Base):
    __tablename__="testcase"
    id = Column(Integer,primary_key=True)
    api_purpose=Column(String(50))
    request_url=Column(String(100))
    request_method=Column(Enum("POST","GET"))
    request_data_type=Column(Enum("Data","Form","File"))
    request_data=Column(Text,nullable=False)
    assert_method=Column(Enum("assertIn","assertNotIn In"),default="assertIn")
    check_point=Column(String(255))
    correlation=Column(String(100))
    active=Column(Enum("Yes","No"))
    creater = Column(String(50))
    project = Column(Enum("gw", "hw","gw_lt"), default="gw")

    def __repr__(self):
        return "<TestCase.%s>"%self.api_purpose

#全局环境配置表
class EnvConfig(Base):
    __tablename__="env_config"
    id=Column(Integer,primary_key=True)
    host = Column(String(50))  # 默认值 1  0:appapi.5i5j.com，
    def __repr__(self):
        return "<EnvConfig.%s>"%self.host


# 超时接口统计表
class ResponseTime(Base):
    __tablename__ ="response_time"
    id = Column(Integer,primary_key=True)
    num = Column(Integer)
    api_purpose = Column(String(200))
    request_url = Column(String(100))
    run_time = Column(String(200))
    res_time = Column(String(200))

    def __repr__(self):
        return "<ResponseTime.%s>"%self.api_purpose
