import pandas as pd

# constants
impact_dir_30as = 'impact_30as'
impact_dir_15as = 'impact_15as'
impact_comparison_dir = 'impact_comparison'

# Define the columns that need suffixes
columns_to_suffix = ['population', 'loss', 'wind_cat', 'wind_cat_0', 'wind_cat_1', 'wind_cat_2', 'wind_cat_3',
                     'wind_cat_4', 'wind_cat_5']

# Loop over the administrative levels (0, 1, 2)
for i in range(3):
    # Dynamically load the corresponding CSV files
    df_30as = pd.read_csv(f'{impact_dir_30as}/impact_total_adm{i}_30as.csv')
    df_15as = pd.read_csv(f'{impact_dir_15as}/impact_total_adm{i}_15as.csv')

    # Rename the columns for 15as data to add '_15as' suffix
    df_15as.rename(columns={col: col + '_15as' for col in columns_to_suffix}, inplace=True)

    # Rename the columns for 30as data to add '_30as' suffix
    df_30as.rename(columns={col: col + '_30as' for col in columns_to_suffix}, inplace=True)

    # Merge the dataframes on the common columns (adjust this list based on your data)
    if i == 0:
        merge_columns = ['tc_season', 'atcf_id', 'storm_name', 'jtwc_start_time', 'jtwc_end_time', 'tech', 'adm0_name',
                         'adm0_code']
    elif i == 1:
        merge_columns = ['tc_season', 'atcf_id', 'storm_name', 'jtwc_start_time', 'jtwc_end_time', 'tech', 'adm0_name',
                         'adm0_code', 'adm1_name', 'adm1_code']
    else:
        merge_columns = ['tc_season', 'atcf_id', 'storm_name', 'jtwc_start_time', 'jtwc_end_time', 'tech', 'adm0_name',
                         'adm0_code', 'adm1_name', 'adm1_code', 'adm2_name', 'adm2_code']

    # Merge the corresponding dataframes
    merged_df = pd.merge(df_30as, df_15as, on=merge_columns, how='outer')

    # Create lists for 15as and 30as columns, in the exact order you need
    columns_15as = [col for col in columns_to_suffix if f'{col}_15as' in merged_df.columns]
    columns_30as = [col for col in columns_to_suffix if f'{col}_30as' in merged_df.columns]

    # Reorder the columns to have '_15as' and '_30as' columns next to each other
    final_column_order = merge_columns.copy()  # Start with the merge columns
    for col_15as, col_30as in zip(columns_15as, columns_30as):
        final_column_order.append(f'{col_15as}_15as')
        final_column_order.append(f'{col_30as}_30as')

    # Sort columns for each level as specified
    if i == 0:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code']
    elif i == 1:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code', 'adm1_code']
    elif i == 2:
        columns_order = ['tc_season', 'atcf_id', 'adm0_code', 'adm1_code', 'adm2_code']

    # Apply the new column order to the merged dataframe
    merged_df = merged_df[final_column_order].sort_values(by=columns_order)

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(f'{impact_comparison_dir}/impact_total_adm{i}_comparison.csv', index=False)

    # Optionally, print a message for each completed merge
    print(f"Saved: impact_total_adm{i}_comparison.csv")
