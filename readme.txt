Postgre 卡死时

可以杀死进程
select oid,relname from pg_class where relname='ppa';
select pg_terminate_backend('27493');