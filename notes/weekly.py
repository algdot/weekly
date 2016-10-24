#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import logging
import sys
from slackclient import SlackClient
import time

class WeeklyNote:

    def __init__(self, user):
        self.i = -1;
        self.projects = [];
        self.user = user;

    def write(self, text, message_channel) :
        self.i +=1
        project = self.i/5;
        step = self.i %5;
        if step == 0 :
            if project > 0 :
                self.projects[project-1]['odds'] = text;
                client.rtm_send_message(message_channel, u'还有其他项目吗？【格式：项目名称/无】')
                return True
            client.rtm_send_message(message_channel, u'Hi, 我是周报小助手: \n 请问你本周做的项目是？')
            return True
        if step == 1 :
            if text == u'无':
                return False
            self.projects.append({'name' : text})
            client.rtm_send_message(message_channel, u'    %s 的进度？\n【格式：开发/测试/上线阶段：80%%】' % (text))
            return true
        if step == 2 :
            self.projects[project]['progress'] = text;
            client.rtm_send_message(message_channel, u'    %s 的本周进展是？\n 【格式：】\n - 任务一 \n - 任务二' % (self.projects[project]['name']));
            return true
        if step == 3 :
            self.projects[project]['accomplish'] = text;
            client.rtm_send_message(message_channel, u'    %s 的下周计划是？\n ' % (self.projects[project]['name']));
        if step == 4 :
            self.projects[project]['plan'] = text;
            client.rtm_send_message(message_channel, u'    %s 的遇到什么问题了吗？\n ' % (self.projects[project]['name']));


    def send(self, message_channel) :
        result = '';
        template = u'''
            * %s      \n
                %s    \n
                本周进展：  \n
                    %s      \n
                下周计划:   \n
                    %s      \n
                疑难杂症：  \n
                    %s      \n
        '''
        for p in self.projects :
            r = template % (p['name'], p['progress'], p['accomplish'], p['plan'], p['odds'])
            result += r
        client.rtm_send_message(message_channel, result)



#get your personal token from https://api.slack.com/web, bottom of the page.

api_key = sys.argv[1]; 
client = SlackClient(api_key)

weeklyNote = None

if client.rtm_connect():
    while True:
        last_read = client.rtm_read()
        if last_read:
            try:
                print last_read

                for msg in last_read:
                    if msg['type'] == 'message' and not 'bot_id' in msg:
                        text = msg['text']
                        message_channel = msg['channel']
                        if weeklyNote is not None:
                            r = weeklyNote.write(text, message_channel)
                            if not r :
                                weeklyNote.send(message_channel)
                                weeklyNote = None
                        if text and u'周报' in text:
                            weeklyNote = WeeklyNote('demo');
                            weeklyNote.write(text, message_channel)
            except :
                logging.exception('exception: ')
                pass
        time.sleep(1)

