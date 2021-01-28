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
	masterid varchar(500) NOT NULL ,
	master_name varchar(500) NOT NULL DEFAULT 'NULL',
	status varchar(500) NOT NULL DEFAULT '0',
	slave_num int(10) NOT NULL DEFAULT '0',
	sentinel_num int(10) NOT NULL DEFAULT '0' ,
	old_master varchar(500) NOT NULL DEFAULT 'NULL' COMMENT '旧主',
	new_master varchar(500) NOT NULL DEFAULT 'NULL' COMMENT '新主',
	starttime datetime DEFAULT NULL COMMENT '开始操作时间',
	endtime datetime DEFAULT NULL COMMENT '结束操作时间',
	PRIMARY KEY (`masterid`)) 
	ENGINE=InnoDB
;

入库后信息过滤  删除后对比
2.检查主有几个sentinel
3.检查主有几个从
4.检查从是否在新设备列表
新redis录入该表
CREATE TABLE `redis_new_slave` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `master_name` varchar(500) NOT NULL DEFAULT 'NULL',
  `ip` varchar(30) NOT NULL DEFAULT 'NULL',
  `port` varchar(10) NOT NULL DEFAULT 'NULL',
  `role` varchar(10) NOT NULL DEFAULT 'NULL' COMMENT '设计角色 0代表新主  1代表新从 10代表原主 11代表原从',
  PRIMARY KEY (`id`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

insert into redis_new_slave(master_name,ip,port,role) values('mymaster','192.168.1.6','6380','0');
insert into redis_new_slave(master_name,ip,port,role) values('mymaster','192.168.1.6','6383','1');
insert into redis_new_slave(master_name,ip,port,role) values('mymaster','192.168.1.6','6379','10');
insert into redis_new_slave(master_name,ip,port,role) values('mymaster','192.168.1.6','6382','11');

架构一 需检查 redis_new_slave.role
5.检查切换权重参数（未测试）
6.切换
切换检测
7.再次通过sentinel查看主是否在 3步骤中
8.检查redis连接（使用get命令测试）
9.切换成功
```