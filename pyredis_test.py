import redis
import os
from redis.sentinel import Sentinel
#
#sentinel = Sentinel([('192.168.1.10', 26379),('192.168.1.10', 26380),('192.168.1.10', 26381)],socket_timeout=0.5)
#
#master = sentinel.discover_master('mymaster')
##print(master)
#
#
#
#
#master = sentinel.master_for('mymaster',db=0,encoding='utf-8',decode_responses=True)#, socket_timeout=0.5
#
#slave = sentinel.slave_for('mymaster',db=0,encoding='utf-8',decode_responses=True)
#
#print(slave.info(section='Replication'))


#list1=[1,2,3,4,5,6,7,8,9,0]
#tablename="sbtest100"
##str4 = ','.join('%s' %id for id in list1)
#for ide in list1:
#    ide=str(ide)
#    #master.rpush(tablename,ide)
#
#len1=tuple(master.smembers(tablename))
#print(len1)
#for i in len1:
#    print(i)
#from tqdm import tqdm
#from random import random,randint
#import time
# 
##with trange(100) as t:
##  for i in t:
##    #设置进度条左边显示的信息
##    t.set_description("GEN %i"%i)
##    #设置进度条右边显示的信息
##    t.set_postfix(loss=random(),gen=randint(1,999),str="h",lst=[1,2])
##    time.sleep(0.1)
#a=1
#for i in tqdm(range(20), ascii=True,desc="1st loop"):
#  #for j in tqdm(range(10), ascii=True,desc="2nd loop"):
#    a += 1
#    print(a)
#    time.sleep(0.1)


#redis_conf={'host':'192.168.1.10','port':26379,'decode_responses':True}
#r=redis.Redis(**redis_conf)
##logger.debug(r.info(section=None)['master0']['name'])
##logger.debug(r.info(section=None)['master0']['name'])
#all=r.info(section='Sentinel')
#dict_mastername_address={}
#list_master_num=list(r.info(section='Sentinel').keys())
#master_num=list_master_num[4:]
#for num in master_num:
#    #print(num)
#    name_sentinel=all[num]['name']
#    address=all[num]['address']
#    dict_mastername_address[name_sentinel]=address
#print(dict_mastername_address)
#
#address=''
#for key in dict_mastername_address:
#    if key == 'mymaster+3':
#        #print(key+':'+dict_mastername_address[key])
#        address=dict_mastername_address[key]
#        print(address)
#        break
#
#if address == '':
#    print("mymaster in redis-sentinel ip addr error!")
#else:
#    address_1="'"+address+"'"
#    print(address_1)


#-*-coding:utf-8-*-
#import redis
# 连接池连接使用，节省了每次连接用的时间
#conn_pool = redis.ConnectionPool(host='192.168.1.6',port=6379)
## 第一个客户端访问
#re_pool = redis.Redis(connection_pool=conn_pool)
## 第二个客户端访问
#re_pool2 = redis.Redis(connection_pool=conn_pool)
## key value存储到redis数据库
#try:
#    re_pool.set('chinese1', 'hello_world')
#    re_pool2.set('chinese2', 'hello_python')
#except Exception as e:
#    print(e)
## 根据key获取存的数据的内容
#data_info = re_pool.get('chinese1')
#data_info2 = re_pool.get('chinese2')
## 输出从redis库中取出来的数据的内容
#print(data_info)
#print(data_info2)
## 获取两个连接的信息
#id1 = re_pool.client_list()
#id2 = re_pool2.client_list()
## 输出两个连接的id,判断是否一致
#print('re_pool_id{}======re_pool2_id{}'.format(id1[0]['id'], id2[0]['id']))
#print(id1)
#print(id2)

s = "China's Legend Holdings will split its several business arms to go public on stock markets, the group's president Zhu Linan said on Tuesday.该集团总 裁朱利安周二表示，中国联想控股将分拆其多个业务部门在股市上市。"
result = "".join(i for i in s if ord(i) > 256)
print(result)


redis_ip='192.168.1.6'
redis_port='6379'
reids_1= "redis-cli -h %s -p %s client list |awk -F ' ' '{print $2}' |awk -F '=' '{print $2}'|awk -F ':' '{print $1}'|sort |uniq -c|sort -n|grep -v 127.0.0.1 |grep -v 192 |grep -v  172.28.48 |awk -F ' ' '{ print $2 }'"%(redis_ip,redis_port)
client_ip=os.popen(reids_1).readlines()
print(client_ip)

if len(client_ip) == 0:
    print('1')
