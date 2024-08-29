import time
import requests
import requests.cookies
import hashlib
from ustcjwxt import log, request_info


class StudentSession:
    def __init__(self, username=None, password=None, session=None):
        self.request_session = requests.Session()
        self.password_useable = False
        self.cache = dict()
        self.smcode_hook = None
        for key in request_info.base_cookie:
            self.request_session.cookies.set(key, request_info.base_cookie[key])
        # login with session
        if session is not None:
            self.login_with_session(session)
        # login with username and password
        if username is not None and password is not None:
            self.login_with_password(username, password)
        elif username is not None or password is not None:
            log.log_error('username 和 password 必须同时提供')
    
    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        return self.request_session.cookies

    def get(self, url, params=None, data=None, headers=request_info.header_uaonly, **kwargs) -> requests.Response:
        response = self.request_session.get(url, headers=headers, params=params, data=data, **kwargs)
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            log.log_warning(f'get {url} redirect to {response.url}')
            if self.password_useable:
                log.log_warning('session 无效, 正在尝试重新用密码登录')
                self.clear_cache()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.get(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cache()
        return response
   
    def post(self, url, data=None, params=None, headers=request_info.header_uaonly, content_type = '', **kwargs) -> requests.Response:
        if content_type:
            headers['content-type'] = content_type + '; charset=UTF-8'
        response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            log.log_warning(f'post {url} redirect to {response.url}')
            if self.password_useable:
                log.log_warning('session 无效, 正在尝试重新用密码登录')
                self.clear_cache()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cache()
        return response

    def clear_cache(self) -> None:
        self.request_session.cookies.clear()
        for key in request_info.base_cookie:
            self.request_session.cookies.set(key, request_info.base_cookie[key])
        self.cache = dict()

    def login_with_password(self, username: str, password: str, smcode_hook = None) -> bool:
        self.clear_cache()
        self.username = username
        self.password = password
        if smcode_hook is None:
            smcode_hook = self.smcode_hook
        else:
            self.smcode_hook = smcode_hook
        fingerprint = hashlib.sha256(b'ustcjwxt-lib-' + username.encode()).hexdigest()[:64]

        loginParams = {
            'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
        }
        response = self.get('https://passport.ustc.edu.cn/login', params=loginParams)

        # 自 2023.9 之后，教务系统经历了一次更新
        # CAS_LT 从网页静态写入，变为动态写入
        # 因此提取方式发生改变，但仍是同一个网页
        # 下方语句不再生效
        # cas_lt = response.text.split('name="CAS_LT" value="')[-1].split('">')[0]
        # 正确做法如下
        cas_lt = response.text.split('$("#CAS_LT").val("')[-1].split('");')[0]
        
        loginForm = {
            'model': 'uplogin.jsp',
            'CAS_LT': cas_lt,
            'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
            'showCode': '',
            'username': username,
            'password': password,
            'resultInput': fingerprint,
        }
        response = self.post('https://passport.ustc.edu.cn/login', params=loginParams, data=loginForm)
        log.log_debug(f'login redirect to {response.url}')
        log.log_debug(f'login response status code {response.status_code}')
        if response.url.startswith('https://passport.ustc.edu.cn/login'):
            # 检测二步验证相关设置
            msg = response.text.split('var msg = "')[-1].split('";')[0]
            log.log_debug(f'{msg = }')
            if msg == '4003' or msg == '4002':
                log.log_info('需要二步验证')
                if smcode_hook is None:
                    log.log_error('无法获取验证码, 登录失败')
                    log.log_error('suggest: 请传入 smcode_hook 以获取验证码')
                    return False
                # 获取验证码
                log.log_info('正在发送验证码')
                params = {
                    'type': {'4002': 1, '4003': 2}[msg],
                    'mobile': response.text.split('var mobile = "')[-1].split('";')[0],
                    'code_mobile': response.text.split('var code_mobile = "')[-1].split('";')[0],
                    'trust': response.text.split('var trust=\'')[-1].split('\';')[0],
                    'secondCode': response.text.split('var secondCode=\'')[-1].split('\';')[0],
                    'isWx': response.text.split('var isWx=\'')[-1].split('\';')[0],
                }
                if msg == '4003':
                    params['time'] = 60
                response = self.get('https://passport.ustc.edu.cn/loginSm.jsp', params=params)
                log.log_info('等待 hook 函数回传验证码')
                smCode = smcode_hook()
                response = self.post('https://passport.ustc.edu.cn/loginValidateSm', data={
                    'code_mobile': params['code_mobile'],
                    'smCode': smCode,
                    'trust': 'trust_checkbox',
                    'fingerprint': fingerprint,
                    'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
                    'secondCode': params['secondCode'],
                })
                response = self.post('https://passport.ustc.edu.cn/login', data={
                    'secondCode': params['secondCode'],
                    'second': '2',
                })
        if response.url == 'https://jw.ustc.edu.cn/home' and self.check_cookie_useable():
            self.password_useable = True
            time.sleep(1) # 应等待教务系统缓存更新
            return True
        else:
            log.log_error('username 和 password 无效, 登陆失败')
            self.password_useable = False
            self.clear_cache()
            return False

    def login_with_session(self, session: str) -> bool:
        self.clear_cache()
        self.request_session.cookies['SESSION'] = session
        if not self.check_cookie_useable():
            log.log_error('session 无效')
            self.clear_cache()
            return False
        return True
        
    def check_cookie_useable(self) -> bool:
        response = self.get('https://jw.ustc.edu.cn/my/profile')
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            return False
        return True
    
    # return binary data with jpg format(will not cache avatar)
    def get_student_avatar(self) -> bytes:
        response = self.get('https://jw.ustc.edu.cn/my/avatar')
        return response.content

    def get_student_info(self, force_retrieve = False) -> dict:
        if not force_retrieve and 'profile_info' in self.cache:
            return self.cache['profile_info']
        response = self.get('https://jw.ustc.edu.cn/my/profile')
        stuinfo_list = ['名称', '性别', '证件类型', '证件号', '生日', '政治面貌', '邮箱', '电话', '手机', '地址', '邮编', '简介']
        stuinfo = {}
        for dtype in stuinfo_list:
            specify = f'<span class="pull-left"><strong>{dtype}</strong></span>'
            p = response.text.find(specify)
            if p == -1:
                log.log_warning(f'get_student_info: {dtype} not found')
                continue
            data = response.text[p+len(specify):].split('</span>')[0].split('<span>')[-1]
            stuinfo[dtype] = data
        self.cache['profile_info'] = stuinfo
        return stuinfo
    
    def get_student_ID(self, force_retrieve = False) -> str:
        if not force_retrieve and 'student_ID' in self.cache:
            return self.cache['student_ID']
        # 从课表页面获取学号
        courseTablePage = self.get(f'https://jw.ustc.edu.cn/for-std/course-table/info/{self.get_student_assocID()}').text
        p = courseTablePage.find('<h2 class="info-title">')
        if p != -1:
            log.log_debug('从课表页面成功获取学号')
            student_ID = courseTablePage[p:].split('(')[1].split(')')[0]
            self.cache['student_ID'] = student_ID
            return student_ID
        log.log_warning('未能在课表页面找到学号')
        # 从 cookie 中获得学号
        if 'uc' in self.request_session.cookies:
            log.log_debug('从 cookies 中成功获取学号')
            student_ID = self.request_session.cookies['uc']
            self.cache['student_ID'] = student_ID
            return student_ID
        log.log_warning('未能在 cookies 中找到学号')
        # 均失败
        log.log_warning('未能获得学号')
        return ''
    
    def get_student_assocID(self, force_retrieve = False) -> int:
        if not force_retrieve and 'assocID' in self.cache:
            return self.cache['assocID']
        response = self.get('https://jw.ustc.edu.cn/for-std/course-select')
        if response.url.startswith('https://jw.ustc.edu.cn/for-std/course-select/turns/'):
            assocID = int(response.url.split('/')[-1])
            log.log_info(f'学生唯一 assocID 获取成功: {assocID}')
            self.cache['assocID'] = assocID
            return assocID
        log.log_error(f'学生唯一 assocID 获取失败')
        return -1