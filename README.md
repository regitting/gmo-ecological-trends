# GMO Ecological Trends – Technical Pipeline

This repository contains the technical/data-analysis portion of a BACSA research project.
It combines GMO adoption data with pesticide-use data and produces graphs used in the report.

You do not need to know computer science to run this, but the steps must be followed in order.

---

## What this project does

1. Reads GMO adoption data (USDA ERS)
2. Reads pesticide-use data (USGS)
3. Combines them into one cleaned dataset
4. Generates graphs in a Jupyter notebook

---

## Folder overview

- `data/raw/`  
  Place original data files here (CSV or TXT)

- `data/processed/`  
  Automatically generated merged dataset

- `src/`  
  Python scripts that clean and combine the data  
  (you do not need to edit these)

- `notebooks/analysis.ipynb`  
  Notebook used to generate graphs

- `config.json`  
  **This is the only file you edit when using different data**

---

## Step 1: Install Python (Windows)

1. Go to https://www.python.org/downloads/
2. Download **Python 3** for Windows
3. During installation:
   - Check **“Add Python to PATH”**
   - Click Install
4. Restart your computer

---

## Step 2: Install required packages

1. Open **Command Prompt**  
   (Press `Windows + R`, type `cmd`, press Enter)

2. Navigate to the project folder (example):
    cd Documents\GitHub\gmo-ecological-trends

3. Install dependencies:
```bat
python -m pip install -r requirements.txt
```

Wait until installation finishes.

---

## Step 3: Add data files

1. Place raw data files into:
    data\raw\
    File names can be anything.

## Step 4: Select which data files to use

Open `config.json` in a text editor.

Example:
```bat
{
"ers_files": [
"data/raw/biotech-crops-all-tables-2024.csv"
],
"usgs_files": [
"data/raw/usgs_pesticide_use.txt"
],
"output_file": "data/processed/merged_ers_usgs.csv"
}
```

When you change data:
- Put new files in `data/raw/`
- Update file paths in `config.json`
- Save the file

---

## Step 5: Build the merged dataset

In Command Prompt:
```bat
python src\wrangle.py
```

If successful, you will see:
```bat
Saved merged dataset: (rows, columns)
```

A new file will appear in:
data\processed\merged_ers_usgs.csv

---

## Step 6: View graphs and analysis

1. In Command Prompt, run:
```bat
jupyter notebook
```
2. A browser window will open
3. Open: notebooks/analysis.ipynb
4. Click **Run All**

Graphs will appear in the notebook.

## If something goes wrong

- If Python says a package is missing, run:
python -m pip install -r requirements.txt

- If a file is not found:
  - Make sure it exists in `data/raw/`
  - Make sure the name matches `config.json` exactly

- If a login page appears, copy the URL with the token from the terminal into your browser.
---

## Important note

Every time you:
- change data files
- add new data
- use a different year

You must:
1. Update `config.json`
2. Re-run:
```bash
python src\wrangle.py
```