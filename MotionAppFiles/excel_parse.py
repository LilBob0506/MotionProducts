import pandas as pd

def get_entries(file_path):
    try:
        df = pd.read_excel(file_path)
        #For testing purposes, limit the number of rows to 10
        #df = pd.read_excel(file_path, nrows=10)
        if "MFR_NAME" in df.columns and "Part Number" in df.columns and "Product Description" and "[<ID>]" in df.columns:
            # Convert each row to a tuple (manufacturer, part_number, Product Description, [<ID>])
            entries = [tuple(row) for row in df[["MFR_NAME", "Part Number", "Product Description", "[<ID>]"]].dropna().values]
            return entries
        else:
            print("Required columns not found in the Excel file.")
            return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

if __name__ == "__main__":
    excel_file = input("Enter the Excel file path: ")  #Input file path as ~/Directory/fileName.xlsx
    entry = get_entries(excel_file)
    if entry:
        print(f"First entry: {entry}")
    else:
        print("No valid entries found.")
