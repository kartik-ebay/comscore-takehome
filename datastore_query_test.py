from unittest import mock

import datastore_query
import constants

import argparse
import csv
import operator
import os
import pytest


class TestDelimiterSeparatedInput(object):

    def setup(self):
        self.delimited_separated_input = (
            datastore_query.DelimiterSeparatedInput(str))

    def test_null_or_empty_values(self):
        assert self.delimited_separated_input(None) == []
        assert self.delimited_separated_input([]) == []

    def test_parse_strings__returns__list(self):
        assert self.delimited_separated_input('TITLE,REV,DATE') == (
            ['TITLE', 'REV', 'DATE'])

    def test_parse_list__raises_argument_error(self):
        values = [1, 2, 3]
        separated_input = datastore_query.DelimiterSeparatedInput(int)
        with pytest.raises(argparse.ArgumentTypeError):
            separated_input(values)


@pytest.fixture
def datastore():
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'datastore.csv'))


@pytest.fixture()
def root_directory():
    """Returns the root directory for test output data files."""
    return os.path.normpath(os.path.dirname(os.path.abspath(__file__)))


class TestQuery(object):

    def test_no_arguments__returns_all_inputs(self, datastore, root_directory):
        query = datastore_query.Query()
        with mock.patch(
                'os.listdir',
                side_effect=lambda root_dir: [datastore]) as mock_list_dir:
            actual_rows = query(root_directory)
            with open(datastore, 'r') as open_file:
                expected_rows = [', '.join(row.replace('\n', '').split('|'))
                                 for row in open_file]
                # The first row is the title
                assert actual_rows == expected_rows[1:]
                assert mock_list_dir.call_count == 1
                assert mock_list_dir.call_args[0][0] == root_directory

    def test_select_arguments__returns_filtered_outputs_by_select(
            self, datastore, root_directory):
        select_criteria = ['TITLE', 'PROVIDER', 'REV']
        query = datastore_query.Query(select_criteria)
        with mock.patch(
                'os.listdir',
                side_effect=lambda root_dir: [datastore]) as mock_list_dir:
            actual_rows = query(root_directory)
            with open(datastore, 'r') as open_file:
                csv_writer = csv.DictReader(open_file, delimiter='|')
                expected_rows = []
                for row in csv_writer:
                    expected_rows.append(
                        ', '.join([row.get(select_column, '')
                                   for select_column in select_criteria]))
                # The first row is the title
                assert actual_rows == expected_rows
                assert mock_list_dir.call_count == 1
                assert mock_list_dir.call_args[0][0] == root_directory

    def test_order_criteria__returns_filtered_outputs(
            self, datastore, root_directory):
        select_criteria = ['TITLE', 'PROVIDER', 'REV']
        order_criteria = ['REV']
        query = datastore_query.Query(select_criteria, order_criteria)
        with mock.patch(
                'os.listdir',
                side_effect=lambda root_dir: [datastore]) as mock_list_dir:
            actual_rows = query(root_directory)
            with open(datastore, 'r') as open_file:
                csv_writer = csv.DictReader(open_file, delimiter='|')
                sorted_rows = sorted(
                    [row for row in csv_writer],
                    key=operator.itemgetter(*order_criteria))
                expected_rows = []
                for sorted_row in sorted_rows:
                    expected_rows.append(
                        ', '.join([sorted_row.get(select_column, '')
                                   for select_column in select_criteria]))
                # The first row is the title
                assert actual_rows == expected_rows
                assert mock_list_dir.call_count == 1
                assert mock_list_dir.call_args[0][0] == root_directory

    def test_filter_criteria__returns_filtered_outputs(
            self, datastore, root_directory):
        select_criteria = ['TITLE', 'PROVIDER', 'REV']
        order_criteria = ['REV']
        filter_criteria = 'DATE=2014-04-01'
        query = datastore_query.Query(
            select_criteria, order_criteria, [filter_criteria])
        # Copy file to allow filtering
        filter_file_arr = datastore.split('.')
        output_file = '{}_{}.{}'.format(
            filter_file_arr[0], filter_criteria.split('=')[-1],
            filter_file_arr[-1])
        output_data = [
            '"STB"|"TITLE"|"PROVIDER"|"DATE"|"REV"|"VIEW_TIME"\n',
            '"stb1"|"the matrix"|"warner bros"|"2014-04-01"|"4.00"|"1:30"\n'
        ]
        with open(output_file, 'w') as out_file:
            for output_datum in output_data:
                out_file.write(output_datum)
        try:
            with mock.patch(
                    'os.listdir',
                    side_effect=lambda root: [output_file]) as mock_list_dir:
                actual_rows = query(root_directory)
                with open(datastore, 'r') as open_file:
                    csv_writer = csv.DictReader(open_file, delimiter='|')
                    sorted_rows = sorted(
                        [row for row in csv_writer],
                        key=operator.itemgetter(*order_criteria))
                expected_rows = []
                filter_queries = [
                    (filter_query[0], filter_query[1])
                    for filter_query in (query.split('=')
                                         for query in [filter_criteria])]
                for sorted_row in sorted_rows:
                    for (filter_column,
                         filter_value) in filter_queries:
                        if sorted_row.get(filter_column, '') == filter_value:
                            expected_rows.append(
                                ', '.join(
                                    [sorted_row.get(select_column, '')
                                     for select_column in select_criteria]))
                assert actual_rows == expected_rows
                assert mock_list_dir.call_count == 1
                assert mock_list_dir.call_args[0][0] == root_directory
        finally:
            os.remove(output_file)


@mock.patch('datastore_query.Query')
def test_query_data_store(mock_query_object):
    expected_output = ['test output']
    mocked_func = mock.MagicMock(return_value=expected_output)
    mock_query_object.return_value = mocked_func
    select_criteria = ['TITLE', 'PROVIDER', 'REV']
    order_criteria = ['REV']
    filter_criteria = 'DATE=2014-04-01'
    actual_output = datastore_query.query_datastore(select_criteria,
                                                    order_criteria,
                                                    filter_criteria)
    assert actual_output == expected_output
    assert mock_query_object.call_count == 1
    assert mocked_func.call_count == 1
    assert mocked_func.call_args[0][0] == constants.OUTPUT_DIRECTORY
