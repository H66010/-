# 遠方操作でDER機器をSETした項目の状態確認（SET＆GET）
# - 引数
#   - なし
# - 動作
#   1. コード文中のSET内容の事前GETを実施
#   2. コード文中のSET内容をもとにSET信号を送信
#   3. コード文中で設定された秒数だけWAITしたあとに、GET信号を送信
# - 出力
#   - GET, SET の結果をそれぞれコンソールへ表示する

import requests
import json
import os
from dotenv import load_dotenv
import time
import sys

load_dotenv()

url = os.environ['TARGET_URL']

payload_get = {
  "requests": [
    {
      "command": [
        {
        "command_type": "character",
        "command_code": "get_property_value",
        #get内容の設定
        "command_value": "actualOperationMode"
        }
      ],
      #######
      # 遠方操作対象のDER機器を指定してください（DRIVER_ID, R_EDGE_ID, THINGS_UUID）
      #######
      "driver_id": os.environ['DRIVER_ID'], 
      "r_edge_id": os.environ['R_EDGE_ID'],
      "thing_uuid": os.environ['THING_UUID']
    }
  ]
}

# command_valueはecnonetliteのweb APIの仕様書と対応している（はず(海原さん))

payload_set = {
  "requests": [
    {
      "command": [
        {
        "command_type": "character", # IoT-EX社の定義しているものなので、自分で作れない？それかEchonetliteの定義式？
        "command_code": "set_property_value",
        #######
        # SET内容を指定してください（operationStatus, operationMode, ...)
        #######
        "command_value": "operationMode=discharging"
        }
      ],
      #######
      # 遠方操作対象のDER機器を指定してください（DRIVER_ID, R_EDGE_ID, THINGS_UUID）
      #######
      "driver_id": os.environ['DRIVER_ID'],
      "r_edge_id": os.environ['R_EDGE_ID'],
      "thing_uuid": os.environ['THING_UUID']
    }
  ]
}

headers = {
  "Content-type": "application/json",
  "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
  "X-IOT-API-KEY": os.environ['API_KEY']
}

try:
   response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
   print(response_get1.text)
   jsonData = response_get1.json()
   
   # ecnonetliteの応答が使用上の都合で複数あるので、それに対応するためのコード
   for result in jsonData['results']:
       for command in result["command"]:
           for response in command["response"]:
               get1 = {
                   'command_code': command["command_code"],
                   'command_value': command["command_value"],
                   'response_result': response["response_result"],
                   'response_value': response["response_value"]
               }
               print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")

except TimeoutError:
   print("get1 is timed out")
   pass


try:
   response_set = requests.request("POST", url, headers=headers, json=payload_set, timeout=200)
   print(response_set.text)
   jsonData = response_set.json()
   for result in jsonData['results']:
       for command in result["command"]:
           for response in command["response"]:
               set1 = {
                   'command_code': command["command_code"],
                   'command_value': command["command_value"],
                   'response_result': response["response_result"],
                   'response_value': response["response_value"]
               }
               print(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})")
except TimeoutError:
   print("set is timed out")
   pass
time.sleep(5)

try:
   response_get2 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
   print(response_get2.text)
   jsonData = response_get2.json()
   
 
   for result in jsonData['results']:
       for command in result["command"]:
           for response in command["response"]:
               get2 = {
                   'command_code': command["command_code"],
                   'command_value': command["command_value"],
                   'response_result': response["response_result"],
                   'response_value': response["response_value"]
               }
               print(f"{get2['command_code']} ({get2['command_value']}) ... {get2['response_result']} ({get2['response_value']})")

except TimeoutError:
   print("get2 is timed out")
   pass