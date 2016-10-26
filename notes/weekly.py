#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
from slackclient import SlackClient
import time
import datetime
import smtplib
from email.mime.text import MIMEText



class WeeklyNote:

    default_date_format = '%Y-%m-%d';

    def __init__(self, user, client, channel):
        self.i = -1;
        self.projects = [];
        self.user = user;
        self.client = client;
        self.channel = channel;
        self.result = '';

    def write(self, text) :
        self.i +=1
        project = self.i/5;
        step = self.i %5;
        if step == 0 and project > 0 :
            self.projects[project-1]['odds'] = text.splitlines();
            self.client.rtm_send_message(self.channel, u'还有其他项目吗？【格式：项目名称/无】')
            return True
        if step == 1 and text == u'无':
            return False

        if step == 0 :
            self.client.rtm_send_message(self.channel, u'Hi, 我是周报小助手: \n 请问你本周做的项目是？')
            return True
        if step == 1 :
            self.projects.append({'name' : text})
            self.client.rtm_send_message(self.channel, u'    %s 的进度是？\n【格式：开发/测试/上线，80%%；正常/延期】' % (text))
            return True
        if step == 2 :
            self.projects[project]['progress'] = text;
            self.client.rtm_send_message(self.channel, u'    %s 的本周进展是？\n 【格式：】\n  任务一 \n  任务二' % (self.projects[project]['name']));
            return True
        if step == 3 :
            self.projects[project]['accomplish'] = text.splitlines();
            self.client.rtm_send_message(self.channel, u'    %s 的下周计划是？\n ' % (self.projects[project]['name']));
            return True
        if step == 4 :
            self.projects[project]['plan'] = text.splitlines();
            self.client.rtm_send_message(self.channel, u'    %s 的疑难杂症有？\n ' % (self.projects[project]['name']));
            return True

    def sendConfirm(self):
        template = u'''
* %s
    %s
    本周进展：
       - %s
    下周计划:
       - %s
    疑难杂症:
       - %s
'''
        blank = '\n        - '
        for p in self.projects :
            r = template % (p['name'], p['progress'], blank.join(p['accomplish']), blank.join(p['plan']), blank.join(p['odds']))
            self.result += r
        print self.result
        self.client.rtm_send_message(self.channel, self.result)
        self.client.rtm_send_message(self.channel, '请确认是否正确，回复【ok】发送邮件，否则重写。')

    def sendMail(self):
        sender = 'no-reply@domain.com'
        receivers = ['test@domain.com']

        today = datetime.date.today()
        weekday = today.weekday()
        # default start_day is monday, end_day is friday
        start_day = today- datetime.timedelta(weekday)
        end_day = start_day + datetime.timedelta(5)

        msg = MIMEText(self.result.encode('utf-8'),_subtype='plain',_charset='utf-8')
        msg['From'] = sender
        msg['Subject'] = '基础平台研发部周报-%s（%s~%s）' % (self.user, start_day.strftime(WeeklyNote.default_date_format), end_day.strftime(WeeklyNote.default_date_format))
        msg['To'] = ";".join(receivers)
        smtpObj = smtplib.SMTP('mail.domain.com')
        smtpObj.sendmail(sender, receivers, msg.as_string())
        smtpObj.quit()
        self.client.rtm_send_message(self.channel,'邮件发送成功')

def main():
    #get your personal token from https://api.slack.com/web, bottom of the page.

    api_key = sys.argv[1];
    client = SlackClient(api_key)

    weeklyNotes= {}

    if client.rtm_connect():
        while True:
            last_read = client.rtm_read()
            if last_read:
                try:
                    print str(last_read).encode('utf-8')

                    for msg in last_read:
                        if "type" in msg.keys() and msg['type'] == 'message':
                            text = msg['text']
                            message_channel = msg['channel']
                            user = msg['user']
                            if u'重写周报' in text:
                                del weeklyNotes[user]
                            if user in weeklyNotes:
                                if weeklyNotes[user]['writing']:
                                   weeklyNotes[user]['writing'] = weeklyNotes[user]['wn'].write(text)
                                   if not weeklyNotes[user]['writing']:
                                        weeklyNotes[user]['wn'].sendConfirm()
                                        weeklyNotes[user]['waitConfirm'] = True
                                elif weeklyNotes[user]['waitConfirm'] and 'ok' in text.lower():
                                    weeklyNotes[user]['wn'].sendMail();
                                    del weeklyNotes[user]
                                else:
                                    client.rtm_send_message(message_channel, '请重新周报');
                                continue
                            # entry
                            if text and u'周报' in text:
                                weeklyNote = WeeklyNote('demo', client, message_channel);
                                weeklyNote.write(text)
                                weeklyNotes[user] = {'wn': weeklyNote, 'writing': True, 'waitConfirm': False}
                except :
                    logging.exception('exception: ')
                    pass
            time.sleep(1)


if __name__ == '__main__':
    main()
