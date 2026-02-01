import json
import time
import random

import requests

# 最开始的接口，产生csrf等
csgo_url = "https://buff.163.com/market/csgo"
notification_url = "https://buff.163.com/api/message/notification?"

# 需要修改的地方,notification_url = "https://buff.163.com/api/message/notification?"从这获取，cookie去除session和csrf
# headers = {
#     "Cookie":"Device-Id=CNJ34cgAjIaMsHaH7Hbj; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=dlqh0q8dQbtt6xaQ_wC6Y.05DnZu7dyYw80EZm5HDDNuqC5iqgFBt6PLqQISw60O_CZglHfG9yKxvLBY8GsUaYUCmjGo.XNmPnDla0Fd3VgGBwG.DUHecIHrsPg.DUC6049oj6NK0.T.6aZm_mlwkaPSIkyIn46uvohGsTOtKttQ_.bkO_DzDDJAUncSKVa10CbmV97kDlfwYk.xWeOijIc4GafypNGxy24Q0s490jIhP; S_INFO=1766302068|0|0&60##|16670494952; P_INFO=16670494952|1766302068|1|netease_buff|00&99|gud&1765437860&netease_buff#gud&440100#10#0#0|&0||16670494952; remember_me=U1092505075|ELofcBSBtGkUxg9PM4WCwjG2rYJrAmzS",
#     "Host": "buff.163.com",
#     "Referer": "https://buff.163.com/market/csgo",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "X-Requested-With": "XMLHttpRequest"
# }
#
# # 需要修改的地方,从"https://buff.163.com/market/csgo"获取,cookie去除csrf,保留session_id
# headers_csgo = {
#     "Cookie": "Device-Id=CNJ34cgAjIaMsHaH7Hbj; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=dlqh0q8dQbtt6xaQ_wC6Y.05DnZu7dyYw80EZm5HDDNuqC5iqgFBt6PLqQISw60O_CZglHfG9yKxvLBY8GsUaYUCmjGo.XNmPnDla0Fd3VgGBwG.DUHecIHrsPg.DUC6049oj6NK0.T.6aZm_mlwkaPSIkyIn46uvohGsTOtKttQ_.bkO_DzDDJAUncSKVa10CbmV97kDlfwYk.xWeOijIc4GafypNGxy24Q0s490jIhP; S_INFO=1766302068|0|0&60##|16670494952; P_INFO=16670494952|1766302068|1|netease_buff|00&99|gud&1765437860&netease_buff#gud&440100#10#0#0|&0||16670494952; remember_me=U1092505075|ELofcBSBtGkUxg9PM4WCwjG2rYJrAmzS; session=1-yUMxilJFT8imPvThDdgmmelbUMT4unW9qiWJQke_I9h52043728555",
#     "Referer": "https://buff.163.com/",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0   Safari/537.36"
# }


