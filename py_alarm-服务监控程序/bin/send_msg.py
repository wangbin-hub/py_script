from  bin import *
# from conf.get_config import Get_Alarm_Service_Config
def GetTime():
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return times
def get_host_data():
    try:
        ret = subprocess.run("ip a | grep ens",shell=True,check=True,capture_output=True).stdout.decode()
        ret_ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", ret)[0]
        ret_host = subprocess.run("hostname",shell=True,check=True,capture_output=True).stdout.decode().strip()
    except Exception as e:
        ret = subprocess.run("ip a | grep eth0",shell=True,check=True,capture_output=True).stdout.decode()
        ret_ip = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", ret)[0]
        ret_host = subprocess.run("hostname",shell=True,check=True,capture_output=True).stdout.decode().strip()
    return ret_ip,ret_host
def send_msg_webhook(msg):
    """
    :var token : 微信webhook
    :var host_ip:服务器主机ip
    :var host_name : 服务器主机名
    :param msg: tuple 需要发送的服务
    :return: null

    """
    token = Get_Alarm_Service_Config("webhook").get_value() #企业微信群webhook
    host_env = Get_Alarm_Service_Config("host_env").get_value() #主机运行环境
    service_name,service_status = msg
    host_ip,host_name = get_host_data()
    title = "# <font color=\"info\">主机服务监控报警|%s</font>\n"%host_env
    contend = \
        ">告警主机：<font color=\"comment\">%s</font>\n \
        >告警IP：<font color=\"comment\">%s</font>\n \
        >告警服务: <font color=\"comment\">%s</font>\n \
        >告警状态: <font color=\"comment\">%s</font>\n \
        >触发时间: <font color=\"comment\">%s</font>\n\n \
        "%(host_name,host_ip,service_name,service_status,GetTime())
    head = {"content-Type": "Application/json;charset:utf-8"}
    test = title + contend
    send_data = {
        "msgtype": "markdown",
        "markdown": {
            "content":test
        }
    }
    try:
        requests.post(token, data=json.dumps(send_data), headers=head).content
    except Exception as e:
        print(e)

