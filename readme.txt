Postgre 卡死时

psql -h 10.68.2.182  -U k2data -p 30012 -d ppa
SELECT pid,state FROM pg_stat_activity limit5;
可以杀死进程
select oid,relname from pg_class where relname='ppa';
select pg_terminate_backend('27493');

## 查看端口
lsof -i:8868 