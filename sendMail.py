#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
from loop_timer import LoopTimer
import smtplib
#from smtplib import SMTP_SSL  
from email.mime.text import MIMEText
import logging
import datetime



mailto_list=["yckj_jxg@163.com"] #邮件通知（默认支持163邮箱，需要开通smtp,pop服务）
mail_host="smtp.163.com"  #设置服务器
mail_user="yckj_jxg@163.com"    #用户名
mail_pass="yckj123456"   #口令
mail_postfix="163.com"  #发件箱的后缀


start_point=0

keyvalue ='主链路连接已断开'  #匹配的关键字
keyfile = "/home/logs/bh-led-dxs"   #监测的日志文件
logfile = '/home/logs/bh.log'       #输出的日志文件

logging.basicConfig(level=logging.INFO,  
                    format='%(asctime)s %(levelname)s %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S', #返回2016/05/26 03:12:56 PM
                    filename=logfile#,  
                   ) 


def send_mail(to_list,sub,content):  #to_list：收件人；sub：主题；content：邮件内容
    me="系统运维"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='gb2312')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = sub    #设置主题
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    try:
        s = smtplib.SMTP(host='smtp.163.com')
        s.connect(mail_host,25)  #连接smtp服务器

        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me,to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except smtplib.SMTPException as e:  
        #print(str(e))
        logging.info(str(e))
        return False



def read_logs():
    fo = open("/home/logs/bh-led-dxs","rb") # 一定要用'rb'因为seek 是以bytes来计算的
    #print ("文件名为: ", fo.name)
    global start_point  #使用全局变量，让start_point 时刻保持在已经输出过的那个字节位
    fo.seek(start_point, 1)#移动文件读取指针到指定位置 
    
    #生成一个新文件，专门用于分析
    with open('/home/logs/obj.log','a+') as f1:
        for line in fo.readlines():
            #print ("读取的数据为:" + str(line.decode()))
            f1.writelines(str(line.decode()))

    #输出后的指针位置赋值给start_piont
    start_point=fo.tell()
    fo.close()


def led_chk():
    #print('开始转存日志....') 
    #logging.info('开始转存日志....')
    #read_logs()
    #print('转存日志结束....')
    #logging.info('转存日志结束....')

    #print('LED链路检测开始....')
    logging.info('LED链路检测开始....')

    fo = open(keyfile,"rb") # 一定要用'rb'因为seek 是以bytes来计算的
    #print ("文件名为: ", fo.name)
    global start_point  #使用全局变量，让start_point 时刻保持在已经输出过的那个字节位
    
    #范围时间
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'00:00', '%Y-%m-%d%H:%M')
    d_time1 =  datetime.datetime.strptime(str(datetime.datetime.now().date())+'00:01', '%Y-%m-%d%H:%M')
 
    #当前时间
    n_time = datetime.datetime.now()
    #判断当前时间是否在范围时间内
    if n_time > d_time and n_time<d_time1:
        start_point=0

    fo.seek(start_point, 1)#移动文件读取指针到指定位置 

 
    for line in fo.readlines():
        #line = line.strip() 
        str_line = str(line.decode())
        str_line= str_line.strip() 
        flag = str_line.find(keyvalue)  #主链路连接已断开
        #print(str_line)
        #flag = 0
        if(flag != -1):
            #print('LED链路异常，准备发送告警邮件给值班人员')
            logging.info('LED链路异常，准备发送告警邮件给值班人员')
            suc = send_mail(mailto_list,"LED广告平台链路异常告警(正式消息)","LED平台链路出现异常，请检查网络通信或重启相关软件")
            #print('邮件发送结果：%s'%(suc))
            logging.info('邮件发送结果：%s'%(suc))
            break


    #输出后的指针位置赋值给start_piont
    start_point=fo.tell()
    fo.close()

    #print('LED链路检测结束....')
    logging.info('LED链路检测结束....\n')


if __name__ == '__main__':
    t = LoopTimer(15, led_chk)
    t.start()



