Postgre ����ʱ

psql -h 10.68.2.182  -U k2data -p 30012 -d ppa
SELECT pid,state FROM pg_stat_activity limit5;
����ɱ������
select oid,relname from pg_class where relname='ppa';
select pg_terminate_backend('27493');

## �鿴�˿�
lsof -i:8868 