# 账号池配置
ACCOUNTS = [
    {
        "name": "Account_0",
        # 需要修改的地方,notification_url = "https://buff.163.com/api/message/notification?"从这获取，cookie去除session和csrf
        "headers": {
    "Cookie":"Device-Id=L7zN7l3WUU0FHHffDOdn; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=LQ32xgyWusF2PJgpuJhKjVokOSlcZ8hSOZs0yIjWTTzDv4jcvh2dqAKrvl9MXAs8p4yh3WGg7ESVxrd_ZguHQ_H4IwgUifzIKmT3Qs2LRBhgdXgiTHW519W6uKhiTH4AsL2cF5.STqFCF48ghvtHSNxh8A9QpTmzVppXp3xfSRaiGadzFR8PpXBMa1Oz9oqKZEnMlH5tD4VbzAfL213_JuQagQGEnzgVEbalsua7sw9YK; S_INFO=1769940715|0|0&60##|16670494952; P_INFO=16670494952|1769940715|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|eCST7zU3UqgUWDyr8Q3XDHOs5HeQcLgw",
    "Host": "buff.163.com",
    "Referer": "https://buff.163.com/market/csgo",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
        },
        "headers_csgo": {
    "Cookie": "Device-Id=L7zN7l3WUU0FHHffDOdn; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=LQ32xgyWusF2PJgpuJhKjVokOSlcZ8hSOZs0yIjWTTzDv4jcvh2dqAKrvl9MXAs8p4yh3WGg7ESVxrd_ZguHQ_H4IwgUifzIKmT3Qs2LRBhgdXgiTHW519W6uKhiTH4AsL2cF5.STqFCF48ghvtHSNxh8A9QpTmzVppXp3xfSRaiGadzFR8PpXBMa1Oz9oqKZEnMlH5tD4VbzAfL213_JuQagQGEnzgVEbalsua7sw9YK; S_INFO=1769940715|0|0&60##|16670494952; P_INFO=16670494952|1769940715|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|eCST7zU3UqgUWDyr8Q3XDHOs5HeQcLgw; session=1-nneu4i7r63k-eZD1EYjiS7tSc9TVSpotE_vQwemLPizR2043728555",
    "Referer": "https://buff.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0   Safari/537.36"
                        }

    }
#     ,
#     #xiaohao
#     {
#         "name": "Account_1",
#         "headers": {
#     "Cookie":"Device-Id=cU3NwGMCWrayZcEqoV0G; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=ejo4yGvperDa_BERC7Ed_WK6QO4sy0JDwsNTu.GSqqxtd3GbdnHABw45d8iQhwN093unZS_pcDarL5AIspzKOIK3.gpP2Yx.4kqZONHey6npAhp2qKSfoiSjz4n2qK3wNRcPgwxaN2v2wOu.9.ZhFO4QiFDikRwtLPmpzv0BaBB81AskldA9JXKAZnhEa.6rOitx92U8jqxDbtSnqlQETRVRpO_D7xprDWR8NzRcNgim4; S_INFO=1766906853|0|0&60##|16670494952; P_INFO=16670494952|1766906853|1|netease_buff|00&99|gud&1766302068&netease_buff#gud&440100#10#0#0|&0||16670494952; r_ntcid=730:222; qr_code_verify_ticket=194FwfG16d39c99830672c3870dea3d332d8; remember_me=U1084862224|4t6L9BXzZ5bT9AVO44UTCnWeijGa40zD",
#     "Host": "buff.163.com",
#     "Referer": "https://buff.163.com/market/csgo",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "X-Requested-With": "XMLHttpRequest"
# }
#         ,
#         "headers_csgo": {
#     "Cookie": "Device-Id=cU3NwGMCWrayZcEqoV0G; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=ejo4yGvperDa_BERC7Ed_WK6QO4sy0JDwsNTu.GSqqxtd3GbdnHABw45d8iQhwN093unZS_pcDarL5AIspzKOIK3.gpP2Yx.4kqZONHey6npAhp2qKSfoiSjz4n2qK3wNRcPgwxaN2v2wOu.9.ZhFO4QiFDikRwtLPmpzv0BaBB81AskldA9JXKAZnhEa.6rOitx92U8jqxDbtSnqlQETRVRpO_D7xprDWR8NzRcNgim4; S_INFO=1766906853|0|0&60##|16670494952; P_INFO=16670494952|1766906853|1|netease_buff|00&99|gud&1766302068&netease_buff#gud&440100#10#0#0|&0||16670494952; r_ntcid=730:222; qr_code_verify_ticket=194FwfG16d39c99830672c3870dea3d332d8; remember_me=U1084862224|4t6L9BXzZ5bT9AVO44UTCnWeijGa40zD; session=1-bk4bqoRLOrnWcvrYAqTQ9Ab0Bq7eJtenEycVUkQYrCUQ2020028488",
#     "Referer": "https://buff.163.com/",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0   Safari/537.36"
# }
#     }
]




query_params = {"from": "market"}

# 传入时间戳给notification接口
base_params = {
    "_": int(time.time() * 1000)
}


