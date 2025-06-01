import concurrent.futures
import json
from decimal import Decimal, ROUND_FLOOR

import requests
from lxml import etree
import time
import os
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


notification = "https://buff.163.com/api/message/notification?"
no_pa = {
    "_": int(time.time() * 1000)
}
# 保留session
no_head = {
    "Cookie": "Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1709623940; vinfo_n_f_l_n3=801eba530a3c1593.1.1.1709623939065.1709624085379.1709631285413; Device-Id=x6E3DzVuXF8y73bMsSwB; _ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; Locale-Supported=zh-Hans; game=csgo; steam_verify_result=; AQ_HD=1; YD_SC_SID=EE2D0BDBB0834E60811933566731A7E3; AQ_REQ_FROM=webzj; NETS_utid=uDTc5TpoghhacqVslwZaqPkx5HVZQbAU; NTES_YD_SESS=TB6zd8lSqUbtgI3gbn2DIvUtBpDb0hZtcMQaCXx.RR83Eox_E6mDyt1NEWf2BtQS5oC6J.LrG4Fs0NDeMrlkHekoXVr7Yd8X1wRJHQmTPu6rDBrYRk.vpf.zl16YRkotQUG7Vt8FQYOYtHCX5XJBhH12fh4fwUt307ArlOSyFyyNkEm51GzkS7AK8CHzJJe3akIAxetR3Qxap4bVvuqYNvpUrHL4j8rs4IUWQlUGQVfA1; S_INFO=1722599930|0|0&60##|16670494952; P_INFO=16670494952|1722599930|1|netease_buff|00&99|CN&1719916642&netease_buff#gud&440100#10#0#0|&0|null|16670494952; remember_me=U1092505075|VblpAM1gjW2Tc3NaHrVL18PWiWs4xYzi; session=1-UL0oSQfjdavBZcSJP3TDlLw_jddvgAC6heqL3qbLu2oc2043728555",
    "Referer": "https://buff.163.com/market/sell_order/on_sale?game=csgo&mode=2,5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

market = 'https://buff.163.com/market/sell_order/on_sale?'
market_parmas = {
    "game": "csgo",
    "mode": "2,5",
    "sort_by" : "updated.asc"
}
# 在售接口保留session
market_header = {
    "Cookie": "Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1709623940; vinfo_n_f_l_n3=801eba530a3c1593.1.1.1709623939065.1709624085379.1709631285413; Device-Id=x6E3DzVuXF8y73bMsSwB; _ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; Locale-Supported=zh-Hans; game=csgo; steam_verify_result=; AQ_HD=1; YD_SC_SID=EE2D0BDBB0834E60811933566731A7E3; AQ_REQ_FROM=webzj; NETS_utid=uDTc5TpoghhacqVslwZaqPkx5HVZQbAU; NTES_YD_SESS=TB6zd8lSqUbtgI3gbn2DIvUtBpDb0hZtcMQaCXx.RR83Eox_E6mDyt1NEWf2BtQS5oC6J.LrG4Fs0NDeMrlkHekoXVr7Yd8X1wRJHQmTPu6rDBrYRk.vpf.zl16YRkotQUG7Vt8FQYOYtHCX5XJBhH12fh4fwUt307ArlOSyFyyNkEm51GzkS7AK8CHzJJe3akIAxetR3Qxap4bVvuqYNvpUrHL4j8rs4IUWQlUGQVfA1; S_INFO=1722599930|0|0&60##|16670494952; P_INFO=16670494952|1722599930|1|netease_buff|00&99|CN&1719916642&netease_buff#gud&440100#10#0#0|&0|null|16670494952; remember_me=U1092505075|VblpAM1gjW2Tc3NaHrVL18PWiWs4xYzi; session=1-UL0oSQfjdavBZcSJP3TDlLw_jddvgAC6heqL3qbLu2oc2043728555",
    "Referer": "https://buff.163.com/market/sell_order/on_sale?mode=2,5&game=csgo",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
# 每把枪的接口
search_header = {
    "Cookie": "Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1709623940; vinfo_n_f_l_n3=801eba530a3c1593.1.1.1709623939065.1709624085379.1709631285413; Device-Id=x6E3DzVuXF8y73bMsSwB; _ntes_nnid=701170eacefadd792754a0a48efaa075,1716454981484; _ntes_nuid=701170eacefadd792754a0a48efaa075; _ga=GA1.1.1261352027.1718247638; _clck=1ren23j%7C2%7Cfml%7C0%7C1625; Qs_lvt_382223=1718247643; Qs_pv_382223=1900562704502862000; _ga_C6TGHFPQ1H=GS1.1.1718247637.1.0.1718247671.0.0.0; Locale-Supported=zh-Hans; game=csgo; steam_verify_result=; AQ_HD=1; YD_SC_SID=EE2D0BDBB0834E60811933566731A7E3; AQ_REQ_FROM=webzj; NETS_utid=uDTc5TpoghhacqVslwZaqPkx5HVZQbAU; NTES_YD_SESS=TB6zd8lSqUbtgI3gbn2DIvUtBpDb0hZtcMQaCXx.RR83Eox_E6mDyt1NEWf2BtQS5oC6J.LrG4Fs0NDeMrlkHekoXVr7Yd8X1wRJHQmTPu6rDBrYRk.vpf.zl16YRkotQUG7Vt8FQYOYtHCX5XJBhH12fh4fwUt307ArlOSyFyyNkEm51GzkS7AK8CHzJJe3akIAxetR3Qxap4bVvuqYNvpUrHL4j8rs4IUWQlUGQVfA1; S_INFO=1722599930|0|0&60##|16670494952; P_INFO=16670494952|1722599930|1|netease_buff|00&99|CN&1719916642&netease_buff#gud&440100#10#0#0|&0|null|16670494952; remember_me=U1092505075|VblpAM1gjW2Tc3NaHrVL18PWiWs4xYzi",
    "Referer": "https://buff.163.com/goods",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
res2 = requests.get(url=notification, headers=no_head, params=no_pa)
# print(res2.headers)

cf2, sid2 = get_csrf(res2)
new_headers = no_head.copy()
new_headers["Cookie"] = no_head["Cookie"] + f"; csrf_token={cf2}"

res2 = requests.get(url=notification, headers=new_headers, params=no_pa)
# print(res2.headers)
cf2, sid2 = get_csrf(res2)

new_headers = market_header.copy()
new_headers["Cookie"] = market_header["Cookie"] + f"; csrf_token={cf2}"

# 查询在售接口
res = requests.get(url=market, headers=new_headers, params=market_parmas)
# print(res.text)
# 返回在售的html
# print(res.text)

# 传给查询每个枪的接口
cf2, sid2 = get_csrf(res)
# print()
new_headers = search_header.copy()
new_headers["Cookie"] = search_header["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"

time.sleep(2)
page = res.text
page = etree.HTML(page)
dl_list = page.xpath('//div[@class="list_card list_card_small2"]/ul/li')

wear_list = []
origin_price = []
sell_ids = []
goods_ids = []
set_price = []
names = []
buy_prices = []
print('1')

for dl in dl_list:
    # name = dl.xpath('.//data-goods-name/text()')[0]
    name = dl.get("data-goods-name")
    sell_id = dl.get("id")
    sell_id = sell_id.split('_')[2]
    price = dl.get("data-price")
    goods_id = dl.get("data-goodsid")
    wear_value = dl.xpath('.//div[@class="wear-value"]/text()')
    if wear_value:
        wear_list.append(wear_value[0])
    else:
        wear_list.append(None)
    buy_price_dict = dl.get("data-order-extra")
    buy_price_dict = json.loads(buy_price_dict)
    # 提取buy_price中的数字价格
    buy_price = buy_price_dict["buy_price"]
    names.append(name)
    origin_price.append(price)

    sell_ids.append(sell_id)
    goods_ids.append(goods_id)
    buy_prices.append(buy_price)
    print(name, sell_id, price, goods_id, '价格为', buy_price)

change_url = "https://buff.163.com/api/market/sell_order/change"
search_url = "https://buff.163.com/api/market/goods/sell_order?"
print(len(dl_list), len(wear_list))

wear_list = [float(re.search(r'\d+\.\d+', wear).group()) if wear is not None else 0.0 for wear in wear_list]
# print(wear_list)


def set_wear(wear_list):
    min_paintwears = []
    max_paintwears = []
    min_paintwear = None
    max_paintwear = None
    for i in wear_list:
        if i == 0:
            min_paintwear = None
            max_paintwear = None
        elif i < 0.0001:
            min_paintwear = None
            max_paintwear = 0.0001
        elif i < 0.001:
            min_paintwear = None
            max_paintwear = 0.001
        elif i < 0.01:
            min_paintwear = 0.00
            max_paintwear = 0.01
        elif i < 0.02:
            min_paintwear = 0.01
            max_paintwear = 0.02
        elif i < 0.03:
            min_paintwear = 0.02
            max_paintwear = 0.03
        elif i < 0.04:
            min_paintwear = 0.03
            max_paintwear = 0.04
        elif i < 0.05:
            min_paintwear = 0.04
            max_paintwear = 0.05
        elif i < 0.06:
            min_paintwear = 0.05
            max_paintwear = 0.06
        elif i < 0.08:
            min_paintwear = 0.07
            max_paintwear = 0.08
        elif i < 0.09:
            min_paintwear = 0.08
            max_paintwear = 0.09
        elif i < 0.1:
            min_paintwear = 0.09
            max_paintwear = 0.10
        elif i < 0.11:
            min_paintwear = 0.10
            max_paintwear = 0.11
        elif i < 0.12:
            min_paintwear = 0.11
            max_paintwear = 0.12
        elif i < 0.18:
            min_paintwear = 0.15
            max_paintwear = 0.18
        elif i < 0.21:
            min_paintwear = 0.18
            max_paintwear = 0.21
        elif i < 0.24:
            min_paintwear = 0.21
            max_paintwear = 0.24
        elif i < 0.27:
            min_paintwear = 0.24
            max_paintwear = 0.27
        else:
            min_paintwear = None
            max_paintwear = None
        # print(min_paintwear, max_paintwear, i)
        min_paintwears.append(min_paintwear)
        max_paintwears.append(max_paintwear)
    return min_paintwears, max_paintwears


def calculate_price(price):
    # 计算原始结果
    price = float(price)
    result = (price - 0.01) * 0.975

    # 将结果转换为 Decimal，并向下取整保留两位小数
    decimal_result = Decimal(result).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)
    return float(decimal_result)


def search_price(names, gun_id, search_url, new_headers, min_w, max_w):
    low_prices = []
    max_retries = 5  # 最大重试次数
    initial_delay = 1  # 初始延迟时间，单位为秒
    count = 0
    for index, gid in enumerate(gun_id):
        count += 1
        search_params = {
            "game": "csgo",
            "goods_id": f"{gid}",
            "page_num": "1",
            "sort_by": "default",
            "mode": "",
            "allow_tradable_cooldown": "1"
        }
        if min_w[index] is not None:
            search_params["min_paintwear"] = f"{min_w[index]}"
        if max_w[index] is not None:
            search_params["max_paintwear"] = f"{max_w[index]}"
        retries = 0
        delay = initial_delay
        print(f'正在查询第{count}个', names[index])
        while retries < max_retries:
            res5 = requests.get(url=search_url, params=search_params, headers=new_headers)
            try:
                data = res5.json().get('data', {}).get('items', [])
                if data:
                    low_price = data[0]['price']
                    low_prices.append(low_price)
                    break  # 成功获取数据，跳出循环
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                print("Response text:", res5.text)

            retries += 1
            print(f"太快了,Retrying... ({retries}/{max_retries})")
            time.sleep(delay)
            delay *= 2  # 指数退避

        if retries == max_retries:
            print(f"Failed to get data for gun_id: {gid} after {max_retries} retries.")
            low_prices.append(None)  # 如果多次尝试仍然失败，添加一个占位符
            initial_delay = 1

        time.sleep(0.5)  # 每个请求之间的延迟，避免过于频繁

    return low_prices


minw, maxw = set_wear(wear_list)

lp = search_price(names, goods_ids, search_url, new_headers, minw, maxw)

lp = list(map(float, lp))
buy_prices = list(map(float, buy_prices))   # 购入价
origin_price = list(map(float, origin_price))  # 没改的价格
result = [calculate_price(price) for price in lp]  # income
change = [0] * len(lp)  # 更改价

for i in range(len(lp)):
    print(names[i],"磨损：",wear_list[i],'改前价格为：', origin_price[i],'在售最低价格为：', lp[i], "改后价格为",round(lp[i] - 0.01, 2),
          "预期收入为：", result[i], '购入价格为', buy_prices[i],'实际收入为', round((result[i] - buy_prices[i]),2))
    if result[i] - buy_prices[i] < 0:
        change[i] = round(origin_price[i]+0.06, 1)
        print(f'价格亏了，价格向上取整一毛,从{origin_price[i]}元改成{change[i]}元')
    else:
        change[i] = round(lp[i] - 0.01, 2)

sell_orders = []
for i in range(len(lp)):  # 假设要包含50个物品
    order = {
        "sell_order_id": f"{sell_ids[i]}",
        "price": f"{change[i]}",
        "income":  f"{result[i]}",
        "has_market_min_price": "false",
        "goods_id": f"{goods_ids[i]}",
        "paintwear": f"{wear_list[i]}",
        "reward_points": 0,
        "origin_price": f"{origin_price[i]}",
        "desc": "好磨损啊,价格实惠,秒发货。",
        "cdkey_id": ""
    }
    sell_orders.append(order)

flag = input('按1确认修改:')
if flag == "1":
    max_retries = 5  # 最大重试次数
    initial_delay = 1  # 初始延迟时间，单位为秒

    retries = 0
    while retries < max_retries:
        res2 = requests.get(url=notification, headers=no_head, params=no_pa)
        cf2, sid2 = get_csrf(res2)
        new_headers = no_head.copy()
        new_headers["Cookie"] = no_head["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"
        new_headers["X-Csrftoken"] = cf2
        params = {
            "game": "csgo",
            "sell_orders": sell_orders
        }
        res = requests.post(url=change_url, headers=new_headers, json=params)
        print(res.text)
        if res.status_code == 200:
            print('修改成功')
            break
        else:
            print('修改不成功，重试中...')
            retries += 1
            time.sleep(initial_delay)
            initial_delay *= 2  # 指数退避

    if retries == max_retries:
        print(f"在重试{max_retries}次后仍未能成功修改")
else:
    print('不修改')
