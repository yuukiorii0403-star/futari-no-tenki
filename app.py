from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ★ここにLINEの情報を入れる（あとで貼る）
CHANNEL_ACCESS_TOKEN = "xt6cwUms1Vd4oC0dCCDin9T9ZbvCXbE/Y34weON6Tioa1N2yajB0qQpDHUqWp3vV5WCSDIYrb1f+QG9Pfdg9YhOgOllbg7iXGZP6Fum8iFxXUeoNH+9noq0S/hfAjJ0Zp7ZfB78eTth/DG9E9Nx6ywdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "0fc6deeed51eb52f8c27df2f3065b9e2"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/")
def home():
    return "ふたりの天気 🌤️"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    reply = "ふたりの天気だよ🌤️"

    if text == "こんにちは":
        reply = "こんにちは！🌤️"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


if __name__ == "__main__":
    app.run(port=5001, debug=True)