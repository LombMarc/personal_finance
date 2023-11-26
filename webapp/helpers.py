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
    fig = fig.update_layout(
        title=f'Categories on {month_dict[month]} - {year}',
        xaxis_title='Categories',
        yaxis_title='amount',
        showlegend=False
    )
    fig = opy.plot(fig, auto_open=False, output_type='div')
    # General query
    query = """
                SELECT 
                  strftime('%m', time_inserted) as month, 
                  SUM(amount) AS residual_liquidity,
                  SUM(SUM(amount)) OVER (ORDER BY strftime('%m', time_inserted) ASC) AS cumulative_residual_liquidity
                FROM transactions 
                WHERE user_id = ? AND strftime('%Y', time_inserted) = ?
                GROUP BY month
                ORDER BY month ASC;
                    """
    monthly_summary = dict_of_list(query_db(db, query, user_id,year))
    monthly_summary['month'] = [month_dict[i] for i in monthly_summary['month']]

    fig_mon = px.line(monthly_summary, x='month', y='cumulative_residual_liquidity', markers=True,
                      labels={'cumulative_residual_liquidity': 'Cumulative Residual Liquidity'})
    fig_mon = fig_mon.add_bar(x=monthly_summary['month'], y=monthly_summary['residual_liquidity'],
                              name='Monthly residual')
    fig_mon = fig_mon.update_layout(
        title='Monthly Summary',
        xaxis_title='Month',
        yaxis_title='Liquidity',
        legend_title='Liquidity Type',
        showlegend=False
    )
    fig_mon = opy.plot(fig_mon, auto_open=False, output_type='div', config={'displayModeBar': False})
    return fig, fig_mon


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
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
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
    monthly_summary = dict_of_list(query_db(db, query_liquidity, user_id,str(year)))

    '''fig_mon = px.bar(monthly_summary, x='month_year', y='liquidity',
                      labels={'liquidity': 'Residual Liquidity'})
    fig_mon = fig_mon.add_bar(x=monthly_summary['month_year'], y=monthly_summary['cumulative_wealth'],name='Wealth')
    '''
    fig_mon = px.bar(monthly_summary, x='month_year', y=['liquidity', 'cumulative_wealth'],
                     labels={'value': 'Residual Liquidity', 'variable': 'Bars'},
                     title='Monthly Summary', barmode='group')

    fig_mon = fig_mon.update_layout(
        title='Monthly Summary',
        xaxis_title='Month',
        yaxis_title='Wealth - liquidity',
        legend_title='Liquidity Type',
        showlegend=False
    )
    fig_mon = opy.plot(fig_mon, auto_open=False, output_type='div', config={'displayModeBar': False})

    return fig_mon
