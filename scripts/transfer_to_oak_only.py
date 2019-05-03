import dataflow as flow

full_target = 'F:/FTP_IMPORTS/20190425'
oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
extensions_for_oak_transfer = ['.nii', '.csv', '.xml']

flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)