# do build and install
import sys, os
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('usage: python main.py <username> <password> [rebuild]')
    exit(1)
if len(sys.argv) == 4 and sys.argv[3] in ['rebuild', 'build-only']:
    os.chdir('..')
    os.system('python -m build')
    os.chdir('dist')
    os.system('pip install ustcjwxt-0.0.3.dev0-py3-none-any.whl --force-reinstall --no-deps')
    print('========================================')
    print('        build and install done          ')
    print('========================================')
    if sys.argv[3] == 'build-only':
        exit(0)

# test
from ustcjwxt import log
from ustcjwxt.session import StudentSession
from ustcjwxt.score import *
from ustcjwxt.course_select import *


log.set_logger_level('DEBUG')

def test_stuInfo():
    print(s.get_student_info())
    print('ID:', s.get_student_ID())
    print('assocID:', s.get_student_assocID())
    with open('avatar.jpg', 'wb') as f:
        f.write(s.get_student_avatar())

def test_scoreCalc():
    gradeList = get_gradeList_all(s)
    print(grade_calcGpa(gradeList))
    # print([grade['score'] for grade in gradeList if grade['gp'] is not None])
    print(grade_calcWeightedScore(gradeList))
    print(grade_calcArithmeticScore(gradeList))


s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])

print(s.get_cookies())
test_stuInfo()
# test_scoreCalc()
