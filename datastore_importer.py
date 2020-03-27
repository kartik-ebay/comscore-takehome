"""Entry point for importer and datastore. It accepts arguments in two ways.

1. through the file argument. The invocation would be something like

python importer_datastore.py datastore.csv

2. through standard input such as

python importer_datastore.py < datastore.csv
"""

import csv
import fileinput
import logging
from logging import config
import os

import constants


config.fileConfig('logging.conf')
logger = logging.getLogger('root')


# Global variables
FILE_HEADER: str = None


def store_data_to_file():
    """The implementation does the following

    1. Creates a directory output directory if it does not exist.
    2. Reads the header if it not already parsed; if the header has not been
       parsed, then a file is created in write mode such a file name is a
       combination of "stb", "title,", and "date" and the header is written to
       a file
    3. The contents of the datastore are written to a file; if the file already
       exists, then the contents are overwritten.
    """
    # Step 1: Create a directory if it does not exist.
    os.makedirs(constants.OUTPUT_DIRECTORY, exist_ok=True)
    is_header_parsed: bool = False
    for content in fileinput.input():
        content = content.replace('\n', '')
        if not is_header_parsed:
            FILE_HEADER = content.split('|')
            is_header_parsed = True
            continue

        # Step # 2: Parse the header
        data_set = content.split('|')
        stb, title, _, date, _, _ = data_set
        # Creating the directory per stb, title, and date
        file_name = constants.OUTPUT_FILE_PATH.format(
            stb.lower(), title.lower(), date)
        with open(file_name, 'w',
                  encoding='utf-8') as file_object:
            file_writer = csv.writer(file_object, delimiter='|',
                                     quoting=csv.QUOTE_ALL)
            if FILE_HEADER and is_header_parsed:
                file_writer.writerow(FILE_HEADER)
                is_header_parsed = True
            file_writer.writerow(data_set)


if __name__ == '__main__':
    store_data_to_file()
