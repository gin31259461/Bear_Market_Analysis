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

    plt.title("Bear Market Plot", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.show()


def plot_bear_market_step(date, target, target_name):
    fontsize = 14

    plt.step(date, target)
    plt.title("Bear Market Binary Plot", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.show()


def save_bear_market_step(date, target, target_name):
    fontsize = 14

    plt.clf()
    plt.step(date, target)
    plt.title("Bear Market Analysis", fontsize=fontsize + 4)
    plt.xlabel("timestamp", fontsize=fontsize)
    plt.ylabel(target_name, fontsize=fontsize)
    plt.savefig(f"./result/figures/{target_name}.png")


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
        raise UnboundLocalError("target size must >= 2")

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

        if len(false_tp_idx) > 0:
            pick_tp_idx.append(target.loc[false_tp_idx].idxmax(axis="index"))

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

        if len(false_tp_idx) > 0:
            pick_tp_idx.append(target.loc[false_tp_idx].idxmin(axis="index"))

    return date.loc[pick_tp_idx], target.loc[pick_tp_idx]


# step 3
def delete_start_end_6_month(date: pd.Series, target: pd.Series):
    if date.size < 12:
        raise UnboundLocalError("date and target size must >= 12")

    copy_date: pd.Series = date.iloc[7 : date.size - 6]
    copy_target: pd.Series = target.iloc[7 : date.size - 6]

    copy_date, copy_target = force_turning_point(copy_date, copy_target)

    return copy_date, copy_target


# step 4
# high low high ...
# NaT  NaT high low high ... (shift -> 2)
def delete_period_less_than_16_month(date: pd.Series, target: pd.Series):
    pick_rule: pd.Series = pd.Series()
    copy_date = date.copy()
    copy_target = target.copy()

    while True:
        diff_period = copy_date.dt.to_period("M").astype(int) - copy_date.dt.to_period(
            "M"
        ).astype(int).shift(2)

        pick_rule = (diff_period <= 16).astype(int)

        period_less_than_16_month: pd.Series = pick_rule.loc[pick_rule == 1]

        # break loop until not period less than 16 month occur
        if period_less_than_16_month.size == 0:
            break

        # pick first period less than 16 month to delete
        copy_date: pd.Series = copy_date.loc[
            copy_date.index != period_less_than_16_month.index[0]
        ]
        copy_target: pd.Series = copy_target.loc[copy_date.index]

        # then force turning point again
        copy_date, copy_target = force_turning_point(copy_date, copy_target)

    pick_idx = pick_rule.index

    return date.loc[pick_idx], target.loc[pick_idx]


# step 5
def delete_half_period_less_than_4_month(date: pd.Series, target: pd.Series):
    pick_rule: pd.Series = pd.Series()
    copy_date = date.copy()
    copy_target = target.copy()

    while True:
        diff_period = copy_date.dt.to_period("M").astype(int) - copy_date.dt.to_period(
            "M"
        ).astype(int).shift(1)

        diff_value_change = (copy_target - copy_target.shift(1)) / copy_target.shift(1)

        pick_rule = ((diff_period < 4) & (diff_value_change <= 0.2)).astype(int)

        half_period_less_than_4_month: pd.Series = pick_rule.loc[pick_rule == 1]

        # break loop until not period less than 4 month occur
        if half_period_less_than_4_month.size == 0:
            break

        # pick first period less than 4 month to delete
        copy_date: pd.Series = copy_date.loc[
            copy_date.index != half_period_less_than_4_month.index[0]
        ]
        copy_target: pd.Series = copy_target.loc[copy_date.index]

        # then force turning point again
        # copy_date, copy_target = force_turning_point(copy_date, copy_target)

    pick_idx = pick_rule.index

    return date.loc[pick_idx], target.loc[pick_idx]


def target_to_binary_series(target: pd.Series):
    binary_target = target - target.shift(1)
    binary_target = (binary_target > 0).astype(int)

    if target.iloc[0] > target.iloc[1]:
        binary_target.iloc[0] = 1

    return binary_target


if __name__ == "__main__":
    date_col = "date"
    data = pd.read_csv("./data/Bear_Market.csv")
    target_names = data.columns.drop(date_col).tolist()

    for target_name in target_names:
        date, target = df_to_date_target(data, target_name)

        picked_date, picked_target = init_turning_point(date, target)

        date_turning_point, target_turning_point = force_turning_point(
            picked_date, picked_target
        )

        date_turning_point, target_turning_point = delete_start_end_6_month(
            date_turning_point, target_turning_point
        )

        date_turning_point, target_turning_point = delete_period_less_than_16_month(
            date_turning_point, target_turning_point
        )

        final_date, final_target = delete_half_period_less_than_4_month(
            date_turning_point, target_turning_point
        )

        binary_target = target_to_binary_series(final_target)

        save_bear_market_step(final_date, binary_target, target_name)

        final_binary_step_df = pd.DataFrame(
            {
                "date": final_date,
                f"{target_name}_value": final_target,
                f"{target_name}_binary": binary_target,
            }
        )

        final_binary_step_df.to_csv(f"./result/data/{target_name}.csv", index=False)

        # plot_bear_market(date, target, target_name)
        # plot_bear_market(picked_date, picked_target, target_name)
        # plot_bear_market(date_turning_point, target_turning_point, target_name)
        # plot_bear_market(final_date, final_target, target_name)
        # plot_bear_market_step(final_date, binary_target, target_name)
