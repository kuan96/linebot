# linebot introduction

我的linebot主要功能是和用戶做一些簡單的互動，主要分為user和另外五個state，每個state在做完相對應的task後都會回到user state，所以每次的起始state都會是user state

**我的finite state machine diagram:**

![](https://i.imgur.com/SwfLmho.png)

**自動推播:**
當程式開始執行後，Linbot會自動傳給用戶歡迎的訊息:

```
line_bot_api.push_message(
    'Udaa53119f038c9c8a346b9a6b5a770e5', TextSendMessage(text='我是你的個人小助理nikey,很高興為你服務'))
```

## state介紹

1. imgState :
在這個state用戶只要輸入跟"頭貼"有關的句子，linebot就會回傳channel的大頭貼照，像是這樣:

![](https://i.imgur.com/jf6KQdh.jpg)

code:

```
def on_enter_imgState(self, event):
        reply_token = event.reply_token
        text = "這是我的大頭貼"
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

        img_url = 'https://upload.wikimedia.org/wikipedia/zh/thumb/b/b1/Tokyo_Revengers_volume_1_cover.jpg/220px-Tokyo_Revengers_volume_1_cover.jpg'
        image_message = ImageSendMessage(
            original_content_url=img_url, preview_image_url=img_url)
        line_bot_api.push_message(to_user, image_message)
        self.go_back()
```

2.  ttState & songState :
這兩個state的功能比較像，當用戶輸入"繞口令"相關的句子，linebot就會回傳一段繞口令(ttstate)，而輸入"兒歌"相關的句子則會回傳一段兒歌的內容，像是這樣:

![](https://i.imgur.com/Vcx9TzJ.jpg)

而我的實作方式是將data存在global的List裡，需要的時候會隨機選一個出來用，類似這樣:

```
tt = ["和尚端湯上塔堂，塔滑湯灑湯燙塔", "吃葡萄不吐葡萄皮，不吃葡萄倒吐葡萄皮", "表哥抱表弟，表哥抱表弟的弟弟，表弟抱表哥的弟弟",
      "鋼彈盪單槓，盪斷單槓，單槓不給鋼彈盪",
      "扁擔長，板凳寬，扁擔想綁在板凳上，板凳不讓扁擔綁在板凳上，扁擔偏要綁在板凳上，板凳偏不讓扁擔綁在板凳上，到底是扁擔長還是板凳寬"]
```

3. searchImage :
只要讀到有關"搜尋"或"圖片"的句子，Linebot便會去google上搜尋相關的圖片並回傳:

![](https://i.imgur.com/5mbiPQy.jpg)

這個部份我是用爬蟲的方式實作:

```
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
```

4. weather :
當linebot讀到"天氣"相關的句子，便會去氣象資料開放平台搜尋12小時內的天氣預報並回傳:

![](https://i.imgur.com/56KOgqA.jpg)

這部分我一樣式用爬蟲來完成，先將平台上的資料抓下來:

```
token = "CWB-7A3D016E-7F19-40AA-94D6-E29866104ED3"
        url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + \
            token + '&format=JSON&locationName=' + city
        Data = requests.get(url)
```

在load成字典的格式抓取我要的資料:

```
res = dic_data['records']['location'][0]['weatherElement']
        stime = res[1]["time"][0]["startTime"]
        etime = res[1]["time"][0]["endTime"]
        condition = res[0]["time"][0]["parameter"]["parameterName"]
        pop = res[1]["time"][0]["parameter"]["parameterName"]
        mint = res[2]["time"][0]["parameter"]["parameterName"]
        maxt = res[4]["time"][0]["parameter"]["parameterName"]
```

如果用戶的輸入都跟上述無關，則linebot會回傳一段字串給用戶:


```
line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="不好意思我看不懂你的指令..可以再問一次嗎?")
```
