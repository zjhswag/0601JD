import concurrent.futures
import gc
import json
import logging
import time

import requests
import os
import urllib3
from function import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start_time = int(time.time() * 1000)

# 导入枪和查找适合的磨损区间
json_file_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'merged_data2.json')
with open(json_file_path, 'r', encoding='utf-8') as f:
    buy_guns = json.load(f)
# json_file_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'merged_data2.json')
# with open(json_file_path, 'r', encoding='utf-8') as f:
#     buy_guns_1 = json.load(f)
# json_file_path = os.path.join(os.path.dirname(__file__), '..', 'dist', 'merged_data2.json')
# with open(json_file_path, 'r', encoding='utf-8') as f:
#     buy_guns_2 = json.load(f)

# 接收notification的响应头传给市场请求头的cookie,修改请求参数的地方,wearcategory2
# 注意去掉了崭新
market_params = {
    "game": "csgo",
    "page_num": "1",
    "max_price": "250",
    # legendary_weapon,legendary_weapon
    # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
    "rarity": "mythical_weapon,legendary_weapon,ancient_weapon",
    "quality": "normal,strange",
    "exterior": "wearcategory0,wearcategory1",
    "tab": "selling",
    "use_suggestion": "0",
    "_": int(time.time() * 1000)
}
market_params_special = {
    "game": "csgo",
    "page_num": "1",
    "max_price": "1000",
    # legendary_weapon,legendary_weapon
    # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
    "rarity": "ancient_weapon",
    "quality": "normal",
    "exterior": "wearcategory0,wearcategory1",
    "tab": "selling",
    "use_suggestion": "0",
    "_": int(time.time() * 1000)
}
market_params_gun_gui = {
    "game": "csgo",
    "page_num": "1",
    "max_price": "100",
    # legendary_weapon,legendary_weapon
    # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
    "rarity": "rare_weapon",
    "quality": "normal,strange",
    "exterior": "wearcategory0",
    "tab": "selling",
    "use_suggestion": "0",
    "_": int(time.time() * 1000)
}
market_params_jiu_jin = {
    "game": "csgo",
    "page_num": "1",
    "max_price": "300",
    # legendary_weapon,legendary_weapon
    # legendary_weapon是保密，ancient是隐秘，剩下一个是受限
    "rarity": "legendary_weapon,ancient_weapon",
    "quality": "normal,strange",
    "exterior": "wearcategory2",
    "tab": "selling",
    "use_suggestion": "0",
    "_": int(time.time() * 1000)
}
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("csgo_gun.log", encoding='utf-8'),
                    ])

logger = logging.getLogger(__name__)
i = 0
previous_guns = set()


