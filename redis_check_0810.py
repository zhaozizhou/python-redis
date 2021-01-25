#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import subprocess
import pymysql
import time

db = pymysql.connect(host='172.29.60.184', port=3306, user='mozis', passwd='ktlshy34YU$',db='mozis_paas',charset="utf8")
cursor = db.cursor()
# 使用 execute()  方法执行 SQL 查询 
#cursor.execute("select a.name from service a where a.db_type = 'Redis' and a.topology = 'RedisMasterSlave' group by name;")
cursor.execute("select a.name from service a where a.db_type = 'Redis' group by name;")
# 使用 fetchone() 方法获取单条数据.
RedisMasterSlave_mastername = cursor.fetchall()
db.close()



def redis_check():
    reids_role=""
    reids_role_cmd= "redis-cli -h %s -p %s info Replication |grep role |awk -F ':' '{ print $2 }'"%(redis_ip,redis_port)
    try:
        reids_role_tmp=os.popen(reids_role_cmd).readlines()
        reids_role=str(reids_role_tmp[0]).strip("\n")
    except Exception as e:
        print(e)
    #print(redis_ip,redis_port,reids_role)
    if reids_role == "master" :
        reids_1= "redis-cli -h %s -p %s client list |awk -F ' ' '{print $2}' |awk -F '=' '{print $2}'|awk -F ':' '{print $1}'|sort |uniq -c|sort -n|grep -v 127.0.0.1 |grep -v 172.29 |grep -v  172.28.48 |awk -F ' ' '{ print $2 }'"%(redis_ip,redis_port)
        redis_ops_tmp1="redis-cli -h %s -p %s info stats |grep total_commands_processed |awk -F ':' '{ print $2 }'"%(redis_ip,redis_port)
        redis_ops_tmp1_tmp=os.popen(redis_ops_tmp1).readlines()
        redis_ops_tmp1=str(redis_ops_tmp1_tmp[0]).strip("\n")
        time.sleep(1)
        redis_ops_tmp2="redis-cli -h %s -p %s info stats |grep total_commands_processed |awk -F ':' '{ print $2 }'"%(redis_ip,redis_port)
        redis_ops_tmp2_tmp=os.popen(redis_ops_tmp2).readlines()
        redis_ops_tmp2=str(redis_ops_tmp2_tmp[0]).strip("\n")
        redis_ops=int(redis_ops_tmp2)-int(redis_ops_tmp1)
        #print(redis_ops)
        redis_used_mem="redis-cli -h %s -p %s info Memory |grep used_memory_human |awk -F ':' '{ print $2 }'"%(redis_ip,redis_port)
        redis_used_mem_tmp=os.popen(redis_used_mem).readlines()
        redis_used_mem=str(redis_used_mem_tmp[0]).strip("\n")
        #print(redis_used_mem)
        redis_max_mem="redis-cli -h %s -p %s config get maxmemory |sed -n '2p'"%(redis_ip,redis_port)
        redis_max_mem_tmp=os.popen(redis_max_mem).readlines()
        redis_max_mem=str(redis_max_mem_tmp[0]).strip("\n")
        #print(redis_max_mem)
        client_ip=os.popen(reids_1).readlines()
        ip_list = ""
        ip_list_2 = """''"""
        for app_ip in client_ip :
            app_ip = app_ip.strip("\n")
            ip_list += "'{0}',".format(app_ip)
            ip_list_2 = ip_list[0:-1]
        sql = "select distinct A_name,owner from v_app_node4 where B_busi_ip in ({0})".format(ip_list_2)
        app_name_tmp = os.popen('mysql -h 172.29.25.54 -P3306 -umozis -p"ktlshy34YU$" -A night_watcher -N -e "{0}"'.format(sql)).readlines()
        #print(app_name_tmp)
        app_set = set()
        map_mastername_appname = {}
        for app_name in app_name_tmp:
            app_name = str(app_name).strip('\n')
            app_set.add(app_name)
            map_mastername_appname[tmp_1] = (redis_ip,redis_port,redis_ops,redis_used_mem,redis_max_mem,app_set,)
        for item in map_mastername_appname[tmp_1]:
            key = tmp_1[0:-1]         
            print(item[5])
            print(type(item[5]))
            for i in item[5]:
                print ("{0},{1},{2},{3},{4},{5},{6}".format(key,item[0],item[1],item[2],item[3],item[4],i)) 




#dict_RedisMasterSlave_host={}
for tmp_1 in RedisMasterSlave_mastername :
    db = pymysql.connect(host='172.29.60.184', port=3306, user='mozis', passwd='ktlshy34YU$',db='mozis_paas',charset="utf8")
    #cursor_owner = db.cursor()
    #cursor_owner.execute("select owner from service,db_schema,product where db_schema.service = service.id and product.id = db_schema.product and service.name=('%s') and owner != ('毛震鹏') group by owner;"%(tmp_1))
    #RedisMasterSlave_owner = cursor_owner.fetchall()
    cursor_host = db.cursor()
    cursor_host.execute("select c.data_ip,a.service_name,a.topology from service a,instance b,host c where a.id = b.service and b.host = c.id and a.db_type = 'Redis' and a.name = ('%s') and c.data_ip not in('172.29.48.224') group by data_ip;"%(tmp_1))
    #cursor_host.execute("select c.data_ip,a.service_name,a.topology from service a,instance b,host c where a.id = b.service and b.host = c.id and a.db_type = 'Redis' and a.topology = 'RedisMasterSlave'and a.name = ('%s');"%(tmp_1))
    RedisMasterSlave_host = cursor_host.fetchall()
    db.close()
    #print(RedisMasterSlave_host)
    #break
    #dict_RedisMasterSlave_owner[tmp_1]=(RedisMasterSlave_owner,RedisMasterSlave_host)
    #print(RedisMasterSlave_host)
    for tmp_2 in RedisMasterSlave_host :
        redis_type=tmp_2[2]
        if redis_type == "RedisMasterSlave" :
            #print(tmp_2)
            redis_ip=tmp_2[0]
            redis_port=tmp_2[1]
            redis_check()
            #print("redis_check_RedisMasterSlave")
            break
        elif redis_type == "RedisCluster" :
            redis_ip=tmp_2[0]
            redis_port_tmp=tmp_2[1]
            redis_port=redis_port_tmp.split('-')
            redis_port_num=int(redis_port[1])-int(redis_port[0])
            redis_port_num_tmple=0
            redis_port_num_tmp=int(redis_port[0])
            while redis_port_num_tmple <= redis_port_num :
                redis_port=redis_port_num_tmp
                redis_port_num_tmp=int(redis_port_num_tmp)+1
                redis_port_num_tmple=redis_port_num_tmple+1
                redis_check()
                #print("redis_check_RedisCluster")
                #break
            break
    #break






