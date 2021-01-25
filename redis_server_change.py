import redis
import pymysql
#import sqlite3
from redis.sentinel import Sentinel
#sentinel = Sentinel([('192.168.1.10', 26379)], socket_timeout=0.1)

###声明变量
dic_name_to_sentinel={}
num_of_sentinel=3 #判断每个redis的sentinel数
num_of_slave=2 #判断每个redis的slave数

###创建数据库连接
#conn = pymysql.connect(host='192.168.1.6', port=3306, user='mozis', passwd='ktlshy34YU$',db='server_change',charset="utf8")
#cursor = conn.cursor()
# 使用 execute()  方法执行 SQL 查询 
#cursor.execute("select 1;")
# 使用 fetchone() 方法获取单条数据.
#data = cursor.fetchall()
# 关闭数据库连接
#conn.close()

#取master0  mastername sentinel等信息
def all_sentinel_get():
    conn = pymysql.connect(host='192.168.1.6', port=3306, user='mozis', passwd='ktlshy34YU$',db='server_change',charset="utf8")
    cursor = conn.cursor()
    try:
        cursor.execute("truncate table redis_sentinel;")
    except pymysql.Error as e:
        return(e.args[0], e.args[1])
    r=redis.Redis(host='192.168.1.10',port=26379)
    #print(r.info(section=None)['master0']['name'])
    all=r.info(section='Sentinel')
    #print(r.info(section='Sentinel')['master0'])
    list_master_num=list(r.info(section='Sentinel').keys())
    master_num=list_master_num[4:]
    #print(master_num)
    for num in master_num:
        #print(i)
        name_sentinel=all[num]['name']
        num_sentinel=all[num]['sentinels']
        #print(num_sentinel)
        status_sentinel=all[num]['status']
        slave_sentinel=all[num]['slaves']
        try:
            cursor.execute("insert into redis_sentinel values('{0}','{1}','{2}','{3}','{4}');".format(num,name_sentinel,status_sentinel,slave_sentinel,num_sentinel))
            conn.commit()
        except:
            conn.rollback()
    conn.close()
    return("all get ok")


##删除不在列表里的sentinle name
def delete_no_use():
    conn = pymysql.connect(host='192.168.1.6', port=3306, user='mozis', passwd='ktlshy34YU$',db='server_change',charset="utf8")
    cursor = conn.cursor()
    list_table_name_tmp=[]
    try:
        f = open("/tools/python_test/python-redis/sentinle_name.txt")             # 返回一个文件对象  
    except IOError as e:
        #print(e)
        return(e)
    else:
        lines = f.readlines()
        for line in lines:
            list_table_name_tmp.append(line)
        f.close()
        list_table_name=[x.strip() for x in list_table_name_tmp]
        tuple_table_name=tuple(list_table_name)
        #print(tuple_table_name)
        try:
            #cursor.execute("select master_name from redis_sentinel where master_name not in {0};".format(tuple_table_name))
            #select_master_name_tmp = cursor.fetchall()
            cursor.execute("delete from redis_sentinel where master_name not in {0};".format(tuple_table_name))
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            conn.close()
            return(e.args[0], e.args[1])
        #conn.close()
        ###删除之后判断是否一致
        cursor.execute("select count(*) from redis_sentinel ;")
        count = cursor.fetchall()
        #print(count[0][0])
        len_table_name=len(list_table_name)
        #print(len_table_name)
        if count[0][0] == len_table_name:
            print("delete ok")
            conn.close()
            return 1
        else:
            conn.close()
            return ("delete error")
        #return("delete  ok")


##检查redis的sentinel数
def check_sentinel(num_of_sentinel):
    conn = pymysql.connect(host='192.168.1.6', port=3306, user='mozis', passwd='ktlshy34YU$',db='server_change',charset="utf8")
    cursor = conn.cursor()
    cursor.execute("select count(*) from redis_sentinel where sentinel != {0};".format(num_of_sentinel))
    count_sentinel = cursor.fetchall()
    #print(count_sentinel[0][0])
    if count_sentinel[0][0] == 0:
        conn.close()
        print("check sentinel ok")
        return 1
    else:
        cursor.execute("select master_name,sentinel from redis_sentinel where sentinel != {0};".format(num_of_sentinel))
        error_sentinel = cursor.fetchall()
        conn.close()
        #print(error_sentinel)
        for li in error_sentinel:
            #print (li)
            print("ERROR sentinel for {0} is {1}".format(li[0],li[1]))
        return 2


##检查redis的slave数
def check_slave(num_of_slave):
    conn = pymysql.connect(host='192.168.1.6', port=3306, user='mozis', passwd='ktlshy34YU$',db='server_change',charset="utf8")
    cursor = conn.cursor()
    cursor.execute("select count(*) from redis_sentinel where slave != {0};".format(num_of_slave))
    count_slave = cursor.fetchall()
    #print(count_sentinel[0][0])
    if count_slave[0][0] == 0:
        conn.close()
        print("check sentinel ok")
        return 1
    else:
        cursor.execute("select master_name,slave from redis_sentinel where slave != {0};".format(num_of_slave))
        error_slave = cursor.fetchall()
        conn.close()
        #print(error_sentinel)
        for li in error_slave:
            #print (li)
            print("ERROR slave for {0} is {1}".format(li[0],li[1]))
        return 2






def main():
    sentinel_get=all_sentinel_get()
    print(sentinel_get)
    delete_note=delete_no_use()
    if delete_note != 1:
        print("ERROR")
        return("ERROR")
    check_sentinel_note=check_sentinel(num_of_sentinel)
    if check_sentinel_note != 1:
        #print("ERROR")
        return("ERROR")
    check_slave_note=check_slave(num_of_slave)
    if check_slave_note != 1:
        #print("ERROR")
        return("ERROR")
    print("done")



if __name__ == "__main__":
    main() 