def query_gun(gun, head,market_res):
    try:
        gun_id = gun['id']
        name = gun['name']
        quick_price = float(gun['quick_price']) * 0.88
        sell_num = float(gun['sell_num'])

        # print(res3.json())
        buy_paint = search_wearpaint(name, buy_guns)
        # print(buy_paint)
        cf4, sid4 = get_csrf(market_res)
        new_headers = update_headers_with_csrf(head, cf4, sid4)

        search_params = {"game": "csgo",
                         "goods_id": f"{gun_id}",
                         "page_num": "1",
                         "sort_by": "default",
                         "mode": "",
                         "allow_tradable_cooldown": "1",
                         "_": int(time.time() * 1000)
                         }

        res5, data2, new_headers = try_again(new_headers, search_url, search_params)
        cf5, sid5 = get_csrf(res5)
        # print(data)
        # 得到磨损数据
        st_price = res5.json()['data']["goods_infos"][f"{gun_id}"]['steam_price_cny']
        if data2 is not None and buy_paint is not None:
            for item in data2[:5]:
                paintwear = float(item['asset_info']['paintwear'])
                price = float(item['price'])  # 购买价格
                sell_id = item['id']
                sp, st = decide_buy(gun['sell_min_price'], st_price)
                # print(f"磨损：{paintwear},价格{price}，名字{name}")
                if price > sp or price > st:
                    logger.info(f"价格不合适: {name}, 价格: {price}")
                    continue
                is_first = (item == data2[0])
                is_wear_ok = (paintwear <= buy_paint)
                is_quick_buy_ok = is_first and (price < quick_price and sell_num > 80)

                if is_wear_ok or is_quick_buy_ok:
                    # 3. 构造统一的支付参数
                    new_headers = update_headers_with_csrf(headers, cf5, sid5)
                    new_headers["X-Csrftoken"] = cf5

                    buy_params = {
                        "game": "csgo",
                        "goods_id": f"{gun_id}",
                        "sell_order_id": f"{sell_id}",
                        "price": f"{price}",
                        "pay_method": "49",  # 先尝试支付宝
                        "allow_tradable_cooldown": "0",
                        "hide_non_epay": "ture"
                    }

                    # 4. 封装支付尝试逻辑 (定义一个内部函数或直接循环尝试)
                    for method in ["49", "63"]:  # 49:支付宝, 63:余额
                        buy_params["pay_method"] = method
                        res = requests.post(url=buy_last, headers=new_headers, json=buy_params)
                        resp_data = res.json()
                        print(resp_data)
                        logger.info(resp_data)
                        if resp_data.get("code") == "OK":
                            logger.info(f"购买成功! 方式:{method}, 饰品:{name}, 磨损:{paintwear}")
                            break  # 支付成功，跳出支付方式循环
                    else:
                        # 如果两个支付方式都走完了还没成功
                        logger.info(f"所有支付方式均失败: {name},磨损：{paintwear}")
                else:
                    logger.info(f"磨损不合适: {name}")
        return gun['name'], gun['sell_min_price']
    except requests.RequestException as e:
        return str(e)


while True:
    i += 1

    # 通过csgo_url给后续接口产生csrf和session
    res = requests.get(url=csgo_url, headers=headers_csgo)
    cf1, sid1 = get_csrf(res)

    new_headers = update_headers_with_csrf(headers, cf1, sid1)

    # 防止请求过快
    random_sleep(0,2)
    f1 = time.time() * 1000

    # 市场刷新接口，传入参数为崭新，略磨，皮肤隐秘程度，设置价格等
    # first_url = "https://buff.163.com/api/market/goods?"
    # if i % 2 == 0:
    #     res3, data, new_headers = try_again(new_headers, first_url, market_params_gun_gui)
    # else:
    #     res3, data, new_headers = try_again(new_headers, first_url, market_params_jiu_jin)

    # if i % 2 != 0:
    #     res3, data, new_headers = try_again(new_headers, first_url, market_params)
    # else:
    res3, data, new_headers = try_again(new_headers, first_url, market_params_special)

    if data is not None:
        print('************')
        # print(data)
        current_guns = set()
        # 存储市场接口返回来最新枪的数据，枪名，最低价格，在售数量
        guns = []
        for item in data[:2]:
            gun_name = item.get('name', None)
            if gun_name not in previous_guns:
                gun = {
                    'name': item.get('name', None),
                    'sell_min_price': item.get('sell_min_price', None),
                    'sell_num': item.get('sell_num', None),
                    'id': item.get('id', None),
                    'quick_price': item.get('quick_price', None)
                }
                guns.append(gun)
                current_guns.add(gun_name)
        # print(guns)
        # 买枪函数

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_gun = {executor.submit(query_gun, gun, new_headers,res3): gun for gun in guns}
            for future in concurrent.futures.as_completed(future_to_gun):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    # print("moo")
                    logger.error(f'Generated an exception: {exc}')
        # print(results)
        last_time = int(time.time() * 1000)
        print(f"这是第{i}次刷新:")
        print('程序查询时间为:', last_time - f1, 'ms')
        print('程序运行时间为:', last_time - start_time, 'ms')
        previous_guns = current_guns
    if i % 12 == 0:
        time.sleep(10)
    if i % 100 == 0:
        time.sleep(15)
    if i % 400 == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('清空控制台')
    del guns
    del results
    del data
    # gc.collect()
