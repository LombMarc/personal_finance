import datetime
import json
import sqlite3
import plotly.express as px
import plotly.offline as opy
from flask_login import UserMixin
from flask import make_response
import csv
from io import StringIO

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def query_db(db,query, *args):
    """
    execute query returning a list of dictionary
    :param db:
    :param query:
    :param args:
    :return:
    """
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        if args:
            cur.execute(query,args)
        else:
            cur.execute(query)
        #fetch tuple of results
        rows = cur.fetchall()
        #get cols name from description
        cols = [c[0] for c in cur.description]
        #iterate through each tuple trnasformin into a dictionary
        res = []
        for row in rows:
            res.append({c:row[i] for i, c in enumerate(cols)})
        cur.close()
        con.close()
        return res
    except Exception as e:
        print("An error occurred when getting data to db: ",e)

def insert_db(db, query, *args):
    """
    Used to insert/update values into db
    :param db:
    :param query:
    :param args:
    :return:
    """
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        if args:
            cur.execute(query, args)
        else:
            cur.execute(query)
        con.commit()
        cur.close()
        con.close()
        return 0
    except Exception as e:
        print("An error occurred when inserting data into the database: ", e)
        return -1  # Return a code indicating an error

def dict_of_list(list_of_dicts):
    """
    From the list of dicitonary arriving from the query result, generate the dictionary of lists as expected by
    plotly.
    :param list_of_dicts:
    :return:
    """
    dict_of_lists = {}
    for d in list_of_dicts:
        for key, value in d.items():
            if key in dict_of_lists:
                dict_of_lists[key].append(value)
            else:
                dict_of_lists[key] = [value]
    return dict_of_lists


def create_summary_figures(data,user_id,month,year,db):
    """
    create figure for summary page
    :param data:
    :param user_id:
    :param month:
    :param year:
    :return:
    """
    month_dict = {
        '01': 'January',
        '02': 'February',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }
    plotly_data = dict_of_list(data)
    fig = px.bar(plotly_data, x='category', y='tot', labels={'tot':'Amount','category':'Categories'})
    fig.update_traces(marker=dict(color=px.colors.sequential.Rainbow),width=0.4).update_layout(bargap=0.55)
    fig = fig.update_layout(
        title=f'Categories on {month_dict[month]} - {year}',
        xaxis_title='Categories',
        yaxis_title='amount'
    )

    fig = opy.plot(fig, auto_open=False, output_type='div', config={'displayModeBar': False, 'displaylogo': False})
    return fig

def summary_data(data):
    """
    create figure for summary page
    :param data:
    :param user_id:
    :param month:
    :param year:
    :return:
    """
    month_dict = {
        '01': 'January',
        '02': 'February',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }
    plotly_data = dict_of_list(data)

    return json.dumps(plotly_data)

def create_csv_file(data):
    """
    return the csv respone for the download
    :param data:
    :return:
    """
    #create in memory file
    csv_data = StringIO()
    # prepare dictionary writer
    csv_writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
    # write headers
    csv_writer.writeheader()
    # write data
    csv_writer.writerows(data)

    response = make_response(csv_data.getvalue())

    response.headers['Content-Disposition'] = f'attachment; filename=data_{datetime.datetime.now().timestamp()}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def create_history_figure(user_id,year,db):
    """
    create figure for summary page
    :param user_id:
    :param year:
    :return:
    """
    month_dict = {
        '01': 'January',
        '02': 'February',
        '03': 'March',
        '04': 'April',
        '05': 'May',
        '06': 'June',
        '07': 'July',
        '08': 'August',
        '09': 'September',
        '10': 'October',
        '11': 'November',
        '12': 'December'
    }
    query_liquidity = """
    SELECT month_year, liquidity, cumulative_wealth
FROM (
    select * from
    (
    SELECT
        strftime('%m', t.time_inserted) as month,
        strftime('%Y', t.time_inserted) as year,
        (strftime('%m', t.time_inserted) || '-' || strftime('%Y', t.time_inserted)) as month_year,
        sum(SUM(t.amount)) OVER (order BY  strftime('%Y', t.time_inserted) ASC, strftime('%m', t.time_inserted) ASC) AS liquidity
        FROM transactions as t
    where user_id = :param1 and year <= :param2
    GROUP BY year,month
    ) as liq
    left join
    (
    SELECT
    strftime('%m', time_inserted) as months,
    strftime('%Y', time_inserted) as years,
    (strftime('%m', time_inserted) || '-' || strftime('%Y', time_inserted)) AS month_year,
    SUM(SUM(amount)) OVER (order BY  strftime('%Y', time_inserted) ASC, strftime('%m', time_inserted) ASC) as cumulative_wealth
    FROM transactions
    WHERE user_id = :param1 AND years <= :param2 AND category IN (select category from categories where is_wealth <> 1)
    GROUP BY  months,years
    ) as wel
    ON liq.month_year = wel.month_year
    ORDER BY year asc, month ASC
);
    """
    plotly_data = dict_of_list(query_db(db, query_liquidity, user_id,str(year)))

    fig_mon = px.bar(plotly_data, x='month_year', y=['liquidity', 'cumulative_wealth'],
                     labels={'value': 'Residual Liquidity', 'variable': 'Bars'},
                     title='Monthly Summary', barmode='group')

    fig_mon = fig_mon.update_traces(width=0.2).update_layout(bargap=0.55)
    fig_mon = fig_mon.update_layout(
        title='Monthly Summary',
        xaxis_title='Month',
        yaxis_title='Wealth - liquidity',
        showlegend=True,
        legend=dict(title='Liquidity Type', orientation='h', y=1.1)

    )
    return json.dumps(plotly_data)


