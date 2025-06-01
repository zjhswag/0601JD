import concurrent.futures
import json
import requests
from lxml import etree
import time
import os

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

buy_url = "https://buff.163.com/api/market/goods/buy"
noti = "https://buff.163.com/api/message/notification?"
headers1 = {
    "Cookie": "Device-Id=pRvONfjhQxta16QRPGH7; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=t.xCXoIkCqbj1WYh.GLGwf.G6pmkQShb5aR3Qgd1ZZE8uWdmu57zsxbquKhUrxR4XWQ5S1AeYloTDqzwaeOcPwcWgLein6EgbGZSPR7tMN5ezrenZc1BIh1vOb5nZcWxRt7m9BpoZs9H9W4e5u0coyD54xhPXZGETcKWw4p9WywxLv5MRWMIlrEMFnbE8i7DIyYhXFLYv4yI3.k5c0dEwV6JePAlfEeTlkJKROJYRLhjb; S_INFO=1718438098|0|0&60##|16670494952; P_INFO=16670494952|1718438098|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|C5UZUW2xLytb93PG18wgqAq8AHkRmrkH; steam_verify_result=",
    "Pragma": "no-cache",
    "Referer": "https://buff.163.com/goods/878844?from=market",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

headers2_no = {
    "Cookie":
        "Device-Id=pRvONfjhQxta16QRPGH7; Locale-Supported=zh-Hans; game=csgo; NTES_YD_SESS=t.xCXoIkCqbj1WYh.GLGwf.G6pmkQShb5aR3Qgd1ZZE8uWdmu57zsxbquKhUrxR4XWQ5S1AeYloTDqzwaeOcPwcWgLein6EgbGZSPR7tMN5ezrenZc1BIh1vOb5nZcWxRt7m9BpoZs9H9W4e5u0coyD54xhPXZGETcKWw4p9WywxLv5MRWMIlrEMFnbE8i7DIyYhXFLYv4yI3.k5c0dEwV6JePAlfEeTlkJKROJYRLhjb; S_INFO=1718438098|0|0&60##|16670494952; P_INFO=16670494952|1718438098|1|netease_buff|00&99|null&null&null#gud&440100#10#0|&0|null|16670494952; remember_me=U1092505075|C5UZUW2xLytb93PG18wgqAq8AHkRmrkH",
    "Origin": "https://buff.163.com",

    "Referer": "https://buff.163.com/goods/878844?from=market",

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Csrftoken": "IjU2NDJmNjY4OGRiMjUxY2FhYzlmNzBkN2Y3YzRkZjE4MDAzZGM5NDUi.GU8JCQ.z8c-PMWOrHs2FS5Tdqsk9bVmT2E",
    "X-Requested-With": "XMLHttpRequest"
}
no_params ={
"_":  int(time.time() * 1000)
}
res = requests.get(url=noti,headers=headers2_no,params=no_params)
# print(res.headers)
cf2, sid2 = get_csrf(res)
headers1["Cookie"] = headers1["Cookie"] + f"; csrf_token={cf2}" + f"; session={sid2}"
headers1["X-Csrftoken"] = cf2
print(headers1)
buy_params ={
  "game": "csgo",
  "goods_id": "878844",
  "sell_order_id": "3375384775-8986-134357271",
  "price": "0.06",
  "pay_method": "1",
  "allow_tradable_cooldown": "0",
  "token": "",
  "cdkey_id": "",
  "hide_non_epay": "false"
}
res2 = requests.post(url=buy_url,headers=headers1,json=buy_params)
print(res2.text)
print(res2.json())
