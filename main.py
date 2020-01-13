from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests
from bs4 import BeautifulSoup
import json

def searchDict(verb):
    url = "https://api.verbix.com/conjugator/iv1/ab8e7bb5-9ac6-11e7-ab6a-00089be4dcbc/1/13/113/%s" % verb
    res = requests.get(url)
    dictionary = res.text
    content = json.loads(dictionary)['p1']['html']

    soup = BeautifulSoup(content, features="html.parser")

    result = []
    searchResult = ""

    if "NOTRECOGVERB" in content:
        searchResult = "Cannot find this word"
        return searchResult
    else:
        for div in soup.select('.columns-sub div')[0:6]:
            divH4 = div.select('h4')
            tense = "【" + divH4[0].text + "】"
            result.append(tense)
            for tr in div.select('tr'):
                td = tr.select('td')
                verb = td[0].text + ":" + td[1].text
                result.append(verb)
        searchResult = '\n'.join(result)
        return searchResult


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('Channel Access Token')
# Channel Secret
handler = WebhookHandler('Channel Secret')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    verb = event.message.text
    searchResult = searchDict(verb)

    message = TextSendMessage(text=searchResult)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)