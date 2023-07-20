# do build and install
import sys, os
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('usage: python main.py <username> <password> [rebuild]')
    exit(1)
if len(sys.argv) == 4 and sys.argv[3] in ['rebuild', 'build-only']:
    os.chdir('..')
    os.system('python -m build')
    os.chdir('dist')
    os.system('pip install ustcjwxt-0.0.2-py3-none-any.whl --force-reinstall --no-deps')
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
    print('assocID:', s.get_student_assocID())
    with open('avatar.jpg', 'wb') as f:
        f.write(s.get_student_avatar())

def test_scoreCalc():
    gradeList = get_gradeList_all(s)
    print(grade_calcGpa(gradeList))
    # print([grade['score'] for grade in gradeList if grade['gp'] is not None])
    print(grade_calcWeightedScore(gradeList))
    print(grade_calcArithmeticScore(gradeList))

def test_courseSelect():
    # 退课: IS4001.01
    uuid = send_dropRequest(s, 'IS4001.01')
    print(query_response(s, uuid))
    # 选课: IS4001.01
    if check_courseAvailable(s, 'IS4001.01'):
        print('课程可选')
        uuid = send_addRequest(s, 'IS4001.01')
        print(query_response(s, uuid))
    else:
        print('课程不可选 (人员已满)')


s = StudentSession()
s.login_with_password(sys.argv[1], sys.argv[2])

def _get_allLesson(s: StudentSession, force_retrieve: bool = False) -> list:
    url = 'https://jw.ustc.edu.cn/ws/for-std/course-select/addable-lessons'
    formData = { 'bizTypeId': 2, 'studentId': s.get_student_assocID() }
    response = s.post(url, data=formData, content_type='application/x-www-form-urlencoded')
    print(response.text)
    allLesson = response.json()
    for lesson in allLesson:
        cated = []
        for teacher in lesson['teachers']:
            cated.append(teacher['nameZh'])
        lesson['teacher_cated'] = ','.join(cated)
    return allLesson
_get_allLesson(s)
# print(s.get_cookies())
# test_stuInfo()
# test_scoreCalc()
test_courseSelect()