from webapp.helpers import  dict_of_list, create_history_figure, query_db
from unittest.mock import patch
import json

# dict_of_list tests
def test_dict_of_list_empty_input():
    result = dict_of_list([{}])
    assert result == {}

def test_dict_of_list_single_dict():
    input_data = [{'a': 1, 'b': 2, 'c': 3}]
    result = dict_of_list(input_data)
    assert result == {'a': [1], 'b': [2], 'c': [3]}

def test_dict_of_list_multiple_dicts():
    input_data = [
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 5, 'c': 6},
        {'a': 7, 'b': 8, 'c': 9},
    ]
    result = dict_of_list(input_data)
    assert result == {'a': [1, 4, 7], 'b': [2, 5, 8], 'c': [3, 6, 9]}

#create_history_figure test
@patch('webapp.helpers.query_db')
def test_create_history_figure(mock_query_db):
    mock_query_db.return_value = [
        {'month_year': '01-2023', 'liquidity': 100, 'cumulative_wealth': 50},
        {'month_year': '02-2023', 'liquidity': 150, 'cumulative_wealth': 80},

    ]

    result = create_history_figure(user_id='123', year=2023, db='mock_db')

    expected_result = json.dumps({'month_year': ['01-2023', '02-2023'],
                                  'liquidity': [100, 150],
                                  'cumulative_wealth': [50, 80]})

    # Assert the entire result
    assert result == expected_result




