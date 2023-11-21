import os
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


header = [                   # Replace with your actual column headers
    "start_date", "end_date", "total_days", "profit_days", "loss_days",
    "capital", "end_balance", "max_drawdown", "max_ddpercent",
    "max_drawdown_duration", "total_net_pnl", "daily_net_pnl",
    "total_commission", "daily_commission", "total_slippage",
    "daily_slippage", "total_turnover", "daily_turnover",
    "total_trade_count", "daily_trade_count", "total_return",
    "annual_return", "daily_return", "return_std", "sharpe_ratio",
    "return_drawdown_ratio", "name"
    ]
def concatenate_csv_files(nPoints_list, timeframe, directory_path):
    """
    Concatenate CSV files based on a list of nPoints and a single timeframe.

    :param nPoints_list: List of points to filter by in the filename.
    :param timeframe: Time frame to filter by in the filename.
    :param directory_path: Path to the directory containing the CSV files.
    :return: Concatenated DataFrame of all matching CSV files.
    """
    # List to hold data from each matching CSV
    data_frames = pd.DataFrame(columns=header)

    # Iterate over all files in the directory
    for file in os.listdir(directory_path):
        if file.endswith(".csv"):
            # Check if file matches any of the nPoints values in the list
            if any(f"nPoints_{nPoints}_timeframe_{timeframe}" in file for nPoints in nPoints_list):
                file_path = os.path.join(directory_path, file)
                df = pd.read_csv(file_path,names=header, header=None)
                data_frames = data_frames.append(df,ignore_index=True)

    # Concatenate all the dataframes if the list is not empty
    data_frames.reset_index(inplace=True)
    return data_frames

def find_best_sharpe_ratio(df):
    """
    Find the 'name' and 'total_trade_count' with the maximum 'sharpe_ratio' from the DataFrame.

    :param df: DataFrame containing the performance metrics.
    :return: A dictionary with the 'name' and 'total_trade_count' of the best sharpe_ratio.
    """
    # Find the row with the maximum 'sharpe_ratio'
    best_row = df.loc[df['sharpe_ratio'].idxmax()]

    # Extract the 'name' and 'total_trade_count'
    best_name = best_row['name']
    best_trade_count = best_row['total_trade_count']

    print({'name': best_name, 'total_trade_count': best_trade_count, "sharpe_ratio": best_row['sharpe_ratio']})

# Example usage:
insID = ["BTCUSDT", "ETHUSDT"]
year = ["2021", "2122", "2223"]
directory_path = f'/Users/huangxuanhao/{insID[0]}/backtest_results{year[1]}/statistics/'  # Replace with the correct directory path
nPoints_list = [13,21,34,55,89,144,233,377,610,987,1597]  # Replace with the actual list of nPoints you want to use
timeframe = [5, 15, 30, 45, 60, 120, 240]  # Replace with the actual timeframe you're interested in

# Call the function and get the concatenated DataFrame
for time in timeframe:
    concatenated_df = concatenate_csv_files(nPoints_list, time, directory_path)
    find_best_sharpe_ratio(concatenated_df)
