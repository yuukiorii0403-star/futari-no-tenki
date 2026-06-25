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
)

app = Flask(__name__)

# =========================
# 環境変数（Renderに設定）
# =========================
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# =========================
# Webhookエンドポイント
# =========================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

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

    # シンプル応答
    if text == "天気":
        message = TextSendMessage(text="今日はどう？☀️")
        line_bot_api.reply_message(event.reply_token, message)

    elif text == "気分":
        buttons = TemplateSendMessage(
            alt_text="今日の気分を教えて",
            template=ButtonsTemplate(
                title="今日の気分",
                text="今の気分はどれ？",
                actions=[
                    PostbackAction(label="良い😊", data="good"),
                    PostbackAction(label="普通🙂", data="normal"),
                    PostbackAction(label="悪い😢", data="bad"),
                ],
            ),
        )
        line_bot_api.reply_message(event.reply_token, buttons)

    else:
        message = TextSendMessage(text="「天気」か「気分」と送ってみてね！")
        line_bot_api.reply_message(event.reply_token, message)


# =========================
# ポストバック処理（ボタン）
# =========================
@handler.add(MessageEvent)
def handle_postback(event):
    pass


# =========================
# 起動（Render対応）
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)