  #                                         Internet Speed Test 

<p align="center">
  <img src="https://img.shields.io/static/v1?label=python&message=3.12&color=blue&style=for-the-badge&logo=python"/>
</p>


### Topics :writing_hand:

- [Project Description](#project-description-file_folder)
- [Funcionalities](#funcionalities-gear)
- [Requirements](#requirements-pushpin)
- [How to run the app](#how-to-run-the-app-arrow_forward)
- [ToDo](#ToDo-rocket)
- [License](#License-grey_exclamation)



## Project Description :file_folder:

<p align="justify">
  Manage and save speed test checks every 15 minutes (default)
  Tkinter interface + system tray icon so when window is closed it runs on background
  Toast Notification on windows 11 with the results of the speed test
  Using Speed test API
</p>


## Funcionalities :gear:

:heavy_check_mark: Storage the results in a Excel file 

:heavy_check_mark: Windowed interface + systemtray icon 

:heavy_check_mark: Ajustable intervals to check 

:heavy_check_mark: Ajustable timer to run software


## Requirements :pushpin:

install all requirements in requirements.txt

'''''''''''''''''''''''''''''''
pip install -r requirements.txt
'''''''''''''''''''''''''''''''


## How to run it :arrow_forward:

Store all files under the same directory.
Open a CMD on the same directory and run:

''''''''''''''''
python main.py
''''''''''''''''


## ToDo :rocket:

:memo: Add, ping, Starting, Stopping date/time to run the app.
:memo: Check why its showing timeout message on toast notfication and how to avoid its display "(<ToastDismissalReason.TIMED_OUT: 2>,)"
:memo: Run it on background in Windows.

## License :grey_exclamation:

The [MIT License]() (MIT)


