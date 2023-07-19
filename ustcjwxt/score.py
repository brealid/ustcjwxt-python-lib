from ustcjwxt import log, session

def get_semesters(s: session.StudentSession) -> list:
    response_semesters = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getSemesters').json()
    return response_semesters

def get_gradeSheetTypes(s: session.StudentSession) -> list:
    response_gradeSheetTypes = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getGradeSheetTypes').json()
    return response_gradeSheetTypes

def get_gradeList(s: session.StudentSession, trainTypeId: int = 1, semesterIds: list | str = 'default') -> list:
    if semesterIds == 'default':
        semesterIds = [semester['id'] for semester in get_semesters(s)]
    if type(semesterIds) == list:
        semesterIds = ','.join([str(semesterId) for semesterId in semesterIds])
    queryParams = {
        'trainTypeId': trainTypeId,
        'semesterIds': semesterIds
    }
    response_gradeList = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getGradeList', params=queryParams).json()
    return response_gradeList

def get_gradeList_major(s: session.StudentSession, semesterId: list | str = 'default') -> list:
    return get_gradeList(s, 1, semesterId)

def get_gradeList_minor(s: session.StudentSession, semesterId: list | str = 'default') -> list:
    return get_gradeList(s, 2, semesterId)