# ustcjwxt-python-lib

ustc jwxt api, for study only

## Installation

```bash
pip install ustcjwxt
```

## Structure

- log  
  实现了一个简单的日志系统
- request_info  
  记录了一些 requests 需要使用的信息
- session  
  可以登录到教务系统，并提供 StudentSession 类，用于存储登录信息
- score  
  可以获取学生的成绩  
  当前功能: 获取成绩列表，计算 GPA / 加权平均分 / 算术平均分
- course_select  
  可以进行选课 / 退课操作  

## Usage

simple sample
```python
from ustcjwxt import log
from ustcjwxt.session import StudentSession
from ustcjwxt.score import *

log.set_logger_level('DEBUG')

# login
s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])
print(s.get_cookies())

# get basic info
print(s.get_student_info())
with open('avatar.jpg', 'wb') as f:
    f.write(s.get_student_avatar())

# get score
gradeList = get_gradeList_all(s)
print(grade_calcGpa(gradeList))
print(grade_calcWeightedScore(gradeList))
print(grade_calcArithmeticScore(gradeList))
```

course operation sample
```python
import sys
from ustcjwxt import log
from ustcjwxt.session import StudentSession
from ustcjwxt.course_select import *


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
```

课程交易
```python
import sys, time
from ustcjwxt.session import StudentSession
from ustcjwxt.course_select import *

courseCode = 'IS4001.01'
s_give = StudentSession()
s_give.login_with_password('PB********', '********')
s_get = StudentSession()
s_get.login_with_password('PB********', '********')

# 预加载数据，减小延迟
load_cache(s_give)
load_cache(s_get)

time.sleep(1)

drop_Lesson(s_give, courseCode, delay_ms=0)
add_Lesson(s_get, courseCode, delay_ms=0)
```