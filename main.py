import requests
from bs4 import BeautifulSoup
import pandas as pd
from draftdict import clean_draft_dict  # cleaned up the data from wikipedia so all player names
                                        # match names on Basketball Reference.


# -------------- Code for scraping draft data from Wikipedia, making the draft dict -----------------#
# for i in range(1966, 2016):
#
#     response = requests.get(f"https://en.wikipedia.org/wiki/{i}_NBA_draft")
#     sp = BeautifulSoup(response.text, "html.parser")
#     draft_table = sp.find(class_="sortable")
#     players = draft_table.find_all("tr")
#     for p in range(1, 15):
#         pick_no = int(players[p].find_all("td")[1].text.split("\n")[0])
#         name = players[p].find("a").text
#         draft_dict[name] = {"pick_no": pick_no}

#-----------Adding keys to player's dictionaries -------------#
# draft_year = 1966
# count = 0
# for key in draft_dict:
#     if count == 14:
#         draft_year += 1
#         count = 0
#     draft_dict[key]["year drafted"] = draft_year
#     count += 1
#     draft_dict[key]["career_ws"] = 0.0
#     draft_dict[key]["years played"] = 0
#     draft_dict[key]["avg_ws"] = 0
# print(draft_dict)

#-------------------Code for getting win-shares from basketball reference----------------------#

for i in range(1967, 2021):
    print(f"started {i}")
    ws_dict = {}
    response = requests.get(f"https://www.basketball-reference.com/leagues/NBA_{i}_advanced.html#advanced_stats")
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
        if key in clean_draft_dict:
            clean_draft_dict[key]["career_ws"] += ws_dict[key]
            clean_draft_dict[key]["years played"] += 1
            clean_draft_dict[key]["avg_ws"] = clean_draft_dict[key]["career_ws"] / clean_draft_dict[key]["years played"]


# --------------- Rounding the win shares -----------------#
for key in clean_draft_dict:
    clean_draft_dict[key]["avg_ws"] = round(clean_draft_dict[key]["avg_ws"], 2)
    clean_draft_dict[key]["career_ws"] = round(clean_draft_dict[key]["career_ws"], 2)

# Mike Dunleavy Sr. also played in the NBA in the 70's (not a top 14 pick)
# On Basketball Reference Jr. and Sr. are both just Mike Dunleavy so Jr. gets his stats added manually.
clean_draft_dict["Mike Dunleavy Jr."] = {'pick_no': 3, 'year drafted': 2002, 'career_ws': 58.50, 'years played': 15, 'avg_ws': 3.90}
# --------------- Creating a data frame and csv ------------#
draft_frame = pd.DataFrame.from_dict(clean_draft_dict, orient="index")
with open("draft.csv", mode="w") as file:
    data = draft_frame.to_csv()
    file.write(data)
print(draft_frame.head())

# check for players with no data added. Used to find name differences between wikipedia and basketball reference
# and make clean dictionary.  Since we're using clean_draft_dict it currently it prints players who never played in the NBA.
# RIP Len Bias.
print(clean_draft_dict)
for key in clean_draft_dict:
    if clean_draft_dict[key]["years played"] == 0:
        print(key)
