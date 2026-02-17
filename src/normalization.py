import re
import pandas as pd

US_STATE_ABBR = {
    "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA","colorado":"CO",
    "connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI","idaho":"ID",
    "illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY","louisiana":"LA",
    "maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN",
    "mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV",
    "new hampshire":"NH","new jersey":"NJ","new mexico":"NM","new york":"NY",
    "north carolina":"NC","north dakota":"ND","ohio":"OH","oklahoma":"OK","oregon":"OR",
    "pennsylvania":"PA","rhode island":"RI","south carolina":"SC","south dakota":"SD",
    "tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT","virginia":"VA",
    "washington":"WA","west virginia":"WV","wisconsin":"WI","wyoming":"WY",
    "district of columbia":"DC"
}

def normalize_state(state):
    if pd.isna(state):
        return None
    s = str(state).strip().lower()
    # if already an abbreviation, keep it
    if len(s) == 2 and s.isalpha():
        return s.upper()
    return US_STATE_ABBR.get(s, state)

def normalize_crop(crop):
    if pd.isna(crop):
        return None
    s = str(crop).lower().strip()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s)

    aliases = {
        "corn": "corn",
        "soybean": "soybeans",
        "soybeans": "soybeans",
        "wheat": "wheat",
        "cotton": "cotton",
        "rice": "rice",
        "alfalfa": "alfalfa",
        "vegetables and fruit": "vegetables_and_fruit",
        "orchards and grapes": "orchards_and_grapes",
        "pasture and hay": "pasture_and_hay",
        "other crops": "other_crops",
    }
    return aliases.get(s, s)