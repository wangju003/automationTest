import os
class Config(object):
    DEBUG=False
    def __getitem__(self, item):
        return self.__getattribute__(item)


class OnlineConfig(Config):
    HOST="appapi.5i5j.com"
class ReleaseConfig(Config):
    HOST="appts.5i5j.com"

mapping = {
    "online":OnlineConfig,
    "release":ReleaseConfig
}

#根据脚本参数，来决定用那个环境配置
import sys
# print(sys.argv)
num = len(sys.argv)-1
if num<1 or num >1:
    exit("参数错误,必须传环境变量!比如: python xx.py online|release")
env = sys.argv[1]
# print(env)
APP_ENV=os.environ.get("APP_ENV",env).lower()
config=mapping[APP_ENV]()

if __name__ == "__main__":
    def ssh2(host):
        print(host)


    res = ssh2(config.HOST)
    # print(res)
