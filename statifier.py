import os
import matplotlib.pyplot as plt
import requests
import pandas as pd
import matplotlib.dates as mdates
import matplotlib as mpl

tautulli_token = os.getenv("TAUTULLI_TOKEN")


def __fetch_metadata_by_key(rating_key):
    base_url = "http://192.168.0.109:8181/api/v2?"

    response = requests.get(base_url, params={
        "apikey": tautulli_token,
        "cmd": "get_metadata",
        "rating_key": rating_key
    }).json()

    return response


def __history():
    base_url = "http://192.168.0.109:8181/api/v2?"

    records = True
    chunk_size = 100
    start = 0
    complete_data = []

    while records:
        chunk = requests.get(base_url, params={
            "apikey": tautulli_token,
            "cmd": "get_history",
            "user_id": "238358519",
            "length": chunk_size,
            "start": start
        }).json()

        data = chunk["response"]["data"]["data"]

        records = len(data) == chunk_size
        start += chunk_size
        print(f"Records: {start} {len(data)}")
        complete_data += data

    df_raw = pd.DataFrame(complete_data)
    df = df_raw[
        [
            'reference_id',
            'row_id',
            'id',
            'date',
            'started',
            'stopped',
            'duration',
            'play_duration',
            'paused_counter',
            'user_id',
            'user',
            'friendly_name',
            'platform',
            'product',
            'player',
            'ip_address',
            'location',
            'secure',
            'media_type',
            'full_title',
            'title',
            'parent_title',
            'grandparent_title',
            'year',
            'percent_complete',
            'watched_status',
            'rating_key',
            'parent_rating_key',
            'grandparent_rating_key'
        ]
    ]
    df = df[df['media_type'] != 'movie']
    df['date'] = pd.to_datetime(df['date'], unit='s')

    # Drop rows with missing values
    df = df.dropna()
    df.isna().sum()

    # Drop rows with missing values
    df = df.drop(df[df['full_title'] == '-'].index)
    df = df.drop(df[df['title'] == ''].index)

    return df


def get_global_stats():
    df = __history()

    total_play_duration = df['play_duration'].sum()
    # Convert seconds to hours, minutes and seconds
    h = total_play_duration // 3600
    m = (total_play_duration % 3600) // 60
    s = total_play_duration % 60

    total_plays = len(df)

    return (
        f"You listened for **{h}** hours **{m}** minutes and **{s}** "
        f"seconds spread over **{len(df['date'].dt.date.unique())}** days\n"
        f"That's an average of **{(total_play_duration / 3600) / len(df['date'].dt.date.unique()):.2f}** hours per day\n"
        f"You played a total of **{total_plays}** songs"
    )


def get_most_played(n):
    df = __history()

    title_type = "full_title"

    df_top = df.groupby(title_type).size().reset_index(name='counts')
    df_top['grandparent_title'] = df.groupby(title_type)['grandparent_title'].first().values
    df_top = df_top.sort_values('counts', ascending=False)

    top = ""

    for i in range(n):
        top += (f"**{df_top.iloc[i]['counts']}** plays of "
                f"**{df_top.iloc[i][title_type]}** by "
                f"**{df_top.iloc[i]['grandparent_title']}**\n")

    return f"\n{top}\n"


def get_most_played_artist(n):
    df = __history()

    title_type = "grandparent_title"

    df_top = df.groupby(title_type).size().reset_index(name='counts')
    df_top['rating_key'] = df.groupby(title_type)['rating_key'].first().values
    df_top = df_top.sort_values('counts', ascending=False)

    top = ""

    for i in range(n):
        top += (f"**{df_top.iloc[i]['counts']}** plays of "
                f"**{df_top.iloc[i][title_type]}**\n")

    return f"\n{top}\n"


def get_history_plot(n):
    df = __history()

    # Create a dataframe with all dates from the first play to today
    current_date = pd.to_datetime('today').date()
    df_date_range = pd.date_range(start='2024-01-01', end=current_date)
    df_date_range = pd.DataFrame(df_date_range, columns=['date'])

    df_date_grouped = df.groupby(df['date'].dt.date).size().reset_index(name='counts')
    df_date_grouped['date'] = pd.to_datetime(df_date_grouped['date'])
    df_date_grouped['counts'] = df_date_grouped['counts'].astype(int)

    df_plays_per_day = pd.merge(df_date_range, df_date_grouped, left_on='date', right_on='date', how='left')

    df_plays_per_day['counts'] = df_plays_per_day['counts'].fillna(0).astype(int)

    n_days = df_plays_per_day.nlargest(n, 'date')
    frequency: str

    # Make style dark
    plt.style.use('dark_background')
    mpl.rcParams['axes.spines.left'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = False

    plt.figure(figsize=(21, 9))
    if n < 33:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        frequency = 'day'
    elif n < 200:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())
        n_days = n_days.groupby(pd.Grouper(key='date', freq='W')).sum().reset_index()
        frequency = 'week'
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        n_days = n_days.groupby(pd.Grouper(key='date', freq='M')).sum().reset_index()
        frequency = 'month'

    plt.plot(n_days['date'], n_days['counts'], marker='o', color=(0.5, 0.55, 0.8))

    plt.title(f'Plays per {frequency}', color=(0.5, 0.55, 0.8))
    plt.xlabel('Date', color=(0.5, 0.55, 0.8))
    plt.ylabel('Plays', color=(0.5, 0.55, 0.8))

    # Make all background elements dark

    plt.xticks(rotation=45)
    plt.grid()
    plt.savefig('plays_per_day.png', dpi=300, bbox_inches='tight', facecolor=plt.gcf().get_facecolor())
    return 'plays_per_day.png'

