import os
from flask import Flask, request, abort
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

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def home():
    return "Futari no Tenki is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    user_id = event.source.user_id

    if text == "気分":
        buttons = TemplateSendMessage(
            alt_text="今日の心の天気",
            template=ButtonsTemplate(
                title="ふたりの天気 ☀️",
                text="今日の心の天気はどう？",
                actions=[
                    PostbackAction(label="☀️ 晴れ", data="sunny"),
                    PostbackAction(label="⛅️ くもり", data="cloudy"),
                    PostbackAction(label="🌧️ 雨", data="rainy"),
                    PostbackAction(label="❓ まだわからない", data="unknown"),
                ],
            ),
        )
        line_bot_api.reply_message(event.reply_token, buttons)
        
    elif text == "ID":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"あなたのユーザーID:\n{user_id}")
        )
        
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="『気分』と送ると心の天気を記録できるよ☀️")
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data

    # ====== 1段階目（天気を選んだとき） ======
    if data == "sunny":
        # テキストとボタンをセットにして送ります
        messages = [
            TextSendMessage(text="☀️ だね！素敵な一日になりますように。"),
            TemplateSendMessage(
                alt_text="どんな気分？",
                template=ButtonsTemplate(
                    title="☀️ 晴れ",
                    text="どんな気分？",
                    actions=[
                        PostbackAction(label="💬 話を聞いてほしい", data="ans_sunny_1"),
                        PostbackAction(label="🎉 一緒に喜んでほしい", data="ans_sunny_2"),
                        PostbackAction(label="🤗 甘えたい", data="ans_sunny_3"),
                        PostbackAction(label="😌 特に何もなくて大丈夫", data="ans_sunny_4"),
                    ],
                ),
            )
        ]
        line_bot_api.reply_message(event.reply_token, messages)

    elif data == "cloudy":
        messages = [
            TextSendMessage(text="⛅️ くもりなんだね。無理せず過ごそう。"),
            TemplateSendMessage(
                alt_text="どんな気分？",
                template=ButtonsTemplate(
                    title="⛅️ くもり",
                    text="どんな気分？",
                    actions=[
                        PostbackAction(label="👂 話を聞いてほしい", data="ans_cloudy_1"),
                        PostbackAction(label="💌 メッセージがほしい", data="ans_cloudy_2"),
                        PostbackAction(label="🤝 少し励ましてほしい", data="ans_cloudy_3"),
                        PostbackAction(label="😌 そっとしておいてほしい", data="ans_cloudy_4"),
                    ],
                ),
            )
        ]
        line_bot_api.reply_message(event.reply_token, messages)

    elif data == "rainy":
        messages = [
            TextSendMessage(text="🌧️ 雨なんだね。今日は自分を労わってあげてね。"),
            TemplateSendMessage(
                alt_text="どんな気分？",
                template=ButtonsTemplate(
                    title="🌧️ 雨",
                    text="どんな気分？",
                    actions=[
                        PostbackAction(label="🫂 慰めてほしい", data="ans_rainy_1"),
                        PostbackAction(label="👂 話を聞いてほしい", data="ans_rainy_2"),
                        PostbackAction(label="❤️ 優しくしてほしい", data="ans_rainy_3"),
                        PostbackAction(label="😌 今日はそっとしておいてほしい", data="ans_rainy_4"),
                    ],
                ),
            )
        ]
        line_bot_api.reply_message(event.reply_token, messages)

    elif data == "unknown":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❓ まだわからない日もあるよね。ゆっくりいこう。")
        )

    # ====== 2段階目（どんな気分かを選んだとき） ======
    elif data.startswith("ans_"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="教えてくれてありがとう！この後、相手に伝える仕組みを作るよ！")
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)