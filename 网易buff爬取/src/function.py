import json
import time
import random

import requests

# 最开始的接口，产生csrf等
csgo_url = "https://buff.163.com/market/csgo"
notification_url = "https://buff.163.com/api/message/notification?"

# 需要修改的地方,notification_url = "https://buff.163.com/api/message/notification?"从这获取，cookie去除session和csrf
headers = {
    "Cookie":"Device-Id=L7zN7l3WUU0FHHffDOdn; Locale-Supported=zh-Hans; game=csgo; gdxidpyhxdE=NBCf2b9uEBswwRBYxNRztlLyefawXRCyHq1GVef5jo7QwNjKaQhYX5YiU%5C3DodsIQIxrnKS4WWspPa8xN8ghb1g%2Be5mgQY%2F5r9ItVQoa6Sgdtq%5Cc2cYmsr%2BLwjc82PXxwmBYI91uRKHQpr8jPWtAyQ5vW7ZzmvvAafaHwTPC3gKC6U00%3A1769945351692; NTES_YD_SESS=S0k2OZaiZg4VZDqeZ0v3VeCRNFDajm1y39i.7TleFFb1HglxHydKU4wMH_NfR4iIsg7ype8ZzkXJWMK09ZcAY0AgT3Z6vObTwDFpYidSnPyZKRZvFAeQVNeCcwyvFAg4iSdxBQqXFUBGBgIZyHoAX2WyI4NYsFDbJssRspWOXnhDJSSYysC6DUaupeoNwhzxOtpMRb1nH43BdT5s6X0bDdVhZY8kubZJkLh_ichzi3NEw; S_INFO=1769944902|0|0&60##|16670494952; P_INFO=16670494952|1769944902|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gqhVeQBYEomt29M6R49cYBToMHkdsQHW",
    "Host": "buff.163.com",
    "Referer": "https://buff.163.com/market/csgo",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# 需要修改的地方,从"https://buff.163.com/market/csgo"获取,cookie去除csrf,保留session_id
headers_csgo = {
    "Cookie": "Device-Id=L7zN7l3WUU0FHHffDOdn; Locale-Supported=zh-Hans; game=csgo; gdxidpyhxdE=NBCf2b9uEBswwRBYxNRztlLyefawXRCyHq1GVef5jo7QwNjKaQhYX5YiU%5C3DodsIQIxrnKS4WWspPa8xN8ghb1g%2Be5mgQY%2F5r9ItVQoa6Sgdtq%5Cc2cYmsr%2BLwjc82PXxwmBYI91uRKHQpr8jPWtAyQ5vW7ZzmvvAafaHwTPC3gKC6U00%3A1769945351692; NTES_YD_SESS=S0k2OZaiZg4VZDqeZ0v3VeCRNFDajm1y39i.7TleFFb1HglxHydKU4wMH_NfR4iIsg7ype8ZzkXJWMK09ZcAY0AgT3Z6vObTwDFpYidSnPyZKRZvFAeQVNeCcwyvFAg4iSdxBQqXFUBGBgIZyHoAX2WyI4NYsFDbJssRspWOXnhDJSSYysC6DUaupeoNwhzxOtpMRb1nH43BdT5s6X0bDdVhZY8kubZJkLh_ichzi3NEw; S_INFO=1769944902|0|0&60##|16670494952; P_INFO=16670494952|1769944902|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gqhVeQBYEomt29M6R49cYBToMHkdsQHW; session=1-BrwLSyKW5FVouMq1Xa5-k9QpEZz_D7-OEHz3pIqQkCDt2043728555; EPAY_SSID=85D22EA2E3586ACE0612D91698C00688DFF543586509A1C4698CD3B92637B865; EPAY_CrosId=85D22EA2E3586ACE0612D91698C00688DFF543586509A1C4698CD3B92637B865; hb_MA-B480-7AA0C2ACD2CD_source=buff.163.com",
    "Referer": "https://buff.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0   Safari/537.36"
}







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
    # print(sleep_time)
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
    返回能买的最大磨损 (float) 或者 None
    """
    print_red(search_name) # 调试打印，生产环境建议注释掉以提高速度

    # 1. 直接从字典获取值，找不到默认返回 None
    wear_value = weapon_dict.get(search_name)

    # 2. 如果没找到，或者值为 "no"，直接返回 None (不买)
    if wear_value is None or wear_value == "no":
        return None

    try:
        # 3. 尝试转换为浮点数
        paint_wear = float(wear_value)
    except (ValueError, TypeError):
        # 防止 json 里写了奇怪的字符串导致报错
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


# def get_csrf(response):
#     """
#     传入res
#     根据notification提取csrf_token和session_id
#     返回处理的csrf_token和session_id
#     # 保持健壮性应该如下：
#         # print(cookies)
#         # for cookie in cookies:
#         #     if 'csrf_token' in cookie:
#         # break
#     """
#     # print('headers:',res.headers)
#     set_cookie_header = response.headers.get('set-cookie')
#     ct = None
#     session = None
#     if set_cookie_header:
#         cookies = set_cookie_header.split(';')
#         # print(cookies[0])
#         ct = cookies[2].split('=')[2]
#         session = cookies[0].split('=')[1]
#         # print('session:',session,'cookie:',ct)
#     return ct, session


def get_csrf(response):
    """
    直接从 response.cookies 中提取，不需要手动分割字符串
    """
    ct = response.cookies.get('csrf_token')
    session = response.cookies.get('session')

    # 如果通过 .cookies 拿不到（有时是因为还没存入 jar），再考虑从 headers 拿
    if not ct or not session:
        # 使用 requests 提供的工具解析复杂的 set-cookie
        cookies_dict = response.cookies.get_dict()
        ct = cookies_dict.get('csrf_token')
        session = cookies_dict.get('session')

    # print(f"提取结果 -> Session: {session}, CSRF: {ct}")
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
