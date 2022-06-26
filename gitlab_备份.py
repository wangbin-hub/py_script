#!/usr/local/python3/bin/python3
import os,socket
import datetime
import  requests
import  json
import subprocess
def wexin(path):
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a5a7a0a1-ea1b-4387-889b-693bd5312f18"
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        inner_ip = s.getsockname()[0]
    finally:
        s.close()
    test = "# <font color=\"info\">gitlab备份</font>\n \
            >备份主机：<font color=\"comment\">%s</font>\n \
            >备份文件：<font color=\"comment\">%s</font>\n \
            >完成时间: <font color=\"comment\">%s</font> \
            "%(inner_ip,path,datetime.datetime.now())
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
def shell_exec(content):
    subprocess.run(content,shell=True,check=True)
def backup_gitlab():
    git_path = "/var/opt/gitlab/backups"
    try:
        # shell_exec("gitlab-rake gitlab:backup:create")
        os.chdir(git_path)
        file_name  = os.listdir("/var/opt/gitlab/backups")[0]
        print(file_name)
        jion_file_name = os.path.join(git_path,file_name)
        shell_exec("scp -r %s root@10.0.0.205:/data/gitlab"%jion_file_name)
        shell_exec("rm -rf %s"%jion_file_name)
        wexin(file_name)
    except  Exception as e:
        print(e)
if __name__ =="__main__":
    backup_gitlab()

