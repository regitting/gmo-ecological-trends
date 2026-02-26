# GMO Ecological Trends – Technical Pipeline

This repository contains the technical and data-analysis portion of a BACSA research project.  
It combines GMO adoption data, pesticide use data, and soil erosion data, and produces graphs used in the report.

You do **not** need to know computer science to run this project, but the steps must be followed in order.

---

## What this project does

1. Reads GMO adoption data (USDA ERS)
2. Reads pesticide-use data (USGS)
3. Reads soil erosion data (USDA NRI)
4. Combines them into a cleaned panel dataset
5. Generates graphs and trends in Jupyter notebooks

---

## Folder overview

- `data/raw/`  
  Original data files (CSV or TXT).  
  These are **inputs** and should not be modified by the code.

- `data/processed/`  
  Automatically generated cleaned datasets  
  (do not edit manually).

- `data/analysis/`  
  Final collapsed datasets used for plotting and interpretation.

- `src/`  
  Python scripts that ingest, clean, and merge the data  
  (you do not need to edit these).

- `notebooks/`  
  Jupyter notebooks used to check data quality and generate graphs.

---

## Step 1: Install Python (Windows)

1. Go to https://www.python.org/downloads/
2. Download **Python 3**
3. During installation:
   - Check **“Add Python to PATH”**
   - Click **Install**
4. Restart your computer

---

## Step 2: Install required packages

1. Open **Command Prompt**  
   (Press `Windows + R`, type `cmd`, press Enter)

2. Navigate to the project folder (example):
```bat
cd Documents\GitHub\gmo-ecological-trends
```

3. Install dependencies
```bat
python -m pip install -r requirements.txt
```
Wait until installation finishes.

---

## Step 3: Build the cleaned datasets
In Command Prompt, run:
```bat
In Command Prompt, run:
```

If successful, cleaned files will be written to:

- `data/processed/`

- `data/analysis/`

You do not need to run individual scripts manually

---

## Step 4: View graphs and analysis

1. In Command Prompt, run:
```bat
jupyter notebook
```

2. A browser window will open

3. Open the notebooks in order:

- `01_sanity_check.ipynb`

- `02_trends.ipynb`

4. In each notebook, click Run All