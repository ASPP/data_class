import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

# ## Load data from clinical trial
# Data comes in two different files. The file `predimed_records.csv` file contains the
# clinical data for each patient, except which diet group they were assigned. The file
# `predimed_mapping.csv` contain the information of which patient was assigned to which diet group.
plt.style.use('/Users/verjim/laptop_D_17.01.2022/Schmitz_lab/teaching/ASPPLatAm_2026/data_class/exercises/tabular_join/presentation_plots.mplstyle')

#%%
def main():
    plot_performance()

def solve_2_for_loops(df, df_info):
    '''
    merges the two dataframes using two for loops
    '''

    # insert the column where info willbe stored
    df.insert(0, 'group_2_for_loops', '')

    for patient in df['patient-id'].unique():
        df_patient = df[df['patient-id'] == patient]
        for loc in df_patient['location-id']:
            row_df_info = df_info[(df_info['patient-id'] == patient) &
                                (df_info['location-id'] == loc)]
            if len(row_df_info) == 0:
                group = np.nan
            if len(row_df_info) == 1:
                group = row_df_info.group.values[0]
            indx_df = df[(df['patient-id'] == patient) &
                                (df['location-id'] == loc)].index.tolist()
            df.loc[indx_df, 'group_2_for_loops'] = group
    return df


def solve_1_for_loop(df, df_info):

    '''
    merges the two tables using 1 for loop and enumerate
    '''

    groups = []
    for i, patient in enumerate(df['patient-id']):
        loc = df['location-id'][i]
        row_df_info = df_info[(df_info['patient-id'] == patient) &
                                (df_info['location-id'] == loc)]
        if len(row_df_info) == 0:
            group = np.nan
        if len(row_df_info) == 1:
            group = row_df_info.group.values[0]
        if len(row_df_info) > 1:
            print(f'error repeated rows for patient {patient} at {loc}')

        groups.append(group)
    df.insert(1, 'group', groups)
    return df


def solve_1_line(df, df_info):
    '''
    merges the two dataframes using a built-in pandas function
    '''
    df_with_info = df.merge(df_info, on = ['patient-id', 'location-id'], how = 'left')
    return df_with_info


def repeat_dataframe(df, n):
    '''
    repeats the dataframe n-number of times
    '''
    big_df = pd.concat([df] * n, ignore_index=True)
    return big_df


def get_performance(func, num_repeats):

    '''
    returns the number of repetitions and the time it takes to merge using
    the function func
    '''
    df = pd.read_csv('../../data/predimed_records.csv')
    df_info = pd.read_csv('../../data/predimed_mapping.csv')

    times = []

    for i in range(0, num_repeats+1):
        if i == 0:
            times.append(0)
            continue
        big_df = repeat_dataframe(df, i)

        start = time.perf_counter()
        _ = func(big_df, df_info)
        # put out in ms
        times.append((time.perf_counter() - start) * 1000)

    return list(range(0, num_repeats+1)), times

def plot_performance(num_repeats = 32):
    '''
    plots the performance of the three functions
    '''

    funcs_dict = {
        'O(n*m + n^2)': [solve_2_for_loops, 'purple'],
        'O(n * m)': [solve_1_for_loop, 'green'],
        'O (n + m)': [solve_1_line, 'orange']
    }

    fig, ax = plt.subplots(1,1, figsize = (6, 5))

    for method_name, detail in funcs_dict.items():
        func = detail[0]
        col = detail[1]
        repeats, times = get_performance(func, num_repeats)
        ax.plot(repeats, times, label = method_name, color = col)
        ax.scatter(repeats, times, color = col)

    ax.set_xlabel('Input size')
    ticks_ = np.arange(0, num_repeats, 2)
    labels_ = [f'{a}x' for a in ticks_]
    ax.set_xticks(ticks_, labels_)
    ax.set_ylabel('Time (ms)')
    plt.savefig('plot_performance_tabular.png')
    plt.show()

if __name__ == "__main__":
    main()



# %%
