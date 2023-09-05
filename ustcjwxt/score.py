from ustcjwxt import log, session

#### definition

gradeToScore = {
    'A+': {'interval': (95, 100), 'as-score': 98, 'as-gpa': 4.3},
    'A': {'interval': (90, 94), 'as-score': 93, 'as-gpa': 4.0},
    'A-': {'interval': (85, 89), 'as-score': 88, 'as-gpa': 3.7},
    'B+': {'interval': (82, 84), 'as-score': 84, 'as-gpa': 3.3},
    'B': {'interval': (78, 81), 'as-score': 80, 'as-gpa': 3.0},
    'B-': {'interval': (75, 77), 'as-score': 77, 'as-gpa': 2.7},
    'C+': {'interval': (72, 74), 'as-score': 74, 'as-gpa': 2.3},
    'C': {'interval': (68, 71), 'as-score': 70, 'as-gpa': 2.0},
    'C-': {'interval': (65, 67), 'as-score': 67, 'as-gpa': 1.7},
    'D+': {'interval': (64, 64), 'as-score': 65, 'as-gpa': 1.5},
    'D': {'interval': (61, 63), 'as-score': 63, 'as-gpa': 1.3},
    'D-': {'interval': (60, 60), 'as-score': 61, 'as-gpa': 1.0},
    'F': {'interval': (0, 59), 'as-score': 0, 'as-gpa': 0.0}
}

def levelToScore(level: str) -> float:
    if level in gradeToScore:
        return gradeToScore[level]['as-score']
    else:
        return float(level)

#### API for jwxt.ustc.edu.cn

def jwxtApi_getSemesters(s: session.StudentSession) -> list:
    response_semesters = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getSemesters').json()
    return response_semesters

def jwxtApi_getGradeSheetTypes(s: session.StudentSession) -> list:
    response_gradeSheetTypes = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getGradeSheetTypes').json()
    return response_gradeSheetTypes

def jwxtApi_getGradeList(s: session.StudentSession, trainTypeId: int = -1, semesterIds = 'default') -> list:
    if semesterIds == 'default':
        semesterIds = [semester['id'] for semester in jwxtApi_getSemesters(s)]
    if type(semesterIds) == list:
        semesterIds = ','.join([str(semesterId) for semesterId in semesterIds])
    queryParams = {
        'trainTypeId': trainTypeId if trainTypeId != -1 else None,
        'semesterIds': semesterIds
    }
    response_gradeList = s.get('https://jw.ustc.edu.cn/for-std/grade/sheet/getGradeList', params=queryParams).json()
    return response_gradeList

#### user interface

# 所有成绩
def get_gradeList_all(s: session.StudentSession, semesterIds = 'default') -> list:
    return sum([x['scores'] for x in jwxtApi_getGradeList(s, -1, semesterIds)['semesters']], [])

# 主修成绩
def get_gradeList_major(s: session.StudentSession, semesterIds = 'default') -> list:
    return sum([x['scores'] for x in jwxtApi_getGradeList(s, 1, semesterIds)['semesters']], [])

# 辅修成绩
def get_gradeList_minor(s: session.StudentSession, semesterIds = 'default') -> list:
    return sum([x['scores'] for x in jwxtApi_getGradeList(s, 2, semesterIds)['semesters']], [])

# 修读课程总数
def grade_countCourse(gradeList: list, hasGpOnly: bool = False) -> int:
    return len([grade for grade in gradeList if not hasGpOnly or grade['gp'] is not None])

# 修读课程学分总数
def grade_countCredit(gradeList: list, hasGpOnly: bool = False) -> float:
    return sum([grade['credits'] for grade in gradeList if not hasGpOnly or grade['gp'] is not None])

# 修读课程绩点总数(非均值)
def grade_countGpTotal(gradeList: list) -> float:
    return sum([grade['gp'] * grade['credits'] for grade in gradeList if grade['gp'] is not None])

# 修读课程百分制总数(非均值)
def grade_countScoreTotal(gradeList: list, weighted = True) -> float:
    if weighted:
        return sum([levelToScore(grade['score']) * grade['credits'] for grade in gradeList if grade['gp'] is not None])
    else:
        return sum([levelToScore(grade['score']) for grade in gradeList if grade['gp'] is not None])

# 修读课程平均绩点    
def grade_calcGpa(gradeList: list) -> float:
    return grade_countGpTotal(gradeList) / grade_countCredit(gradeList, True)

# 修读课程平均百分制(加权平均)
def grade_calcWeightedScore(gradeList: list) -> float:
    return grade_countScoreTotal(gradeList) / grade_countCredit(gradeList, True)

# 修读课程平均百分制(算术平均)
def grade_calcArithmeticScore(gradeList: list) -> float:
    return grade_countScoreTotal(gradeList, weighted=False) / grade_countCourse(gradeList, True)