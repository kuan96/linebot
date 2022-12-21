import os
import re
from transitions.extensions import GraphMachine

from flask import Flask, request, abort
from flask import jsonify,  send_file
from flask_ngrok import run_with_ngrok
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from flask import render_template, jsonify, send_from_directory

import configparser

import random

from urllib import request
from urllib.parse import urlencode
import requests

import json

config = configparser.ConfigParser()
config.read('config.ini')

handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))

app = Flask(__name__, static_url_path='/image')

to_user = 'Udaa53119f038c9c8a346b9a6b5a770e5'

tt = ["和尚端湯上塔堂，塔滑湯灑湯燙塔", "吃葡萄不吐葡萄皮，不吃葡萄倒吐葡萄皮", "表哥抱表弟，表哥抱表弟的弟弟，表弟抱表哥的弟弟",
      "鋼彈盪單槓，盪斷單槓，單槓不給鋼彈盪",
      "扁擔長，板凳寬，扁擔想綁在板凳上，板凳不讓扁擔綁在板凳上，扁擔偏要綁在板凳上，板凳偏不讓扁擔綁在板凳上，到底是扁擔長還是板凳寬"]
bool_tt = [False for i in range(5)]

songs = ["兩隻老虎，兩隻老虎♫，跑的快 跑的快♫，一隻沒有眼睛，一隻沒有尾巴♪，真奇怪！真奇怪♬！",
         "一隻哈巴狗♫，坐在大門口♬，眼睛黑黝黝♫，想吃肉骨頭♪，一隻哈巴狗♫，吃完肉骨頭♫，尾巴搖一搖♫，向我點點頭♫。",
         "我有一隻小毛驢，我從來也不騎♫，有一天我心血來潮騎著去趕集♫，我手裡拿著小皮鞭，我心裡真得意♬，不知怎麼嘩啦啦啦，我摔了一身泥♫。",
         "小小螢火蟲，飛到西又飛到東♬，這邊亮，那邊亮，好像許多小燈籠♬。",
         "嗡嗡嗡，嗡嗡嗡，大家一起去做工♫。來匆匆，去匆匆，做工興味濃♫。天暖花好不做工，將來哪裡好過冬♫？嗡嗡嗡，嗡嗡嗡，別學懶惰蟲♬。"]
bool_songs = [False for i in range(5)]


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_imgState(self, event):
        text = event.message.text
        return ("頭貼" in text)

    def is_going_to_ttState(self, event):
        text = event.message.text
        return ("繞口令" in text)

    def is_going_to_songState(self, event):
        text = event.message.text
        return ("兒歌" in text)

    def is_going_to_searchImage(self, event):
        text = event.message.text
        return ("搜尋" in text)

    def is_going_to_answer(self, event):
        text = event.message.text
        return (("謝謝" in text) or ("感謝" in text))

    def is_going_to_weather(self, event):
        text = event.message.text
        return ("天氣" in text)

    # image
    def on_enter_imgState(self, event):
        reply_token = event.reply_token
        text = "這是我的大頭貼"
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

        img_url = 'https://upload.wikimedia.org/wikipedia/zh/thumb/b/b1/Tokyo_Revengers_volume_1_cover.jpg/220px-Tokyo_Revengers_volume_1_cover.jpg'
        image_message = ImageSendMessage(
            original_content_url=img_url, preview_image_url=img_url)
        line_bot_api.push_message(to_user, image_message)
        self.go_back()

    def on_exit_imgState(self):
        line_bot_api.push_message(to_user, TextSendMessage(text="謝謝你喜歡我的頭貼!"))

    # tt

    def on_enter_ttState(self, event):
        global bool_tt

        index = random.randint(0, 4)
        while bool_tt[index] is True:
            index = random.randint(0, 4)

        bool_tt[index] = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=tt[index]))

        if False not in bool_tt:
            bool_tt = [False for i in range(5)]

        self.go_back()

    def on_exit_ttState(self):
        line_bot_api.push_message(to_user, TextSendMessage(text="希望你喜歡"))

    # song

    def on_enter_songState(self, event):
        global bool_songs

        index = random.randint(0, 4)
        while bool_songs[index] is True:
            index = random.randint(0, 4)

        bool_songs[index] = True
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=songs[index]))

        if False not in bool_songs:
            bool_songs = [False for i in range(5)]

        self.go_back()

    def on_exit_songState(self):
        line_bot_api.push_message(to_user, TextSendMessage(text="希望你喜歡"))

    # search image

    def on_enter_searchImage(self, event):
        text = str(event.message.text)
        tmp = text.split(" ")
        text = tmp[1]

        img_search = {'tbm': 'isch', 'q': text}
        query = urlencode(img_search)
        base = "https://www.google.com/search?"
        url = str(base+query)

        headers = {'user-agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        res = request.Request(url, headers=headers)
        con = request.urlopen(res)
        data = con.read()

        pattern = '"(https://encrypted-tbn0.gstatic.com[\S]*)"'

        img_list = []
        for match in re.finditer(pattern, str(data, "utf-8")):
            if len(match.group(1)) < 150:
                img_list.append(match.group(1))

        random_img_url = img_list[random.randint(0, len(img_list)+1)]

        line_bot_api.push_message(to_user, ImageSendMessage(original_content_url=random_img_url,
                                                            preview_image_url=random_img_url))

        self.go_back()

    def on_exit_searchImage(self):
        line_bot_api.push_message(to_user, TextSendMessage(text="希望這是你要搜尋的圖片"))

    # answer

    def on_enter_answer(self, event):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="不會"))
        self.go_back()

    def on_exit_answer(self):
        line_bot_api.push_message(to_user, TextSendMessage(text="有問題歡迎問我"))

    # weather
    def on_enter_weather(self, event):
        text = str(event.message.text)
        tmp = text.split(" ")
        city = tmp[1]

        token = "CWB-7A3D016E-7F19-40AA-94D6-E29866104ED3"
        url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
            token + '&format=JSON&locationName=' + city
        Data = requests.get(url)
        f = open('weather.json', 'w', encoding='utf-8')
        f.write(Data.text)
        f.close()

        jf = open('weather.json', 'r', encoding='utf-8')
        dic_data = json.load(jf)
        jf.close()

        res = dic_data['records']['location'][0]['weatherElement']
        stime = res[1]["time"][0]["startTime"]
        etime = res[1]["time"][0]["endTime"]
        condition = res[0]["time"][0]["parameter"]["parameterName"]
        pop = res[1]["time"][0]["parameter"]["parameterName"]
        mint = res[2]["time"][0]["parameter"]["parameterName"]
        maxt = res[4]["time"][0]["parameter"]["parameterName"]

        t1 = f'{city}十二小時天氣預報\n'
        t2 = f'(從{stime}到{etime})\n'
        t3 = f'天氣狀況: {condition}\n'
        t4 = f'最高溫: {maxt}\n'
        t5 = f'最低溫: {mint}\n'
        t6 = f'降雨機率: {pop}'
        t = t1+t2+t3+t4+t5+t6

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=t))
        if int(maxt) < 20:
            line_bot_api.push_message(
                to_user, TextSendMessage(text="天氣冷要注意保暖，出門記得帶個雨具<3"))

        self.go_back()

    def on_exit_weather(self):
        pass
