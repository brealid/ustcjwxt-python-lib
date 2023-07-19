# do build and install
import sys, os
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('usage: python main.py <username> <password> [rebuild]')
    exit(1)
if len(sys.argv) == 4 and sys.argv[3] == 'rebuild':
    os.chdir('..')
    os.system('python -m build')
    os.chdir('dist')
    os.system('pip install ustcjwxt-0.0.1-py3-none-any.whl --force-reinstall --no-deps')
    print('========================================')
    print('        build and install done          ')
    print('========================================')

# test
from ustcjwxt import log
from ustcjwxt.session import StudentSession
from ustcjwxt.score import *


log.set_logger_level('DEBUG')

s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])
print(s.get_cookies())
# print(s.get_student_info())
# with open('avator.jpg', 'wb') as f:
#     f.write(s.get_student_avator())

gradeList = get_gradeList_all(s)
print(grade_calcGpa(gradeList))
# print([grade['score'] for grade in gradeList if grade['gp'] is not None])
print(grade_calcWeightedScore(gradeList))
print(grade_calcArithmeticScore(gradeList))

# ['77', '93', '85', '75', 'A', 'B+', '72', '92', '92', '71', 'B', '85', '83', '83', '83', '87', '91', '60', 'A', '85', 'A-', '83', '96', '89', '44', '80.1', 'B+', '61', 'A', '62', '68', 'B+', 'B+', '78', '79', '80', '65', 'B+', '62', '79', '96']

# ['85', '92', '92', '71', '93', '93', '75', '77', '72', '84', '80', '60', '85', '93', '91', '83', '83', '87', '83', '85', '88', '61', '84', '96', '89', '93', '44', '84', '84', '83', '80.1', '62', '68', '84', '78', '79', '79', '62', '96', '80', '65']
# 79.2904109589041
# 80.56341463414634