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

MY_USER_ID = os.environ.get("MY_USER_ID")
PARTNER_USER_ID = os.environ.get("PARTNER_USER_ID")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

MOOD_DICTIONARY = {
    "ans_sunny_1": "☀️ 晴れ\n💬 話を聴いてほしい",
    "ans_sunny_2": "☀️ 晴れ\n🎉 一緒に喜んでほしい",
    "ans_sunny_3": "☀️ 晴れ\n🤗 甘えたい",
    "ans_sunny_4": "☀️ 晴れ\n😌 特に何もなくて大丈夫",
    "ans_cloudy_1": "⛅️ くもり\n👂 話を聴いてほしい",
    "ans_cloudy_2": "⛅️ くもり\n💌 メッセージがほしい",
    "ans_cloudy_3": "⛅️ くもり\n🤝 少し励ましてほしい",
    "ans_cloudy_4": "⛅️ くもり\n😌 そっとしておいてほしい",
    "ans_rainy_1": "🌧️ 雨\n🫂 慰めてほしい",
    "ans_rainy_2": "🌧️ 雨\n👂 話を聴いてほしい",
    "ans_rainy_3": "🌧️ 雨\n❤️ 優しくしてほしい",
    "ans_rainy_4": "🌧️ 雨\n😌 今日はそっとしておいてほしい",
    "ans_unknown_1": "❓ まだわからない\n💬 とりあえず話を聴いてほしい",
    "ans_unknown_2": "❓ まだわからない\n☕️ 気分転換に付き合ってほしい",
    "ans_unknown_3": "❓ まだわからない\n🫂 ただそばにいてほしい",
    "ans_unknown_4": "❓ まだわからない\n😌 今は何も考えたくない",
}

@app.route("/")
def home():
    return "Futari no Tenki is running!"

@app.route("/morning-trigger", methods=["GET"])
def morning_trigger():
    if not MY_USER_ID or not PARTNER_USER_ID:
        return "User IDs are not set in environment variables.", 400

    buttons = TemplateSendMessage(
        alt_text="今日の心の天気",
        template=ButtonsTemplate(
            title="ふたりの天気 ☀️",
            text="おはよう！☀️ 今日の心の天気はどう？",
            actions=[
                PostbackAction(label="☀️ 晴れ", data="sunny"),
                PostbackAction(label="⛅️ くもり", data="cloudy"),
                PostbackAction(label="🌧️ 雨", data="rainy"),
                PostbackAction(label="❓ まだわからない", data="unknown"),
            ],
        ),
    )

    try:
        line_bot_api.push_message(MY_USER_ID, buttons)
        line_bot_api.push_message(PARTNER_USER_ID, buttons)
        return "Successfully sent morning message to both users!"
    except Exception as e:
        return f"Error: {str(e)}", 500

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
    user_id = event.source.user_id

    # ====== 1段階目（天気を選んだとき） ======
    if data == "sunny":
        messages = [
            TextSendMessage(text="☀️ だね！素敵な一日になりますように。"),
            TemplateSendMessage(
                alt_text="どんな気分？",
                template=ButtonsTemplate(
                    title="☀️ 晴れ",
                    text="どんな気分？",
                    actions=[
                        PostbackAction(label="💬 話を聴いてほしい", data="ans_sunny_1"),
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
                        PostbackAction(label="👂 話を聴いてほしい", data="ans_cloudy_1"),
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
                        PostbackAction(label="👂 話を聴いてほしい", data="ans_rainy_2"),
                        PostbackAction(label="❤️ 優しくしてほしい", data="ans_rainy_3"),
                        PostbackAction(label="😌 今日はそっとしておいてほしい", data="ans_rainy_4"),
                    ],
                ),
            )
        ]
        line_bot_api.reply_message(event.reply_token, messages)

    elif data == "unknown":
        messages = [
            TextSendMessage(text="❓ まだわからない日もあるよね。ゆっくりいこう。"),
            TemplateSendMessage(
                alt_text="どんな気分？",
                template=ButtonsTemplate(
                    title="❓ まだわからない",
                    text="どんな気分？",
                    actions=[
                        PostbackAction(label="💬 とりあえず話を聴いてほしい", data="ans_unknown_1"),
                        PostbackAction(label="☕️ 気分転換に付き合ってほしい", data="ans_unknown_2"),
                        PostbackAction(label="🫂 ただそばにいてほしい", data="ans_unknown_3"),
                        PostbackAction(label="😌 今は何も考えたくない", data="ans_unknown_4"),
                    ],
                ),
            )
        ]
        line_bot_api.reply_message(event.reply_token, messages)

    # ====== 2段階目（プッシュ通知で相手に送信） ======
    elif data.startswith("ans_"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="記録したよ！相手にもそっと伝えておくね🕊️")
        )

        target_id = None
        if user_id == MY_USER_ID:
            target_id = PARTNER_USER_ID
        elif user_id == PARTNER_USER_ID:
            target_id = MY_USER_ID

        if target_id:
            try:
                profile = line_bot_api.get_profile(user_id)
                sender_name = profile.display_name
            except:
                sender_name = "パートナー"

            mood_text = MOOD_DICTIONARY.get(data, "今の気分")
            push_text = f"{sender_name}さんから今日の気分が届いたよ！\n\n{mood_text}"
            
            try:
                line_bot_api.push_message(target_id, TextSendMessage(text=push_text))
            except Exception as e:
                print(f"Push failed: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)