# import sys
# print(sys.path)
from service_info import Service_INfo_Parse
from bin import *
from send_msg import send_msg_webhook
q = Queue(maxsize=10)
def start_docker(one_service_tuple):
    if not Service_INfo_Parse().start_docker_service(one_service_tuple):  #启动成功返回0 失败返回1
        time.sleep(0.4) # 间隔0.4秒检查服务是否启动成功，失败在执行拉起
        check_ret = Service_INfo_Parse().check_docker_status(one_service_tuple[0])
        return check_ret
    else:
        return 1
def start_binary(one_service_tuple):
    """
    :param one_service_tuple:
    :return: 0 表示启动成功 1表示启动是吧
    """
    if not Service_INfo_Parse().start_binary_service(one_service_tuple):  #启动成功返回0 失败返回1
        time.sleep(0.4)  # 间隔0.4秒检查服务是否启动成功，失败在执行拉起
        ret_check = Service_INfo_Parse().check_binary_status(one_service_tuple[0])
        return ret_check
    else:
        return 1
def pull_up_service(msg):
    # 提取单个服务信息 tuple
    """
    :param msg:
    :return:
    """
    for i in msg.items():
        if i[1]['command']:
            count = 0 #拉起失败累加变量，每次失败加一 最多拉起三次
            while True:
                run_path = os.getcwd() #获取当前运行目录
                exec_ret = start_binary(i)
                os.chdir(run_path)  #切换回执行目录
                if count < 3 and exec_ret == 1:
                    count +=1
                    time.sleep(0.5)
                else:
                    if count == 2:
                        send_msg_webhook([i[0],"拉起失败"])
                        break
                    else:
                        pass
                send_msg_webhook([i[0],"拉起成功"])
                break
        else:
            count = 0 #拉起失败累加变量，每次失败加一 最多拉起三次
            while True:
                exec_ret = start_docker(i) #执行拉起返回结果
                if count < 3 and  exec_ret== 1:
                    count +=1
                    time.sleep(0.5)
                else:
                    if count == 2:
                        send_msg_webhook([i[0],"拉起失败"])
                        break
                    else:
                        pass
                send_msg_webhook([i[0],"拉起成功"])
                break
def merge_service_info():
    docker_service = Service_INfo_Parse().get_docker_service() #获取要监控的容器服务
    binary_service = Service_INfo_Parse().get_common_server()  #获取要监控的二进制服务
    # docker_merge_binary = docker_service.update(binary_service)
    #合并docker服务和二进制服务信息
    docker_merge_binary =  {k:v for d in [docker_service,binary_service] for k,v in d.items()}
    return  docker_merge_binary
def update_config():
    total_service_list = Service_INfo_Parse().get_service_total_list()
    service_count = len(total_service_list)
    while True:
       time.sleep(3600)  #配置更新等待时间
       total_service_list = Service_INfo_Parse().get_service_total_list()
       if service_count != len(total_service_list):
           logger.info("配置发生改变，需重新获取配置")
           service_count = len(total_service_list )
           q.put(1)
       else:
           logger.info("配置无变化,当前监控服务数为：%i"%service_count)
# def silence_period(t):
#     print("%s监控静默时间%ss%s"%('*'*25,t,'*'*25))
#     start = time.perf_counter()
#     for i in range(t + 1):
#         finsh = "▓" * i
#         need_do = "-" * (t - i)
#         progress = (i / t) * 100
#         dur = time.perf_counter() - start
#         print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(progress, finsh, need_do, dur), end="")
#         time.sleep(1)
#     print("")
def Check_Service():
    if os.path.isfile("update.log"): # 生成更新文件 主机服务更新 触发文件 使报警服务静默
        pass

    else:
        os.system("touch update.log")
    check_dict = merge_service_info()
    logger.info("检索列表")
    logger.info(",".join(check_dict.keys()))
    #获取当前运行目录，执行拉起需要切换目录
    root_path = os.getcwd()
    while True:
        #计算需要监控的服务个数
        # service_conunt = len(check_dict)
        abnormal_service = {}
        check_interval = int(Get_Alarm_Service_Config("check_interval").get_value())
        #判断有没有服务更新，如果查询到有服务更新 静默60秒
        if time.time() - os.stat("update.log").st_mtime > check_interval and q.empty():
            # print("开始检索".center(20, "-"))
            logger.info("开始检索")
            pids = psutil.pids() #获取系统PID
            for key,value in check_dict.items():
                logger.info("start searching: %s"%key)
                time.sleep(0.5)
                #判断服务pid信息 是不是在系统存在
                if value["pid"] not in pids:
                    abnormal_service[key] = value
            if abnormal_service:
                logger.info("异常服务:%s"%",".join(abnormal_service.keys()))
                #拉取服务函数
                pull_up_service(abnormal_service)
                os.chdir(root_path)   #返回程序执行执行目录
                check_dict = merge_service_info() #重新获取服务信息
            logger.info("检测结束")
            # silence_period(90)
            time.sleep(check_interval)
        else:
            if not q.empty():
                q.get()
            logger.info("更新静默120秒")
            check_dict = merge_service_info()
            # silence_period(120)
            time.sleep(20)






