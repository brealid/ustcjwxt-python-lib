import requests
import requests.cookies
from ustcjwxt import log, request_info


class StudentSession:
    def __init__(self, username=None, password=None, session=None):
        self.request_session = requests.Session()
        self.password_useable = False
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
                self.clear_cookie()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.get(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cookie()
        return response
   
    def post(self, url, data=None, params=None, headers=request_info.header_uaonly, **kwargs) -> requests.Response:
        response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            log.log_warning(f'post {url} redirect to {response.url}')
            if self.password_useable:
                log.log_warning('session 无效, 正在尝试重新用密码登录')
                self.clear_cookie()
                if self.login_with_password(self.username, self.password):
                    response = self.request_session.post(url, headers=headers, params=params, data=data, **kwargs)
                else:
                    log.log_error('密码登录失败')
            else:
                log.log_error('session 无效')
                self.clear_cookie()
        return response

    def clear_cookie(self) -> None:
        self.request_session.cookies.clear()
        for key in request_info.base_cookie:
            self.request_session.cookies.set(key, request_info.base_cookie[key])

    def login_with_password(self, username: str, password: str) -> bool:
        self.username = username
        self.password = password

        loginParams = {
            'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
        }
        response = self.get('https://passport.ustc.edu.cn/login', params=loginParams)
        cas_lt = response.text.split('name="CAS_LT" value="')[-1].split('">')[0]
        loginForm = {
            'model': 'uplogin.jsp',
            'CAS_LT': cas_lt,
            'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
            'showCode': '',
            'username': username,
            'password': password,
        }
        response = self.post('https://passport.ustc.edu.cn/login', params=loginParams, data=loginForm)
        log.log_debug(f'login redirect to {response.url}')
        log.log_debug(f'login response status code {response.status_code}')
        if response.url == 'https://jw.ustc.edu.cn/home' and self.check_cookie_useable():
            self.password_useable = True
            return True
        else:
            log.log_error('username 和 password 无效, 登陆失败')
            self.password_useable = False
            self.clear_cookie()
            return False

    def login_with_session(self, session: str) -> bool:
        self.request_session.cookies['SESSION'] = session
        if not self.check_cookie_useable():
            log.log_error('session 无效')
            self.clear_cookie()
            return False
        return True
        
    def check_cookie_useable(self) -> bool:
        response = self.get('https://jw.ustc.edu.cn/my/profile')
        if response.url.startswith('https://jw.ustc.edu.cn/login'):
            return False
        return True
    
    # return binary data with jpg format
    def get_student_avator(self) -> bytes:
        response = self.get('https://jw.ustc.edu.cn/my/avatar')
        return response.content

    def get_student_info(self) -> dict:
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
        return stuinfo
