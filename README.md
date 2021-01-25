# 解决redis设备替换问题

```
1.sentinel name  表
2.老设备列表
3.新设备列表
```

## 流程

```
1.取sentinel列表值找到目前的redis主
  信息存入数据库  
  库名 server_change
  
create table redis_sentinel (
	id varchar(500) NOT NULL ,
	master_name varchar(500) NOT NULL DEFAULT 'NULL',
	status varchar(500) NOT NULL DEFAULT '0',
	slave int(10) NOT NULL DEFAULT '0',
	sentinel int(10) NOT NULL DEFAULT '0' ,PRIMARY KEY (`id`)) 
	ENGINE=InnoDB
;

入库后信息过滤  删除后对比
2.检查主有几个sentinel
3.检查主有几个从
4.检查从是否在新设备列表
5.检查切换权重参数（未测试）
6.切换
7.再次通过sentinel查看主是否在 3步骤中
8.检查redis连接（使用get命令测试）
9.切换成功
```