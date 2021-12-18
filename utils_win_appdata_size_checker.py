#!/usr/bin/env python
# coding: utf-8

"""
Determine which folder is hogging the most space under AppData (Windows OS only).

You can see names of files being processed by uncommenting print statements inside calc_appdata_size. This drastically increases processing time!

Files which cannot be processed are saved to app_data_errors.log
"""

import os


def convert_file_size(bytes_size):
    """Convert size in bytes to MB and GB, also rounds to two decimal places"""
    _mega_bytes = bytes_size/1024/1024
    _giga_bytes = _mega_bytes/1024
    return round(_mega_bytes, 2), round(_giga_bytes, 2)

def calc_appdata_size(app_data_path):
    size_folder_map = {}
    final_data = {}
    output = []
    error_files = []

    for folder in os.listdir(app_data_path): # Folder will be Local, LocalLow, Roaming, etc
        size_folder_map[folder] = {} # {Local: {}}
        _folder_path = fr'{app_data_path}\{folder}'
        for _internal_folder in os.listdir(_folder_path): # List folders inside Local, e.g. Adobe, Apple, etc
            size_folder_map[folder][_internal_folder] = {} # {Local: {Adobe: {}}}
            for path, _, files in os.walk(fr'{_folder_path}\{_internal_folder}'):
                for file in files:
                    size_folder_map[folder][_internal_folder][file] = 0 # {Local: {Adobe: {something.json: 0}}}
                    _file_data = os.path.join(path, file)
                    try:
                        size = os.path.getsize(_file_data) # Will raise OSError if the file does not exist or is inaccessible.
                    except Exception as err:
                        error_files.append(_file_data)
                        print(f'Exception ({err}) while processing file: {_file_data}')
                    # print(f'{file} -> {size}')
                    size_folder_map[folder][_internal_folder][file] += size # {Local: {Adobe: {something.json: 1234}}}

    for _root_folders, _folder in size_folder_map.items():
        for _sec_folder in _folder:
            _folder_size = 0
            _dict_value = f'{_root_folders} > {_sec_folder}'
            # Construct reverse dict -> Size of files in folder: Folder
            # Add everything under Adobe {Local: {Adobe: {SUM OF FILES IN FOLDER} }}
            for _file, _size in size_folder_map[_root_folders][_sec_folder].items():
                _folder_size += _size
            if _folder_size not in final_data.keys():
                final_data[_folder_size] = [] # Use array, in case two folders have sime file size
            final_data[_folder_size].append(_dict_value)
            # print(_root_folders, _sec_folder, _file)

    file_sizes = list(final_data.keys()) # Get list of folder size

    file_sizes.sort() # Sort in ascending order

    file_sizes.reverse() # Reverse ascending order, we want biggest folder size first

    # os.path.getsize returns size in bytes
    _total_size_mb, _total_size_gb = convert_file_size(sum(file_sizes))
    output.append(f'\n\Calculated folder size of AppData: {_total_size_mb} MB | {_total_size_gb} GB\n')
    # Above size does not contain files that threw errors
    for _size in file_sizes:
        _mega_bytes, _giga_bytes = convert_file_size(_size)
        for _folders in final_data[_size]:
            output.append(f'{_folders} -> {_mega_bytes} MB | {_giga_bytes} GB')
    return output, error_files

if __name__ == '__main__':
    app_data_path = r'C:\Users\jmahesaa\AppData'
    _output, _errors = calc_appdata_size(app_data_path)
    for line in _output:
        print(line)
    if _errors:
        _error_log_name = 'app_data_errors.log'
        print(f'\nWriting error logs to {_error_log_name}')
        with open(_error_log_name, 'w+', encoding='utf-8') as err_log:
            for line in _errors:
                err_log.write(f'{line}\n')
        print('Finished writing error logs.')
