import os, random
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import (
    MessagingApi, Configuration,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
from linebot.v3.messaging import ApiClient

# Load secrets
load_dotenv()
app = Flask(__name__)

config = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
api_client = ApiClient(config)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Word list
word_list = [
    {"emoji": "🍎", "word": "apple"},
    {"emoji": "🐶", "word": "dog"},
    {"emoji": "🐱", "word": "cat"},
    {"emoji": "🍌", "word": "banana"},
    {"emoji": "🐘", "word": "elephant"},
]

user_quiz = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Webhook body:", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    print("Received message:", event.message.text)
    user_id = event.source.user_id
    text = event.message.text.strip().lower()

    if text in ["start", "quiz", "play"]:
        quiz = random.choice(word_list)
        user_quiz[user_id] = quiz["word"]
        reply = f"🐼 Panda Sensei: What is this? {quiz['emoji']}"
    elif user_id in user_quiz:
        correct = user_quiz[user_id]
        if text == correct:
            reply = f"🎉 Great job! That's correct! {text} {random.choice(['✨', '👍', '👏'])}"
            del user_quiz[user_id]
        else:
            reply = "❌ Not quite! Try again 😊"
    else:
        reply = "Type 'start' to begin a new quiz! 🐼"

    # Send reply
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

if __name__ == "__main__":
    app.run(port=5000)
