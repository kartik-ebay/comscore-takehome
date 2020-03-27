"""The file serves as an entry point to query tool.

The query tool accepts command line arguments representing the query parameters
"""

import argparse
import csv
import operator
import os
import sys
import typing

import constants


class DelimiterSeparatedInput(object):
    """An callable that accepts the separator, and converts to a list"""

    def __init__(self, item_type: typing.Callable[[str], typing.List[str]],
                 separator: str = ','):
        """Initialises the separated type.

        Args:
            item_type: typee to which the argument is to be converted
            separator: separator string
        """
        self.item_type = item_type
        self.separator = separator

    def __call__(self, values) -> typing.List[str]:
        """Creates a separator delimited list of arguments."""
        if not values:
            return list()
        try:
            return [self.item_type(val)
                    for val in values.split(self.separator)]
        except Exception:
            raise argparse.ArgumentTypeError(
                'The value {} can not be parsed'.format(values))


class Query(object):
    """An instance of this class encapsulates all the selection criteria to
    query the underlying data.
    """

    def __init__(self, select: typing.List[str] = None,
                 order: typing.List[str] = None,
                 filter_list: typing.List[str] = None):
        """Initialises the criteria.

        Args:
            select: selection criteria
            order: order criteria
            filter: filter criteria
        """
        self.select = select or []
        self.order = order or []
        self.filter_list = filter_list or []

    def __call__(self, root_dir: str) -> typing.List[str]:  # noqa: C901
        """Applies the criteria to filter a row by criteria.

        The implementation executes the following steps:

        1. Filters all files by filter list if provided; If it is not available,
           then the all the files are available for parsing

        2. The contents of all the filtered are read and stored to a list

        3. The contents are sorted by the keys provided by order
        """
        # Step 1: Filter files
        if self.filter_list:
            filtered_combo: typing.List[str] = [
                row_filter[1]
                for row_filter in (f.split('=') for f in self.filter_list)]
            data_files: typing.List[str] = []
            for data_file in os.listdir(root_dir):
                filter_count: int = 0
                for filter_value in filtered_combo:
                    if filter_value in data_file:
                        filter_count += 1
                if filter_count == len(filtered_combo):
                    data_files.append(data_file)
        else:
            # Need to ignore hidden files.
            data_files = [data_file for data_file in os.listdir(root_dir)
                          if not data_file.startswith('.')]

        # Step 2 : Read files' content
        filtered_rows: typing.List[typing.Dict[str, str]] = []
        for data_file in data_files:
            with open(os.path.join(constants.OUTPUT_DIRECTORY, data_file), 'r',
                      encoding='utf-8') as data_file:
                csv_reader = csv.DictReader(data_file, delimiter='|')
                for row in csv_reader:
                    filtered_rows.append(row)

        # Step 3 : Order by keys
        if self.order:
            filtered_rows = sorted(filtered_rows,
                                   key=operator.itemgetter(*self.order))

        # Select list
        if self.select:
            output_rows = []
            for filtered_row in filtered_rows:
                output_rows.append(
                    ', '.join([filtered_row.get(select_column, '')
                               for select_column in self.select]))
        else:
            output_rows = []
            for filtered_row in filtered_rows:
                output_rows.append(', '.join([filtered_row.get(column, '')
                                              for column in filtered_row]))

        return output_rows

    def __repr__(self):
        return '{}[{}]'.format(self.__class__.__name__,
                               self.__dict__)


def query_datastore(select: typing.List[str] = None,
                    order: typing.List[str] = None,
                    filter_list: typing.List[str] = None) -> typing.List[str]:
    """Query the data stores by selection criteria."""
    query = Query(select, order, filter_list)
    return query(constants.OUTPUT_DIRECTORY)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=DelimiterSeparatedInput(str),
                        help='Fields to be selected', required=False)
    parser.add_argument('-o', type=DelimiterSeparatedInput(str),
                        help='Fields to be ordered', required=False)
    parser.add_argument('-f', type=DelimiterSeparatedInput(str),
                        help='Fields to be filtered by', required=False)
    (arguments, _) = parser.parse_known_args(sys.argv[1:])

    output_rows = query_datastore(arguments.s, arguments.o, arguments.f)
    for output in output_rows:
        print(output)
