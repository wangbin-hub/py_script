from conf import *
class Get_Alarm_Service_Config():
    def __init__(self,key):
        #读取apollo集群配置
        if "Linux" in platform.platform():
            path =  os.getcwd()+ "/conf/config.toml"
        else:
            path = os.getcwd()+"\\conf\\config.toml"
        with open(path,"r",encoding="utf-8") as fin:
            ret_apollo_config = toml.loads(fin.read())["apollo"]
        #实例化apollo 对象
        self.apollo_clinet = ApolloClient(app_id=ret_apollo_config["app_id"],
                                         config_server_url=ret_apollo_config["config_server_url"],cluster=ret_apollo_config["cluster"])
        #需要获取的key值
        self.key = key
    #获取value 值
    def get_value(self):
       return self.apollo_clinet.get_value(self.key)
