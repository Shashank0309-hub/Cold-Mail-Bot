import time
from datetime import datetime

import pyautogui


def search_in_chrome(queries, chrome_windows):
    for query in queries:
        if not chrome_windows:
            print("No Chrome window found")
            return

        chrome_window = chrome_windows[0]
        chrome_window.activate()
        time.sleep(1)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(1)
        pyautogui.write(query)
        pyautogui.press('enter')
        time.sleep(3)
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('enter')


def schedule_drafts(num_of_drafts, chrome_windows):
    chrome_window = chrome_windows[0]
    chrome_window.activate()

    time.sleep(2)
    pyautogui.press('f5')
    time.sleep(10)
    pyautogui.hotkey('g', 'd')
    time.sleep(10)

    for i in range(num_of_drafts):
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)

        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('down')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)

        # if today is saturday then schedule draft for monday morning
        if datetime.today().weekday() == 5:
            pyautogui.press('down')
            pyautogui.press('down')

        pyautogui.press('enter')
