from unittest import mock

import os
import shutil
import typing

import constants
import datastore_importer


def input_datastore_file():
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(current_path, 'datastore.csv'))


def read_input_file():
    """Simulates the generators that read file contents."""
    with open(input_datastore_file(), 'r') as f:
        for line in f:
            yield line


@mock.patch('fileinput.input', side_effect=read_input_file)
def test_handle_command_line_inputs(mocked_fileinput):
    try:
        rows = []
        csv_writer_object = mock.Mock()
        csv_writer_object.writerow = lambda row: rows.append(row)
        with mock.patch('csv.writer',
                        return_value=csv_writer_object) as mock_csv_writer:
            datastore_importer.store_data_to_file()
            header_row: typing.List[str] = None
            expected_rows: typing.List[str] = []
            with open(input_datastore_file(), 'r') as f:
                for line in f:
                    line_row = line.replace('\n', '').split('|')
                    if header_row is None:
                        header_row = line_row
                        continue
                    expected_rows.extend([header_row, line_row])
            assert expected_rows == rows
            assert mocked_fileinput.call_count == 1
            assert mock_csv_writer.call_count == 4
    finally:
        shutil.rmtree(constants.OUTPUT_DIRECTORY, ignore_errors=True,
                      onerror=None)
