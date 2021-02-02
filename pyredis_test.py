#import redis
#from redis.sentinel import Sentinel
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
from tqdm import tqdm
from random import random,randint
import time
 
#with trange(100) as t:
#  for i in t:
#    #设置进度条左边显示的信息
#    t.set_description("GEN %i"%i)
#    #设置进度条右边显示的信息
#    t.set_postfix(loss=random(),gen=randint(1,999),str="h",lst=[1,2])
#    time.sleep(0.1)
a=1
for i in tqdm(range(20), ascii=True,desc="1st loop"):
  #for j in tqdm(range(10), ascii=True,desc="2nd loop"):
    a += 1
    print(a)
    time.sleep(0.1)