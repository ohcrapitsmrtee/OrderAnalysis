import streamlit as st
import pandas as pd

def parse_time_column(time_series):
    parsed_times = pd.to_datetime(time_series, errors='coerce', format='%I:%M:%S %p').dt.time
    if parsed_times.isnull().any():
        parsed_times = pd.to_datetime(time_series, errors='coerce', format='%H:%M').dt.time
    return parsed_times

def process_csv(file):
    df = pd.read_csv(file)

    # Remove the first six rows
    df_cleaned = df.iloc[6:].reset_index(drop=True)

    # Set the correct header row
    df_cleaned.columns = df_cleaned.iloc[2]
    df_cleaned = df_cleaned.drop([0, 1, 2]).reset_index(drop=True)

    # Updated list of items to remove
    items_to_remove = [
        "*0.9%NS 1000cc",
        "*0.9%NS 250 mL",
        "*0.9%NS 500cc",
        "Alpha Lipoic Acid (ALA)",
        "Ascorbic Acid",
        "Ascorbic Acid (Vit C)",
        "Ascorbic Acid (Vit C) - Cisplatin Bag 1",
        "Ascorbic Acid (Vit C) 1",
        "Ascorbic Acid (Vit C) -Bag #1 Vitamin",
        "Ascorbic Acid (Vit C) IV",
        "Calcium Gluconate 1000 mg/ 10 mL",
        "Dexamethasone",
        "Dexamethasone Inj (Decadron, Dexa)",
        "Dexamethasone Inj (Decadron, Dexa) 4-8 mg",
        "Dexamethasone Inj (Decadron, Dexa)- Admix",
        "Dexamethasone Inj-Admix",
        "Dexamethasone-Admix",
        "Diphenhydramine (Benadryl) IVP",
        "Diphenhydramine HCl injection (Benadryl) 25-50 mg",
        "Famotidine (Pepcid)",
        "Famotidine (Pepcid) - Admix",
        "Famotidine (Pepcid)-Admix",
        "Magnesium Sulfate",
        "Magnesium Sulfate - Bag #1 Vitamin",
        "Magnesium Sulfate - Cis",
        "Magnesium Sulfate - Vit",
        "Magnesium Sulfate 1",
        "Magnesium Sulfate Bag#1",
        "Magnesium Sulfate BAG#2",
        "Magnesium Sulfate IV",
        "Magnesium Sulfate-Vit",
        "Palonosetron (Aloxi)",
        "Palonosetron (Aloxi) - Admix",
        "Palonosetron (Aloxi)-Admix",
        "Pepcid",
        "Sterile Water",
        "Sterile Water IV"
        "Atropine"
    ]

    # Filter out rows with specified items in the 'sComponentName_1' column
    df_filtered = df_cleaned.loc[~df_cleaned['sComponentName_1'].isin(items_to_remove)].copy()

    # Split 'OrderDateTime' into 'OrderDate' and 'Time'
    if 'OrderDateTime' in df_filtered.columns:
        df_filtered[['OrderDate', 'Time']] = df_filtered['OrderDateTime'].str.split(' ', n=1, expand=True)
        df_filtered = df_filtered.drop(columns=['OrderDateTime'])

    # Split 'LastDoseDate' into 'LastDoseDate' and 'LastDoseTime'
    if 'LastDoseDate' in df_filtered.columns:
        df_filtered[['LastDoseDate', 'LastDoseTime']] = df_filtered['LastDoseDate'].str.split(' ', n=1, expand=True)

    # Split 'NextDoseDate' into 'NextDoseDate' and 'NextDoseTime'
    if 'NextDoseDate' in df_filtered.columns:
        df_filtered[['NextDoseDate', 'NextDoseTime']] = df_filtered['NextDoseDate'].str.split(' ', n=1, expand=True)

    # Convert 'OrderDate', 'LastDoseDate', and 'NextDoseDate' to datetime for sorting
    df_filtered['OrderDate'] = pd.to_datetime(df_filtered['OrderDate'], errors='coerce').dt.date
    df_filtered['LastDoseDate'] = pd.to_datetime(df_filtered['LastDoseDate'], errors='coerce').dt.date
    df_filtered['NextDoseDate'] = pd.to_datetime(df_filtered['NextDoseDate'], errors='coerce').dt.date

    # Convert 'Time', 'LastDoseTime', and 'NextDoseTime' to time format for sorting
    df_filtered['Time'] = parse_time_column(df_filtered['Time'])
    df_filtered['LastDoseTime'] = parse_time_column(df_filtered['LastDoseTime'])
    df_filtered['NextDoseTime'] = parse_time_column(df_filtered['NextDoseTime'])

    # Combine 'OrderDate' and 'Time' into a single datetime column for sorting
    df_filtered['OrderDateTime'] = df_filtered.apply(
        lambda row: pd.to_datetime(f"{row['OrderDate']} {row['Time']}", errors='coerce'), axis=1
    )

    # Calculate the difference in days and convert to weeks
    df_filtered['WeekSinceLastDose'] = (df_filtered['OrderDate'] - df_filtered['LastDoseDate']).dt.days / 7

    # Define the order of columns to keep
    columns_to_keep = [
        'patientname', 'mrn', 'DateofBirth', 'OrderDate', 'Time', 'RegimenName',
        'sComponentName_1', 'orderedamount', 'orderedunits', 'LastDoseDate', 
        'LastDose', 'CrCl', 'CREAT_Result', 'WeekSinceLastDose'
    ]

    # Sort by 'mrn' and 'OrderDateTime'
    df_filtered = df_filtered.sort_values(by=['mrn', 'OrderDateTime'], kind='mergesort')

    # Reorder the DataFrame to keep only the specified columns
    df_reordered = df_filtered[columns_to_keep]

    return df_reordered

def main():
    st.title("Order Analysis App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        processed_df = process_csv(uploaded_file)
        st.dataframe(processed_df)

        # Option to download the processed file
        st.download_button(
            label="Download Processed CSV",
            data=processed_df.to_csv(index=False).encode('utf-8'),
            file_name='processed_orders.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
