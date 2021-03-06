# !/usr/bin/env python
#-*- coding: utf-8 -*-
#=============================================================================
#     FileName: check_data.py
#         Desc:
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      Version: 0.0.1
#   LastChange: 2014-09-03
#      History: 
#=============================================================================

import re

#初始化ip库
from api.QQWry import *

#导入白名单
from config.whiteurl import *
import acl
from sqlalchemy.orm import sessionmaker
from database.db import Hack, session


tt = IPSearch('api/QQWry.Dat')

class hack_filter:
    """
    黑客数据行为分析
    user-agent, cookies, uri, body
    匹配特征即触发上报机志
    """

    def __init__(self, http_data):
        self.uri = http_data.uri
        user_agent_data = http_data.headers.get("user-agent", False)
        if user_agent_data:
            self.user_agent = http_data.headers["user-agent"]
        else:
            self.user_agent = "None"
        if http_data.headers.get("cookie"):
            self.cookie = http_data.headers["cookie"]
        else:
            self.cookie = False
        if http_data.body:
            self.body = http_data.body
        else:
            self.body = False

    def run(self):
        """
        开始匹配分析
        """
        if self.cookie:
            for rule in acl.cookie_acl:
                #result = re.compile(rule).findall(self.cookie)
                #if result:
                #    return {"status": True, "acl": rule}
                try:
                    result = re.compile(rule).findall(self.cookie)
                    if result:
                        return {"status": True, "acl": rule}
                except Exception, e:
                    result = re.compile(rule).findall(','.join(self.cookie))
                    if result:
                        return {"status": True, "acl": rule}
        if self.body:
            for rule in acl.post_acl:
                result = re.compile(rule).findall(self.body)

                if result:
                    return {"status": True, "acl": rule}

        for rule in acl.args:
            result = re.compile(rule).findall(self.uri)
            if result:
                return {"status": True, "acl": rule}


        for rule in acl.useragent:
            result = re.compile(rule).findall(self.user_agent)
            if result:
                return {"status": True, "acl": rule}

        for rule in acl.url_list:
            result = re.compile(rule).findall(self.uri)
            if result:
                return {"status": True, "acl": rule}

        return {"status": False, "message": "no find acl"}

class hackerinfo:
    """
    黑客详细信息分析
    """
    def __init__(self, http_data, acl, src_ip, src_time):
        self.uri = http_data.uri
        self.user_agent = http_data.headers["user-agent"]
        self.src_ip = src_ip
        self.src_time = src_time
        self.host = http_data.headers["host"]
        self.method = http_data.method
        self.acl = acl
        self.headers = http_data.headers

        if http_data.headers.get("cookie"):
            self.cookie = http_data.headers["cookie"]
        else:
            self.cookie = ""
        if http_data.body:
            self.body = http_data.body
        else:
            self.body = ""

    def run(self):
        """
        黑客详细信息
        :return:
        """


        if self.method == 'POST':


            city_data = tt.find(self.src_ip)
            hacker_city = unicode(city_data[0], 'gb2312').encode('utf-8')
            hacker_addr = unicode(city_data[1], 'gb2312').encode('utf-8')
            domain = "http://%s%s" % (self.host, self.uri)

            s = "时间: %s\n" \
                "攻击URL: %s\n" \
                "域名: %s\n" \
                "攻击ip: %s\n" \
                "攻击所在地: %s%s\n" \
                "User-Agent: %s\n" \
                "状态: POST\n" \
                "提交数据: %s\n" \
                "详细信息: %s\n" \
                "匹配规则: %s\n--------------------------------------\n" % \
                (self.src_time, domain, self.host, self.src_ip, hacker_city, hacker_addr, self.user_agent, self.body, self.headers, self.acl)
            try:
                hack_db = Hack(src_time=self.src_time, url=domain, hack_city=hacker_city, hack_addr=hacker_addr,
                               method="POST", host=self.host, ip=self.src_ip, acl=str(self.acl), headers=str(self.headers),
                               user_agent=self.user_agent, cookie=self.cookie, post_data=self.body)
                session.add(hack_db)
                session.commit()
            except Exception, e:
                print e
            return s

        else:
            city_data = tt.find(self.src_ip)
            hacker_city = unicode(city_data[0], 'gb2312').encode('utf-8')
            hacker_addr = unicode(city_data[1], 'gb2312').encode('utf-8')
            domain = "http://%s%s" % (self.host, self.uri)

            s = "时间: %s\n" \
                "攻击URL: %s\n" \
                "域名: %s\n" \
                "攻击ip: %s\n" \
                "攻击所在地: %s%s\n" \
                "User-Agent: %s\n" \
                "状态: GET\n" \
                "详细信息: %s\n" \
                "匹配规则: %s\n--------------------------------------\n" % \
                (self.src_time, domain, self.host, self.src_ip, hacker_city, hacker_addr, self.user_agent, self.headers, self.acl)
            try:
                hack_db = Hack(src_time=self.src_time, url=domain, hack_city=hacker_city, hack_addr=hacker_addr,
                               method="GET", host=self.host, ip=self.src_ip, acl=str(self.acl), headers=str(self.headers),
                               user_agent=self.user_agent, cookie=self.cookie)
                session.add(hack_db)
                session.commit()
            except Exception, e:
                print e
            return s
