import time
from typing import Iterable
from ustcjwxt import log
from ustcjwxt.session import StudentSession

class SingleCacheDataInfo:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.openTurns = None
        self.allLesson = None
        self.selectedLesson = None
        self.currentTrun = None

class CacheDataInfo:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.singleCache = {}
    
    def get(self, s: StudentSession) -> SingleCacheDataInfo:
        assocID = s.get_student_assocID()
        if assocID not in self.singleCache:
            self.singleCache[assocID] = SingleCacheDataInfo()
        return self.singleCache[assocID]


cacheData = CacheDataInfo()

# basic api
# 课程参数均为 courseID (int 格式), 形如 123456

def _get_openTurns(s: StudentSession, force_retrieve: bool = False) -> list:
    if not force_retrieve and cacheData.get(s).openTurns is not None:
        return cacheData.get(s).openTurns
    url = 'https://jw.ustc.edu.cn/ws/for-std/course-select/open-turns'
    formData = { 'bizTypeId': 2, 'studentId': s.get_student_assocID() }
    response = s.post(url, data=formData)
    cacheData.get(s).openTurns = response.json()
    return cacheData.get(s).openTurns

def _get_allLesson(s: StudentSession, force_retrieve: bool = False) -> list:
    if not force_retrieve and cacheData.get(s).allLesson is not None:
        return cacheData.get(s).allLesson
    url = 'https://jw.ustc.edu.cn/ws/for-std/course-select/addable-lessons'
    formData = { 'turnId': _get_currentTurn(s), 'studentId': s.get_student_assocID() }
    response = s.post(url, data=formData)
    cacheData.get(s).allLesson = response.json()
    for lesson in cacheData.get(s).allLesson:
        cated = []
        for teacher in lesson['teachers']:
            cated.append(teacher['nameZh'])
        lesson['teacher_cated'] = ','.join(cated)
    return cacheData.get(s).allLesson

def _get_selectedLesson(s: StudentSession, force_retrieve: bool = True) -> list:
    if not force_retrieve and cacheData.get(s).selectedLesson is not None:
        return cacheData.get(s).selectedLesson
    url = 'https://jw.ustc.edu.cn/ws/for-std/course-select/selected-lessons'
    formData = { 'turnId': _get_currentTurn(s), 'studentId': s.get_student_assocID() }
    response = s.post(url, data=formData)
    cacheData.get(s).selectedLesson = response.json()
    for lesson in cacheData.get(s).selectedLesson:
        cated = []
        for teacher in lesson['teachers']:
            cated.append(teacher['nameZh'])
        lesson['teacher_cated'] = ','.join(cated)
    return cacheData.get(s).selectedLesson

def _get_chooseCount(s: StudentSession, courseIdList) -> dict:
    isSingle = type(courseIdList) in (int, str)
    try:
        courseIdList = [courseIdList] if isSingle else list(courseIdList)
    except TypeError:
        log.log_error(f'所提供的的 courseIdList 无法转为 list')
    url_fetch = 'https://jw.ustc.edu.cn/ws/for-std/course-select/std-count'
    formData = {'lessonIds[]': courseIdList}
    response = s.post(url_fetch, data=formData).json()
    response = { int(courseId): response[courseId] for courseId in response }
    if isSingle:
        return response[int(courseIdList[0])]
    return response

def _get_lesson_byID(s: StudentSession, courseId: int) -> dict:
    allLesson = _get_allLesson(s)
    for lesson in allLesson:
        if lesson['id'] == courseId:
            return lesson
    return None

def _get_lesson_byCode(s: StudentSession, courseCode: str) -> dict:
    allLesson = _get_allLesson(s)
    for lesson in allLesson:
        if lesson['code'] == courseCode:
            return lesson
    return None

def _get_currentTurn(s: StudentSession) -> int:
    openTurns = _get_openTurns(s)
    if len(openTurns) == 0:
        log.log_error(f'当前没有开放的选课')
        return None
    if len(openTurns) == 1:
        cacheData.get(s).currentTrun = openTurns[0]['id']
    elif cacheData.get(s).currentTrun is None:
        log.log_error(f'当前开放的选课数不为 1, 请调用 ustcjwxt.course_select.set_currentTurn 以设定当前选课')
        return None
    return cacheData.get(s).currentTrun

