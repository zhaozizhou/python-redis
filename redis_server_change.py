import redis
import os.path
import pymysql
from redis.sentinel import Sentinel
import datetime
import time
import argparse
from argparse import RawTextHelpFormatter
from tqdm import tqdm
import logging

###传入参数
def _argparse():
    head = '''--------------------------------------------------------------------------
                    5年设备替换 -- redis切换脚本
--------------------------------------------------------------------------'''
    example_text = '''examples:
    redis_server_change.py -w 10 -S 3 -s 3 -t check
    \n
'''
    parser = argparse.ArgumentParser(description=head,formatter_class=RawTextHelpFormatter, epilog=example_text)
    parser.add_argument('-w',dest='wait',required=True,help='切换等待时间')
    parser.add_argument('-S',dest='sentinel',required=True,help='切换所需sentinel个数')
    parser.add_argument('-s',dest='slave',required=True,help='每个master切换所需的slave个数')
    parser.add_argument('-t',choices=['check','execute'],default='check',dest='_type',required=True,help='检查check OR 执行切换execute')
    return parser.parse_args()

#取master0  mastername sentinel等信息
def all_sentinel_get():
    logger.info("===== START GET SENTINEL LIST =====")
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    try:
        cursor.execute("truncate table redis_sentinel;")
    except pymysql.Error as e:
        logger.error(e.args[0], e.args[1])
        return(e.args[0], e.args[1])
    r=redis.Redis(**redis_conf)
    #logger.debug(r.info(section=None)['master0']['name'])
    #logger.debug(r.info(section=None)['master0']['name'])
    all=r.info(section='Sentinel')
    print(all )
    list_master_num=list(r.info(section='Sentinel').keys())
    master_num=list_master_num[4:]
    logger.info("===== ALL SENTINEL LIST =====")
    logger.info(str(master_num))
    #for num in tqdm(master_num,desc="GET REDIS_MASTER_NAME"):
    for num in master_num:
        #print(num)
        name_sentinel=all[num]['name']
        num_sentinel=all[num]['sentinels']
        status_sentinel=all[num]['status']
        slave_sentinel=all[num]['slaves']
        address=all[num]['address']
        try:
            cursor.execute("insert into redis_sentinel(masterid,master_name,status,slave_num,sentinel_num,old_master) values('{0}','{1}','{2}','{3}','{4}','{5}');".format(num,name_sentinel,status_sentinel,slave_sentinel,num_sentinel,address))
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            conn.close()
            logger.error(e.args[0], e.args[1])
            return(e.args[0], e.args[1])
    conn.close()
    logger.info("===== SENTINEL GET OK =====")
    return(0)

##删除不在列表里的sentinle name
def delete_no_use():
    logger.info("===== START DELETE SENTINEL NO CHANGE =====")
    tuple_table_name=[]
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    list_table_name_tmp=[]
    try:
        f = open(file_sentinle_name)             # 返回一个文件对象  
    except IOError as e:
        logger.error(e)
        return(e)
    else:
        lines = f.readlines()
        for line in lines:
            list_table_name_tmp.append(line)
        f.close()
        #list_table_name=[x.strip() for x in list_table_name_tmp]
        #print(list_table_name)
        list_tmp1 = ""
        tuple_table_name = """''"""
        for list_table_name in list_table_name_tmp :
            list_table_name = list_table_name.strip("\n")
            list_tmp1 += "'{0}',".format(list_table_name)
            tuple_table_name = list_tmp1[0:-1]
        logger.info("===== ALL SENTINEL LIST =====")
        logger.info(tuple_table_name)
        try:
            #cursor.execute("select master_name from redis_sentinel where master_name not in {0};".format(tuple_table_name))
            #select_master_name_tmp = cursor.fetchall()
            cursor.execute("delete from redis_sentinel where master_name not in ({0});".format(tuple_table_name))
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            conn.close()
            logger.error(e.args[0], e.args[1])
            return(e.args[0], e.args[1])
        #conn.close()
        ###删除之后判断是否一致
        cursor.execute("select count(*) from redis_sentinel ;")
        count = cursor.fetchall()
        #print(count[0][0])
        len_table_name=len(list_table_name_tmp)
        #print(len_table_name)
        if count[0][0] == len_table_name:
            logger.info("===== DELETE OK =====")
            conn.close()
            return 0
        else:
            conn.close()
            logger.error("+++++ DELETE ERROR +++++")
            return 1
        #return("delete  ok")

