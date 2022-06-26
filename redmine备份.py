#!/usr/bin/python3
import os,time,json,requests,socket,subprocess
def tar():
    host = socket.gethostname()
    ip = socket.gethostbyname(socket.gethostname())
    if not subprocess.getoutput("netstat -tnlp | awk '{print $NF}' | awk -F'/' '{print $NF}' | uniq | grep httpd"):
        test = "备份主机：%s\n备份ip：%s\n备份项目：redmine\n报警状态：服务不存在" % (host, ip)
        wexin(test)
    else:
        time2 = time.strftime("%Y%m%d%H%M%S", time.localtime())
        files ="redmine%s.tar.gz"%time2
        os.chdir("/opt/redmine-4.1.1-0")
        os.system("./ctlscript.sh stop")
        os.chdir("/opt")
        try:
            os.system("tar -pzcvf %s redmine-4.1.1-0"%files)
        except Exception as e:
            print(e)
            test = "备份主机：%s\n备份ip：%s\n备份项目：redmine\n执行状态：备份失败" % (host, ip)
            wexin(test)
        else:
            os.system("scp  %s root@10.0.3.103:/backup/redmine"%files)
            os.remove(files)
            os.chdir("/opt/redmine-4.1.1-0")
            os.system("./ctlscript.sh start")
            test = "备份主机：%s\n备份ip：%s\n备份项目：redmine\n执行状态：备份成功"%(host,ip)
            wexin(test)
def wexin(test):
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ab38de33-cb27-4d52-8b6a-bb5c9ff385bf"
    head = {"content-Type": "Application/json;charset:utf-8"}
    a1 = {
        "msgtype": "text",
        "text": {
            "content": test
        },
        "at": {
            "atMobiles": [
                ""
            ]
        }
    }
    requests.post(url, data=json.dumps(a1), headers=head).content
if __name__ == "__main__":
    tar()












