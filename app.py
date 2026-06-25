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

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("xt6cwUms1Vd4oC0dCCDin9T9ZbvCXbE/Y34weON6Tioa1N2yajB0qQpDHUqWp3vV5WCSDIYrb1f+QG9Pfdg9YhOgOllbg7iXGZP6Fum8iFxXUeoNH+9noq0S/hfAjJ0Zp7ZfB78eTth/DG9E9Nx6ywdB04t89/1O/w1cDnyilFU=")
CHANNEL_SECRET = os.environ.get("C0fc6deeed51eb52f8c27df2f3065b9e2")
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# =========================
# Webhookエンドポイント
# =========================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# =========================
# メッセージ受信
# =========================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    if text == "天気":
        buttons = TemplateSendMessage(
            alt_text="今日の心の天気は？",
            template=ButtonsTemplate(
                title="今日の心の天気 ☁️",
                text="今の気分はどれに近い？",
                actions=[
                    PostbackAction(label="☀️ 晴れ", data="weather=sunny"),
                    PostbackAction(label="⛅ くもり", data="weather=cloudy"),
                    PostbackAction(label="🌧️ 雨", data="weather=rainy"),
                    PostbackAction(label="❓ まだわからない", data="weather=unknown"),
                ],
            ),
        )
        line_bot_api.reply_message(event.reply_token, buttons)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="「天気」と送ると今日の気分を教えてくれるよ☁️")
        )

# =========================
# ポストバック受信（ボタンの回答）
# =========================
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data

    weather_map = {
        "weather=sunny":   "☀️ 晴れ",
        "weather=cloudy":  "⛅ くもり",
        "weather=rainy":   "🌧️ 雨",
        "weather=unknown": "❓ まだわからない",
    }

    if data in weather_map:
        label = weather_map[data]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"今日は {label} なんだね。教えてくれてありがとう☁️")
        )

# =========================
# 起動
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)