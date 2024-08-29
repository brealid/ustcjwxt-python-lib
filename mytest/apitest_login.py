import requests, sys
import hashlib

s = requests.Session()
response = s.get('https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin')
cas_lt = response.text.split('$("#CAS_LT").val("')[-1].split('");')[0]
print(cas_lt)

username, password = sys.argv[1], sys.argv[2]
fingerprint = hashlib.sha256(b'ustcjext-lib-' + username.encode()).hexdigest()[:64]

header = {
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Linux NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/19.19.8.10 Safari/537.36'
}
loginParams = {
    'service': '',
}
loginForm = {
    'model': 'uplogin.jsp',
    'CAS_LT': cas_lt,
    'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
    'showCode': '',
    'username': username,
    'password': password,
    'resultInput': fingerprint,
}

response = s.post('https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin', data=loginForm, headers=header)
print(response.headers)


# url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
# data = {
#     'model': 'uplogin.jsp',
#     'service': 'http://weixine.ustc.edu.cn/2020/caslogin',
#     'username': username,
#     'password': password,
# }
# response = s.post(url, data=data)

print(f'login redirect to {response.url}')
print(f'login response status code {response.status_code}')
print(f'login response headers {response.headers}')
# print(f'login response text {response.text}')
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

if response.url.startswith('https://passport.ustc.edu.cn/login'):
    # Check if Phone
    msg = response.text.split('var msg = "')[-1].split('";')[0]
    print(f"msg = {msg}")
    if msg == '4003' or msg == '4002':
        print('需要二步验证')
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
        response = s.get('https://passport.ustc.edu.cn/loginSm.jsp', params=params, headers=header)
        print(f'loginSm.jsp redirect to {response.url}')
        print(f'loginSm.jsp response status code {response.status_code}')
        print(f'loginSm.jsp response headers {response.headers}')
        with open('test1.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(s.cookies)
        smCode = input('请输入验证码:')
        response = s.post('https://passport.ustc.edu.cn/loginValidateSm', data={
            'code_mobile': params['code_mobile'],
            'smCode': smCode,
            'trust': 'trust_checkbox',
            'fingerprint': fingerprint,
            'service': 'https://jw.ustc.edu.cn/ucas-sso/login',
            'secondCode': params['secondCode'],
        }, headers=header)
        print(f'loginValidateSm redirect to {response.url}')
        print(f'loginValidateSm response status code {response.status_code}')
        print(f'loginValidateSm response headers {response.headers}')
        with open('test2.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        response = s.post('https://passport.ustc.edu.cn/login', data={
            'secondCode': params['secondCode'],
            'second': '2',
        }, headers=header)
        print(f'login redirect to {response.url}')
        print(f'login response status code {response.status_code}')
        print(f'login response headers {response.headers}')
        with open('test3.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(s.cookies)