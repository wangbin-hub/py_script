#!/usr/local/python3/bin/python3
from datetime import datetime,timedelta
import time
import json
import requests
from elasticsearch import Elasticsearch
from loguru import logger
logger.add('runtime.log', retention='10 days')
import toml
with open("config.toml",'r') as fin:
    read_config_contend = toml.loads(fin.read())["es"]
host = read_config_contend["host"]
port = read_config_contend["port"]
timeout = read_config_contend["timeout"]
interval = read_config_contend["interval"]
web_hook = read_config_contend["web_hook"]
es = Elasticsearch(hosts=host, port=port, timeout=timeout)
def wexin(uri,contend):
    test = "# <font color=\"info\">海外nginx日志报警</font>\n \
            >route_addr:<font color=\"comment\">%s</font>\n \
            >domain_addr：<font color=\"comment\">%s</font>\n \
            >status_code: <font color=\"comment\">%s</font>\n \
            >client_adds：<font color=\"comment\">%s</font>\n \
            >response_time: <font color=\"comment\">%s</font>\n \
            >access_time: <font color=\"comment\">%s</font> \
            "%(uri,contend["domain"],contend["status"],contend["client"],
               contend["responsentime"],contend["time"])
    head = {"content-Type": "Application/json;charset:utf-8"}
    data = {
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
    try:
        requests.post(web_hook, data=json.dumps(data), headers=head).content
        logger.info("发送信息成功")
    except Exception as e:
        logger.error(e)
def get_utc_time(interval_time):#interval_time 单位为分
    timestamp = time.time()
    st_time = datetime.utcfromtimestamp(timestamp-interval_time*60).strftime("%Y-%m-%dT%H:%M:%SZ")
    ens_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")
    return st_time,ens_time
#解析utc時間戳
def utc_pasre_local(times):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    utcTime = datetime.strptime(times, UTC_FORMAT)
    localtime = utcTime + timedelta(hours=8)
    return localtime
def process_data(st_time,end_time):
    query = {
    "version": "true",
    "size": 500,
    "sort": [
        {
            "@timestamp": {
                "order": "desc",
                "unmapped_type": "boolean"
            }
        }
    ],
    "aggs": {
        "2": {
            "date_histogram": {
                "field": "@timestamp",
                "calendar_interval": "1m",
                "time_zone": "Asia/Shanghai",
                "min_doc_count": 1
            }
        }
    },
    "stored_fields": [
        "*"
    ],
    "script_fields": {},
    "docvalue_fields": [
        {
            "field": "@timestamp",
            "format": "date_time"
        }
    ],
    "_source": {
        "excludes": []
    },
    "query": {
        "bool": {
            "must": [],
            "filter": [
                {
                    "match_all": {}
                },
                {
                    "range": {
                        "status": {
                            "gte": 400,
                            "lt": 600
                        }
                    }
                },
                {
                    "range": {
                        "@timestamp": {
                            "gte": st_time,
                            "lte": end_time,
                            "format": "strict_date_optional_time"
                        }
                    }
                }
            ],
            "should": [],
            "must_not": []
        }
    }
}
    allDoc = es.search(index="nginx_abroad*",body=query)
    extraction_data = {}
    try:
        for i in allDoc["hits"]["hits"]:
            keys = i["_source"]
            times = utc_pasre_local(keys["@timestamp"])
            extraction_data[keys["url"]] = {"domain":keys["domain"],
                                         "client":keys["client"],
                                         "responsentime":keys["responsentime"],
                                         "status":keys["status"],
                                        "time": times
                                         }
        logger.info(extraction_data)
        return extraction_data
    except Exception as e:
        logger.error(e)
def main():
    while True:
        st_time,end_time = get_utc_time(interval)
        logger.info("查询任务开始")
        logger.info("检索开始时间%s"%st_time)
        logger.info("检索结束时间%s"%end_time)
        ret_data = process_data(st_time,end_time)
        try:
            if not bool(ret_data):
                logger.info("没有查询到数据")
            else:
                for key,value  in ret_data.items():
                    wexin(key,value)
        except Exception as e:
            logger.info(e)
        time.sleep(interval*60)
if __name__ == "__main__":
    main()





