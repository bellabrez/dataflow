import os

def datadir_appender(directory_suffix):
    my_data_directory = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging'
    if directory_suffix[0] in ['/', '\\']:
        directory_suffix = directory_suffix[1:]
    directory = os.path.join(my_data_directory, directory_suffix)
    print('new directory is: {}'.format(directory))
    return directory