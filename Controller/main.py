import csv
import threading
from collections import defaultdict
from Battery import BatteryManager
import time

# 最大KWh容量、初期SoC値、および最大充放電電力の設定
max_kwh_capacity = 15  # KWh
initial_soc = 50  # %
max_charging_power = 120  # （W）
max_discharging_power = 100  # （W）

# BatteryManagerのインスタンスを作成
battery_manager = BatteryManager(
    max_kwh_capacity=max_kwh_capacity,
    initial_soc=initial_soc,
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

def extract_soc_bid_data(file_path):
    soc_bid_data = defaultdict(list)
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            year = row['year']
            month = row['month']
            day = row['day']
            hour = row['hour']
            soc_bid = row['SoC_bid[%]']
            time_key = (year, month, day, hour)
            soc_bid_data[time_key].append(soc_bid)
    
    return dict(soc_bid_data)

def monitor_power_thread():
    battery_manager.monitor_SoC_Method()

def run_controller_edge(soc_bid_data):
    for time_key, soc_bids in soc_bid_data.items():
        soc_bids_float = [float(soc_bid) for soc_bid in soc_bids]
        average_soc_bid = sum(soc_bids_float) / len(soc_bids_float)
        
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            continue
        
        current_soc = float(soc_result['RemainingCapacity3'])
        if current_soc < average_soc_bid:
            battery_manager.charging_method(battery_manager.max_charging_power)
        elif current_soc > average_soc_bid:
            battery_manager.discharging_method(battery_manager.max_discharging_power)
        else:
            battery_manager.standby_method()

def run_controller_smooth(soc_bid_data):
    for time_key, soc_bids in soc_bid_data.items():
        soc_bids_float = [float(soc_bid) for soc_bid in soc_bids]
        average_soc_bid = sum(soc_bids_float) / len(soc_bids_float)
        
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            continue
        
        current_soc = float(soc_result['RemainingCapacity3'])
        soc_difference = average_soc_bid - current_soc
        remaining_time_hours = 1
        required_power = (soc_difference / 100) * battery_manager.max_kwh_capacity / remaining_time_hours * 1000

        if required_power > 0:
            charging_power = min(required_power, battery_manager.max_charging_power)
            battery_manager.charging_method(charging_power)
        elif required_power < 0:
            discharging_power = min(abs(required_power), battery_manager.max_discharging_power)
            battery_manager.discharging_method(discharging_power)
        else:
            battery_manager.standby_method()

# CSVファイルのパスを指定
file_path = '/workspaces/der_tester/tools/scripts/iothub/result_dataframe.csv'
soc_bid_data = extract_soc_bid_data(file_path)

# ユーザーが選択した制御モードに応じて関数を実行
mode = input("Enter control mode ('edge' or 'smooth'): ").strip().lower()

monitor_thread = threading.Thread(target=monitor_power_thread, daemon=True)
monitor_thread.start()

if mode == 'edge':
    run_controller_edge(soc_bid_data)
elif mode == 'smooth':
    run_controller_smooth(soc_bid_data)
else:
    print("Invalid mode selected. Please choose 'edge' or 'smooth'.")

monitor_thread.join()
