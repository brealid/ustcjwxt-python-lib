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
- score  
  可以获取学生的成绩  
  当前功能: 获取成绩列表，计算 GPA / 加权平均分 / 算术平均分
- session
  可以登录到教务系统，并提供 StudentSession 类，用于存储登录信息

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
with open('avator.jpg', 'wb') as f:
    f.write(s.get_student_avator())

# get score
gradeList = get_gradeList_all(s)
print(grade_calcGpa(gradeList))
print(grade_calcWeightedScore(gradeList))
print(grade_calcArithmeticScore(gradeList))
```
