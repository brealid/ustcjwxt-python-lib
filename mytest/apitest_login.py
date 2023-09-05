import requests

s = requests.Session()
response = s.get('https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin')
cas_lt = response.text.split('$("#CAS_LT").val("')[-1].split('");')[0]
print(cas_lt)

username = ''
password = ''

header = {
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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