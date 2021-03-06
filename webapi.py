#coding:utf-8
'''
Created on 2016年10月6日
@author: 肖雄
'''

import web
from wxlogin import *
from pprint import pprint
import threading
import Queue



web.config.debug = False

q_timer = Queue.PriorityQueue()

urls = (
    '/msg/','MsgApi',
    '/reply/','AutoReplyApi',
    '/groupLists/','GroupListsApi',
    '/group/','GroupApi',
    '/contactList/','ContactListApi',
    '/timemsg/','TimeMsgApi',
    )

class AutoReplyApi():
    '''
    AutoReplyApi 对自动回复状态进行操作
    GET 方法查看自动回复状态，返回json格式的自动回复状态
    POST 字段reply对自动回复状态进行更改，返回json格式的自动回复状态['操作boolean','状态']
    True为开启，False为关闭
    '''
    
    def GET(self):
        return json.dumps(webwx.autoReplyMode)

    
    def POST(self):
        data = web.data()
        data = data.decode('utf-8')
        data = json.loads(data)
        try:
            webwx.reply_change(data)
            return json.dumps([True,webwx.autoReplyMode])
        except:
            return json.dumps([False,webwx.autoReplyMode])

class TimeMsgApi():
    
    def GET(self):
        pass
    
    def POST(self):
        data = web.data()
        data = data.decode('utf-8')
        data = json.loads(data)
        
        msgName = data.get('msgName',None)
        msgTime = data.get('msgTime',None)
        msgWord = data.get('msgWord',None)
        #msgTime 12,15
        if msgName != None and msgTime != None and msgWord != None:
            now_time = time.time()
            ltime = time.localtime(now_time)
            year = int(ltime.tm_year)
            mon = int(ltime.tm_mon)
            mday = int(ltime.tm_mday)
            hour = int(msgTime.split(',')[0])
            min = int(msgTime.split(',')[1])
            sec = 0
            timeC = datetime.datetime(year,mon,mday,hour,min,sec)
            timestamp = time.mktime(timeC.timetuple())
            print timestamp
            q_timer.put(timerJob(timestamp,msgName,msgWord))
            lastest_timer = int(timestamp)
            print '入队列之前',q_timer
            return json.dumps([msgName,msgTime,msgWord])
    

class GroupApi():
    '''
    GroupListApi 对单个群进行增删改查操作
    GET 返回json格式[群名字,[name1,name2,...]]
    POST 参数 groupName,参数add(name),del(name),rnm(name),cpy(name),返回json格式[groupname,[name1,name2,...]]
    '''
    def GET(self):
        param = web.input(groupName = None)
        group = webwx.lsUseringp(param.groupName)
        if group != None:
            return json.dumps([param.groupName,group])
        else:
            return None
    
    def POST(self):
        data = web.data()
        data = data.decode('utf-8')
        data = json.loads(data)
    
        groupName = data.get('groupName',None)
        nameAdd = data.get('addName',None)
        nameDel = data.get('delName',None)
        
        
        if groupName != None:
            if nameAdd != None:
                webwx.addUseringp(groupName,nameAdd)
            if nameDel != None:
                webwx.rmUseringp(groupName,nameDel)

            
            group = webwx.lsUseringp(groupName)
            res = [len(group),group]
            return json.dumps(res)
        else:
            return None
    


class ContactListApi():
    '''
    返回联系人列表
    '''
    pass


class GroupListsApi():
    '''
    GroupListsApi 对群进行增删改查操作
    GET 返回json格式['群数',[name1,name2,...]]
    POST 参数add(对应增加群srcname),del(删除群srcname),mvn(修改群srcname,dstname),返回json格式['群数',[name1,name2,...]]
    '''
    def GET(self):
        groups = webwx.lsGroup()
        res = [len(groups),groups]
        return json.dumps(res)
    
    def POST(self):
        data = web.data()
        data = data.decode('utf-8')
        data = json.loads(data)
    
        nameAdd = data.get('addName',None)
        nameDel = data.get('delName',None)
        
        srcRnm = data.get('srcRnm',None)
        dstRnm = data.get('dstRnm',None)
        
        srcCpy = data.get('srcCpy',None)
        dstCpy = data.get('dstCpy',None)
        
        if nameAdd != None:
            webwx.newgroup(nameAdd)
        if nameDel != None:
            webwx.rmgroup(nameDel)
        if srcRnm != None and dstRnm != None:
            webwx.reNamegp(srcRnm,dstRnm)
        if srcCpy != None and dstRnm != None:
            webwx.copyGroup(srcCpy,dstCpy)
        
        groups = webwx.lsGroup()
        res = [len(groups),groups]
        return json.dumps(res,ensure_ascii=False)
       
        
class MsgApi():
            
    def __init__(self):
        
        pass
       
            
    def GET(self):
        
        print 'qsize api' + str(webwx.q.qsize())
        print u'[*] 共有 %d 个群 | %d 个直接联系人 | %d 个特殊账号 ｜ %d 公众号或服务号' % (len(webwx.GroupList),len(webwx.ContactList), len(webwx.SpecialUsersList), len(webwx.PublicUsersList))
  
             
        if not webwx.q.empty():
            data = webwx.q.get()
            print(json.dumps(data, indent=4, ensure_ascii=False))
            if data:
                #data = json.dump(data)
                return data
            else :
                return None
        else:
            return None
    
    def POST(self):
        data = web.data()
        data = data.decode('utf-8')
        pprint(data)
        data = json.loads(data)
        name = data['name']
        word = data['word']
        webwx.sendMsg(name, word)
        
