#！/usr/bin/python3
import subprocess
import time
import re
import toml
import os
#读取config.toml配置
with open("config.toml",'r',encoding="utf-8") as fin:
    read_config = toml.loads(fin.read())
    load_conf = read_config['test']
def test_rate(name,url):
    times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    args = '\'time_connect: %{time_connect} s\ntime_namelookup: %{time_namelookup}  s\nspeed_download: %{speed_download}' \
           ' B/s\ntime_total: %{time_total} s\n\''
    try:
        curl_contend = subprocess.getoutput("curl -Lo /dev/null -skw  %s %s"%(args,url))
        # parse_data = {"time":times,name:url}
        parse_data = "timestamp:%s %s:%s "%(times,name,url)
        for i in curl_contend.split('\n'):
            k,v =i.strip('\'').split(':')
            if k =="speed_download":
                v = round(float(re.findall(r'(.*) B/s',v)[0])/1024/1024,5)
                parse_data = parse_data+"%s:%sMB/S  "%(k,v)
                # parse_data[k] ="%sMB/s"%v
            else:
                parse_data = parse_data+"%s:%s  "%(k,v)
                # parse_data[k]=v
    except Exception as e:
        parse_data = {"timestamp":times,name:url,"response":"time_out"}
    with open("test_log","a+",encoding="utf-8") as fin:
        fin.write(parse_data+'\n')
if __name__== '__main__':
    while True:
        for key,value in load_conf.items():
            test_rate(key,value)
        time.sleep(300)