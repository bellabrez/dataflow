import dataflow as flow

ip='171.65.18.54'
username = 'user'
passwd = 'flyeye'
bruker_folder = 'luke/20190425__flag__'
full_target = 'F:/FTP_IMPORTS/20190425'

flow.confirm_bruker_transfer(ip, username, passwd, bruker_folder, full_target)