# player-season-performance

Converts table from format shown in 'Original-GB.csv' to format shown in 'Modified-GB.csv' file.

## Instructions
The original table has to be manually taken from https://www.whoscored.com since they do not entertain scraping.
Steps to obtain original table:
1. Go to https://www.whoscored.com, search for a player and open their profile.
2. Go to 'History' tab in the profile. (Example URL: https://www.whoscored.com/Players/13812/History/Gareth-Bale)
3. Select and copy the table from top-left header (Season) to bottom-right cell (Average rating).
4. Open a new blank sheet at sheets.google.com
5. Paste the table as it is on cell A1.
6. Go to File>Download as> .csv

Now run main.py and paste path to the downloaded file.

## Todo
Will add ability to create simple bar charts soon.

### Note:
1. Original file is changed. Keep a backup if you need the original file as well.
2. All float values are rounded off to 2 digits of decimal.
3. Whoscored does not have data for National cups.
