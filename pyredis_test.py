import redis
from redis.sentinel import Sentinel

sentinel = Sentinel([('192.168.1.10', 26379),('192.168.1.10', 26380),('192.168.1.10', 26381)],socket_timeout=0.5)

master = sentinel.discover_master('mymaster')
#print(master)




master = sentinel.master_for('mymaster',db=0,encoding='utf-8',decode_responses=True)#, socket_timeout=0.5



list1=[1,2,3,4,5,6,7,8,9,0]
tablename="sbtest100"
#str4 = ','.join('%s' %id for id in list1)
for ide in list1:
    ide=str(ide)
    #master.rpush(tablename,ide)

len1=tuple(master.smembers(tablename))
print(len1)
for i in len1:
    print(i)
