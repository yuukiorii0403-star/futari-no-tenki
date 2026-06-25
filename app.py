from flask import Flask, request, abort
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
MessageEvent,
TextMessage,
TextSendMessage,
TemplateSendMessage,
ButtonsTemplate,
PostbackAction,
PostbackEvent,
)

app = Flask(**name**)

# RenderのEnvironment Variablesに設定

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
signature = request.headers["X-Line-Signature"]

```
body = request.get_data(as_text=True)

try:
    handler.handle(body, signature)
except InvalidSignatureError:
    abort(400)

return "OK"
```

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

```
text = event.message.text

if text == "天気":
    message = TextSendMessage(
        text="今日の心の天気を教えてね☀️"
    )
    line_bot_api.reply_message(event.reply_token, message)

elif text == "気分":

    buttons = TemplateSendMessage(
        alt_text="今日の心の天気",
        template=ButtonsTemplate(
            title="ふたりの天気 ☀️",
            text="今日の心の天気はどう？",
            actions=[
                PostbackAction(
                    label="☀️ 晴れ",
                    data="sunny"
                ),
                PostbackAction(
                    label="⛅️ くもり",
                    data="cloudy"
                ),
                PostbackAction(
                    label="🌧️ 雨",
                    data="rainy"
                ),
                PostbackAction(
                    label="❓ まだわからない",
                    data="unknown"
                ),
            ],
        ),
    )

    line_bot_api.reply_message(
        event.reply_token,
        buttons
    )

else:
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text="『気分』と送ると心の天気を記録できるよ☀️"
        ),
    )
```

@handler.add(PostbackEvent)
def handle_postback(event):

```
data = event.postback.data

if data == "sunny":
    reply = "☀️ 晴れだね！素敵な一日になりますように。"

elif data == "cloudy":
    reply = "⛅️ くもりなんだね。無理せず過ごそう。"

elif data == "rainy":
    reply = "🌧️ 雨なんだね。今日は自分を労わってあげてね。"

elif data == "unknown":
    reply = "❓ まだわからない日もあるよね。ゆっくりいこう。"

else:
    reply = "ありがとう！"

line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=reply)
)
```

if **name** == "**main**":
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
