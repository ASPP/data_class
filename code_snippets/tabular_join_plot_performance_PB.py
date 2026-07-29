import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

# ## Load data from clinical trial
# Data comes in two different files. The file `predimed_records.csv` file contains the
# clinical data for each patient, except which diet group they were assigned. The file
# `predimed_mapping.csv` contain the information of which patient was assigned to which diet group.
plt.style.use('presentation_plots.mplstyle')

# s_a_c for split-apply-combine

#%%
def main():
    join_plot_performance(num_repeats = 32)
    # s_a_c_plot_performance()

def join_solve_2_for_loops(df_patients, df_locations):
    '''
    merges the two dataframes using two for loops
    '''

    patients_with_city = df_patients.copy()
    patients_with_city['city_2_for_loops'] = 'n/a'

    for idx, row in patients_with_city.iterrows():  # O(N)
        location = row['location-id']
        matching_city = [r['location-id'] == location for _, r in df_locations.iterrows()]
        city = df_locations.loc[matching_city, 'city']
        if len(city) > 0:
            patients_with_city.loc[idx, 'city'] = city.iloc[0]
    return patients_with_city


def join_solve_with_sorting(df_patients, df_locations):

    '''
    merges the two tables using 1 for loop and enumerate
    '''
    patients_with_city = df_patients.copy()
    patients_with_city['city_with_sort'] = 'n/a'

    sorted_patients = patients_with_city.sort_values(['location-id'])   # O(N log N)
    sorted_locations = df_locations.sort_values(['location-id'])           # O(M log M)

    city_2_col = sorted_patients.columns.get_loc('city_with_sort') # get the column location (number)
    locations_idx = 0
    patients_idx = 0

    while True:    # O(N + M)
        row_locations = sorted_locations.iloc[locations_idx]
        key_locations = row_locations['location-id']

        row_patients = sorted_patients.iloc[patients_idx]
        key_patients = row_patients['location-id']

        if key_patients == key_locations:
            original_idx = sorted_patients.index[patients_idx]
            patients_with_city.iloc[original_idx, city_2_col] = row_locations['city']
            patients_idx += 1
        else:
            locations_idx += 1
            if locations_idx >= len(sorted_locations):
                break
        if patients_idx >= len(sorted_patients):
            break
    return patients_with_city


def join_solve_1_line(df_patients, df_locations):
    '''
    merges the two dataframes using a built-in pandas function
    '''
    patients_with_city = df_patients.merge(df_locations, on = ['location-id'], how = 'left')
    return patients_with_city


def repeat_dataframe(df, n):
    '''
    repeats the dataframe n-number of times
    '''
    big_df = pd.concat([df] * n, ignore_index=True)
    return big_df


def join_get_performance(func, num_repeats):

    '''
    returns the number of repetitions and the time it takes to merge using
    the function func
    '''

    times = []

    for i in range(0, num_repeats+1):
        if i == 0:
            times.append(0)
            continue

        # create artificial data with increasing size
        M = 10 * i
        a = 5
        N = M * a
        big_df = pd.DataFrame({'location-id': list(range(M)) * a,
            'blah': np.random.randint(0, 1000, size=(N,))}).sample(frac=1).reset_index(drop=True)
        big_df_info = pd.DataFrame({'location-id': list(range(M)),
            'city': list(str(x) for x in range(M))}).sample(frac=1).reset_index(drop=True)

        start = time.perf_counter()
        _ = func(big_df, big_df_info)
        # put out in ms
        times.append((time.perf_counter() - start) * 1000)

    return list(range(0, num_repeats+1)), times

