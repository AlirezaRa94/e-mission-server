import emission.core.get_database as edb
import emission.net.ext_service.push.notify_usage as pnu
import pandas as pd
import logging
import calendar
from itertools import count, groupby


def get_unlabelled_confirmed_trips():
    query_result = edb.get_analysis_timeseries_db().find(
        # query
        {'$and':
            [
                {'metadata.key': 'analysis/confirmed_trip'},
                {'data.user_input.trip_user_input': {'$exists': False}}
            ]
         },
        # fields to extract
        {
            "_id": 0,
            "user_id": 1,
            "trip_start_time_str": "$data.start_fmt_time",
            "trip_start_time_tz": "$data.start_local_dt.timezone",
            "travel_modes": "$data.user_input.trip_user_input.data.jsonDocResponse.data.travel_mode"
        }
    )
    return (pd.DataFrame(list(query_result)))


def add_date_columns(df):
    df = df.assign(trip_start_time = lambda df: pd.to_datetime(df['trip_start_time_str'], errors='coerce', utc=True))
    df['trip_start_time_local'] = df.apply(lambda x: x['trip_start_time'].tz_convert(x['trip_start_time_tz']), axis=1)
    df['trip_start_day'] = [x.day for x in df.reset_index()['trip_start_time_local']]
    df['trip_start_month'] = [x.month for x in df.reset_index()['trip_start_time_local']]
    df['trip_start_year'] = [x.year for x in df.reset_index()['trip_start_time_local']]

    return (df)


def summarise_label_daysK(x):
    return (pd.Series({'dates': [x['trip_start_day']]}))


def summarise_label_stats(x):
    return (pd.Series({'dates': [x['trip_start_day']]}))


def re_range(L):
    G = (list(x) for _, x in groupby(sorted(L), lambda x, c=count(): next(c)-x))
    return (G)


def concat_rr(G):
    return (', '.join(["-".join(map(str, (g[0], g[-1])[:len(g)])) for g in G]))


def summarise_data(df):
    df2 = (
        df
        .copy()
        .groupby(['user_id', 'trip_start_month', 'trip_start_year'])
        .apply(lambda x:
               pd.Series(
                   {
                       'n_unlabelled_trips': len(x),
                       'dates': list(set(x['trip_start_day'])),
                       'dates_str': concat_rr(re_range(list(set(x['trip_start_day']))))
                   }
               )
               )
        .reset_index()
        .assign(month_str=lambda df: [calendar.month_abbr[i] for i in df['trip_start_month']])
        .assign(year_str=lambda df: [str(i) for i in df['trip_start_year']])
        .groupby(['user_id', 'trip_start_year'])
        .apply(lambda df:
               pd.Series(
                   {
                       'msg': ' and '.join(df['dates_str'] + ' of ' + df['month_str']),
                       'year_str': ''.join(list(set(df['year_str']))),
                       'n_unlabelled_trips': sum(df['n_unlabelled_trips'])
                   }
               )
               )
        .reset_index()
        .assign(msg=lambda df: df['msg'] + ' ' + df['year_str'])
        .groupby(['user_id'])
        .apply(lambda df:
               'You have ' + str(sum(df['n_unlabelled_trips'])) + (' trips' if sum(df['n_unlabelled_trips']) > 1 else ' trip') +
               ' without details on ' +
               ' & '.join(df['msg']) + '. Add details to all your trips to earn your full incentive.')
        .reset_index(name='msg')
    )
    return (df2)


# ./e-mission-py.bash bin/push/label_reminder_push_v2.py
if __name__ == "__main__":
    logging.info("Querying unlabelled confirmed trips")
    unlabelled_confirmed_trips = get_unlabelled_confirmed_trips()
    unlabelled_confirmed_trips = add_date_columns(unlabelled_confirmed_trips)
    summ_table = summarise_data(unlabelled_confirmed_trips)
    # print(summ_table)

    for _uuid, msg in zip(summ_table['user_id'].to_list(), summ_table['msg'].to_list()):
        json_data = {
            "alert_type": "popup",
            "title": "Reminder",
            "message": msg,
            "spec": {
                "title": "Trip label reminder",
                "text": msg
            }
        }
        # print(json_data)
        response = pnu.send_visible_notification_to_users([_uuid],
                                                          json_data["title"],
                                                          json_data["message"],
                                                          json_data)
        pnu.display_response(response)
