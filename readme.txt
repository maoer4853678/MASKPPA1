Postgre 卡死时

10.68.2.168  30012

psql -h 10.68.2.182  -U k2data -p 30012 -d ppa


查看pg进程
df = pd.read_sql_query("SELECT datname,pid,state,query from pg_stat_activity where datname = 'ppa' ",con =conn.obj.conn)
杀死pg进程
select pg_terminate_backend('27493');


前端地址 ：http://10.68.2.38:8868/

## 查看服务器端口占用
lsof -i:8868 

shell杀死服务器进程
kill 9 pid

开启前端 程序  并后台执行
cd /root/ppa/
nohup bash runserver.sh

数据ETL程序：
cd /root/ppa/muradefect/server/


cycleid 逻辑校验