def _send_addRequest(s: StudentSession, courseId: int) -> str:
    courseInfo = _get_lesson_byID(s, courseId)
    log.log_info(f'[+] 正在发送选课请求: {courseInfo["code"]} {courseInfo["course"]["nameZh"]} ({courseInfo["teacher_cated"]})')
    requestData = {
        'studentAssoc': s.get_student_assocID(),
        'lessonAssoc': courseId,
        'courseSelectTurnAssoc': _get_currentTurn(s),
        'scheduleGroupAssoc': '',
        'virtualCost': '0',
    }
    response_request = s.post('https://jw.ustc.edu.cn/ws/for-std/course-select/add-request', data=requestData)
    log.log_info(f'[+] 获得服务器返回信息: 【请求唯一 UUID】 {response_request.text}')
    return response_request.text

def _send_dropRequest(s: StudentSession, courseId: int) -> str:
    courseInfo = _get_lesson_byID(s, courseId)
    log.log_info(f'[+] 正在发送退课请求: {courseInfo["code"]} {courseInfo["course"]["nameZh"]} ({courseInfo["teacher_cated"]})')
    requestData = {
        'studentAssoc': s.get_student_assocID(),
        'lessonAssoc': courseId,
        'courseSelectTurnAssoc': _get_currentTurn(s),
    }
    response_request = s.post('https://jw.ustc.edu.cn/ws/for-std/course-select/drop-request', data=requestData)
    log.log_info(f'[+] 获得服务器返回信息: 【请求唯一 UUID】 {response_request.text}')
    return response_request.text

def _query_opertaionResponse(s: StudentSession, requestID: str) -> dict:
    requestData = {
        'studentId': s.get_student_assocID(),
        'requestId': requestID,
    }
    response_request = s.post('https://jw.ustc.edu.cn/ws/for-std/course-select/add-drop-response', data=requestData)
    log.log_info(f'[+] 获得服务器返回信息: {response_request.json()}')
    return response_request.json()

# user interface
# 课程参数均为 courseCode (str 格式), 形如 IS4001.01

def set_currentTurn(s: StudentSession, turnID: int) -> None:
    cacheData.get(s).currentTrun = turnID

def get_chooseCount(s: StudentSession, courseCodeList) -> dict:
    if type(courseCodeList) is str:
        return _get_chooseCount(s, get_lesson_byCode(s, courseCodeList)['id'])
    courseIdList = [get_lesson_byCode(s, courseCode)['id'] for courseCode in courseCodeList]
    return _get_chooseCount(s, courseIdList)

def check_courseAvailable(s: StudentSession, courseCode: str) -> dict:
    course = get_lesson_byCode(s, courseCode)
    return _get_chooseCount(s, course['id']) < course['limitCount']

def add_Lesson(s: StudentSession, courseCode: str, delay_ms: float = 0.1) -> str:
    courseId = get_lesson_byCode(s, courseCode)['id']
    uuid = _send_addRequest(s, courseId)
    if len(uuid) == 36:
        time.sleep(delay_ms / 1000)
        return _query_opertaionResponse(s, uuid)
    return { 'success': False, 'errorMessage': { 'textZh': uuid } }

def drop_Lesson(s: StudentSession, courseCode: str, delay_ms: float = 0.1) -> str:
    courseId = get_lesson_byCode(s, courseCode)['id']
    uuid = _send_dropRequest(s, courseId)
    if len(uuid) == 36:
        time.sleep(delay_ms / 1000)
        return _query_opertaionResponse(s, uuid)
    return { 'success': False, 'errorMessage': { 'textZh': uuid } }

def load_cache(s: StudentSession, force_retrieve: bool = True) -> None:
    _get_openTurns(s, force_retrieve)
    _get_allLesson(s, force_retrieve)
    _get_selectedLesson(s, force_retrieve)
    _get_currentTurn(s)

send_addRequest = _send_addRequest
send_dropRequest = _send_dropRequest
query_opertaionResponse = _query_opertaionResponse
get_openTurns = _get_openTurns
get_allLesson = _get_allLesson
get_selectedLesson = _get_selectedLesson
get_lesson_byID = _get_lesson_byID
get_lesson_byCode = _get_lesson_byCode
get_currentTurn = _get_currentTurn