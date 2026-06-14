import json
import os
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import speed
import toast
import systray_helper


class SpeedTrayApp:
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speedtray_config.json")
    OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "internet_speed.xlsx")
    DEFAULT_CONFIG = {"run_hours": 0, "run_minutes": 15, "interval_minutes": 5}

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SpeedTest Monitor")
        self.root.geometry("700x450")
        self.root.resizable(True, True)

        self.config = self.load_config()
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.tray_app = None
        self.tray_thread = None

        self.create_output_file()
        self.create_widgets()
        self.start_speed_checks()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as file:
                    saved = json.load(file)
                    return {**self.DEFAULT_CONFIG, **saved}
            except Exception:
                pass

        self.save_config(self.DEFAULT_CONFIG)
        return dict(self.DEFAULT_CONFIG)

    def save_config(self, config):
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(config, file, indent=2)
            self.config = dict(config)
        except Exception as error:
            self.append_text(f"Unable to save settings: {error}\n")

    def create_output_file(self):
        if not os.path.exists(self.OUTPUT_FILE):
            columns = ["Speed Agreed", "Download - Mbps", "Upload - Mbps", "Date - Time"]
            df = speed.pd.DataFrame(columns=columns)
            df.to_excel(self.OUTPUT_FILE, sheet_name="Internet Speed", index=False)
            self.append_text(f"Created output file: {self.OUTPUT_FILE}\n")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(controls_frame, text="Run duration:").grid(row=0, column=0, sticky="w")
        ttk.Label(controls_frame, text="Hours").grid(row=1, column=0, sticky="w", padx=(0, 8))
        ttk.Label(controls_frame, text="Minutes").grid(row=1, column=2, sticky="w", padx=(20, 8))
        ttk.Label(controls_frame, text="Check interval (min):").grid(row=0, column=4, sticky="w", padx=(20, 0))

        hours_values = [str(item) for item in range(0, 25)]
        minutes_values = [str(item) for item in range(0, 60, 15)]
        interval_values = [str(item) for item in range(5, 61, 5)]

        self.hours_var = tk.StringVar(value=str(self.config["run_hours"]))
        self.minutes_var = tk.StringVar(value=str(self.config["run_minutes"]))
        self.interval_var = tk.StringVar(value=str(self.config["interval_minutes"]))

        self.hours_box = ttk.Combobox(controls_frame, values=hours_values, textvariable=self.hours_var, width=4, state="readonly")
        self.hours_box.grid(row=1, column=1, sticky="w")
        self.minutes_box = ttk.Combobox(controls_frame, values=minutes_values, textvariable=self.minutes_var, width=4, state="readonly")
        self.minutes_box.grid(row=1, column=3, sticky="w")
        self.interval_box = ttk.Combobox(controls_frame, values=interval_values, textvariable=self.interval_var, width=4, state="readonly")
        self.interval_box.grid(row=1, column=5, sticky="w")

        self.hours_var.trace_add("write", self.on_setting_changed)
        self.minutes_var.trace_add("write", self.on_setting_changed)
        self.interval_var.trace_add("write", self.on_setting_changed)

        self.save_button = ttk.Button(main_frame, text="Save changes", command=self.on_save, state="disabled")
        self.save_button.pack(anchor="e", pady=(0, 8))

        results_frame = ttk.LabelFrame(main_frame, text="Speed Test Results")
        results_frame.pack(fill="both", expand=True)

        self.result_text = tk.Text(results_frame, wrap="word", relief="sunken", borderwidth=1)
        self.result_text.pack(side="left", fill="both", expand=True)
        self.result_text.configure(state="disabled")

        scrollbar = ttk.Scrollbar(results_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.append_text("This app allows you to monitor your internet speed at regular intervals. using SpeedTest API.\n\n" \
                        "Use the options to change the runtime and/or test interval.\n\n" \
                        "Close the window to minimize to tray. You will be notified with the results.\n\n" \
                        "All executed tests will be logged in the 'internet_speed.xlsx' file, in the same directory as the application.\n\n")

    def on_setting_changed(self, *args):
        try:
            current = {
                "run_hours": int(self.hours_var.get()),
                "run_minutes": int(self.minutes_var.get()),
                "interval_minutes": int(self.interval_var.get()),
            }
        except ValueError:
            self.save_button.config(state="disabled")
            return

        if current != self.config:
            self.save_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")

    def on_save(self):
        try:
            new_config = {
                "run_hours": int(self.hours_var.get()),
                "run_minutes": int(self.minutes_var.get()),
                "interval_minutes": int(self.interval_var.get()),
            }
        except ValueError:
            self.append_text("Invalid settings. Please choose valid numbers.\n")
            return

        self.save_config(new_config)
        self.append_text("Settings saved. Restarting checks with updated values...\n")
        self.save_button.config(state="disabled")
        self.restart_speed_checks()

    def restart_speed_checks(self):
        self.stop_speed_checks()
        self.start_speed_checks()

    def start_speed_checks(self):
        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self.run_speed_loop, daemon=True)
        self.worker_thread.start()

    def stop_speed_checks(self):
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)

    def run_speed_loop(self):
        run_minutes = self.config.get("run_hours", 0) * 60 + self.config.get("run_minutes", 0)
        interval_minutes = self.config.get("interval_minutes", 5)

        if run_minutes <= 0:
            self.append_text("The configured runtime is zero minutes. No speed tests will be performed until you save a nonzero duration.\n")
            return

        self.append_text(f"Starting speed checks for {run_minutes} minutes every {interval_minutes} minutes.\n")
        start_time = time.monotonic()
        end_time = start_time + run_minutes * 60
        next_run = start_time

        while not self.stop_event.is_set() and time.monotonic() < end_time:
            now = time.monotonic()
            if now >= next_run:
                self.perform_speed_test()
                next_run = now + interval_minutes * 60
            time.sleep(0.5)

        if not self.stop_event.is_set():
            self.append_text("Runtime completed. Waiting for updated settings or restart.\n")

    def perform_speed_test(self):
        try:
            tester = speed.speedtest.Speedtest()
            tester.get_best_server()
            download_speed = tester.download(threads=None) * 1e-6
            upload_speed = tester.upload(threads=None) * 1e-6
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{timestamp} - Download: {round(download_speed)} Mbps | Upload: {round(upload_speed)} Mbps"
            self.append_text(message + "\n")
            self.log_to_excel(round(download_speed), round(upload_speed), timestamp)
            notifier = toast.WindowsToastNotifier()
            notifier.send("Speed Check Result", message)
        except Exception as error:
            self.append_text(f"Error during speed test: {error}\n")

    def log_to_excel(self, download_speed, upload_speed, timestamp):
        try:
            if os.path.exists(self.OUTPUT_FILE):
                df = speed.pd.read_excel(self.OUTPUT_FILE, sheet_name="Internet Speed")
            else:
                df = speed.pd.DataFrame(columns=["Speed Agreed", "Download - Mbps", "Upload - Mbps", "Date - Time"])

            df.loc[len(df)] = ["GUI", download_speed, upload_speed, timestamp]
            df.to_excel(self.OUTPUT_FILE, sheet_name="Internet Speed", index=False)
        except Exception as error:
            self.append_text(f"Unable to log results to Excel: {error}\n")

    def append_text(self, message):
        self.result_text.configure(state="normal")
        self.result_text.insert("end", message)
        self.result_text.see("end")
        self.result_text.configure(state="disabled")

    def on_close(self):
        self.root.withdraw()
        self.append_text("Window hidden. Application is running in the tray.\n")
        self.start_tray()

    def start_tray(self):
        if self.tray_app is not None:
            return

        self.tray_app = systray_helper.TrayApp(self.on_show_request, self.on_quit_request)
        self.tray_thread = threading.Thread(target=self.tray_app.start, daemon=True)
        self.tray_thread.start()

    def on_show_request(self):
        if not self.root.winfo_exists():
            return
        self.root.after(0, self.show_window)

    def show_window(self):
        if self.tray_app is not None:
            self.tray_app.stop()
            self.tray_app = None
        if self.tray_thread is not None:
            self.tray_thread.join(timeout=5)
            self.tray_thread = None

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def on_quit_request(self):
        self.append_text("Quitting application from tray.\n")
        self.quit_app()

    def quit_app(self):
        self.stop_speed_checks()
        if self.tray_app is not None:
            self.tray_app.stop()
            self.tray_app = None
        if self.tray_thread is not None:
            self.tray_thread.join(timeout=5)
            self.tray_thread = None
        if self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    SpeedTrayApp()