def join_plot_performance(num_repeats = 32):
    '''
    plots the performance of the three functions
    '''

    save_dir_plots = '.'

    funcs_dict = {
        'O(N*M)': [join_solve_2_for_loops, 'purple'],
        'O(N log N + M log M)': [join_solve_with_sorting, 'green'],
        'O(n+m)': [join_solve_1_line, 'orange']
    }

    fig, ax = plt.subplots(1,1, figsize = (6, 5))

    for method_name, detail in funcs_dict.items():
        func = detail[0]
        col = detail[1]
        repeats, times = join_get_performance(func, num_repeats)
        ax.plot(repeats, times, label = method_name, color = col)
        ax.scatter(repeats, times, color = col)

    ax.set_xlabel('Input size')
    ticks_ = np.arange(0, num_repeats, 2)
    labels_ = [f'{a}x' for a in ticks_]
    ax.set_xticks(ticks_, labels_)
    ax.set_ylabel('Time (ms)')
    plt.savefig(f'{save_dir_plots}plot_performance_tabular_location.png')
    plt.savefig(f'{save_dir_plots}plot_performance_tabular_location.svg',
            format='svg', bbox_inches='tight', dpi=300)
    plt.show()


def s_a_c_nested_for_loop(df_patients):
    '''
    using this solution of calculation just for visualization. Never to be used irl.
    returns: dictionary with groups as keys and count of cardiovascualr events as values
    '''
    # change events to int
    df_patients['event_int'] = df_patients['event'].map({'Yes': 1, 'No': 0})

    events_nested = {}
    for group in df_patients['group'].unique():
        total = 0
        for event, group_label in zip(df_patients['event_int'], df_patients['group']):
            if group_label == group:
                total += event
        events_nested[group] = total

    return events_nested


def s_a_c_row_iteration(df_patients):
    '''
    iterates through rows to get eh number of cardiovascular events per diet group
    returns: dictionary with groups as keys and count of cardiovascualr events as values
    '''
    # change events to int
    df_patients['event_int'] = df_patients['event'].map({'Yes': 1, 'No': 0})

    events_rows = {}
    for i, row in df_patients.iterrows():
        group = row['group']
        event = row['event_int'] # 1 or 0
        if group not in events_rows:
            events_rows[group] = 0
        events_rows[group] += event

    return events_rows

def s_a_c_one_line(df_patients):
    '''
    usees built-in pandas functions (groupby) to get the number of cardiovascular events
    per diet group
    returns: pandas series
    '''

    events_groupby = df_patients.groupby('group')['event'].sum()
    return events_groupby


def s_a_c_get_performance(func, num_repeats):

    '''
    returns the number of repetitions and the time it takes to merge using
    the function func
    '''
    df_data = '../../data'
    df = pd.read_csv(f'{df_data}/processed_data_predimed.csv')

    times = []

    for i in range(0, num_repeats+1):
        if i == 0:
            times.append(0)
            continue
        big_df = repeat_dataframe(df, i)

        start = time.perf_counter()
        _ = func(big_df)
        # put out in ms
        times.append((time.perf_counter() - start) * 1000)

    return list(range(0, num_repeats+1)), times

def s_a_c_plot_performance(num_repeats = 33):
    '''
    plots the performance of the three functions
    '''

    save_dir_plots = '.'

    funcs_dict = {
        'O(N*G)': [s_a_c_nested_for_loop, 'purple'],
        'O(N) + Series object': [s_a_c_row_iteration, 'green'],
        'O(N)': [s_a_c_one_line, 'orange']
    }

    fig, ax = plt.subplots(1,1, figsize = (6, 5))

    for method_name, detail in funcs_dict.items():
        func = detail[0]
        col = detail[1]
        repeats, times = s_a_c_get_performance(func, num_repeats)
        ax.plot(repeats, times, label = method_name, color = col)
        ax.scatter(repeats, times, color = col)

    ax.set_xlabel('Input size')
    ticks_ = np.arange(0, num_repeats, 2)
    labels_ = [f'{a}x' for a in ticks_]
    ax.set_xticks(ticks_, labels_)
    ax.set_ylabel('Time (ms)')
    plt.savefig(f'{save_dir_plots}plot_performance_s_a_c.png')
    plt.savefig(f'{save_dir_plots}plot_performance_s_a_c.svg',
            format='svg', bbox_inches='tight', dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