##检查redis的sentinel数
def check_sentinel(num_of_sentinel):
    logger.info("===== START CHECK NUMBER OF SENTINEL =====")
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    cursor.execute("select count(*) from redis_sentinel where sentinel_num != {0};".format(num_of_sentinel))
    count_sentinel = cursor.fetchall()
    #print(count_sentinel[0][0])
    if count_sentinel[0][0] == 0:
        conn.close()
        logger.info("===== CHECK NUMBER OF SENTINEL OK =====")
        return 0
    else:
        cursor.execute("select master_name,sentinel_num from redis_sentinel where sentinel_num != {0};".format(num_of_sentinel))
        error_sentinel = cursor.fetchall()
        conn.close()
        #print(error_sentinel)
        for li in error_sentinel:
            #print (li)
            logger.error("+++++  sentinel for {0} is {1} +++++".format(li[0],li[1]))
        return 1

##检查redis的slave数
def check_slave(num_of_slave):
    logger.info("===== START CHECK NUMBER OF SLAVE =====")
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    cursor.execute("select count(*) from redis_sentinel where slave_num != {0};".format(num_of_slave))
    count_slave = cursor.fetchall()
    #print(count_sentinel[0][0])
    if count_slave[0][0] == 0:
        conn.close()
        logger.info("===== CHECK NUMBER OF SLAVE OK =====")
        return 0
    else:
        cursor.execute("select master_name,slave_num from redis_sentinel where slave_num != {0};".format(num_of_slave))
        error_slave = cursor.fetchall()
        conn.close()
        #print(error_sentinel)
        for li in error_slave:
            #print (li)
            logger.error("+++++  slave for {0} is {1} +++++".format(li[0],li[1]))
        return 1

#检查slave在不在列表中
def check_slave_in_new():
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    test_host='192.168.1.6'
    test_port=6379
    redis_conf={'host':test_host,'port':test_port,'decode_responses':True}
    r = redis.Redis(**redis_conf)
    all=dict(r.info(section='Replication'))
    #print(all)
    for key, value in all.items(): # iter on both keys and values 
        if key.startswith('slave'): 
            #print(key, value)
            tmp1=dict(value)
            #print(type(tmp1['ip']))
            port=value['port']
            if (str("192.168.1"))  in tmp1['ip']: #####该处填写新ip地址
                ip=value['ip']
            else:
                print("{0}:{1} is old slave ".format(value['ip'],port))
                continue
            #port=value['port']
            #print(port)
            state=value['state']
            if state == 'online':
                cursor.execute("select count(*) from redis_new_slave where ip='{0}' and port='{1}'".format(ip,port))
                count_slave_in_new = cursor.fetchone()
                if count_slave_in_new[0] == 1:
                    print("{0}:{1} in new".format(ip,port))
                elif count_slave_in_new[0] == 0:
                    print("ERROR ! {0}:{1} not in new".format(ip,port))
                else:
                    print("ERROR ! {0}:{1} not one of new is {2}".format(ip,port,count_slave_in_new[0]))
            elif state == 'offline':
                print("ERROR ! {0}:{1} status offline".format(ip,port))
            else:
                print("ERROR ! {0}:{1} status error is {2}".format(ip,port,state))

