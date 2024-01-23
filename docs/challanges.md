# List of challenges

- Getting URL of the of the current tab.
- Different keyboards, different keys.
- Running App Efficiently, crashing when multiple events asking for same log file.
- App name are not always very sensible, eg. PyCharm is getting named as `java` and vs code as `electron` in some computers.
- Making sure all keys from keyboard are being recorded properly and sequentially, To differentiate between intentional key combination and unintentional key combination presses, eg. `ctrl+c` we logged which makes sense that someone is trying to copy, but if someone is typing too fast then he might press multiple keys together which can get logged as `h+e+l+l+o`.
- Creating list of apps and categorise them for chat, meetings, ide, presentation etc.
- Understanding App name properly, Google chrome's name can be google_chrome, Google Chrome, Chrome Browser or just be chrome.
- Capturing simultaneous parallel presses keystrokes as 1 keystroke.
- Capturing screenshots in Linux VMs.
- Running application in stealth mode when application is required to ask username and password with a prompt. if we move username and password prompts from main script all runs well.
- Running multiple threads, using same variables and file to read and write from multiple threads.
- Local JSON file management, as we get to stoge logs locally and in a json file, the frequesncy to read and write to file is high which is resulting in crash sometimes (replace this with sqlite in MVP).
