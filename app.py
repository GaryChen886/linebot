import os
import sys
import requests
import pandas as pd
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import re
from pyngrok import ngrok
import json
import twstock
from fsm import TocMachine
# from utils import send_text_message
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('05f7b5de38b2a0fcf2a52d1634f06e33')
public_url = ''
lock_ip = '192.168.113.202'


machine = TocMachine(
    states=["user", "menu", "Help", "searchEx", "searchStock", "usdEx", "eurEx", "jpyEx"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "searchStock",
            "conditions": "is_going_to_searchStock",
        },
        {
            "trigger": "advance",
            "source": "Help",
            "dest": "searchStock",
            "conditions": "is_going_to_searchStock",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "Help",
            "conditions": "is_going_to_Help",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "searchEx",
            "conditions": "is_going_to_searchEx",
        },
        {
            "trigger": "advance",
            "source": "searchEx",
            "dest": "usdEx",
            "conditions": "is_going_to_usdEx",
        },
        {
            "trigger": "advance",
            "source": "searchEx",
            "dest": "eurEx",
            "conditions": "is_going_to_eurEx",
        },
        {
            "trigger": "advance",
            "source": "searchEx",
            "dest": "jpyEx",
            "conditions": "is_going_to_jpyEx",
        },
        {
            "trigger": "go_back", 
            "source": ["menu", "Help", "searchEx", "searchStock", "usdEx", "eurEx", "jpyEx"], 
            "dest": "user",
        },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)


#get channel_secret and channel_access_token from your environment variable
# channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
# channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = '05f7b5de38b2a0fcf2a52d1634f06e33'
channel_access_token = '9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU='
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        if machine.state != "user" and event.message.text.lower() == 'back':
            line_bot_api.reply_message(

                event.reply_token, TextSendMessage('歡迎回到主頁面!')
            )
            machine.go_back()
        else:
            response = machine.advance(event)
            # if response == False:
            #     if machine.state == "user":
            #         send_text_message(event.reply_token, "請輸入 [搜尋] 即可進入搜尋模式，尋找自己喜愛的電影、影集或演員!\n或是輸入 [熱門清單] 即可查看今日Top4的熱門電影、影集或演員!")
            #     elif machine.state == "chose_list" or machine.state == "search" or machine.state == "movie_result" or machine.state == "actor_result" or machine.state == "series_result" or machine.state == "popular_movies" or machine.state == "popular_series" or machine.state == "popular_actor":
            #         send_text_message(event.reply_token, "請乖乖按按鈕!")
            #     elif machine.state == "search_movie" or machine.state == "search_actor" or machine.state == "search_series":
            #         send_text_message(event.reply_token, "抱歉，我找不到你要的資料QQ，請你重新輸入一次!")
            #     elif machine.state == "actor_details" or machine.state == "movie_details" or machine.state == "series_details":
            #         send_text_message(event.reply_token, "可以查看其他搜尋結果，或是輸入menu就可以回到主選單囉!")

    return "OK"


@app.route("/show-fsm", methods=["POST"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port, debug=True)




    