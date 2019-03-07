import requests
import sqlite3
#import jieba
import json

class Login(object):
    def __init__(self):
        self.headers ={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://assist.sanjieke.cn/Login/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        self.login_url = 'https://assist.sanjieke.cn/Login' #登录页面地址
        self.index_url ='https://assist.sanjieke.cn/index#/' # 助教首页地址
        self.summary_url ='https://assist.sanjieke.cn/correct/summary' #助教批改总计接口
        self.correct_list_url = 'https://assist.sanjieke.cn/correct/correctList' #批改记录接口
        self.homework_detail_url ='https://assist.sanjieke.cn/correct/homeworkDetail?homework_id={}' # 作业评价接口
        self.praise_record_url ='https://assist.sanjieke.cn/correct/praiseRecords?page={}' #作业点赞接口
        self.session = requests.Session()
        self.conn = sqlite3.connect('sanjieke.db')

#模拟登录
    def login(self,phone,password):
        post_data = {
            'phone':phone,
            'password':password
        }
        response = self.session.post(self.login_url,data=post_data,headers=self.headers)
        if response.status_code == 200:
            print('登录成功！')
        else:
            print('登录失败，请重试!')
#获取批改总量
    def get_correct_total(self):
        response = self.session.get(self.summary_url)
        correct_total = response.json()['data']['total_count']
        print(correct_total)
#获取批改明细
    def get_correct_list(self,page=1):
        while True:
            post_data = {
                'page':str(page),
                'page_count':10,
                'class_id':0, #班期
                'user_search':'', # 搜索昵称
                'question_search':'', #搜索作业标题
            }
            response = self.session.post(self.correct_list_url,data=post_data,headers=self.headers)
            if  page < int(response.json()['data']['total_count'])/10 + 1: #校验抓取循环是否超过最大列数
                correct_list = response.json()['data']['correct_list']
                for data in correct_list:
                    print(data)
                    self.insert_correct_list(data)
                    self.get_comment_info(data['homework_id'])

                print('-----已完成一项-----')
                page+= 1
            else:
                print('抓取完毕')
                break
#获取助教对学员的作业点评内容
    def get_comment_info(self,homework_id):
        try:
            response = self.session.get(self.homework_detail_url.format(homework_id))
            comment = response.json()['data']['correct_list'][0]
            comment.update({'homework_id':homework_id})
            self.insert_comment_info(comment)
        except:
            pass


#获取作业点赞信息
    def get_praise_record(self,page =1):
        while True:
            response = self.session.get(self.praise_record_url.format(page))
            data = response.json()['data']['records']
            print(data)
#保存批改明细到数据库
    def insert_correct_list(self,data):
        self.conn.execute('''create table if not exists correct_list
        (homework_id Int primary key not null,
        correct_time text not null,
        class_id int not null,
        question_title text not null,
        create_time text not null,
        status int,
        grade int,
        recommend int,
        comment_score int,
        name text,
        teacher_name text);''')
        sql = '''insert or ignore into correct_list(homework_id,correct_time,class_id,question_title,create_time,status,grade,recommend,comment_score,name,teacher_name) VALUES
('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')''' %(data['homework_id'],data['correct_time'],data['class_id'],data['question_title'],data['create_time'],data['status'],data['grade'],data['recommend'],data['comment_score'],data['name'],data['teacher_name'])
        self.conn.execute(sql)
        self.conn.commit()
        #关闭数据库连接
        #self.conn.close()
#保存作业点评到数据库
    def insert_comment_info(self,data):
        self.conn.execute('''create table if not exists comment_info
        (homework_id int primary key not null,
        name text,
        content text,
        score int,
        correct_time text,
        recommend int
        );''')
        sql = '''insert or ignore into comment_info(homework_id,name,content,score,correct_time,recommend) VALUES
        ('%s','%s','%s','%s','%s','%s')''' %(data['homework_id'],data['name'],data['content'],data['score'],data['correct_time'],data['recommend'])
        self.conn.execute(sql)
        self.conn.commit()

    def inquery_sanjieke(self):
        #批改记录总数
        sql_1 = '''select count(distinct(homework_id)) from correct_list where status != 0''' #一共批改了多少份作业
        total = self.conn.execute(sql_1)
        print(total)


    

if __name__ == '__main__':
    login =Login()
    print('''
    --------------------------------------------------------
    ❤欢迎使用三节课助教信息查询系统V1.0!
    ❤本系统由助教Larus开发，帮助各位助教了解自己的作业批改情况。
    ❤联系邮箱：hi@larus.me
    ❤微信公众号：larus01
    ❤（注：所有内容均保存在本地sqlite3数据库，无任何隐私泄露隐患。
    --------------------------------------------------------
    ''')
    phone = input('请输入三节课后台登录手机号：')
    password = input('请输入三节课后台登录密码：')
    login.login(phone,password)
    login.get_correct_total()
    #login.get_correct_list()
    login.inquery_sanjieke()