# 返回的磨损数据，购买id号等在这里,查询磨损接口
search_url = "https://buff.163.com/api/market/goods/sell_order"
auto_buy = "https://buff.163.com/api/market/bill_order/page_pay"
# 购买接口
buy_url = 'https://buff.163.com/api/market/goods/buy/preview'
buy_last = 'https://buff.163.com/api/market/goods/buy'

# 市场刷新接口，传入参数为崭新，略磨，皮肤隐秘程度，设置价格等
first_url = "https://buff.163.com/api/market/goods"
def send_payment(headers, params):
    try:
        response = requests.post(url=buy_last, headers=headers, json=params)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def extract_gun_name(full_string):
    # 查找最后一个 '|' 的位置
    last_pipe_index = full_string.rfind('|')
    left_parenthesis_index = full_string.find('(', last_pipe_index)
    extracted_part = full_string[last_pipe_index:left_parenthesis_index].strip()
    prefix_part = full_string[last_pipe_index - 2:last_pipe_index]
    result = prefix_part + extracted_part
    return result

def random_sleep(min_sleep, max_sleep):
    sleep_time = random.uniform(min_sleep, max_sleep)
    print(sleep_time)
    time.sleep(sleep_time)

def print_red(text):
    # 文本颜色设置为红色
    print(f"\033[91m{text}\033[0m")


def print_blue(text):
    # 文本颜色设置为蓝色
    print(f"\033[94m{text}\033[0m")


def search_wearpaint(search_name, weapon_dict):
    """
    根据枪名寻找适合的最大磨损区间
    传入枪名和包含枪名的字典
    返回能买的最大磨损
    """
    print_red(search_name)
    try:
        paint_wear = float(weapon_dict.get(search_name, 0.0))
    except TypeError:
        paint_wear = None
    print_blue(paint_wear)
    return paint_wear


def decide_buy(low_price, steam_price):
    """
    传入当前区间的最低价格和steam上的价格
    根据买的价格决定买不买,按照当前区间的最低价格和steam上的价格决定买不买
    返回处理的上限价格和steam价格
    """
    price = float(low_price)
    steam_price = float(steam_price)
    if price < 150:
        spr = price * (1.1 - price / 21 * 0.01)
    elif 150 <= price < 260:
        spr = price + 5
    else:
        spr = price + 6
    st = steam_price * 0.92
    return spr, st


def get_csrf(response):
    """
    传入res
    根据notification提取csrf_token和session_id
    返回处理的csrf_token和session_id
    # 保持健壮性应该如下：
        # print(cookies)
        # for cookie in cookies:
        #     if 'csrf_token' in cookie:
        # break
    """
    # print('headers:',res.headers)
    set_cookie_header = response.headers.get('set-cookie')
    ct = None
    session = None
    if set_cookie_header:
        cookies = set_cookie_header.split(';')
        # print(cookies[0])
        ct = cookies[2].split('=')[2]
        session = cookies[0].split('=')[1]
        # print('session:',session,'cookie:',ct)
    return ct, session


def update_headers_with_csrf(headers, csrf, session):
    """
    根据notification产生的crsf和session
    更新后面的头用于其他接口
    """
    new_headers = headers.copy()
    new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={csrf}" + f"; session={session}"
    return new_headers


def try_again(headers2, request_url, params, max_retries=5, delay=1):
    """
    传入请求头和url,参数
    防止请求失败，多次刷新，最大为5次
    返回请求到的data和数据头
    """
    retries = 0
    data = None
    newheaders = None
    while retries < max_retries:
        try:
            res = requests.get(url=request_url, headers=headers2, params=params)
            cf3, sid3 = get_csrf(res)
            newheaders = update_headers_with_csrf(headers2, cf3, sid3)
            data = res.json()["data"]["items"]
            break
        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSONDecodeError: {e}")
            print("Response text:", res.text)
        retries += 1
        print(f"Retrying2... ({retries}/{max_retries})")
        time.sleep(delay)
        delay *= 2  # 指数退避
    return res,data, newheaders
