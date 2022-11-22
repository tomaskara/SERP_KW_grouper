import requests
import json


def scrap_url_list(query, api_key):
    api_url = "https://api.serpsbot.com/v2/google/organic-search"
    request_body = {
        "query": query,
        "gl": "CZ",
        "hl": "cs_CZ",
        "device": "desktop",
        "autocorrect": 0,
        "page": 1,
        "uule": "string",
        "pages": 1,
        "verbatim": False,
        "raw_html": False
    }
    done = False
    while not done:
        api_call = requests.post(api_url, json=request_body, headers={"X-API-KEY": api_key})
        if api_call.status_code != 200:
            pass
        else:
            json_response = api_call.json()
            done = True

    url_list = []

    for i in json_response['data']['organic']:
        url_list.append(i['url'])
    return url_list

def allIntersections(frozenSets):
    if len(frozenSets) == 0:
        return []
    else:
        head = frozenSets[0]
        tail = frozenSets[1:]
        tailIntersections = allIntersections(tail)
        newIntersections = [head]
        newIntersections.extend(tailIntersections)
        newIntersections.extend(head & s for s in tailIntersections)
        return list(set(newIntersections))

def all_intersections(name_of_file, accuracy):
    with open(name_of_file) as f:
        data = f.read()
    js = json.loads(data)
    values = list(js.values())
    sets = allIntersections([frozenset(s) for s in values])
    sets_copy = sets.copy()
    for i in sets_copy:
        if len(i) >= 9 or len(i) != accuracy:
            sets.remove(i)
    lists = [tuple(s) for s in sets]
    intersection_dic = {key: [] for key in lists}
    for intersection in intersection_dic:
        for item in js.items():
            if len(set(intersection).intersection(set(item[1]))) >= len(intersection):
                intersection_dic[intersection].append(item[0])
    return intersection_dic
