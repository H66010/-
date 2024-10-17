#必要なライブラリのインポート
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import pytz

#standbyメソッドの実行
def run_standby_method():
    load_dotenv()
    url = os.environ['TARGET_URL']
    
    def getting(getvalue):
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
    
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
        "X-IOT-API-KEY": os.environ['API_KEY']
    }
    
    def try_get():
        global get1
        get1 = None
        try:
            response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
            print(response_get1.text)
            jsonData = response_get1.json()
            for result in reversed(jsonData['results']):
                for command in reversed(result["command"]):
                    for response in reversed(command["response"]):
                        get1 = {
                            'command_code': command["command_code"],
                            'command_value': command["command_value"],
                            'response_result': response["response_result"],
                            'response_value': response["response_value"]
                        }
                        print(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%Y/%m/%d %H:%M:%S"))
                        print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")
                        with open('log.txt', mode='a') as f:
                            f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ")
                            f.write(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})\n")
        except TimeoutError:
            print("get1 is timed out")   
            with open('log.txt', mode='a') as f:
                f.write("get1 is timed out\n")    
            pass
            time.sleep(5)
   
    def try_set():
        try:
            response_set = requests.request("POST", url, headers=headers, json=payload_set, timeout=200)
            print(response_set.text)
            jsonData = response_set.json()
            for result in reversed(jsonData['results']):
                for command in reversed(result["command"]):
                    for response in reversed(command["response"]):
                        set1 = {
                            'command_code': command["command_code"],
                            'command_value': command["command_value"],
                            'response_result': response["response_result"],
                            'response_value': response["response_value"]
                        }
                        print(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})")
                        with open('log.txt', mode='a') as f:
                            f.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " ")                         
                            f.write(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})\n")
        except TimeoutError:
            print("set1 is timed out")
            with open('log.txt', mode='a') as f:
                f.write("set1 is timed out\n")
            pass
            time.sleep(5)
    
    # ここからstandbyメソッドの本体
    # operationModeを取得する
    payload_get = getting("operationMode")
    try_get()
    
    # operationMode取得NGの場合
    if get1['response_result'] == "NG":
        print("Getting_OperationMode_error")
        return "ERROR"
    # operationMode取得OKの場合
    else:
        print("Getting_OperationMode_success")
        # operationModeがstandbyの場合
        if get1['response_value'] == "standby":
            print("already_standby")
            return "SS01"  # 既にstandby状態の場合、SS01を返す
        # operationModeがstandbyでない場合
        else:
            # operationModeをstandbyに設定する
            payload_set = setting("operationMode=standby")
            try_set()
            
            # operationModeの設定結果を確認する
            payload_get = getting("operationMode")
            try_get()
            
            # response_valueがstandbyになっていれば、成功を出す
            if get1['response_value'] == "standby":
                print("setting_operationMode_success")
                return "SS01"
            else:
                print("setting_operationMode_failed")
                return "ERROR"

if __name__ == "__main__":
    run_standby_method()