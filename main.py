import requests
from PIL import Image
from bs4 import BeautifulSoup
import copy
import time
import re
import os
import json
import threading


class Spider:
    class Lesson:

        def __init__(self, name, code, teacher_name, Time, number):
            self.name = name
            self.code = code
            self.teacher_name = teacher_name
            self.time = Time
            self.number = number

        def show(self):
            print(self.toString())

        def toString(self):
            return '  name:' + self.name + '  code:' + self.code + '  teacher_name:' + self.teacher_name + '  time:' + self.time + ' number:' + str(self.number)


    def __init__(self, url):
        self.__uid = ''
        self.__real_base_url = ''
        self.__base_url = url
        self.__name = ''
        self.__base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '',
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        }
        self.session = requests.Session()
        self.__now_lessons_number = 0
        self.__now_lessons_id = []
        self.__session_cache = {}


    def __set_real_url(self):
        '''
        得到真实的登录地址(无Cookie)
        获取Cookie(有Cookie)
        :return: 该请求
        '''
        request = self.session.get(self.__base_url, headers=self.__headers)
        real_url = request.url
        print(real_url)
        self.__session_cache['session_id'] = real_url.split('(')[-1].split(')')[0]
        if real_url != 'http://218.75.197.123:83/' and real_url != 'http://218.75.197.123:83/index.apsx':   # 湖南工业大学
            self.__real_base_url = real_url[:len(real_url) - len('default2.aspx')]
        else:
            if real_url.find('index') > 0:
                self.__real_base_url = real_url[:len(real_url) - len('index.aspx')]
            else:
                self.__real_base_url = real_url
        return request

    def __get_code(self):
        '''
        获取验证码
        :return: 验证码
        '''
        print('请输入接下来打开的图片中的验证码:')
        if self.__real_base_url != 'http://218.75.197.123:83/':
            request = self.session.get(self.__real_base_url + 'CheckCode.aspx', headers=self.__headers)
        else:
            request = self.session.get(self.__real_base_url + 'CheckCode.aspx?', headers=self.__headers)
        with open('code.jpg', 'wb')as f:
            f.write(request.content)
        im = Image.open('code.jpg')
        im.show()
        code = input()
        return code

    def __get_login_data(self, uid, password):
        '''
        得到登录包
        :param uid: 学号
        :param password: 密码
        :return: 含登录包的data字典
        '''
        self.__uid = uid
        request = self.__set_real_url()
        soup = BeautifulSoup(request.text, 'html.parser')
        form_tag = soup.find('input')
        __VIEWSTATE = form_tag['value']
        self.__session_cache['__VIEWSTATE'] = __VIEWSTATE
        code = self.__get_code()
        data = {
            '__VIEWSTATE': __VIEWSTATE,
            'txtUserName': self.__uid,
            'TextBox2': password,
            'txtSecretCode': code,
            'RadioButtonList1': '学生'.encode('gb2312'),
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': '',
        }
        return data

    def __save_session(self):
        # print(self.__session_cache)
        with open('./session', 'w') as f:
            output = json.dumps(self.__session_cache, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(output)
            print('session saved')

    def __verify_local_session(self,session):
        self.__real_base_url = f'{config["url"]}({session["session_id"]})/'
        self.__base_data['__VIEWSTATE'] = session['__VIEWSTATE']
        self.__uid = session['student_number']
        self.__name = session['student_name']
        data = {
            'xh': self.__uid,
            'xm': self.__name.encode('gb2312'),
            'gnmkdm': 'N121501',
        }
        
        self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
        while True:
            request = self.session.get(self.__real_base_url + 'xsgrxx.aspx', headers=self.__headers, params=data)
            soup = BeautifulSoup(request.text, 'html.parser')
            if request.status_code != requests.codes.ok:
                print('4XX or 5XX Error,try to login again')
                time.sleep(0.5)
                continue
            try:
                name_tag = soup.find(id='xm')
                if name_tag.string == self.__name:
                    print('欢迎' + self.__name)
                    self.__enter_lessons_first()
                    return True
                else:
                    print(name_tag.string)
                    return False
            except:

                # print(soup)
                print('本地缓存已过期')
                return False

    def login(self, uid, password):
        '''
        外露的登录接口
        :param uid: 学号
        :param password: 密码
        :return: 抛出异常或返回是否登录成功的布尔值
        '''
        try:
            
            with open('./session',encoding='utf-8')as f:
                session = json.load(f)
                if session['student_number'] != config['student_number']:
                    os.remove('session')
                    print('本地缓存与配置文件用户不一致')
                elif self.__verify_local_session(session):
                    return True
        
        except:
            print('本地缓存不可用')

        while True:
            data = self.__get_login_data(uid, password)
            if self.__real_base_url != 'http://218.75.197.123:83/':
                request = self.session.post(self.__real_base_url + 'default2.aspx', headers=self.__headers, data=data)
            else:
                request = self.session.post(self.__real_base_url + 'index.aspx', headers=self.__headers, data=data)
            soup = BeautifulSoup(request.text, 'html.parser')
            if request.status_code != requests.codes.ok:
                print('4XX or 5XX Error,try to login again')
                time.sleep(0.5)
                continue
            if request.text.find('验证码不正确') > -1:
                print('验证码错误')
                continue
            if request.text.find('密码错误') > -1:
                print('密码错误')
                return False
            if request.text.find('用户名不存在') > -1:
                print('用户名错误')
                return False
            try:
                name_tag = soup.find(id='xhxm')
                self.__name = name_tag.string[:len(name_tag.string) - 2]
                print('欢迎' + self.__name)
                
                # self.__set__VIEWSTATE(soup)
                self.__session_cache['student_number'] = uid
                self.__session_cache['student_name'] = self.__name
                self.__save_session()
                self.__enter_lessons_first()
                return True
            except:
                print('未知错误，尝试再次登录')
                time.sleep(0.5)
                continue

    def __enter_lessons_first(self):
        '''
        首次进入选课界面
        :return: none
        '''
        data = {
            'xh': self.__uid,
            'xm': self.__name.encode('gb2312'),
            'gnmkdm': config['gnmkdm'],
        }

        self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
        selected_lessons_pre_tag = ''
        selected_lessons_tag = ''
        if config['class_type'] == 1:
            print('getting lession data')
            self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
            request = self.session.get(self.__real_base_url + 'xf_xsqxxxk.aspx', params=data, headers=self.__headers)
            self.__headers['Referer'] = request.url
            soup = BeautifulSoup(request.text, 'html.parser')
            self.__set__VIEWSTATE(soup)
            selected_lessons_pre_tag = soup.find('legend', string='已选课程')
            selected_lessons_tag = selected_lessons_pre_tag.parent
            
            # print(soup)

        else:
            print('pregetting viewstate data')
            request = self.session.get(self.__real_base_url + 'xf_xstyxk.aspx', params=data, headers=self.__headers)
            self.__headers['Referer'] = request.url
            # print(request.text)
            soup = BeautifulSoup(request.text, 'html.parser')
            self.__set__VIEWSTATE(soup)
            selected_lessons_pre_tag = soup.find('legend', string='已选列表').parent
            # print(selected_lessons_pre_tag.prettify())
            selected_lessons_tag = selected_lessons_pre_tag.table

        tr_list = selected_lessons_tag.find_all('tr')[1:]
        self.__now_lessons_number = len(tr_list)
        print('您已经选择了以下课程：')
        for tr in tr_list:
            td = tr.find('td')
            print(td.string)
            self.__now_lessons_id.append(td.string)
        # try:
        #     xq_tag = soup.find('select', id='ddl_xqbs')
        #     self.__base_data['ddl_xqbs'] = xq_tag.find('option')['value']
        # except:
        #     pass

    def __set__VIEWSTATE(self, soup):
        __VIEWSTATE_tag = soup.find('input', attrs={'name': '__VIEWSTATE'})
        self.__base_data['__VIEWSTATE'] = __VIEWSTATE_tag['value']

    def __get_lessons(self, soup):
        '''
        提取传进来的soup的课程信息
        :param soup:
        :return: 课程信息列表
        '''
        lesson_list = []
        lessons_tag = soup.find('table', id='kcmcGrid')
        lesson_tag_list = lessons_tag.find_all('tr')[1:]
        for lesson_tag in lesson_tag_list:
            td_list = lesson_tag.find_all('td')
            if config['class_type'] == 1:
                code = td_list[0].input['name']
                name = td_list[1].string
                teacher_name = td_list[3].string
                try:
                    Time = td_list[4]['title']
                except:
                    Time = ''
                number = td_list[10].string
            else:
                code = td_list[9].input['name']
                name = td_list[0].string
                teacher_name = td_list[1].string
                try:
                    Time = td_list[2].string
                except:
                    Time = ''
                raw_str = td_list[1].a.attrs['onclick']
                # sp_strs = raw_str.split('\'')
                # for sp_str in sp_strs:
                #     sp_str.find('xkkh=')
                pattern = re.compile(r'\([0-9]+-[0-9]+-+[0-9]\)-[0-9]+-[0-9]+-[0-9]')
                number = pattern.findall(raw_str)[0]
            lesson = self.Lesson(name, code, teacher_name, Time, number)
            lesson_list.append(lesson)
        return lesson_list

    def __search_lessons(self, lesson_name=''):
        '''
        搜索课程
        :param lesson_name: 课程名字
        :return: 课程列表
        '''
        
        if config['class_type'] == 1:
            self.__base_data['TextBox1'] = lesson_name.encode('gb2312')
            data = self.__base_data.copy()
            data['__EVENTTARGET'] = 'ddl_xqbs'
            data['ddl_xqbs'] = config['sub_class_type']
            data['Button2'] = '确定'.encode('gb2312')
            request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers)
        else:
            data = {
                'xh': self.__uid,
                'xm': self.__name.encode('gb2312'),
                'gnmkdm': config['gnmkdm'],
            }
            data2 = {
                '__EVENTTARGET': 'kj',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': self.__base_data['__VIEWSTATE'],
                'kj': config['sub_class_type'].encode('gb2312')
            }
            print('getting lession data')
            request = self.session.post(self.__real_base_url + 'xf_xstyxk.aspx', params=data, headers=self.__headers, data=data2)
        # print(request.text)
        soup = BeautifulSoup(request.text, 'html.parser')
        self.__set__VIEWSTATE(soup)
        return self.__get_lessons(soup)

    def __select_lesson(self, lesson_list):
        '''
        开始选课
        :param lesson_list: 选的课程列表
        :return: none
        '''
        data = copy.deepcopy(self.__base_data)
        data['Button1'] = '  提交  '.encode('gb2312')
        class_state=True
        while class_state:
            for lesson in lesson_list:
                try:
                    code = lesson.code
                    data[code] = 'on'
                    request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers,timeout=5)
                except:
                    continue
                start = time.time()
                soup = BeautifulSoup(request.text, 'html.parser')
                self.__set__VIEWSTATE(soup)
                error_tag = soup.script
                if not error_tag is None:
                    error_tag_text = error_tag.string
                    r = "alert\('(.+?)'\);"
                    for s in re.findall(r, error_tag_text):
                        print(s)
                if config['class_type'] == 1:
                    selected_lessons_pre_tag = soup.find('legend', string='已选课程')
                    selected_lessons_tag = selected_lessons_pre_tag.next_sibling
                else:
                    selected_lessons_pre_tag = soup.find('legend', string='已选列表').parent
                    selected_lessons_tag = selected_lessons_pre_tag.table
                tr_list = selected_lessons_tag.find_all('tr')[1:]
                if ( len(tr_list) > self.__now_lessons_number) :
                    class_state = False
                    print('抢课成功')
                for tr in tr_list:
                    td = tr.find('td')
                    if (td.string == lesson.number):
                        class_state = False
                        print(td.string+'已在已选列表中')

    def run(self,uid,password):
        '''
        开始运行
        :return: none
        '''
        if self.login(uid, password):
            print('请输入搜索课程名字，直接回车则显示全部可选课程')
            lesson_name = input()
            lesson_list = self.__search_lessons(lesson_name)
            lesson_list_output = ''
            for i in range(len(lesson_list)):
                print(i, end='')
                lesson_list_output = lesson_list_output + str(i) + lesson_list[i].toString() + '\n'
                lesson_list[i].show()
            # with open('lesson_list.txt','w') as f:
            #     f.write(str(lesson_list_output))
            print('请输入想选的课的id,如果没有课程显示,请检查config中gnmkdm和subid设置')
            # spread to muilt input split as ,
            # input_str = input()

            select_id = int(input())
            lesson_list = lesson_list[select_id:select_id + 1]
            thread_list = list()
            for i in range(15):
                thread_list.append(threading.Thread(target=self.__select_lesson,args=(lesson_list,)))
            for i in range(15):
                thread_list[i].start()
            for i in range(15):  
                thread_list[i].join()


if __name__ == '__main__':
    try:
        with open('config.json',encoding='utf-8')as f:
            config = json.load(f)
    except:
        print('本地配置文件错误，请检查后重试！')
    url = config['url']
    uid = config['student_number']
    password = config['password']
    print(f'尝试登录{uid}中...')
    spider = Spider(url)
    spider.run(uid, password)
    os.system("pause")