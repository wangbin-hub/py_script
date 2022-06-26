#!usr/bin/python3
from webhook import *
from webhook.public import  bytes2json,send_msg
from webhook.docker import channel
app = Flask(__name__)
app.register_blueprint(channel)
def parse_data(data,env):
    sum_msg = ""
    times = (datetime.now()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    if len(data["alerts"]) == 1:
        try:
            msg_message = data["alerts"][0]["annotations"]["description"]
        except Exception as e:
            msg_message = ""
        try:
            msg_values = data["alerts"][0]["annotations"]["values"]
        except Exception as e:
            msg_values = ""
        try:
            Indicator ="%s，挂载点：%s"%(data["alerts"][0]['labels']["device"],data["alerts"][0]['labels']["mountpoint"])
        except Exception as e:
            Indicator = ""
        test = "# <font color=\"info\">[%s]|Prometheus|%s|%s</font>\n \
                >告警级别：<font color=\"comment\">%s</font>\n \
                >告警主机：<font color=\"comment\">%s</font>\n \
                >告警详情: <font color=\"comment\">%s</font>\n \
                >当前触发: <font color=\"comment\">%s</font>\n \
                >指标标签: <font color=\"comment\">%s</font>\n \
                >触发时间: <font color=\"comment\">%s</font> \
                "%(env,local_env,data["alerts"][0]["labels"]["alertname"],data["alerts"][0]['labels']['severity']
                                  ,data["alerts"][0]['labels']['instance'],msg_message,msg_values,Indicator,times)
    else:
        judge_data = list(filter(lambda x:x['status'] == 'resolved',data['alerts']))
        if judge_data:
            env = "恢复"
            contend = judge_data
        else:
            contend = data['alerts']
        title = "# <font color=\"info\">[%s]|Prometheus|%s|%s|聚合报警</font>\n"%(env,local_env,data["alerts"][0]["labels"]["alertname"])
        for output in contend:
            try:
                msg_message = output["annotations"]["description"]
            except Exception as e:
                msg_message = ""
            try:
                msg_values = output["annotations"]["values"]
            except Exception as e:
                msg_values = ""
            try:
                Indicator = "%s，挂载点：%s"%(output['labels']["device"],output['labels']["mountpoint"])
            except Exception as e:
                Indicator = ""
            contend = \
                ">告警级别：<font color=\"comment\">%s</font>\n \
                >告警主机：<font color=\"comment\">%s</font>\n \
                >告警详情: <font color=\"comment\">%s</font>\n \
                >当前触发: <font color=\"comment\">%s</font>\n \
                >指标标签: <font color=\"comment\">%s</font>\n \
                >触发时间: <font color=\"comment\">%s</font>\n\n \
                "%(output['labels']['severity'],output['labels']['instance'],msg_message,msg_values,Indicator,times)
            sum_msg = sum_msg + contend
        test = title + sum_msg
    send_data = {
        "msgtype": "markdown",
        "markdown": {
            "content":test
        }
    }
    return send_data
@app.route('/', methods=['POST', 'GET'])
def send():
    print((datetime.now()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
    if request.method == 'POST':
        post_data = request.get_data()
        print(bytes2json(post_data))
        send_msg(parse_data,bytes2json(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager  webhook server!'

if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)
docx=os.path.join(basedir, 'default.docx')
app.run(host='0.0.0.0', port=listen_port)