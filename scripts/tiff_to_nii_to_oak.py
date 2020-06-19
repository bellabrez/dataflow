import sys
import os
import dataflow as flow


oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
#oak_target = 'X:/data/Ashley2/imports'

extensions_for_oak_transfer = ['.nii', '.csv', '.xml', 'json', 'tiff'] # needs to for 4 char

full_target = 'G:/ftp_imports/20200618' # do not put trailing slash!

#flow.convert_raw_to_tiff(full_target)
flow.start_convert_tiff_collections(full_target)
flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)