#根据表redis_new_slave检查参数
def config_check():
    logger.info("===== START CHECK REDIS CONFIG =====")
    tmp_error=0
    #redis_conf={'host':test_host,'port':test_port,'decode_responses':True}
    #mysql_conf={'host':'192.168.1.6', 'port':3306, 'user':'mozis', 'passwd':'ktlshy34YU$','db':'server_change','charset':"utf8"}
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from redis_new_slave;")
    all_redis=cursor.fetchall()
    for each_redis in all_redis:
        #print(each_redis)
        if each_redis['role'] == '10': ##原主
            master_name=each_redis['master_name']
            host=each_redis['ip']
            port=each_redis['port']
            redis_conf={'host':host,'port':port,'decode_responses':True}
            r = redis.Redis(**redis_conf)
            priority=r.config_get('slave-priority')
            #print(priority['slave-priority'])
            if priority['slave-priority'] == '50':
                logger.debug("redis [{0}] ({1}:{2}) [role:10] [slave-priority:50]".format(master_name,host,port))
                #tmp_error=0
                continue
            else:
                logger.warning("redis [{0}] ({1}:{2}) [role:10] slave-priority is not 50".format(master_name,host,port))
                #print("error {0}:{1} slave-priority is not 50".format(host,port))
                r.config_set('slave-priority','50')
                r.config_rewrite()
                logger.warning("redis [{0}] ({1}:{2}) [role:10] slave-priority is change to 50".format(master_name,host,port))
                #print(" {0}:{1} slave-priority is change to 50".format(host,port))
                tmp_error += 1
        elif each_redis['role'] == '11': ##原从
            master_name=each_redis['master_name']
            host=each_redis['ip']
            port=each_redis['port']
            redis_conf={'host':host,'port':port,'decode_responses':True}
            r = redis.Redis(**redis_conf)
            priority=r.config_get('slave-priority')
            #print(priority['slave-priority'])
            if priority['slave-priority'] == '50':
                logger.debug("redis [{0}] ({1}:{2}) [role:11] [slave-priority:50]".format(master_name,host,port))
                #continue
            else:
                logger.warning("redis [{0}] ({1}:{2}) [role:11] slave-priority is not 50".format(master_name,host,port))
                #print("error {0}:{1} slave-priority is not 50".format(host,port))
                r.config_set('slave-priority','50')
                r.config_rewrite()
                logger.warning("redis [{0}] ({1}:{2}) [role:11] slave-priority is change to 50".format(master_name,host,port))
                #print(" {0}:{1} slave-priority is change to 50".format(host,port))
                tmp_error += 1
            status=r.info(section='Replication')['master_link_status']
            #print(status)
            if status == 'up':
                logger.debug("redis [{0}] ({1}:{2}) is up".format(master_name,host,port))
                #print(22)
                #tmp_error=0
                continue
            else:
                logger.error("redis [{0}] ({1}:{2}) is down!!!".format(master_name,host,port))
                #print("error {0}:{1} slave status is down!!!".format(host,port))
                tmp_error += 1
        elif each_redis['role'] == '0': ##新主
            master_name=each_redis['master_name']
            host=each_redis['ip']
            port=each_redis['port']
            redis_conf={'host':host,'port':port,'decode_responses':True}
            r = redis.Redis(**redis_conf)
            priority=r.config_get('slave-priority')
            #print(priority['slave-priority'])
            if priority['slave-priority'] == '30':
                logger.debug("redis [{0}] ({1}:{2}) [role:0] [slave-priority:30]".format(master_name,host,port))
                #continue
            else:
                logger.warning("redis [{0}] ({1}:{2}) [role:0] slave-priority is not 30".format(master_name,host,port))
                #print("error {0}:{1} slave-priority is not 30".format(host,port))
                r.config_set('slave-priority','30')
                r.config_rewrite()
                logger.warning("redis [{0}] ({1}:{2}) [role:0] slave-priority is change to 30".format(master_name,host,port))
                #print(" {0}:{1} slave-priority is change to 30".format(host,port))
                tmp_error += 1
            status=r.info(section='Replication')['master_link_status']
            #print(status)
            if status == 'up':
                logger.debug("redis [{0}] ({1}:{2}) is up".format(master_name,host,port))
                #print(22)
                #tmp_error=0
                continue
            else:
                logger.error("redis [{0}] ({1}:{2}) is down!!!".format(master_name,host,port))
                #print("error {0}:{1} slave status is down!!!".format(host,port))
                tmp_error += 1
        elif each_redis['role'] == '1': ##新从
            master_name=each_redis['master_name']
            host=each_redis['ip']
            port=each_redis['port']
            redis_conf={'host':host,'port':port,'decode_responses':True}
            r = redis.Redis(**redis_conf)
            priority=r.config_get('slave-priority')
            #print(priority['slave-priority'])
            if priority['slave-priority'] == '70':
                logger.debug("redis [{0}] ({1}:{2}) [role:1] [slave-priority:70]".format(master_name,host,port))
                #continue
            else:
                logger.warning("redis [{0}] ({1}:{2}) [role:1] slave-priority is not 70".format(master_name,host,port))
                #print("error {0}:{1} slave-priority is not 70".format(host,port))
                r.config_set('slave-priority','70')
                r.config_rewrite()
                logger.warning("redis [{0}] ({1}:{2}) [role:1] slave-priority is change to 70".format(master_name,host,port))
                #print(" {0}:{1} slave-priority is change to 70".format(host,port))
                tmp_error += 1
            status=r.info(section='Replication')['master_link_status']
            #print(status)
            if status == 'up':
                logger.debug("redis [{0}] ({1}:{2}) is up".format(master_name,host,port))
                #print(22)
                #tmp_error=0
                continue
            else:
                logger.error("redis [{0}] ({1}:{2}) is down!!!".format(master_name,host,port))
                #print("error {0}:{1} slave status is down!!!".format(host,port))
                tmp_error += 1
        else:
            logger.error("mysql [redis_new_slave] ({0}) role error".format(each_redis))
            tmp_error += 1
    conn.close()
    if tmp_error == 0:
        logger.info("=====  CHECK REDIS CONFIG DONE =====")
        return(tmp_error)
    else:
        logger.error("+++++  CHECK REDIS CONFIG ERROR +++++")
        return(tmp_error)

