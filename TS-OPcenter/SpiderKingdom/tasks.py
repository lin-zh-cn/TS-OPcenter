from __future__ import absolute_import, unicode_literals

from celery import shared_task

import smtplib
from email.mime.text import MIMEText
from email.header import Header


sender = 'mingdeop@sina.com'
user = 'mingdeop@sina.com'
password = 'kemingjunde!@#'
smtp_server = 'smtp.sina.com'

@shared_task()
def send_mail(title,content):
    try:
        message = MIMEText(content,'html','utf-8')
        message['From'] = Header(sender)
        message['To'] = Header('警告信息','utf-8')

        subject = title

        message['Subject'] = Header(subject,'utf-8')

        server = smtplib.SMTP_SSL(smtp_server,465)
        server.login(user,password)
        server.sendmail(sender,['4929600429@qq.com'],message.as_string())
        return True
    except smtplib.SMTPException as e:
        return False
    except smtplib.SMTPDataError as e:
        return False



