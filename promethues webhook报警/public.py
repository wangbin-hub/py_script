from  webhook import *
def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)
#判断告警类别
def judge_data(pasre_func,data):
    if data['status'] == 'firing':
        env = '告警'
        send_data =  pasre_func(data,env)
        return send_data
    elif data['status'] == 'resolved':
        env = '恢复'
        send_data =  pasre_func(data,env)
        return send_data

def send_msg(pasre_func,data):
    send_data = judge_data(pasre_func,data)
    token = webhook

    head = {"content-Type": "Application/json;charset:utf-8"}
    try:
        requests.post(token, data=json.dumps(send_data), headers=head).content
    except Exception as e:
        print(e)
def get_config():
    # with open("./config.toml","r",encoding="utf-8") as fin:
    #     files_contend = fin.read()
    # pasre_files_contend = toml.loads(files_contend)["apollo"]
    apollo_client = ApolloClient(app_id=sys.argv[1],
                                 config_server_url=sys.argv[2],
                                 cluster=sys.argv[3])
    local_env = apollo_client.get_value("local_env")
    webhook = apollo_client.get_value("webhook")
    listen_port = apollo_client.get_value("listen")
    return local_env,webhook,listen_port
local_env,webhook,listen_port = get_config()
