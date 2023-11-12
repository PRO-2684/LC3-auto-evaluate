from requests import Session
from json import load
from re import compile, findall
from rich import print_json

"""
Example config.json:
{
    "course_id": "_***_*",
    "cookies": {
        "JSESSIONID": "******",
        "nginx_auth_uid": "******",
        "nginx_auth_expire": "******",
        "nginx_auth_hash": "******",
        "session_id": "******",
        "s_session_id": "******",
        "web_client_cache_guid": "***-***-***-***-***",
        "xythosdrive": "0"
    },
    "headers": {
        "authority": "www.bb.ustc.edu.cn",
        "accept": "text/javascript, text/html, application/xml, text/xml, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "referer": "https://www.bb.ustc.edu.cn/webapps/gradebook/do/instructor/enterGradeCenter?course_id=<Your course_id here>&cvid=fullGC",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "x-prototype-version": "1.7",
        "x-requested-with": "XMLHttpRequest"
    },
    "additional": {
        "httpSessionId": "***",
        "scriptSessionId": "***"
    }
"""

with open("config.json") as f:
    config = load(f)

x = Session()
x.cookies.update(config["cookies"])
x.headers.update(config["headers"])
COURSE_ID = config["course_id"]
DESIRED_LAB = "Lab 1"

r = x.get("https://www.bb.ustc.edu.cn/webapps/gradebook/do/instructor/getJSONData", params={ "course_id": COURSE_ID })
assert r.status_code == 200, "Failed to fetch data"
rawData = r.json()

colName_to_colId = {
    DESIRED_LAB: None,
    "姓名": None,
    "用户名": None
}

for col in rawData["colDefs"]:
    if col["name"] in colName_to_colId:
        colName_to_colId[col["name"]] = col["id"]
for col, colId in colName_to_colId.items():
    assert colId is not None, f"Column {col} not found"
LAB_ID = colName_to_colId[DESIRED_LAB]

PATTERN = compile(r's\d+\.id ?= ?"(_\d+_\d+)";')
def getAttempts(uid) -> list[str]:
    temp = {
        "callCount": "1",
        "httpSessionId": config["additional"]["httpSessionId"],
        "scriptSessionId": config["additional"]["scriptSessionId"],
        "c0-scriptName": "GradebookDWRFacade",
        "c0-methodName": "getAttemptsInfo",
        "c0-id": "0",
        "c0-param0": f"number:{COURSE_ID[1:-2]}", # Course id
        "c0-param1": f"string:{uid}", # Student id
        "c0-param2": f"string:{LAB_ID}", # Lab id
        "batchId": "1"
    }
    data = ""
    for k, v in temp.items():
        data += f"{k}={v}\n"
    r = x.post("https://www.bb.ustc.edu.cn/webapps/gradebook/dwr/call/plaincall/GradebookDWRFacade.getAttemptsInfo.dwr", data=data)
    assert r.status_code == 200, "Failed to fetch attempts"
    data = r.text
    matches = findall(PATTERN, data)
    return matches

data = {}
for row in rawData["rows"]:
    if not row[0]["avail"]:
        continue # Skip unavailable students
    uid = None
    stuId = None
    stuName = None
    for col in row:
        if col.get("uid"):
            uid = col["uid"]
        elif col.get("c") == colName_to_colId["用户名"]:
            stuId = col["v"]
        elif col.get("c") == colName_to_colId["姓名"]:
            stuName = col["v"]
    assert uid and stuId and stuName, "Failed to parse student info"
    attempts = getAttempts(uid)
    data[stuId] = {
        "name": stuName,
        "attempts": attempts
    }

# _902226_1
