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

    date = data[date_col]
    target = data[target_col]

    return date, target


def plot_bear_market(date, target, target_name):
    fontsize = 14

    _, ax = plt.subplots()
    ax.plot(date, target)

    plt.title("Bear Market Analysis", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.show()


# for step 1
def group_date_per_8_month(date_sereis: pd.DataFrame | pd.Series):
    date = datetime_sereis_to_pereod_month(date_sereis)

    group_date = []
    current_idx = 0

    for i in range(date.size):
        if i > 0 and (i % 8 == 0 or i == date.size - 1):
            group_date.append(date[current_idx:i])
            current_idx = i

    return group_date


def pick_high_low_from_group_date(
    group_date: list[pd.Series], target: pd.DataFrame | pd.Series
):
    picked_group_date = []

    for i in range(len(group_date)):
        values: pd.Series = target.loc[group_date[i].index]
        min_idx = values.idxmin(axis="index")
        max_idx = values.idxmax(axis="index")

        picked_group_date.append(group_date[i].loc[[min_idx, max_idx]].sort_index())

    return picked_group_date


if __name__ == "__main__":
    target_name = "sp500"
    data = pd.read_csv("./Bear_Market.csv")

    date, target = df_to_date_target(data, target_name)

    group_date = group_date_per_8_month(date)
    picked_group_date = pick_high_low_from_group_date(group_date, target)

    new_date: pd.Series = date.loc[pd.concat([*picked_group_date], axis="index").index]
    new_target = target.loc[new_date.index]

    plot_bear_market(new_date, new_target, target_name)
