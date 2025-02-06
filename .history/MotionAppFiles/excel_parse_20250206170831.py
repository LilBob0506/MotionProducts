import pandas as pd

df = pd.read_excel("List.xlsx", nrows=1)
#nrows controls the number of rows to read

data = df[["[<ID>]", "ITEM_NO", "Part Number", "MFR_NAME"]].values.tolist()

print("data successfully read")