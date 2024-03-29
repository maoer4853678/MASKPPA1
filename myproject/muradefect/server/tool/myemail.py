    
import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class SendMail(object):
    def __init__(self, username, passwd, recv, title, content,images=[],
                 file=None, ssl=False,
                 email_host='smtp.163.com', port=25, ssl_port=465):
        '''
        :param username: 用户名
        :param passwd: 密码 此处开启了smtp之后的密码是授权码
        :param recv: 收件人，多个要传list ['a@qq.com','b@qq.com]
        :param title: 邮件标题
        :param content: 邮件正文
        :param file: 附件路径，如果不在当前目录下，要写绝对路径，默认没有附件
        :param ssl: 是否安全链接，默认为普通
        :param email_host: smtp服务器地址，默认为163服务器
        :param port: 非安全链接端口，默认为25
        :param ssl_port: 安全链接端口，默认为465
        '''
        self.username = username  # 用户名
        self.passwd = passwd  # 密码
        self.recv = recv  # 收件人，多个要传list ['a@qq.com','b@qq.com]
        self.title = title  # 邮件标题
        self.content = content  # 邮件正文
        self.images = images
        self.file = file  # 附件路径，如果不在当前目录下，要写绝对路径
        self.email_host = email_host  # smtp服务器地址
        self.port = port  # 普通端口
        self.ssl = ssl  # 是否安全链接
        self.ssl_port = ssl_port  # 安全链接端口

    def send_mail(self):
        msg = MIMEMultipart()
        # 发送内容的对象
        if self.file:  # 处理附件的
            file_name = os.path.split(self.file)[-1]  # 只取文件名，不取路径
            try:
                f = open(self.file, 'rb').read()
            except Exception as e:
                raise Exception('附件打不开！！！！')
            else:
                att = MIMEText(f, "base64", "utf-8")
                att["Content-Type"] = 'application/octet-stream'
                # base64.b64encode(file_name.encode()).decode()
                new_file_name = '=?utf-8?b?' + base64.b64encode(file_name.encode()).decode() + '?='
                # 这里是处理文件名为中文名的，必须这么写
                att["Content-Disposition"] = 'attachment; filename="%s"' % (new_file_name)
                msg.attach(att)
        msg.attach(MIMEText(self.content))  # 邮件正文的内容
        
        if len(self.images):
            for i,image in enumerate(self.images):
                send_str = '<html><body>'
                send_str += '<left>%s</left>'%(image['content'])
                
                # html中以<img>标签添加图片，align和width可以调整对齐方式及图片的宽度
                send_str += '<img src="cid:%s" alt="%s" align="center" width=100%% >'%\
                            ("image%d"%i,"image%d"%i)
                            
                send_str +='<HR style="border:2 dashed #987cb9" width="100%" color=#987cb9 SIZE=1>'
                send_str += '</body></html>'
          
                # 添加邮件内容
                content = MIMEText(send_str, _subtype='html', _charset='utf8')
                msg.attach(content)
                
                try:
                    img1 = MIMEImage(open(image['file'], 'rb').read(), _subtype='octet-stream')
                    img1.add_header('Content-ID', "image%d"%i)
                    msg.attach(img1)
                except:
                    pass

        msg['Subject'] = self.title  # 邮件主题
        msg['From'] = self.username  # 发送者账号
        msg['To'] = ','.join(self.recv)  # 接收者账号列表
        if self.ssl:
            self.smtp = smtplib.SMTP_SSL(self.email_host, port=self.ssl_port)
        else:
            self.smtp = smtplib.SMTP(self.email_host, port=self.port)
        # 发送邮件服务器的对象
        self.smtp.login(self.username, self.passwd)
        try:
            self.smtp.sendmail(self.username, self.recv, msg.as_string())
            pass
        except Exception as e:
            msg = '发送失败 错误代码:%s'%e
        else:
            msg ='发送成功！'
        self.smtp.quit()
        return msg

# if __name__ == '__main__':
#     date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
#     m = SendMail(
#         username='edong_2019@163.com',
#         # 此处开启了smtp之后的密码变化为授权码,如何开启smtp授权请自行百度
#         passwd='v123456789',
#         recv=['dongzhaoyu@k2data.com.cn','edong@visionox.com'],
#         title=date + 'PPA报警',
#         content='PPAX 报警 报警测试',
#         # 发送的附件，可以为不写
#         # file=r'a.txt',
#         ssl=True,
#     )
#     msg = m.send_mail()