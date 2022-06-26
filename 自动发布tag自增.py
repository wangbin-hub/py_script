from   redis import Redis
from gevent import pywsgi
from flask import request,Flask
app = Flask(__name__)
app.debug = True
@app.route('/send',methods=["POST","GET"])
def send():
    if request.method == "GET":
        service_name = request.args.get("service")
        ret = get_version(service_name)
        print("ret:%s"%ret)
        return str(ret)
    else:
        pass

def get_version(name):
    r = Redis(host="10.0.3.198",db=1)
    if r.get("service:{name}:version".format(name = name)):
       key = float(r.get("service:%s:version"%name))
       key =round((key +0.01),2)
       r.set("service:%s:version"%name, key)
       r.close()
       return key
    else:
        r.set("service:%s:version"%name, 0.01)
        key = 0.01
        r.close()
        return key
server = pywsgi.WSGIServer(("0.0.0.0",5612), app)
server.serve_forever()