def input_cmd():
    q_timer.put(timerJob(9997141980,'test','test'))
    '''取一个永远都不可能发送的消息放在队列里'''
    while True:
        cmd = raw_input()
        cmd = cmd.decode(sys.stdin.encoding)
        if cmd == 'quit':
            
            print(u'[*] 退出微信')
            exit()
        elif cmd[:2] == '->':
            [name, word] = cmd[2:].split(':')
            logging.info((name + ':name,' + word + 'word').encode('utf-8'))
            webwx.sendMsg(name, word)
        elif cmd[:6] == 'reply:':
            a = cmd[6:]
            if int(a) == 1:
                webwx.reply_change(True)
            else:
                webwx.reply_change(False)   
        elif cmd[:10] == "sendgpmsg:":
            '''
            作用：发送群消息
            格式： sendgpmsg:groupname:word
            '''
            [groupname, word] = cmd[10:].split(':')
            logging.info((groupname + ':groupname,' + word + 'word').encode('utf-8'))
            webwx.sendGroupmsg(groupname, word)
        elif cmd == 'lsgp':
            '''
            作用：显示出所有群
            '''
            webwx.lsGroup()
        elif cmd[:6] =='newgp:':
            '''
            作用：新建空群
            格式：  newgp:groupname
            '''
            groupname = cmd[6:]
            webwx.newgroup(groupname)
        elif cmd[:9] =='renamegp:':
            '''
            作用：更改群名称
            格式：  renamegp:oldname:newname
            '''
            [oldname, newname] = cmd[9:].split(':')
            webwx.reNamegp(oldname, newname)
            
        elif cmd[:5] =='rmgp:':
            '''
            作用：删除群
            格式：  rmgp:groupname
            '''
            groupname = cmd[5:]
            webwx.rmgroup(groupname)
        elif cmd[:9] =='lsuserin:':
            '''
            作用：展示群中成员
            格式：  lsuserin:groupname
            '''
            groupname = cmd[9:]
            webwx.lsUseringp(groupname)
        elif cmd[:8] == 'adduser:':
            '''
            作用：向群中添加用户
            格式：   adduser:groupname:user1,user,user3......
            '''
            [groupname,data] = cmd[8:].split(':')
            datalist = data.split(',')
            webwx.addUseringp(groupname, datalist)
        elif cmd[:7] == 'rmuser:':
            '''
            作用：删除群中用户
            格式：   rmuser:groupname:user1,user,user3......
            '''
            [groupname,data] = cmd[7:].split(':')
            datalist = data.split(',')
            webwx.rmUseringp(groupname, datalist)
        elif cmd[:7] == 'copygp:':
            '''
            作用：复制群成员到另外一个群
            格式：来源群，  去向群
            '''
            [fromgpname, togpname] = cmd[7:].split(':')
            webwx.copyGroup(fromgpname, togpname)
        elif cmd[:6] == 'timer:':
            '''
            作用：定时发送特定人的消息
            格式：输入定时:人名:时间:信息；时间写小时，分钟就行，默认当天发送
            '''
            [name,timer_flag,word] = cmd[6:].split(':')
            now_time = time.time()
            ltime = time.localtime(now_time)
            year = int(ltime.tm_year)
            mon = int(ltime.tm_mon)
            mday = int(ltime.tm_mday)
            hour = int(timer_flag.split(',')[0])
            min = int(timer_flag.split(',')[1])
            sec = 0
            timeC = datetime.datetime(year,mon,mday,hour,min,sec)
            timestamp = time.mktime(timeC.timetuple())
            print timestamp
            q_timer.put(timerJob(timestamp,name,word))
            lastest_timer = int(timestamp)
            print '入队列之前',q_timer
            
def process_timejob(q_timer):
    '''
    线程：监听离现在最近的定时消息是否可以发送
    计算时间方法：使用优先队列，每次取两个数据，比较时间轴，大的重新放回队列，然后短的时间轴
和现在的时间轴比较，小的话，重新放回队列，休眠一秒，循环此过程
这样可以保证随时输入的定时消息可以取出队列进行比较
    '''
    while True:
        while True:
            next_timejob = q_timer.get()
            next_next_timejob = q_timer.get()
            if next_next_timejob.priority < next_timejob.priority:
                q_timer.put(next_timejob)
                now_timejob = next_next_timejob
            else:
                q_timer.put(next_next_timejob)
                now_timejob = next_timejob
            #print '出队列',q_timer
            
            if int(now_timejob.priority) <= int(time.time()):
                break
            else:
                time.sleep(1)
            q_timer.put(now_timejob) 
        logging.info((now_timejob.name + ':name,' + now_timejob.word + 'word').encode('utf-8'))
        webwx.sendMsg(now_timejob.name, now_timejob.word)
        q_timer.task_done()
            
            
if __name__ == '__main__':
    
   
    webwx = WXLogin()
    webwx.login_module()
    t_listen = threading.Thread(target=webwx.listenMsgMode,args = ())
    t_listen.setDaemon(True)
    t_listen.start()
    
    
    t_input = threading.Thread(target=input_cmd, args=())
    t_input.setDaemon(True)
    t_input.start()

    workers = threading.Thread(target=process_timejob,args=(q_timer,))#,threading.Thread(target=process_timejob(),args=(q_timer,))]
    workers.setDaemon(True)
    workers.start()

  

    app = web.application(urls,globals())
    app.run()
