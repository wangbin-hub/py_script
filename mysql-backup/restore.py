import os
import time
from loguru import logger
import toml
logger.add('runtime.log')
with open("config.toml",'r') as fin:
    config_contend = toml.loads(fin.read())["restore"]
increment_path = config_contend["increment_path"]
all_path = config_contend["all_path"]
try:
    os.system("innobackupex --apply-log --redo-only %s"%all_path)
except Exception as e:
    logger.error(e)
def parse_dir_time(times):
    ret_list = times.split("_")
    pasre_ret_list = ret_list[1].split("-")
    ret_times = "%s %s"%(ret_list[0],":".join(pasre_ret_list))
    timeArray = time.strptime(ret_times, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp
os.chdir(increment_path)
list_dir = list(filter(lambda x:os.path.isdir(x),os.listdir()))
dict_dir = {}
for i in list_dir:
    dict_dir[i] = parse_dir_time(i)
sord_dir = sorted(dict_dir)
logger.info(sord_dir)
try:
    for i in sord_dir:
        logger.info(all_path,os.path.join(increment_path,i))
        os.system("innobackupex --apply-log --redo-only "
                  "%s --incremental-dir=%s"%(all_path,os.path.join(increment_path,i)))
        logger.info("目录%s增量还原完成"%i)
    os.system("innobackupex --apply-log --redo-only %s"%all_path)
    logger.info("目录%s全量还原完成"%all_path)
except Exception as e:
    logger.error(e)








