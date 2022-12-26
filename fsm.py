from transitions.extensions import GraphMachine

#from utils import send_text_message, send_button_message, send_movie_details, send_actor_details, send_series_details
from linebot.models import *
from linebot import LineBotApi, WebhookParser
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import re
from flask import Flask, request, abort
import twstock
import os
import requests
class TocMachine():
    # def __init__(self, **machine_configs):
    #     self.machine = GraphMachine(model=self, **machine_configs)

    
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "menu"

    def is_going_to_Help(self, event):
        text = event.message.text
        return text == "使用說明"

    def is_going_to_searchEx(self, event):
        text = event.message.text
        if "匯率查詢" in text:
            return True
        else:
            return False
    
    def is_going_to_searchStock(self, event):
        text = event.message.text
        if "股票查詢" in text:
            return True
        else :
            return False

    def is_going_to_usdEx(self, event):
        text = event.message.text
        if "美元匯率" in text:
            return True
        else :
            return False
    
    def is_going_to_eurEx(self, event):
        text = event.message.text
        if "歐元匯率" in text:
            return True
        else :
            return False
    
    def is_going_to_jpyEx(self, event):
        text = event.message.text
        if "日元匯率" in text:
            return True
        else :
            return False



    

    # def on_exit_state1(self):
    #     print("Leaving state1")
    def on_enter_menu(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        fix_message = TextSendMessage(text="請輸入 或使用以下功能",
                                         quick_reply=QuickReply(items=[
                                            QuickReplyButton(action=MessageAction(label='使用說明',text='使用說明')),
                                            QuickReplyButton(action=MessageAction(label='匯率查詢',text='匯率查詢'))
                                        ]))
        line_bot_api.reply_message(event.reply_token,fix_message)
    def on_enter_Help(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        reply_message = '輸入: 股票查詢(股票代號)  查詢目前股價'
        message = TextSendMessage(text=reply_message)
        line_bot_api.reply_message(event.reply_token, message)
    
    def on_enter_searchEx(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        fix_message = TextSendMessage(text="選一個吧！",
                                         quick_reply=QuickReply(items=[
                                            QuickReplyButton(action=MessageAction(label='美元對台幣',text='美元匯率')),
                                            QuickReplyButton(action=MessageAction(label='歐元對台幣',text='歐元匯率')),
                                            QuickReplyButton(action=MessageAction(label='日元對台幣',text='日元匯率'))
                                        ]))
        line_bot_api.reply_message(event.reply_token,fix_message)
    
    def on_enter_searchStock(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        message = event.message.text
        message = message[4:]
        reply_message = ''
        stock_info = twstock.realtime.get(message)
        if stock_info.get('success'):
            reply_message = stock_info.get('info').get('name') + '目前價格為:' \
                            + stock_info.get('realtime').get('latest_trade_price')
        else:
            reply_message = '請輸入正確股票代碼'
        message = TextSendMessage(text=reply_message)
        line_bot_api.reply_message(event.reply_token, message)
    
    def on_enter_usdEx(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_twd = currency_data['USDTWD']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對 台幣 TWD ：1:{usd_to_twd}'))
    
    def on_enter_eurEx(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_eur = currency_data['USDEUR']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對 歐元 EUR ：1:{usd_to_eur}'))
    
    def on_enter_jpyEx(self, event):
        line_bot_api = LineBotApi('9gZSJLC23IDdxQDpuVHoezDwz+/EVSkCurgLn5TEvwY8gVfQgZdsRJCLKKlHta9aiFf8dF/4krpkVMiHJJoIzsrmCImF3r8cVVeoRyteEJKvQlxr1kD/0fGJ4htGlImeViqAqoBWaWNlndnGHgmtSQdB04t89/1O/w1cDnyilFU=')
        resp = requests.get('https://tw.rter.info/capi.php')
        currency_data = resp.json()
        usd_to_jpy = currency_data['USDJPY']['Exrate']

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'美元 USD 對 日元 JPY ：1:{usd_to_jpy}'))

    # def on_exit_state2(self):
    #     print("Leaving state2")

    