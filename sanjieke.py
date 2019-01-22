import requests


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
#模拟登录
    def login(self,phone,password):
        post_data = {
            'phone':phone,
            'password':password
        }
        response = self.session.post(self.login_url,data=post_data,headers=self.headers)
        if response.status_code == 200:
            print(response.text)
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
                data = response.json()['data']['correct_list']
                print(data)
                print('-----已完成一项')
                page+= 1
            else:
                print('抓取完毕')
                break
#获取助教对学员的作业点评内容
    def get_comment_info(self,homework_id):
        response = self.session.get(self.homework_detail_url.format(homework_id))
        comment = response.json()['data']['correct_list'][0]['content']
        print(comment)

#获取作业点赞信息
    def get_praise_record(self,page =1):
        response = self.session.get(self.praise_record_url.format(page))
        data = response.json()['data']['records']
        print(data)



if __name__ == '__main__':
    login =Login()
    login.login('15295730742','ygq123456')
    login.get_correct_total()
   # login.get_comment_info('11904207')
   # login.get_correct_list()
    login.get_praise_record()
