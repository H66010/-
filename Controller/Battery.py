# BatteryManagerクラス: 蓄電池の充電、放電、SoCチェック、モニタリング機能を提供するクラス
# 
# 各メソッドの入出力:
#
# __init__:
#   入力:
#     - max_kwh_capacity (float): 蓄電池の最大容量（KWh）
#     - initial_soc (float): 蓄電池の初期のSoC（％）
#   出力: BatteryManagerインスタンスの初期化
#
# create_get_payload:
#   入力: get_value (str): 取得するプロパティの名前
#   出力: dict: GETリクエスト用のペイロード
#
# create_set_payload:
#   入力: set_value (str): 設定するプロパティの名前と値（例: "operationMode=charging"）
#   出力: dict: SETリクエスト用のペイロード
#
# try_get:
#   入力: payload (dict): GETリクエスト用のペイロード
#   出力: dictまたはNone: GETリクエストの結果。成功なら結果の辞書、タイムアウトエラー時はNone
#
# try_set:
#   入力: payload (dict): SETリクエスト用のペイロード
#   出力: dictまたはNone: SETリクエストの結果。成功なら結果の辞書、タイムアウトエラー時はNone
#
# monitor_SoC_Method:
#   入力: なし
#   出力: 30秒ごとにSoC値およびKWh容量をモニタリングし、出力する。エラーがあれば"ERROR"を返して終了
#
# charging_method:
#   入力: charging_power (int): 設定する充電電力（W）
#   出力: str: 充電の状態を示すコード
#     - "DC01"：放電から充電に切り替わった場合
#     - "SC01"：停止から充電に切り替わった場合
#     - "ERROR"：充電切り替えが失敗した場合
#
# discharging_method:
#   入力: discharging_power (int): 設定する放電電力（W）
#   出力: str: 放電の状態を示すコード
#     - "CD01"：充電から放電に切り替わった場合
#     - "SD01"：停止から放電に切り替わった場合
#     - "ERROR"：放電切り替えが失敗した場合
#
# standby_method:
#   入力: なし
#   出力: str: 待機状態への切り替え結果を示すコード
#     - "SS01"：待機状態への切り替えが成功した場合
#     - "ERROR"：待機モード設定が失敗した場合
import datetime
import requests
import os
from dotenv import load_dotenv
import time
import pytz

