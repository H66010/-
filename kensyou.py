import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import pytz

#.envファイルの読み込み
load_dotenv()
#TARGET_URLの取得
url = os.environ['TARGET_URL']
#getのpayloadを簡単に作成するための関数
def  getting(getvalue):
   payload_get = {
       "requests": [
           {
               "command": [
                   {
                       "command_type": "character",
                       "command_code": "get_property_value",
                       "command_value": getvalue
                   }
               ],
               "driver_id": os.environ['DRIVER_ID'], 
               "r_edge_id": os.environ['R_EDGE_ID'],
               "thing_uuid": os.environ['THING_UUID']
           }
       ]
   }
   return payload_get


#setのpayloadを簡単に作成するための関数
def setting(setvalue):
   payload_set = {
       "requests": [
           {
               "command": [
                   {
                       "command_type": "character", 
                       "command_code": "set_property_value",
                       "command_value": setvalue
                   }
               ],
               "driver_id": os.environ['DRIVER_ID'],
               "r_edge_id": os.environ['R_EDGE_ID'],
               "thing_uuid": os.environ['THING_UUID']
           } 
       ]
   }
   return payload_set

#requestのheadersを決める関数
headers = {
   "Content-type": "application/json",
   "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
   "X-IOT-API-KEY": os.environ['API_KEY']
}


#try_get,try_setを簡単に実行するための関数
def try_get():
   #get1をグローバル変数にしてほかの場所から読み込めるようにして、初期化する
   global get1
   get1 = None
     
   try:
       response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
       print(response_get1.text)
       jsonData = response_get1.json()
       #リクエストを行い、get1に入れる。最後にget1が欲しい値になるために、reversed()を使って逆順にしている。
       for result in reversed(jsonData['results']):
           for command in reversed(result["command"]):
               for response in reversed(command["response"]):
                   #辞書型get1の中身
                   get1 = {
                       'command_code': command["command_code"],
                       'command_value': command["command_value"],
                       'response_result': response["response_result"],
                       'response_value': response["response_value"]
                   }
                   #get1の中身をprintする    
                   print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")
                   #タイムスタンプを追加
                   print(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"))
                   #get1の中身をprintする

                   #print()の中身をtxtファイルに書き込む
                   with open('log.txt', mode='a') as f:
                       f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ")
                       f.write(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})\n")
                      
   except TimeoutError:
       print("get1 is timed out")   
       #print()の中身をtxtファイルに書き込む
       with open('log.txt', mode='a') as f:
           f.write("get1 is timed out\n")    
         
       pass
       time.sleep(5)
   

def try_set():
   try:
       response_set1 = requests.request("POST", url, headers=headers, json=payload_set, timeout=200)
       print(response_set1.text)
       jsonData = response_set1.json()
       #リクエストを行い、set1に入れる。最後にset1が欲しい値になるために、reversed()を使って逆順にしている。
       for result in reversed(jsonData['results']):
           for command in reversed(result["command"]):
               for response in reversed(command["response"]):
                   #辞書型set1の中身
                   set1 = {
                       'command_code': command["command_code"],
                       'command_value': command["command_value"],
                       'response_result': response["response_result"],
                       'response_value': response["response_value"]
                   }
                   print(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})")
                   print(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"))
                   #print()の中身をtxtファイルに書き込む
                   with open('log.txt', mode='a') as f:
                       f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ")
                       f.write(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})\n")
   except TimeoutError:
       print("set1 is timed out")
       #print()の中身をtxtファイルに書き込む
       with open('log.txt', mode='a') as f:
           f.write("set1 is timed out\n")
       pass
       time.sleep(5)

payload_get=getting("instantaneousChargingAndDischargingElectricPower")
try_get()

payload_get=getting("operationMode")
try_get()

payload_get=getting("actualOperationMode")
try_get()

payload_set=setting("operationMode=standby")
try_set()



payload_get=getting("instantaneousChargingAndDischargingElectricPower")
try_get()

payload_get=getting("operationMode")
try_get()

payload_get=getting("actualOperationMode")
try_get()

payload_set=setting("operationMode=discharging")
try_set()

time.sleep(30)


payload_get=getting("instantaneousChargingAndDischargingElectricPower")
try_get()

payload_get=getting("operationMode")
try_get()

payload_get=getting("actualOperationMode")
try_get()

payload_set=setting("operationMode=charging")
try_set()

time.sleep(30)

payload_get=getting("instantaneousChargingAndDischargingElectricPower")
try_get()

payload_get=getting("operationMode")
try_get()

payload_get=getting("actualOperationMode")
try_get()

payload_set=setting("operationMode=standby")
try_set()



payload_get=getting("instantaneousChargingAndDischargingElectricPower")
try_get()

payload_get=getting("operationMode")
try_get()

payload_get=getting("actualOperationMode")
try_get()

