import pandas as pd
import numpy as np

def get_cumulative_stats(data, column):
    # groupby column and get cumulative sum
    groupby_counts = data.groupby(['date_added', column])['id'].count().reset_index().rename(columns={'id':'saved'}).sort_values(by='date_added')
    groupby_counts['cum_saved'] = groupby_counts.groupby(column)['saved'].cumsum()
    
    # Create a DataFrame to cover all dates for each name
    all_dates = pd.date_range(start=groupby_counts['date_added'].min(), end=groupby_counts['date_added'].max(), freq='D')
    all_names = groupby_counts[column].unique()
    idx = pd.MultiIndex.from_product([all_dates, all_names], names=['date_added', column])
    names_dates_cross_join = pd.DataFrame(index=idx).reset_index()
    
    # merge all dates with counts dataframe
    groupby_counts['date_added'] = pd.to_datetime(groupby_counts['date_added'])
    names_dates_cross_join['date_added'] = pd.to_datetime(names_dates_cross_join['date_added'])
    
    stats_all_dates = pd.merge(names_dates_cross_join, groupby_counts, on=['date_added', column], how='left')
    stats_all_dates['saved'] = stats_all_dates['saved'].fillna(0)
    
    stats_all_dates['cum_saved'] = stats_all_dates.groupby(column)['saved'].cumsum().astype('int')
    stats_all_dates = stats_all_dates.sort_values(by=['date_added', 'cum_saved', 'saved'], ascending=[True, False, True])  
    
    # get as % of total
    pivoted = stats_all_dates.pivot(index='date_added', columns=column, values='cum_saved')
    pivoted = pivoted.fillna(0.0)
    
    pivoted_pct = pivoted.div(pivoted.sum(axis=1), axis=0) * 100
    pivoted_pct.head()
    
    # convert to long df
    long = pivoted.reset_index().melt(id_vars=['date_added'], var_name=column, value_name='cum_saved')
    long_pct = pivoted_pct.reset_index().melt(id_vars=['date_added'], var_name=column, value_name='%')
    
    # merge % and totals and return final df
    long_df = pd.merge(long, long_pct, on=['date_added', column])

    return long_df


def get_bcr_df(df, name):
    df_bcr = df.copy()
    
    # keep values for end of month only
    months = pd.date_range(start=df_bcr['date_added'].min(), end=df_bcr['date_added'].max(), freq='ME')
    df_bcr = df_bcr[df_bcr['date_added'].isin(months)]
    
    df_bcr = df_bcr.pivot_table(index='date_added', columns=name, values='cum_saved')
    df_bcr = df_bcr.fillna(0)

    return df_bcr


def plot_bar_chart_race(df, filename, n_bars, title):
    bcr.bar_chart_race(
        df=df,
        filename=filename,
        orientation='h',
        sort='desc',
        n_bars=n_bars,
        fixed_order=False,
        fixed_max=False,
        interpolate_period=False,
        label_bars=True,
        bar_size=.95,
        period_label={'x': .99, 'y': .25, 'ha': 'right', 'va': 'center'},
        period_fmt='%B, %Y',
        figsize=(5, 3),
        dpi=144,
        cmap='dark12',
        title=title,
        title_size='',
        bar_label_size=7,
        tick_label_size=7,
        scale='linear',
        writer=None,
        fig=None,
        bar_kwargs={'alpha': .7},
        filter_column_colors=True
    )  