import json
import time
import random

import requests

# 最开始的接口，产生csrf等
csgo_url = "https://buff.163.com/market/csgo"
notification_url = "https://buff.163.com/api/message/notification?"

# 需要修改的地方,notification_url = "https://buff.163.com/api/message/notification?"从这获取，cookie去除session和csrf
headers = {
    "Cookie":"_ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; NTES_CMT_USER_INFO=1203230979%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B17JZA3%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeWQuNzBlMjAyYzRhZmNmNGNmNzhAMTYzLmNvbQ%3D%3D; Device-Id=hQOL5SvXQ4Wo0tXkElVY; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=fPkWeC7MxgBNrAUq45l2u52mhWLcU_65dzxvt2pQddrBeypJekSXAhRGesb8mhxNcytkuQ97oqOj5GXiz7Va0iay2n74WIr2RFdu0xSfDwk7Xm7WdaQ_PbQgVRkWdayhxEo4nhrOxWLWh0t2c2umH0R8bHqbFEhB54.7VLNAOAAGN5U9zR_AMwhfG1ImsmuO8ms2WuWqidW1lcjC3VY0EJ0E709q1r7jqMEsxVEoxnb.R; S_INFO=1748757177|0|0&60##|16670494952; P_INFO=16670494952|1748757177|1|netease_buff|00&99|gud&1747816886&netease_buff#gud&440100#10#0#0|&0||16670494952; remember_me=U1092505075|g7kkQptESW8yftlQBvC3uGlLnCBsqGiS",
    "Host": "buff.163.com",
    "Referer": "https://buff.163.com/market/csgo",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# 需要修改的地方,从"https://buff.163.com/market/csgo"获取,cookie去除csrf,保留session_id
headers_csgo = {
    "Cookie": "_ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; NTES_CMT_USER_INFO=1203230979%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B17JZA3%7Chttp%3A%2F%2Fcms-bucket.nosdn.127.net%2F2018%2F08%2F13%2F078ea9f65d954410b62a52ac773875a1.jpeg%7Cfalse%7CeWQuNzBlMjAyYzRhZmNmNGNmNzhAMTYzLmNvbQ%3D%3D; Device-Id=hQOL5SvXQ4Wo0tXkElVY; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=fPkWeC7MxgBNrAUq45l2u52mhWLcU_65dzxvt2pQddrBeypJekSXAhRGesb8mhxNcytkuQ97oqOj5GXiz7Va0iay2n74WIr2RFdu0xSfDwk7Xm7WdaQ_PbQgVRkWdayhxEo4nhrOxWLWh0t2c2umH0R8bHqbFEhB54.7VLNAOAAGN5U9zR_AMwhfG1ImsmuO8ms2WuWqidW1lcjC3VY0EJ0E709q1r7jqMEsxVEoxnb.R; S_INFO=1748757177|0|0&60##|16670494952; P_INFO=16670494952|1748757177|1|netease_buff|00&99|gud&1747816886&netease_buff#gud&440100#10#0#0|&0||16670494952; remember_me=U1092505075|g7kkQptESW8yftlQBvC3uGlLnCBsqGiS; session=1-tWEiIkDG2vWiO06azF77FR9A87g3fJQ4_4g-_gCWMRyZ2043728555",
    "Referer": "https://buff.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
            newheaders = update_headers_with_csrf(headers, cf3, sid3)
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
