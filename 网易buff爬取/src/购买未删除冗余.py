import concurrent.futures
import json
import requests
from lxml import etree
import time
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入枪和查找适合的磨损区间
json_file_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'merged_data.json')
with open(json_file_path, 'r', encoding='utf-8') as f:
    buy_guns = json.load(f)


def extract_gun_name(full_string):
    # 查找最后一个 '|' 的位置
    last_pipe_index = full_string.rfind('|')
    left_parenthesis_index = full_string.find('(', last_pipe_index)
    extracted_part = full_string[last_pipe_index:left_parenthesis_index].strip()
    prefix_part = full_string[last_pipe_index - 2:last_pipe_index]
    result = prefix_part + extracted_part
    return result


first_time = int(time.time() * 1000)


def search_wearpaint(search_name):
    """
    根据枪名寻找适合的磨损区间
    """
    try:
        paint_wear = float(buy_guns.get(search_name, 0.0))
    except TypeError:
        paint_wear = None
    print(paint_wear)
    return paint_wear
    # return search_name not in no_buy_guns


def decide_buy(price, steam_price):
    """
    根据买的价格决定买不买
    """
    price = float(price)
    if price < 150:
        spr = price * (1.1 - price / 21 * 0.01)
    elif 150 <= price < 260:
        spr = price + 5
    else:
        spr = price + 6
    st = float(steam_price) * 0.92
    return spr, st


def get_csrf(res):
    """
    提取csrf_token，
    # 保持健壮性应该如下：
        # print(cookies)
        # for cookie in cookies:
        #     if 'csrf_token' in cookie:
        # break
    """
    # print('headers:',res.headers)
    set_cookie_header = res.headers.get('set-cookie')
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
    new_headers = headers.copy()
    new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={csrf}" + f"; session={session}"
    return new_headers


def request_with_csrf(url, headers, params):
    res = requests.get(url=url, headers=headers, params=params)
    return res, get_csrf(res)


