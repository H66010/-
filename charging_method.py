#蓄電池を充電状態にしたい場合に実行するプログラム。
#動作：１.瞬時電力を取得し、実機の状態（充放電or待機)を確認する。
#　　　２.getした値と実機の状態が一致しているか確認する。
#　　　３.一致している場合はSOCを取得し、~80なら充電する。すでに充電中の場合は充電中の戻り値を返す。
#　　　４.20秒待ち、実際に充電しているかを電力を見ることで確認する。
#　　　５.成功した場合は下記のように戻り値を返す。
#因数：main.pyから呼び出される。特になし
#戻り値：放電から充電の成功:DC01,停止から充電の成功:SC01,既に充電中：CC01放電から充電の失敗:ERROR （ERRORの原因はlogで確認する。）
#途中経過はlogに書き込まれる。
#全体として、SOCを20~80に保つと同時に、蓄電池の実際の動作と表示上の動作が一致するか確認しつつ、充電への切り替えを行う。

#必要なライブラリのインポート
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import pytz  # type: ignore

#充電メソッドを実行する関数
def run_charging_method():
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
           "command_value": setvalue}
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
                      #print()の中身をtxtファイルに書き込む
                      with open('log.txt', mode='a') as f:
                          f.write(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})\n")
      except TimeoutError:
          print("set1 is timed out")
          #print()の中身をtxtファイルに書き込む
          with open('log.txt', mode='a') as f:
              f.write("set1 is timed out\n")
          pass
          time.sleep(5)
  
#getのpayloadを電力取得にする
  payload_set=setting("operationMode=charging")
  payload_get=getting("instantaneousChargingAndDischargingElectricPower")
#getを実行してみる
  try_get()
#電力取得NGの場合。
  if get1['response_result']=="NG":
        print("Getting_Electric_Power_error")
        return "ERROR"
    #電力取得OKの場合。
  else:
    print("Getting_Electric_Power_success")
    Electric_Power = int(get1['response_value'])
    if Electric_Power >=1: #電力が1以上の場合の分岐
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
            #operationModeがchargingの場合
            if get1['response_value']=="charging":
                print("already_charging")
                return "CC01"
            #operationModeがdischargingの場合
            elif get1['response_value']=="discharging":
                print("unexpected_charging(discharging_setting)")
                return "ERROR"
            #operationModeがstandbyの場合
            elif get1['response_value']=="standby" or "auto":
                print("unexpected_charging(standby_setting)")
                return "ERROR"

    elif Electric_Power<=-1: #電力が-1以下の場合の分岐
        #operationModeを取得する
        payload_get=getting("operationMode")
        try_get()
        #operationMode取得NGの場合
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
            return "ERROR"
        #operationMode取得OKの場合
        else:
            #operationModeがchargingの場合
            if get1['response_value'] == "charging":
                print("unexpected_discharging(charging_setting)")
                return "ERROR"
            #operationModeがstandbyの場合
            elif get1['response_value'] == "standby":
                print("unexpected_discharging(standby_setting)")
                return "ERROR"
            #operationModeがdischargingの場合
            else:
                #remainingCapacity3を取得する
                payload_get = getting("remainingCapacity3")
                try_get()
                #remainingCapacity3取得NGの場合
                if get1['response_result'] == "NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                #remainingCapacity3取得OKの場合
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    #remainingCapacity3が90以下の場合
                    if RemainingCapacity3 <= 90:
                        
                        payload_set = setting("operationMode=charging")
                        try_set()
                        if get1['response_result'] == "NG":
                            print("Setting_OperationMode_error")
                        else:
                            print("Setting_OperationMode_success")
                        time.sleep(20)
                        payload_get = getting("instantaneousChargingAndDischargingElectricPower")
                        try_get()
                        Electric_Power = int(get1['response_value'])
                        if Electric_Power >= 1:
                            print("Charging_success")
                        else:
                            print("charging_error")
                 
                        if get1["response_value"] == "charging":
                            print("Setting_OperationMode_success")
                            time.sleep(20)
                            payload_get = getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power >= 1:
                                print("Charging_success")
                                return "DC01"
                            else:
                                print("charging_error")
                                return "ERROR"
                        else:
                            print("Setting_OperationMode_error")
                            return "ERROR"
                    else:
                        print("too_much_remainingCapacity3(dischaging_setting)")
                        return "ERROR"

    else:#電力が0の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
            return "ERROR"
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="charging":
                print("cannot_charge")
                return "ERROR"
            elif get1['response_value']=="discharging":
                print("cannot_discharge")
                return "ERROR"
            elif get1['response_value']=="standby" or "auto":
                payload_get=getting("remainingCapacity3")
                try_get()
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    if RemainingCapacity3<=90:
                       
                    
                        
                        payload_set=setting("operationMode=charging")
                        try_set()
                        if 'response_result'=="NG":
                            print("Setting_OperationMode_error")
                        else:
                            print("Setting_OperationMode_success")
                        payload_get=getting("operationMode") #実機操作後のモード取得。
                        try_get()
                        #response_valueがchargingになっていれば、成功を出す。
                        if get1['response_value']=="charging" or "auto":
                            print("Setting_OperationMode_success")
                            time.sleep(20)
                            payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power>=1:
                                print("Charging_success")
                                return "SC01"
                            else:
                                print("charging_error")
                                return "ERROR"
                        else:
                            print("Setting_OperationMode_error")
                            return "ERROR"
                    else:
                        print("too_much_remainingCapacity3(standby_setting)")
                        return "ERROR"
          
if __name__ == "__main__":
    run_charging_method()
