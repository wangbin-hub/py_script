from webhook import  *
from webhook.public import  bytes2json,send_msg
channel= Blueprint('channel',__name__)
@channel.route('/channel', methods=['POST', 'GET'])
def send_docker():
    if request.method == 'POST':
        post_data = request.get_data()
        print(bytes2json(post_data))
        send_msg(parse_data,bytes2json(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager  webhook server!'
def parse_data(data,env):
    sum_instance = []
    sum_name = []
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
            msg_instance = data["alerts"][0]['labels']['instance']
        except Exception as e:
            msg_instance = ""
        try:
            msg_name = data["alerts"][0]['labels']['name']
        except Exception as e:
            msg_name = ""
        test = "# <font color=\"info\">[%s]|cadvisor|%s|%s</font>\n \
                >告警主机：<font color=\"comment\">%s</font>\n \
                >告警详情: <font color=\"comment\">%s</font>\n \
                >告警容器: <font color=\"comment\">%s</font>\n \
                >触发时间: <font color=\"comment\">%s</font> \
                "%(env,local_env,data["alerts"][0]["labels"]["alertname"]
                                  ,msg_instance,msg_message,msg_name,times)
    else:
        judge_data = list(filter(lambda x:x['status'] == 'resolved',data['alerts']))
        if judge_data:
            env = "恢复"
            contend = judge_data
        else:
            contend = data['alerts']
        title = "# <font color=\"info\">[%s聚合]|cadvisor|%s|%s</font>\n"%(env,local_env,data["alerts"][0]["labels"]["alertname"])
        """循环获取主机和容器名"""
        for output in contend:
            try:
                msg_instance = output['labels']['instance']
                if msg_instance not in sum_instance:
                    sum_instance.append(msg_instance)
            except Exception as e:
                msg_instance = ""
            try:
                msg_name = output['labels']['name']
                if msg_name not in sum_name:
                    sum_name.append(msg_name)
            except Exception as e:
                msg_name = ""
        try:
            msg_message = data["alerts"][0]["annotations"]["description"]
        except Exception as e:
            msg_message = ""
        contend = \
            " \
            >告警主机：<font color=\"comment\">%s</font>\n \
            >告警详情: <font color=\"comment\">%s</font>\n \
            >告警容器: <font color=\"comment\">%s</font>\n \
            >触发时间: <font color=\"comment\">%s</font>\n\n \
            "%(",".join(sum_instance),msg_message,",".join(sum_name),times)
        test = title + contend
    send_data = {
        "msgtype": "markdown",
        "markdown": {
            "content":test
        }
    }
    return send_data
# __all__=["admin"]