class BatteryManager:
    def __init__(self, max_kwh_capacity, initial_soc, max_charging_power, max_discharging_power):
        load_dotenv()
        self.url = os.environ['TARGET_URL']
        self.driver_id = os.environ['DRIVER_ID']
        self.r_edge_id = os.environ['R_EDGE_ID']
        self.thing_uuid = os.environ['THING_UUID']
        self.headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + os.environ['ACCESS_TOKEN'],
            "X-IOT-API-KEY": os.environ['API_KEY']
        }
        self.max_kwh_capacity = max_kwh_capacity
        self.current_kwh_capacity = (initial_soc / 100) * max_kwh_capacity
        self.max_charging_power = max_charging_power
        self.max_discharging_power = max_discharging_power
    def create_get_payload(self, get_value):
        return {
            "requests": [
                {
                    "command": [
                        {
                            "command_type": "character",
                            "command_code": "get_property_value",
                            "command_value": get_value
                        }
                    ],
                    "driver_id": self.driver_id,
                    "r_edge_id": self.r_edge_id,
                    "thing_uuid": self.thing_uuid
                }
            ]
        }

    def create_set_payload(self, set_value):
        return {
            "requests": [
                {
                    "command": [
                        {
                            "command_type": "character",
                            "command_code": "set_property_value",
                            "command_value": set_value
                        }
                    ],
                    "driver_id": self.driver_id,
                    "r_edge_id": self.r_edge_id,
                    "thing_uuid": self.thing_uuid
                }
            ]
        }

    def try_get(self, payload):
        try:
            response = requests.request("POST", self.url, headers=self.headers, json=payload, timeout=20)
            json_data = response.json()
            for result in reversed(json_data['results']):
                for command in reversed(result["command"]):
                    for response in reversed(command["response"]):
                        return {
                            'command_code': command["command_code"],
                            'command_value': command["command_value"],
                            'response_result': response["response_result"],
                            'response_value': response["response_value"]
                        }
        except TimeoutError:
            with open('log.txt', mode='a') as f:
                f.write("GET request timed out\n")
            return None

    def try_set(self, payload):
        try:
            response = requests.request("POST", self.url, headers=self.headers, json=payload, timeout=20)
            json_data = response.json()
            for result in reversed(json_data['results']):
                for command in reversed(result["command"]):
                    for response in reversed(command["response"]):
                        return {
                            'command_code': command["command_code"],
                            'command_value': command["command_value"],
                            'response_result': response["response_result"],
                            'response_value': response["response_value"]
                        }
        except TimeoutError:
            with open('log.txt', mode='a') as f:
                f.write("SET request timed out\n")
            return None
    def monitor_SoC_Method(self):
        power_interval_hours = 30 / 3600  # 30秒を時間に換算
        last_remaining_capacity = None  # 前回のremainingCapacity3の値を保存

        while True:
            # 充放電電力を取得
            power_payload = self.create_get_payload("instantaneousChargingAndDischargingElectricPower")
            power_response = self.try_get(power_payload)

            if power_response is None or power_response['response_result'] == "NG":
                print("Error occurred in retrieving power. Monitoring failed.")
                return "ERROR"

            # SoCを取得
            soc_payload = self.create_get_payload("remainingCapacity3")
            soc_response = self.try_get(soc_payload)

            if soc_response is None or soc_response['response_result'] == "NG":
                print("Error occurred in retrieving SoC. Monitoring failed.")
                return "ERROR"

            
            electric_power = int(power_response['response_value'])
            soc_value = float(soc_response['response_value'])
            print(f"Current Power: {electric_power}W, Current Observed SoC (remainingCapacity3): {soc_value}%")

            # もし新しいremainingCapacity3の値が前回と異なれば、current_socを更新
            if last_remaining_capacity is None or soc_value != last_remaining_capacity:
                self.current_kwh_capacity = (soc_value / 100) * self.max_kwh_capacity
                self.current_soc = soc_value
                last_remaining_capacity = soc_value
                print(f"Adjusted Current KWh Capacity to {self.current_kwh_capacity:.3f} KWh based on observed SoC.")

            # 充放電電力に基づいてKWhを更新し、SoCを再計算
            self.current_kwh_capacity += (electric_power / 1000) * power_interval_hours
            self.current_soc = (self.current_kwh_capacity / self.max_kwh_capacity) * 100
            print(f"Updated Battery Capacity: {self.current_kwh_capacity:.3f} KWh, Updated SoC: {self.current_soc:.2f}%")

            
            time.sleep(30)
    def charging_method(self, charging_power):
        payload_set_power = self.create_set_payload(f"chargingPower={charging_power}")
        set_power_response = self.try_set(payload_set_power)

        if set_power_response is None or set_power_response['response_result'] == "NG":
            print("Setting_ChargingPower_error")
            return "ERROR"

        payload_set_mode = self.create_set_payload("operationMode=charging")
        set_mode_response = self.try_set(payload_set_mode)

        if set_mode_response is None or set_mode_response['response_result'] == "NG":
            print("Setting_OperationMode_error")
            return "ERROR"

        time.sleep(20)
        payload_get = self.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        get_response = self.try_get(payload_get)

        Electric_Power = int(get_response['response_value'])
        if Electric_Power >= 1:
            return "DC01" if set_mode_response['response_value'] == "discharging" else "SC01"
        else:
            return "ERROR"
    def discharging_method(self, discharging_power):
        payload_set_power = self.create_set_payload(f"dischargingPower={discharging_power}")
        set_power_response = self.try_set(payload_set_power)

        if set_power_response is None or set_power_response['response_result'] == "NG":
            print("Setting_DischargingPower_error")
            return "ERROR"

        payload_set_mode = self.create_set_payload("operationMode=discharging")
        set_mode_response = self.try_set(payload_set_mode)

        if set_mode_response is None or set_mode_response['response_result'] == "NG":
            print("Setting_OperationMode_error")
            return "ERROR"

        time.sleep(20)
        payload_get = self.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        get_response = self.try_get(payload_get)

        Electric_Power = int(get_response['response_value'])
        if Electric_Power <= -1:
            return "CD01" if set_mode_response['response_value'] == "charging" else "SD01"
        else:
            return "ERROR"

    def standby_method(self):
        payload_get = self.create_get_payload("operationMode")
        get_response = self.try_get(payload_get)

        if get_response is None or get_response['response_result'] == "NG":
            return "ERROR"
        
        if get_response['response_value'] == "standby":
            return "SS01"

        payload_set = self.create_set_payload("operationMode=standby")
        set_response = self.try_set(payload_set)

        if set_response is None or set_response['response_result'] == "NG":
            return "ERROR"

        payload_get = self.create_get_payload("operationMode")
        get_response = self.try_get(payload_get)

        if get_response is not None and get_response['response_value'] == "standby":
            return "SS01"
        else:
            return "ERROR"
