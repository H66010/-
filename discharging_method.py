#蓄電池を放電状態にしたい場合に実行するプログラム。
#動作：１.瞬時電力を取得し、実機の状態（充放電or待機)を確認する。
#　　　２.getした値と実機の状態が一致しているか確認する。
#　　　３.一致している場合はSOCを取得し、~80なら放電する。すでに放電中の場合は放電中の戻り値を返す。
#　　　４.20秒待ち、実際に放電しているかを電力を見ることで確認する。
#　　　５.成功した場合は下記のように戻り値を返す。
#因数：main.pyから呼び出される。特になし
#戻り値：充電から放電の成功:CD01,停止から放電の成功:SD01,既に放電中：DD01,放電から充電の失敗:ERROR （ERRORの原因はlogで確認する。）
#途中経過はlogに書き込まれる。
#全体として、SOCを20~80に保つと同時に、蓄電池の実際の動作と表示上の動作が一致するか確認しつつ、放電への切り替えを行う。

#必要なライブラリのインポート
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import pytz # type: ignore


#放電メソッドの実行
def run_discharging_method():
 #.envファイルの読み込み
 load_dotenv()
 #urlの設定
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
         "command_value": setvalue}
       ],
 
       "driver_id": os.environ['DRIVER_ID'],
       "r_edge_id": os.environ['R_EDGE_ID'],
       "thing_uuid": os.environ['THING_UUID']
      } 
    ]
  }
  return payload_set
 #ヘッダーの設定
 headers = {
  "Content-type": "application/json",
  "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
  "X-IOT-API-KEY": os.environ['API_KEY']
 }
 #getとsetを実行するための関数
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
                     #タイムスタンプを追加
                     print(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"))
                        #get1の中身をprintする
                
                     print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")
                     #print()の中身をtxtファイルに書き込む
                     with open('log.txt', mode='a') as f:
                         #タイムスタンプを追加
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
                     #set1の中身をprintする
                     print(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})")
                     #print()の中身をtxtファイルに書き込む
                     
                     with open('log.txt', mode='a') as f:
                         #タイムスタンプを追加
                         f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ")                         
                         f.write(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})\n")
     except TimeoutError:
         print("set1 is timed out")
         #print()の中身をtxtファイルに書き込む
         with open('log.txt', mode='a') as f:
             f.write("set1 is timed out\n")
         pass
         time.sleep(5)
 
#ここから放電メソッドの本体
    #瞬時電力を取得する
 payload_get=getting("instantaneousChargingAndDischargingElectricPower")
 try_get()
 #電力取得NGの場合
 if 'response_result'=="NG":
     print("Getting_Electric_Power_error")
     return "ERROR"
 #電力取得OKの場合
 else:
     print("Getting_Electric_Power_success")
     Electric_Power = int(get1['response_value'])
     if Electric_Power<=-1: #電力が-1以下の場合の分岐
         #operationModeを取得する
         payload_get=getting("operationMode")
         try_get()
            #operationMode取得NGの場合
         if get1['response_result']=="NG":
             print("Getting_OperationMode_error")
             return "ERROR"
            #operationMode取得OKの場合
         else:
             print("Getting_OperationMode_success")
             #operationModeがdischargingの場合(すでに放電中の場合.DD01を返す。)
             if get1['response_value']=="discharging":
                 print("already_discharging")
                 return "DD01"
                #operationModeがchargingの場合
             elif get1['response_value']=="charging":
                 print("unexpected_discharging(charging_setting)")
                 return "ERROR"
                #operationModeがstandbyの場合
             elif get1['response_value']=="standby" or "auto":
                 print("unexpected_discharging(standby_setting)")
                 return "ERROR"
 
     elif Electric_Power>=1: #電力が1以上の場合の分岐
         #operationModeを取得する
         payload_get=getting("operationMode")
         try_get()
            #operationMode取得NGの場合
         if get1['response_result']=="NG":
             print("Getting_OperationMode_error")
             return "ERROR"
            #operationMode取得OKの場合
         else:
             print("Getting_OperationMode_success")
             #operationModeがdischargingの場合
             if get1['response_value']=="discharging":
                 print("unexpected_charging(discharging_setting)")
                 return "ERROR"
                #operationModeがstandbyの場合
             elif get1['response_value']=="standby":
                 print("unexpected_charging(standby_setting)")
                 return "ERROR"
                #operationModeがchargingの場合
             else:
                #SOC残量を取得する
                 payload_get=getting("remainingCapacity3")
                 try_get()
                    #SOC残量取得NGの場合
                 if get1['response_result']=="NG":
                     print("Getting_RemainingCapacity3_error")
                     return "ERROR"
                    #SOC残量取得OKの場合
                 else:
                     print("Getting_RemainingCapacity3_success")
                     RemainingCapacity3 = int(get1['response_value'])
                     if RemainingCapacity3>=10: #残量が10%以上の場合に放電
                         
                         payload_set=setting("operationMode=discharging")
                         try_set()
                         if 'response_result'=="NG":
                             print("Setting_OperationMode_error")
                         else:
                             print("Setting_OperationMode_success")
                         

                         payload_get=getting("operationMode")
                         try_get()
                         #response_valueがdischargingになっていれば、成功を出す。
                         if get1['response_value']=="discharging" or "auto":
                             print("setting_operationMode_success")
                             time.sleep(20)
                             payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                             try_get()
                             Electric_Power = int(get1['response_value'])
                             if Electric_Power<=-1:
                                 print("disCharging_success")
                                 if get1['response_value'] == "charging":
                                     return "CD01"
                                 else:
                                     return "SD01"
                             else:
                                 print("discharging_error")
                                 return "ERROR"
                         else:
                             print("setting_operationMode_failed")
                             return "ERROR"
                     else:
                         print("too_little_remainingCapacity3")
                         return "ERROR"
 
     else: #電力が0の場合の分岐
         payload_get=getting("operationMode")
         try_get()
         if get1['response_result']=="NG":
             print("Getting_OperationMode_error")
             return "ERROR"
         else:
             print("Getting_OperationMode_success")
             if get1['response_value']=="charging":
                 print("cannot_discharge")
                 return "ERROR"
             elif get1['response_value']=="discharging":
                 print("cannot_discharge")
                 return "ERROR"
             else:
                 payload_get=getting("remainingCapacity3")
                 try_get()
                 if get1['response_result']=="NG":
                     print("Getting_RemainingCapacity3_error")
                     return "ERROR"
                 else:
                     print("Getting_RemainingCapacity3_success")
                     RemainingCapacity3 = int(get1['response_value'])
                     if RemainingCapacity3>=20: #残量が20%以上の場合に放電
                         
                         payload_set=setting("operationMode=discharging")
                         try_set()
                         if 'response_result'=="NG":
                             print("Setting_OperationMode_error")
                         else:
                             print("Setting_OperationMode_success")
                         
                         payload_get=getting("operationMode")
                         try_get()
                         #response_valueがdischargingになっていれば、成功を出す。
                         if get1['response_value']=="discharging" or "auto":
                             print("setting_operationMode_success")
                             time.sleep(20)
                             payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                             try_get()
                             Electric_Power = int(get1['response_value'])
                             if Electric_Power<=-1:
                                 print("disCharging_success")
                                 return "SD01"
                             else:
                                 print("discharging_error")
                                 return "ERROR"
                         else:
                             print("setting_operationMode_failed")
                             return "ERROR"
                     else:
                         print("too_little_remainingCapacity3")
                         return "ERROR"
if __name__ == "__main__":
    run_discharging_method()