#切换
def change():
    logger.info("=====  START CHANGE =====")
    change_error=0
    #sentinel = Sentinel([('192.168.1.10', 26379),('192.168.1.10', 26380),('192.168.1.10', 26382),],socket_timeout=0.5)
    #redis_conf={'host':'192.168.1.10','port':26379,'decode_responses':True}
    #mysql_conf={'host':'192.168.1.6', 'port':3306, 'user':'mozis', 'passwd':'ktlshy34YU$','db':'server_change','charset':"utf8"}
    conn = pymysql.connect(**mysql_conf)
    cursor = conn.cursor()
    cursor.execute("select master_name from redis_sentinel;")
    all_redis=cursor.fetchall()
    #print(all_redis)
    for change_sentinel in tqdm(all_redis,desc="CHANGING"):
        dt_begin=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        #print(change_sentinel[0])
        sentinelname=change_sentinel[0]
        #master = sentinel.discover_master(sentinelname)
        #print(master)
        #print(dt)
        sentinelname_1="'"+sentinelname+"'"
        try:
            cursor.execute("update redis_sentinel set starttime = {0} where master_name = {1};".format(dt_begin,sentinelname_1)) ######开始
            conn.commit()
        except pymysql.Error as e:
            logger.error(e.args[0], e.args[1])
            conn.rollback()
        r = redis.Redis(**redis_conf)
        p=r.sentinel_failover(sentinelname)
        #"failover",change_sentinel
        for i in range(number):
            time.sleep(1)
            if p == 'OK':
                #sentinelname_1="'"+sentinelname+"'"
                dict_mastername_address={}
                all=r.info(section='Sentinel')
                list_master_num=list(r.info(section='Sentinel').keys())
                master_num=list_master_num[4:]
                for num in master_num:
                    #print(num)
                    name_sentinel=all[num]['name']
                    address=all[num]['address']
                    dict_mastername_address[name_sentinel]=address
                #logger.debug(dict_mastername_address)
                address=''
                for key in dict_mastername_address:
                    if key == sentinelname:
                        address=dict_mastername_address[key]            
                #cursor.execute("select masterid from redis_sentinel where master_name = {0};".format(sentinelname_1))
                #masterid=cursor.fetchone()
                #print()
                #all=r.info(section='Sentinel')
                #print(all)
                #address=all[masterid[0]]['address']
                if address != '':
                    address_1="'"+address+"'"
                else:
                    logger.error("[{0}] in redis-sentinel ip addr error!".format(sentinelname))
                    change_error += 1
                    break
                try:
                    cursor.execute("update redis_sentinel set new_master = {0} where master_name = {1};".format(address_1,sentinelname_1))
                    conn.commit()
                except pymysql.Error as e:
                    print(e.args[0], e.args[1])
                    conn.rollback()
                cursor.execute("select old_master from redis_sentinel where master_name = {0};".format(sentinelname_1))
                tmp_old_master=cursor.fetchone()[0]
                cursor.execute("select new_master from redis_sentinel where master_name = {0};".format(sentinelname_1))
                tmp_new_master=cursor.fetchone()[0]
                #print(tmp_old_master)
                #print(tmp_new_master)
                if tmp_old_master != tmp_new_master:
                    dt_end=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    cursor.execute("update redis_sentinel set endtime = {0};".format(dt_end)) ######结束
                    conn.commit()
                    logger.info("change {0} ok !".format(sentinelname))
                    break
                else:
                    logger.debug(" {0} change checking ...".format(sentinelname))
            else:
                logger.error("[failover status check ] {0} sentinel failover error !".format(sentinelname))
                change_error += 1
                break
            timeout=i+1
            logger.debug("{0} change timeout = {1}".format(sentinelname,timeout))
            if timeout == number:    
                logger.error("[time out] {0} sentinel failover error !".format(sentinelname))
                change_error += 1
        if change_error >= 3:
            logger.critical("!!!!!!!!!! CHANGE ERROR MORETHAN 3!!!!!!!!!!")
            break
            #return(change_error)
    return(change_error)


