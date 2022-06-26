import redis
from redis.sentinel import Sentinel

# # 连接哨兵服务器(主机名也可以用域名)
sentinel = Sentinel([('10.0.3.191', 26379),
                     ('10.0.3.191', 26380),
                     ('10.0.3.191', 26381),
                     ('10.0.3.192', 26379),
                     ('10.0.3.192', 26380),
                     ('10.0.3.192', 26381),
                     ],
                    socket_timeout=0.1)

# 获取主服务器地址
master = sentinel.discover_master('redistest')
slave = sentinel.discover_slaves("redistest")
print("test master:%s"%str(master))
print("test slave:%s"%str(slave))
print("集群名：redistest")