i = 0
while True:
    i += 1
    # 给notification接口产生csrf和session
    csgo_url = "https://buff.163.com/market/csgo"
    headers_csgo = {
        "Cookie": "Device-Id=3QkxxQrsLtKqchD4k3sQ; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=UrZNC_spvrT3N91QJ1gjqk8UYf4VfnKF5Ymn_ySB77.915ST1ltocJrH1XEACJmhO5_lfBaQ0p62FHoRYQIVwRV5yMQxD4.yrZ7fwmtUGblQoCQD7VBKNEBWIrlD7V5JmUtTzKu67czez5hQl1iV6kFlhJEwO7Z.2gJkxtkb5cYgHvXP2lhW5c74aSDtvsg8ydcSJmiq_FeeRWJUcm7ORM4jQwap8.Q2pqjXmIj0mME3r; S_INFO=1718866601|0|0&60##|16670494952; P_INFO=16670494952|1718866601|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gNrj9KdjJjhslohwFqqauRzgYwRcDlGf; session=1-wV4Lo0_nKodSTjj1-x0R6MQy7mfjgu48p-xY7CGVBTHM2043728555; steam_verify_result=",
        "Referer": "https://buff.163.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    res = requests.get(url=csgo_url, headers=headers_csgo)
    cf1, sid1 = get_csrf(res)
    # 传递产生的csrf和session给notification接口
    # 获取csrf_token，通过notification接口，不需要自带csrf_token
    notification_url = "https://buff.163.com/api/message/notification?"
    headers = {
        "Cookie": "Device-Id=3QkxxQrsLtKqchD4k3sQ; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=UrZNC_spvrT3N91QJ1gjqk8UYf4VfnKF5Ymn_ySB77.915ST1ltocJrH1XEACJmhO5_lfBaQ0p62FHoRYQIVwRV5yMQxD4.yrZ7fwmtUGblQoCQD7VBKNEBWIrlD7V5JmUtTzKu67czez5hQl1iV6kFlhJEwO7Z.2gJkxtkb5cYgHvXP2lhW5c74aSDtvsg8ydcSJmiq_FeeRWJUcm7ORM4jQwap8.Q2pqjXmIj0mME3r; S_INFO=1718866601|0|0&60##|16670494952; P_INFO=16670494952|1718866601|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|gNrj9KdjJjhslohwFqqauRzgYwRcDlGf; session=1-wV4Lo0_nKodSTjj1-x0R6MQy7mfjgu48p-xY7CGVBTHM2043728555; steam_verify_result=",
        "Host": "buff.163.com",
        "Referer": "https://buff.163.com/market/csgo",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    new_headers = headers.copy()
    new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf1}" + f"; session={sid1}"

    # 传入时间戳给notification接口
    base_params = {
        "_": int(time.time() * 1000)
    }

    # 传递notification产生的csrf和session给市场接口
    res2 = requests.get(url=notification_url, headers=new_headers, params=base_params)
    cf2, sid2 = get_csrf(res2)
    new_headers = headers.copy()
    new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"

    time.sleep(2)
    f1 = time.time()*1000
    # 市场刷新接口，传入参数为崭新，略磨，皮肤隐秘程度，设置价格等
    first_url = "https://buff.163.com/api/market/goods?"
    # 接收notification的响应头传给市场请求头的cookie
    params = {
        "appid": "730",
        "game": "csgo",
        "page_num": "1",
        "max_price": "300",
        # legendary_weapon,legendary_weapon
        # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
        "rarity": "mythical_weapon,legendary_weapon,legendary_weapon",
        "quality": "normal,strange",
        "exterior": "wearcategory0,wearcategory1",
        "tab": "selling",
        "use_suggestion": "0",
        "_": int(time.time() * 1000)
    }
    retries = 0
    max_retries = 5
    delay = 1

    while retries < max_retries:
        try:
            res3 = requests.get(url=first_url, headers=new_headers, params=params, verify=False)
            cf3, sid3 = get_csrf(res3)

            new_headers = headers.copy()
            new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf3}" + f"; session={sid3}"
            data = res3.json()["data"]["items"]
            break
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print("Response text:", res3.text)
        retries += 1
        print(f"Retrying... ({retries}/{max_retries})")
        time.sleep(delay)
        delay *= 2  # 指数退避
    if data:
    # 存储市场接口返回来最新枪的数据，枪名，最低价格，在售数量
        guns = []
        for item in data:
            gun = {
                'name': item.get('name', None),
                'sell_min_price': item.get('sell_min_price', None),
                'sell_num': item.get('sell_num', None),
                'id': item.get('id', None)
            }
            guns.append(gun)
        print("本次查询到的枪为:", guns[:4])
        query_params = {"from": "market"}
        buy_base_url = f'https://buff.163.com/goods/{gun["id"]}?'
        # 查找csrf每把枪的csrf不同，根据id获取
        search_url = "https://buff.163.com/api/market/goods/sell_order?"
        buy_url = 'https://buff.163.com/api/market/goods/buy/preview?'
        buy_last = 'https://buff.163.com/api/market/goods/buy'


        def query_gun(gun, head):
            try:
                retries = 0
                max_retries = 5
                delay = 1
                gun_id = gun['id']
                name = gun['name']
                buy_paint = search_wearpaint(name)
                res4 = requests.get(url=buy_base_url, headers=head, params=query_params)  # 根据id,差不多是notification的作用
                cf4, sid4 = get_csrf(res4)
                new_headers = headers.copy()
                new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf4}" + f"; session={sid4}"

                search_params = {"game": "csgo",
                                 "goods_id": f"{gun_id}",
                                 "page_num": "1",
                                 "sort_by": "default",
                                 "mode": "",
                                 "allow_tradable_cooldown": "1",
                                 "_": int(time.time() * 1000)
                                 }
                res5 = requests.get(url=search_url, params=search_params, headers=new_headers)  # 查询磨损接口
                cf5, sid5 = get_csrf(res5)
                new_headers = headers.copy()
                new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf5}" + f"; session={sid5}"
                # 返回的磨损数据，购买id号等在这里
                while retries < max_retries:
                    try:
                        data = res5.json().get('data', {}).get('items', [])
                        st_price = res5.json()['data']["goods_infos"][f"{gun_id}"]['steam_price_cny']
                        break
                    except json.JSONDecodeError as e:
                        print(f"JSONDecodeError: {e}")
                        print("Response text:", res5.text)
                    retries += 1
                    print(f"Retrying... ({retries}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
                if data and buy_paint is not None:
                    for item in data[:6]:
                        paintwear = item['asset_info']['paintwear']
                        paintwear = float(paintwear)
                        price = float(item['price'])  # 购买价格
                        sell_id = item['id']
                        alipay_error = None
                        bank_error = None
                        sp, st = decide_buy(gun['sell_min_price'], st_price)
                        if paintwear <= buy_paint and price <= sp and price <= st:
                            buy_params = {"game": "csgo",
                                          "sell_order_id": f"{sell_id}",
                                          "goods_id": f"{gun_id}",
                                          "price": f"{price}",
                                          "allow_tradable_cooldown": "0",
                                          "cdkey_id": "",
                                          "_": int(time.time() * 1000)
                                          }
                            res6 = requests.get(url=buy_url, headers=new_headers, params=buy_params)  # 获取支付方式接口
                            cf6, sid6 = get_csrf(res6)
                            new_headers = headers.copy()
                            new_headers["Cookie"] = headers["Cookie"] + f"; csrf_token={cf6}" + f"; session={sid6}"
                            new_headers["X-Csrftoken"] = cf4

                            methods = res6.json()['data']['pay_methods']  # 获取到的支付方式,寻找合适的购买方式的皮肤
                            for method in methods:
                                if method['name'] == '支付宝支付':
                                    alipay_error = method['error']
                                elif method['name'] == 'BUFF余额-银行卡':
                                    bank_error = method['error']
                            if bank_error != "该饰品暂不支持此支付方式":
                                buy_params_last = {
                                    "game": "csgo",
                                    "goods_id": f"{gun_id}",
                                    "sell_order_id": f"{sell_id}",
                                    "price": f"{price}",
                                    "pay_method": f'{1}',  # 支付方式
                                    "allow_tradable_cooldown": "0",
                                    "token": "",
                                    "cdkey_id": "",
                                    "hide_non_epay": "false"
                                }
                                res7 = requests.post(url=buy_last, headers=new_headers, json=buy_params_last)  # 支付结束
                                print(f'购买成功{name}')
                                print(res7.json())
                            elif alipay_error != "该饰品暂不支持此支付方式":
                                buy_params_last = {
                                    "game": "csgo",
                                    "goods_id": f"{gun_id}",
                                    "sell_order_id": f"{sell_id}",
                                    "price": f"{price}",
                                    "pay_method": f'{49}',  # 支付方式
                                    "allow_tradable_cooldown": "0",
                                    "token": "",
                                    "cdkey_id": "",
                                    "hide_non_epay": "false"
                                }
                                res7 = requests.post(url=buy_last, headers=new_headers, json=buy_params_last)  # 支付结束
                                print(f'购买成功{name}')
                                print(res7.json())
                            else:
                                print(f"没有合适的支付方式,可买的枪为{gun['name']},磨损: {paintwear}, 价格: {price}")
                        else:
                            print(
                                f"该枪支: {name}不可购买,可买磨损为,{buy_paint},实际磨损: {paintwear}, 价格: {price},上限{sp},steam处理价格{st}")
                            continue

                return gun['name'], gun['sell_min_price']
            except requests.RequestException as e:
                return str(e)


        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_gun = {executor.submit(query_gun, gun, new_headers): gun for gun in guns[:4]}
            for future in concurrent.futures.as_completed(future_to_gun):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    # print("moo")
                    print(f'Generated an exception: {exc}')

        last_time = int(time.time() * 1000)
        print(f"这是第{i}次刷新:")
        print('程序查询时间为:', last_time - f1, 'ms')
        print('程序运行时间为:', last_time - first_time, 'ms')
    del guns
    del results

    # if last_time - first_time > 1900000: # 半小时停止
    #     break
    # else:
    #     print('继续跑！')

    # print(results)
