import requests
from bs4 import BeautifulSoup
import pandas as pd

draft_dict = {}

# -------------- Code for scraping draft data from Wikipedia, making the draft dict -----------------#
for i in range(0, 16):
    if i < 10:
        i = f"0{i}"
    response = requests.get(f"https://en.wikipedia.org/wiki/20{i}_NBA_draft")
    sp = BeautifulSoup(response.text, "html.parser")
    draft_table = sp.find(class_="sortable")
    players = draft_table.find_all("tr")
    for p in range(1, 15):
        pick_no = int(players[p].find_all("td")[1].text.split("\n")[0])
        name = players[p].find("a").text
        draft_dict[name] = {"pick_no": pick_no}

#-----------Adding keys to player's dictionaries -------------#
draft_year = 2000
count = 0
for key in draft_dict:
    if count == 14:
        draft_year += 1
        count = 0
    draft_dict[key]["year drafted"] = draft_year
    count += 1
    draft_dict[key]["total_ws to date"] = 0.0
    draft_dict[key]["years played"] = 0
print(draft_dict)

#-------------------Code for getting win-shares from basketball reference----------------------#

for i in range(1, 22):
    ws_dict = {}
    if i < 10:
        i = f"0{i}"
    response = requests.get(f"https://www.basketball-reference.com/leagues/NBA_20{i}_advanced.html#advanced_stats")
    sp = BeautifulSoup(response.text, "html.parser")
    table = sp.find(id="advanced_stats")
    rows = table.find_all(class_="full_table")
    for row in rows:
        try:
            name = row.find("a").text
            ws = float(row.find(attrs={"data-stat": "ws"}).text)
            ws_dict[name] = ws
        except AttributeError:
            pass

    for key in ws_dict:
        if key in draft_dict:
            draft_dict[key]["total_ws to date"] += ws_dict[key]
            draft_dict[key]["years played"] += 1
            draft_dict[key]["avg_ws"] = draft_dict[key]["total_ws to date"] / draft_dict[key]["years played"]
            print(f"changed {key}")

# --------------- Rounding the win shares -----------------#
for key in draft_dict:
    draft_dict[key]["avg_ws"] = round(draft_dict[key]["avg_ws"], 2)
    draft_dict[key]["total_ws to date"] = round(draft_dict[key]["total_ws to date"], 2)

# --------------- Creating a data frame and csv ------------#
draft_frame = pd.DataFrame.from_dict(draft_dict, orient="index")
with open("draft.csv", mode="w") as file:
    data = draft_frame.to_csv()
    file.write(data)
print(draft_frame.head())


