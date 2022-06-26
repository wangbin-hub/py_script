from bin import *
from bin.service_info import Service_INfo_Parse
from bin.service_test import  Check_Service,update_config
app = Flask(__name__)
#请求并压缩pprof文件 同步到共享目录中
def download_pprof(service_name,port,sync_host_info):
    root_path = os.getcwd()
    dir_name = "%s-%s"%(service_name,datetime.datetime.now().strftime("%Y%m%d%H%M")) #生成存放目录
    container_ip = Service_INfo_Parse().get_docker_ip(service_name) #获取容器IP地址
    try:
        os.mkdir(dir_name)
        # os.chdir(dir_name)
        os.system("curl http://%s:%s/debug/pprof/heap >> %s/mem"%(container_ip,port,dir_name)) #获取内存
        os.system("curl http://%s:%s/debug/pprof/profile?seconds=10  >> %s/cpu"%(container_ip,port,dir_name))#获取cpu
        os.system("curl http://%s:%s/debug/pprof/goroutine  >> %s/goroutine"%(container_ip,port,dir_name))
        os.system("zip  -r  %s.zip %s"%(dir_name,dir_name))
        os.system("scp -r %s.zip %s@%s:%s"%(dir_name,sync_host_info["host"]["login_user"],
        sync_host_info["host"]["host_ip"],sync_host_info["host"]["path"]  ))
        os.system("rm -rf %s*"%dir_name)
    except Exception as e:
        pass
@app.route('/pprof',methods=['GET'])
def pprof():
    service_name = request.args.get("service_name")
    port = Get_Alarm_Service_Config("pprof_port").get_value() #获取pprof端口
    sync_host_info = toml.loads(Get_Alarm_Service_Config("sync_file").get_value())
    #同步到目标目录信息{'host': {'path': '/data/files', 'host_ip': '10.0.3.203', 'login_user': 'root'}}
    pprof_list = Service_INfo_Parse().get_pprof_service() # 判断是否需要生成pprof服务
     # 生成存放pprof 目录
    if service_name in pprof_list:#判断需要生成pprof服务
        Thread(target=download_pprof,args=(service_name,port,sync_host_info)).start()
        return "request suceessful"
    else:
        return "request suceessful"
if __name__ == "__main__":
    Thread(target=Check_Service,).start()
    Thread(target=update_config,).start()
    app.run(host='0.0.0.0')



