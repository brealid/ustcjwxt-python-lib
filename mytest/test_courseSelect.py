import sys
from ustcjwxt import log
from ustcjwxt.session import StudentSession
from ustcjwxt.score import *
from ustcjwxt.course_select import *


log.set_logger_level('DEBUG')

s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])

# 退课: IS4001.01
result = drop_Lesson(s, 'IS4001.01')
if result['success']:
    print('课程已退')
else:
    print(f'课程未退成功 (报错信息：{result["errorMessage"]["textZh"]})')
# 选课: IS4001.01
if check_courseAvailable(s, 'IS4001.01'):
    print('课程可选')
    result = add_Lesson(s, 'IS4001.01')
    if result['success']:
        print('课程已选中')
    else:
        print(f'课程未选中 (报错信息：{result["errorMessage"]["textZh"]})')
else:
    print('课程不可选 (人员已满)')