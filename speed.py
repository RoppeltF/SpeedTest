import speedtest
from datetime import datetime
import pandas as pd
from threading import Timer

import os  
from toast import WindowsToastNotifier


def internet_check(speed_agreed, output_file, interval=15):
    interval = int(interval) * 60  # Convert minutes to seconds
    #print("\nStarting speed test... (This takes a few moments)")
    
    try:
        df = pd.read_excel(output_file, sheet_name='Internet Speed')
        
        s = speedtest.Speedtest()
        s.get_best_server() 
        
        current_date = datetime.now().strftime('%d/%m/%Y')
        current_time = datetime.now().strftime('%H:%M')
        
        download_speed = s.download(threads=None) * (10**-6)
        upload_speed = s.upload(threads=None) * (10**-6)
        
        # Append new data
        df.loc[len(df)] = [speed_agreed, round(download_speed), round(upload_speed), current_date + " " + current_time]
        
        # Save to excel
        df.to_excel(output_file, sheet_name='Internet Speed', index=False)
        #print(f"Logged! Download: {round(download_speed)} Mbps | Upload: {round(upload_speed)} Mbps")

        notifier = WindowsToastNotifier()
        notifier.send("Speed Check Result", f" Download Speed: { round(download_speed) } Mbps \n Upload Speed: { round(upload_speed) } Mbps")

    except Exception as e:
        pass
        #print(f"An error occurred during execution: {e}")

    
    Timer(interval, internet_check, args=(speed_agreed, output_file)).start()
    
    

def main():
    
    #print("This script will log your internet speed every 60 seconds.")
    #print("Please ensure you have a stable internet connection for accurate results.")
    

    speed_agreed = input("Internet Speed( M for mega G for giga ): ")
    interval = input("Test interval (minutes if none defaults to 15): ")
    if not interval:
        interval = 15  # Default to 15 minutes if no input is provided

    output_file = "internet_speed.xlsx"
    cols = ["Speed Agreed", "Download - Mbps", "Upload - Mbps", "Date - Time"]

    if not os.path.exists(output_file):
        df = pd.DataFrame(columns=cols)
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name="Internet Speed", index=False)
        #print(f"Created a fresh file: '{output_file}'")
    #else:
        #print(f"Found existing '{output_file}'. Appending new logs to it.")
    
    try:
        while True:
            internet_check(speed_agreed, output_file, interval)
            #print(f"Waiting {interval} minute(s) for the next check...")
            
    except KeyboardInterrupt:
        print("\nScript stopped by user. Exiting safely.")

if __name__ == "__main__":
    main()