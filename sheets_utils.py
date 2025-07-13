import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def get_gsheet(sheet_name, worksheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("e-collector-465806-q3-e4ed16826fb7.json", scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open(sheet_name)
    worksheet = sh.worksheet(worksheet_name)
    return worksheet

def read_sheet_to_df(sheet_name, worksheet_name):
    worksheet = get_gsheet(sheet_name, worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def write_df_to_sheet(df, sheet_name, worksheet_name):
    worksheet = get_gsheet(sheet_name, worksheet_name)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())