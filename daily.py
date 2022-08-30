from datetime import date, datetime, timedelta
import requests
import random
import math
import os

today = datetime.utcnow() + timedelta(hours=8)
start_date = os.environ["START_DATE"]
city = os.environ["CITY"]
birthday = os.environ["BIRTHDAY"]

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    url = (
        "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city="
        + city
    )
    res = requests.get(url).json()
    weather = res["data"]["list"][0]
    return weather["weather"], math.floor(weather["temp"])


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()["data"]["text"]


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_token():
    res = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"
        % (app_id, app_secret)
    ).json()
    if res.get("errcode", 0) != 0:
        print(res)
        exit(1)
    return res["access_token"]


def send_message(touser, template_id, data, access_token):
    res = requests.post(
        "https://api.weixin.qq.com/cgi-bin/message/template/send",
        params=dict(access_token=access_token),
        json=dict(
            touser=touser,
            template_id=template_id,
            data=data,
            url="https://sw.jackect.cn/heart",
        ),
    ).json()
    return res

def main():
    date_ = today.strftime("%F ") + "星期" + "一二三四五六天"[today.weekday()]
    wea, temperature = get_weather()
    data = {
        "date": {"value": date_, "color": get_random_color()},
        "city": {"value": city, "color": get_random_color()},
        "weather": {"value": wea, "color": get_random_color()},
        "temperature": {"value": temperature, "color": get_random_color()},
        "love_days": {"value": get_count(), "color": get_random_color()},
        "birthday": {"value": get_birthday(), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()},
    }
    token = get_token()
    for userid in user_id.split(","):
        res = send_message(userid, template_id, data, token)
        print(res)

if __name__ == "__main__":
    main()
