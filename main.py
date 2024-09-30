import matplotlib
import pandas as pd

matplotlib.use("GTK3Agg")

import matplotlib.pyplot as plt


def df_col_to_datetime(data: pd.DataFrame, date_col="date"):
    copy_data = data.copy()
    copy_data[date_col] = pd.to_datetime(copy_data[date_col])
    copy_data.sort_values(by=date_col, inplace=True, ascending=True)

    return copy_data


def df_to_date_target(data: pd.DataFrame, target_col, date_col="date"):
    copy_data = data.copy()
    copy_data = df_col_to_datetime(copy_data)

    copy_data: pd.DataFrame = copy_data.resample(rule="MS", on=date_col).sum()

    date: pd.Series = pd.Series(copy_data.index.to_series().tolist())
    target: pd.Series = pd.Series(copy_data[target_col].tolist())

    return date, target


def plot_bear_market(date, target, target_name):
    fontsize = 14

    _, ax = plt.subplots()
    ax.plot(date, target)

    plt.title("Bear Market Analysis", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.show()


# step 1


def init_turning_point(date: pd.Series, target: pd.Series):
    group_date = group_date_per_8_month(date)
    picked_group_date = pick_high_low_from_group_date(group_date, target)

    picked_date: pd.Series = date.loc[
        pd.concat([*picked_group_date], axis="index").index
    ]
    picked_target = target.loc[picked_date.index]

    return picked_date, picked_target


def group_date_per_8_month(date: pd.Series):
    copy_date = date.copy()

    group_date = []
    current_idx = 0

    for i in range(copy_date.size):
        if i > 0 and (i % 8 == 0 or i == copy_date.size - 1):
            group_date.append(copy_date[current_idx:i])
            current_idx = i

    return group_date


def pick_high_low_from_group_date(group_date: list[pd.Series], target: pd.Series):
    picked_group_date = []

    for i in range(len(group_date)):
        values: pd.Series = target.loc[group_date[i].index]
        min_idx = values.idxmin(axis="index")
        max_idx = values.idxmax(axis="index")

        picked_group_date.append(group_date[i].loc[[min_idx, max_idx]].sort_index())

    return picked_group_date


# step 2


# refer to https://stackoverflow.com/questions/49104226/pandas-find-turning-points
def force_turning_point(date: pd.Series, target: pd.Series):
    target = target.copy()

    if target.size < 2:
        raise IndexError("target size must >= 2")

    tp: pd.Series = pd.Series()
    pick_tp_idx = []

    # high -> low -> high
    if target.iloc[0] > target.iloc[1]:
        tp = (target.shift(-1) > target) & (target < target.shift(1))

        false_tp_idx = []

        for i in range(tp.size):
            if tp.iloc[i]:
                pick_tp_idx.append(target.loc[false_tp_idx].idxmax(axis="index"))
                pick_tp_idx.append(tp.index[i])
                false_tp_idx = []
            else:
                false_tp_idx.append(tp.index[i])

    # low -> high -> low
    elif target.iloc[0] < target.iloc[1]:
        tp = (target.shift(-1) < target) & (target > target.shift(1))

        false_tp_idx = []

        for i in range(tp.size):
            if tp.iloc[i]:
                pick_tp_idx.append(target.loc[false_tp_idx].idxmin(axis="index"))
                pick_tp_idx.append(tp.index[i])
                false_tp_idx = []
            else:
                false_tp_idx.append(tp.index[i])

    return date.loc[pick_tp_idx], target.loc[pick_tp_idx]


# step 3


def delete_start_end_6_month(date: pd.Series, target: pd.Series):
    pass


if __name__ == "__main__":
    target_name = "sp500"
    # target_name = "P_gold"
    data = pd.read_csv("./Bear_Market.csv")

    date, target = df_to_date_target(data, target_name)

    picked_date, picked_target = init_turning_point(date, target)

    date_turning_point, target_turning_point = force_turning_point(
        picked_date, picked_target
    )

    delete_start_end_6_month(date_turning_point, target_turning_point)

    # plot_bear_market(date, target, target_name)
    # plot_bear_market(picked_date, picked_target, target_name)
    plot_bear_market(date_turning_point, target_turning_point, target_name)
