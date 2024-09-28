import matplotlib
import pandas as pd

matplotlib.use("GTK3Agg")

import matplotlib.pyplot as plt


def series_to_datetime(data: pd.DataFrame, date_col="date"):
    data[date_col] = pd.to_datetime(data[date_col])
    data.sort_values(by=date_col, inplace=True, ascending=True)

    return data


def datetime_sereis_to_pereod_month(date_sereis: pd.DataFrame | pd.Series):
    return date_sereis.dt.to_period(freq="M")


def df_to_date_target(data: pd.DataFrame, target_col, date_col="date"):
    data = series_to_datetime(data)

    data[date_col] = datetime_sereis_to_pereod_month(data[date_col])
    date = data[date_col]

    target = data[target_col]

    return date, target


def plot_bear_market(date, target, target_name):
    fontsize = 14

    fig, ax = plt.subplots()
    ax.plot(date, target)

    plt.title("Bear Market Analysis", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.show()


# for step 1
def group_date_per_8_month(date_sereis: pd.DataFrame | pd.Series):
    group_date = []
    current_idx = 0

    for i in range(date_sereis.size):
        if i > 0 and (i % 8 == 0 or i == date_sereis.size - 1):
            group_date.append(date_sereis[current_idx:i])
            current_idx = i

    return group_date


if __name__ == "__main__":
    target_name = "sp500"
    data = pd.read_csv("./Bear_Market.csv")

    date, target = df_to_date_target(data, target_name)

    print(date)

    group_date = group_date_per_8_month(date)

    print(group_date)
    print(target.iloc[group_date[0].index])

    # plot_bear_market(date, target, target_name)
