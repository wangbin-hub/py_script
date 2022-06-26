import os
import  subprocess
import datetime
import time
from loguru import logger
import requests
import json
import socket
import toml
#读取配置文件
with open("config.toml",'r') as fin:
    config_contend = toml.loads(fin.read())["backup"]
#mysql 获取用户密码
servic_env = config_contend["servic_env"]
address = config_contend["address"]
user = config_contend["user"]
password = config_contend["password"]
backup_addr = config_contend["backup_addr"]
#webhook地址
url = config_contend["url"]

#日志添加
logger.add('runtime.log', retention='10 days')
#企业微信信息发送
def wexin(contend,path):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        inner_ip = s.getsockname()[0]
    finally:
        s.close()
    test = "# <font color=\"info\">%s</font>\n \
            >备份主机：<font color=\"comment\">%s</font>\n \
            >备份类型：<font color=\"comment\">%s</font>\n \
            >生成目录: <font color=\"comment\">%s</font>\n \
            >完成时间: <font color=\"comment\">%s</font> \
            "%(servic_env,inner_ip,contend,path,datetime.datetime.now())
    head = {"content-Type": "Application/json;charset:utf-8"}
    a1 = {
        "msgtype": "markdown",
        "markdown": {
            "content": test
        },
        "at": {
            "atMobiles": [
                ""
            ]
        }
    }
    requests.post(url, data=json.dumps(a1), headers=head).content
def parse_dir_time(times):
    ret_list = times.split("_")
    pasre_ret_list = ret_list[1].split("-")
    ret_times = "%s %s"%(ret_list[0],":".join(pasre_ret_list))
    timeArray = time.strptime(ret_times, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp
"""获取最新的备份目录"""
def compare_dir():
    day_dir_dict = {}
    for i in os.listdir():
        day_dir_dict[i] = os.stat(os.path.join(os.getcwd(),i)).st_ctime
    ret_max = max(day_dir_dict,key = lambda k:day_dir_dict[k])
    ret_min = min(day_dir_dict,key = lambda k:day_dir_dict[k])
    return [ret_max,ret_min]
def parse_dir_times(times):
    ret_list = times.split("_")
    pasre_ret_list = ret_list[1].split("-")
    ret_times = "%s %s"%(ret_list[0],":".join(pasre_ret_list))
    timeArray = time.strptime(ret_times, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp
def main():
    """
    :var times   :  str 年月拼接
    :var weekdate : int 按照周备份
    :var monthdate : int 按照月进行备份
    """
    times = time.strftime("%Y-%m", time.localtime())
    weekdate = datetime.datetime.now().weekday()
    monthdate = datetime.datetime.now().day

    os.chdir(backup_addr)
    if len(list(filter(lambda x:os.path.isdir(x),os.listdir()))) ==0:
        try:
            os.system("innobackupex --user=%s --password=%s --host=%s --slave-info %s"\
            %(user,password,address,os.path.join(os.getcwd(),"mysqlback_all")))
            logger.info("全量备份成功路径为：%s"%os.path.join(os.getcwd(),"mysqlback_all"))
            search_ret_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))[0]
            wexin("全量备份",search_ret_dir)
        except Exception as e:
            logger.info(e)
    else:
        global mysql_all_data
        get_mysql_dir = os.listdir(os.path.join(backup_addr,"mysqlback_all"))
        mysql_all_data = os.path.join(backup_addr,"mysqlback_all",get_mysql_dir[0])
        make_mon_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))
        if len(make_mon_dir) == 1:
            os.mkdir("increment")
        #判断当前路径是否存在周目录，不存在新建
        os.chdir(os.path.join(os.getcwd(),"increment"))
        make_week_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))
        isocalendar = datetime.datetime.now().isocalendar()
        dir_name = "%sweek"%(isocalendar[1])
        #删除大于两周的文件
        if len(make_week_dir) >= 2:
            ret_min_dir = compare_dir()[1]
            logger.info("删除目录%s"%ret_min_dir)
            os.system("rm -rf %s"%(os.path.join(os.getcwd(),ret_min_dir)))
        #判断月目录下 是否存在周目录，和是不是新的一周
        if len(make_week_dir) == 0:
            os.mkdir(dir_name)
        make_week_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))
        if dir_name not in make_week_dir :
            os.mkdir(dir_name)
        max_dir = compare_dir()[0]
        os.chdir(max_dir)
        #判断周备份有没有有没有备份记录，没有就基于全备做一次备份
        search_week_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))
        if len(search_week_dir) == 0:
            backup_path = os.getcwd()
            try:
                os.system("innobackupex --user=%s --password=%s --incremental %s "
                          "--incremental-basedir %s"%(user,password,backup_path,mysql_all_data))
                logger.info("周增量备份上级目录为：%s"%mysql_all_data)
                logger.info("周增量备份当前目录为：%s"%os.path.join(os.getcwd(),compare_dir()[0]))
                ret_max_dir = compare_dir()[0]
                wexin("周增量备份",ret_max_dir)
            except Exception as e:
                logger.error(e)
        #判断本周最近一次的增量目录
        else:
            ret_max_dir = compare_dir()[0]
            day_back_dir = os.path.join(os.getcwd(),ret_max_dir)
            #增量备份
            try:
                os.system("innobackupex --user=%s --password=%s --incremental %s "
                          "--incremental-basedir %s"%(user,password,os.getcwd(),day_back_dir))
                logger.info("每日增量备份上级目录为：%s"%day_back_dir)
                logger.info("每日增量备份当前目录为：%s"%os.path.join(os.getcwd(),compare_dir()[0]))
                ret_max_dir = compare_dir()[0]
                wexin("日增量备份",ret_max_dir)
            except Exception as e:
                logger.error(e)
if __name__ == "__main__":
    main()













