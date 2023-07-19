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
from ustcjwxt.score import get_gradeList, get_gradeSheetTypes, get_semesters


log.set_logger_level('DEBUG')

s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])
# print(s.get_student_info())
# with open('avator.jpg', 'wb') as f:
#     f.write(s.get_student_avator())

print(get_semesters(s))
print(get_gradeSheetTypes(s))
print(get_gradeList(s))