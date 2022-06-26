from bin import *
class Service_INfo_Parse(object):
    def __init__(self):
        #实例化docker对象
        self.cli = docker.APIClient(base_url="unix://var/run/docker.sock")
    def get_service_total_list(self):

        ret_value = Get_Alarm_Service_Config("docker_service").get_value()
        get_docker_service = [ret_value] if "," not in ret_value else ret_value.split(",")
        ret_value = Get_Alarm_Service_Config("comm_service").get_value()
        get_comm_service = [ret_value] if "," not in ret_value else ret_value.split(",")
        get_comm_service.extend(get_docker_service)
        return get_comm_service
    #获取需要监控的容器息
    def get_docker_service(self):
        """
        :return:{'maoti_api': {'pid': 19665, 'dir': '', 'command': ''}}
        """
        ret_value = Get_Alarm_Service_Config("docker_service").get_value()
        get_docker_service = [ret_value] if "," not in ret_value else ret_value.split(",")

        docker_dict = {}
        #获取容器进程信息
        for i in get_docker_service:
            try:
                data =  self.cli.inspect_container(i)["State"]
                if i not in docker_dict and data['Status'] == "running" :
                    docker_dict[i] = {"pid":int(data["Pid"]),"dir":"","command":""}
            except Exception as e:
                pass
        return  docker_dict
    #获取要监控的二进制信息
    def get_common_server(self):
        """
        :return:{ 'center_api': {'pid': 30322, 'dir': '/data/centapi', 'command': './center_api'}}
        """
        ret_value = Get_Alarm_Service_Config("comm_service").get_value()
        get_comm_service = [ret_value] if "," not in ret_value else ret_value.split(",")
        service_dict = {}
        for line in psutil.pids():
            try:
                pid = psutil.Process(line)
                if pid.name() in get_comm_service and pid.name() not in service_dict:
                    service_dict[pid.name()] = {"pid":line,"dir":os.path.dirname(pid.exe()),"command":pid.cmdline()[0]}
            except Exception as e:
                pass
        return service_dict
    #获取要监控的pprof服务
    def get_pprof_service(self):
        ret_value = Get_Alarm_Service_Config("pprof_service").get_value()
        get_pprof_list = [ret_value] if "," not in ret_value else ret_value.split(",")
        return get_pprof_list
    #拉起容器服务
    def start_docker_service(self,service_tuple):
        """
        :param service_name tuple: 服务信息('maoti_api', {'pid': 19665, 'dir': '', 'command': ''})
        :return: null
        """
        try:
            os.system("docker start %s"%service_tuple[0])
            return 0
        except Exception as fin:
            return 1
    #拉起普通服务
    def start_binary_service(self,service_tuple):
        """
        :param service_tuple: ('center_api', {'pid': 30322, 'dir': '/data/centapi', 'command': './center_api'})
        :return: null
        """
        try:
            os.chdir(service_tuple[1]['dir'])   #切换到需要拉起服务的目录
            os.system("nohup ./%s >> ./myout.file 2>&1 &"%service_tuple[0])
            return 0
        except Exception as fin:
            return 1
    #检查docker容器拉起状态
    def check_docker_status(self,service_name):
        data =  self.cli.inspect_container(service_name)["State"]
        if data['Status'] == "running":
            return 0
        else:
            return 1
    #检查二进制服务拉起状态 限制在linux 服务
    def check_binary_status(self,service_name):
        """
        :param service_name:  需要检查的服务名
        :return: 0表示检测启动成功，1表示检测启动失败
        """
        try:
            subprocess.check_call("ps -axu | grep %s | grep -v grep"%service_name,shell=True)
            return 0
        except Exception as fin:
            return 1
    def get_docker_ip(self,service_name):
        """
        :param service_name: 要获取容器服务名字
        :return: ipv4地址
        """
        ret_inspect_info = self.cli.inspect_container(service_name)
        return ret_inspect_info["NetworkSettings"]["Networks"]['bridge']['IPAddress']
