Postgre ����ʱ

10.68.2.168  30012

psql -h 10.68.2.182  -U k2data -p 30012 -d ppa


�鿴pg����
df = pd.read_sql_query("SELECT datname,pid,state,query from pg_stat_activity where datname = 'ppa' ",con =conn.obj.conn)
ɱ��pg����
select pg_terminate_backend('27493');


ǰ�˵�ַ ��http://10.68.2.38:8868/

## �鿴�������˿�ռ��
lsof -i:8868 

shellɱ������������
kill 9 pid

����ǰ�� ����  ����ִ̨��
cd /root/ppa/
nohup bash runserver.sh

����ETL����
cd /root/ppa/muradefect/server/


cycleid �߼�У��





