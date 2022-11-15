import requests
import time
import hashlib

# 讯代理 http://www.xdaili.cn?invitationCode=745864FF47DD4E7B8D622EBCC81CDD97
orderno = "ZF2022*************"
secret = "********************************"
# 哔哩哔哩 cookies 中 SESSDATA
mycookie = "SESSDATA=********%************%**********"

requests.packages.urllib3.disable_warnings()

def getbyproxy(url):
    timestamp = str(int(time.time()))
    sign = hashlib.md5(str("orderno=" + orderno + ",secret=" + secret + ",timestamp=" + timestamp).encode()).hexdigest().upper()
    auth = "sign=" + sign + "&orderno=" + orderno + "&timestamp=" + timestamp
    proxy = {"http": "http://forward.xdaili.cn:80",
             "https": "http://forward.xdaili.cn:80"}
    headers = {"Proxy-Authorization": auth,
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
               "cookie": mycookie}
    response = requests.get(url, headers=headers, proxies=proxy, verify=False, allow_redirects=False, timeout=5)
    return response