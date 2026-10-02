import pandas as pd
from datetime import datetime

def load_data(path):
    """
    The method reads the data set from a csv file and uploads the information to the main memory.
    :param path: path is the full path to the file (at the end of which is the file name).
    :return data: The output of the method is the df that has been created.
    """
    data = pd.read_csv(path)
    return data


def map_season_name(season):
    """
    this method gets a String 1 of 4 seasons
    :returns 0 if its spring, 1 summer , 2 fall, 3 winter
    """
    season_names = ['spring', 'summer', 'fall', 'winter']
    return season_names[season]


def calculate_is_weekend_holiday(row):
    """
    this method gets a row from the df and checks the value in the
    'is_holiday' 'is_weekend' column and returns the asked value.
    """
    is_weekend_holiday = 0
    if row['is_holiday'] == 1:
        is_weekend_holiday += 2
    if row['is_weekend'] == 1:
        is_weekend_holiday += 1
    return is_weekend_holiday


def calculate_t_diff(row):
    """
    this method gets a row from the df and substracts the value
    of the data on 't1' from 't2' column
    """
    return row['t2'] - row['t1']


def add_new_columns(df):
    """
    The method adds a column named season_name using the pandas apply function on the season column. values
    The column is the names of the seasons according to the season numbers given in the season column
    Adds a column called is_weekend_holiday using pandas' apply on the columns
    is_holiday and is_weekend .
    Adds a column named t_diff using the pandas apply command on columns t1 and t2. The column value will be
    The difference between t2 and t1.
    """
    df['season_name'] = df['season'].apply(map_season_name)
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    df['Hour'] = df['timestamp'].apply(lambda timestamp: timestamp.hour)
    df['Day'] = df['timestamp'].apply(lambda timestamp: timestamp.day)
    df['Month'] = df['timestamp'].apply(lambda timestamp: timestamp.month)
    df['Year'] = df['timestamp'].apply(lambda timestamp: timestamp.year)
    df['is_weekend_holiday'] = df.apply(calculate_is_weekend_holiday, axis=1)
    df['t_diff'] = df.apply(calculate_t_diff, axis=1)


def data_analysis(df):
    """
    The method shows the five pairs of features that
    differ from each other with the highest and lowest correlation in absolute value
    By first calculating all correlation pairs between
    all features and finally displaying it
    In addition, it displays the average t_diff column value
    for each season_name using the groupby command, and in addition the
    average for all records.
    """
    print("describe output:")
    print(df.describe().to_string())
    print()
    print("corr output:")
    numeric_columns = df.select_dtypes(include='number')
    corr = numeric_columns.corr()
    print(corr.to_string())
    print()
    correlation_dict = {}
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            feature_1 = corr.columns[i]
            feature_2 = corr.columns[j]
            correlation_dict[(feature_1, feature_2)] = abs(corr.loc[feature_1, feature_2])
    highest_correlated = sorted(correlation_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    lowest_correlated = sorted(correlation_dict.items(), key=lambda x: x[1])[:5]
    print("Highest correlated are: ")
    for i, (features, correlation) in enumerate(highest_correlated):
        print(f"{i+1}. {features} with {correlation:.6f}")
    print("\nLowest correlated are: ")
    for i, (features, correlation) in enumerate(lowest_correlated):
        print(f"{i+1}. {features} with {correlation:.6f}")
    season_average_t_diff = df.groupby('season_name')['t_diff'].mean()
    all_average_t_diff = df['t_diff'].mean()
    print()
    for season, avg_t_diff in season_average_t_diff.items():
        print(f"{season} average t_diff is {avg_t_diff:.2f}")
    print(f"All average t_diff is {all_average_t_diff:.2f}")