#整備中
import charging_method
import discharging_method
import check_SOC_method
import standby_method
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
from soc_bid_extractor import extract_soc_bid_data
from check_SOC_method import run_check_SOC_method

def process_soc_bid_data(soc_bid_data):
    """
    Processes SoC_bid[%] data for each hour and calls appropriate methods based on current SoC.
    
    Args:
    soc_bid_data (dict): A dictionary with time keys (year, month, day, hour)
                         and lists of SoC_bid[%] values.
    
    Returns:
    dict: A dictionary with processed results for each hour.
    """
    processed_results = {}

    for time_key, soc_bids in soc_bid_data.items():
        year, month, day, hour = time_key

        # SoC_bid[%]の平均を計算
        soc_bids_float = [float(soc_bid) for soc_bid in soc_bids]
        average_soc_bid = sum(soc_bids_float) / len(soc_bids_float)
        
        # 現在のSoC値を取得
        soc_result = run_check_SOC_method()
        if soc_result == "ERROR":
            print(f"Error retrieving SoC data for time {time_key}")
            continue
        
        current_soc = float(soc_result['RemainingCapacity3'])
        
        # SoC_bid[%]と現在のSoCを比較して充電・放電を行う
        if current_soc < average_soc_bid:
            print(f"Charging required at {time_key}: Current SoC ({current_soc}) < SoC_bid ({average_soc_bid})")
            charging_method.run_charging_method()
        elif current_soc > average_soc_bid:
            print(f"Discharging required at {time_key}: Current SoC ({current_soc}) > SoC_bid ({average_soc_bid})")
            discharging_method.run_discharging_method()
        else:
            print(f"No action needed at {time_key}: Current SoC ({current_soc}) == SoC_bid ({average_soc_bid})")
            standby_method.run_standby_method()
        
        # 結果を辞書に格納
        processed_results[time_key] = {
            'average_soc_bid': average_soc_bid,
            'current_soc': current_soc,
            'action': 'charge' if current_soc < average_soc_bid else 'discharge' if current_soc > average_soc_bid else 'standby'
        }

    return processed_results

# CSVファイルのパスを指定
file_path = '/workspaces/der_tester/tools/scripts/iothub/result_dataframe.csv'

# SoC_bidデータを抽出
soc_bid_data = extract_soc_bid_data(file_path)

# データを処理
processed_data = process_soc_bid_data(soc_bid_data)


