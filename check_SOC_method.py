#SoCと現在の充放電状態、電力を取得するコード
#動作：１.瞬時電力を取得し、実機の状態（充放電or待機)を確認する。
#　　　２.getした値と実機の状態が一致しているか確認する。
#　　　３.一致している場合はSOCを取得し下記の戻り値を返す。
#　　　     一致していない場合は、エラーを返す。

#引数：特になし。main.pyから呼び出される。
#戻り値: 1.Res1（辞書型）を返す。Res1は、制御可能か、充放電状態、電力、残容量を格納している。
#        2.エラーが発生した場合は、エラーを返す。エラー内容は、各関数内でprint()で出力され、log.txtにも書き込まれる。

#必要なライブラリのインポート
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
#SOCチェックメソッドの実行
def run_check_SOC_method():
    # .envファイルの読み込み
    load_dotenv()
    # URLの指定
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

    
    #ヘッダーの指定
    headers = {
    "Content-type": "application/json",
    "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
    "X-IOT-API-KEY": os.environ['API_KEY']
    }

    #try_get,try_setの関数
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
                        #get1の中身をprint()で表示
                        print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")
                        #print()の中身をtxtファイルに書き込む
                        with open('log.txt', mode='a') as f:
                            f.write(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})\n")
                        
        except TimeoutError:
            print("get1 is timed out")   
            #print()の中身をtxtファイルに書き込む
            with open('log.txt', mode='a') as f:
                f.write("get1 is timed out\n")    
            
            pass
            time.sleep(5)
    
   

    #電力を取得する
    payload_get=getting("instantaneousChargingAndDischargingElectricPower")
    try_get()
    #電力取得NGの場合
    if  'response_result'=="NG":
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
            #operationModeがdischargingの場合(実動作と同じ)
            if get1['response_value']=="discharging":
                #dischargingの場合、remainingCapacity3を取得する
                payload_get=getting("remainingCapacity3")
                try_get()
                #remainingCapacity3取得NGの場合
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                #   remainingCapacity3取得OKの場合
                else:
                    print("Getting_RemainingCapacity3_success")
                    print(f"discharging_remaingCapacity3 is {get1['response_value']}%")
                   
                    res1 = None
                     #辞書型res1の中身
                    res1 = {
                        
                        'Electric_Power': Electric_Power,
                        'OperationMode': "charging",
                        'RemainingCapacity3': get1['response_value']
                    }
                    #res1を返す
                    return res1
            #operationModeがchargingの場合
            elif get1['response_value']=="charging":
                print("unexpected_discharging(charging_setting)")
                return "ERROR"
            #   operationModeがstandbyの場合
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
            #operationModeがchargingの場合(実動作と同じ)
            else:
                #chargingの場合、remainingCapacity3を取得する
                payload_get=getting("remainingCapacity3")
                try_get()
                #remainingCapacity3取得NGの場合
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                #remainingCapacity3取得OKの場合
                else:
                    print("Getting_RemainingCapacity3_success")
                    print(f"charging_remaingCapacity3 is {get1['response_value']}%")
                    
                    res1 = None
                    #辞書型res1の中身
                    res1 = {
                        
                        'Electric_Power': Electric_Power,
                        'OperationMode': "discharging",
                        'RemainingCapacity3': get1['response_value']
                    }
                    #res1を返す
                    return res1

    else: #電力が0の場合の分岐
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
                print("cannot_charge")
                return "ERROR"
            #operationModeがdischargingの場合
            elif ['response_value']=="discharging":
                print("cannot_discharge")
                return "ERROR"
            #operationModeがstandbyの場合(実動作と同じ)
            else:
                #standbyの場合、remainingCapacity3を取得する
                payload_get=getting("remainingCapacity3")
                try_get()
                #remainingCapacity3取得NGの場合
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                #remainingCapacity3取得OKの場合
                else:
                    print("Getting_RemainingCapacity3_success") 
                    print(f"standby_remaingCapacity3 is {get1['response_value']}%")
                    
                    res1 = None
                    #辞書型res1の中身
                    res1 = {
                        'control':"OK",
                        'Electric_Power': Electric_Power,
                        'OperationMode': "standby",
                        'RemainingCapacity3': get1['response_value']
                    }
                    return res1

                
if __name__ == "__main__":
    run_check_SOC_method()               