#总检查
def all_check():
    check_error=0
    sentinel_get=all_sentinel_get()
    if sentinel_get != 0:
        check_error += 1
        logger.critical("{0} | sentinel get error".format(check_error))
    delete_note=delete_no_use()
    if delete_note != 0:
        check_error += 1
        logger.critical("{0} | delete  error".format(check_error))
    check_sentinel_note=check_sentinel(num_of_sentinel)
    if check_sentinel_note != 0:
        check_error += 1
        logger.critical("{0} | check sentinel  error".format(check_error))
    check_slave_note=check_slave(num_of_slave)
    if check_slave_note != 0:
        check_error += 1
        logger.critical("{0} | check slave  error".format(check_error))
    check_config=config_check()
    if check_config != 0:
        check_error += 1
        logger.critical("{0} | check config  error".format(check_error))   
    return(check_error)


def main():
    if tpye == 'check':
        check_error=all_check()
        if check_error == 0:
            logger.info("===== ALL CHECK DONE =====")
        else:
            logger.critical("+++++ CHECK ERROR {0} +++++".format(check_error))
            return 1
    elif tpye == 'execute':
        check_error=all_check()
        if check_error == 0:
            change_error=change()
            if change_error == 0:
                logger.info("===== ALL CHANGE DONE =====")
            else:
                logger.critical("+++++ CHANGE ERROR {0} +++++".format(change_error))
                return 1
        else:
            logger.critical("+++++ CHECK ERROR {0} +++++".format(check_error))
            return 1
    
if __name__ == "__main__":
    #全局参数
    parser=_argparse()
    tpye=parser._type#检查或者切换
    number = int(parser.wait) #切换后判断等待xxs
    num_of_sentinel=parser.sentinel #判断每个redis的sentinel数
    num_of_slave=parser.slave #判断每个redis的slave数
    file_sentinle_name='/data/python-redis/sentinle_name.txt' #sentinle_name文件位置
    redis_conf={'host':'192.168.1.10','port':26379,'decode_responses':True}
    mysql_conf={'host':'192.168.1.6', 'port':3306, 'user':'mozis', 'passwd':'ktlshy34YU$','db':'server_change','charset':"utf8"}
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Log等级总开关
    # 创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_path = os.getcwd()
    log_name = log_path + '/logs/redis_server_change_' + rq + '.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # 输出到console的log等级的开关
    # 定义handler的输出格式
    formatter = logging.Formatter("(%(funcName)s)[%(levelname)s]: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    main()
    #check_slave_in_new()