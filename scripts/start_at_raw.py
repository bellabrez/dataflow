import dataflow as flow


full_target = 'F:/ftp_imports/20200130'


oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
extensions_for_oak_transfer = ['.nii', '.csv', '.xml', 'json'] # last 4 chars

flow.convert_raw_to_tiff(full_target)

#########################################
### Convert tiff to nii or tiff stack ###
#########################################

flow.start_convert_tiff_collections(full_target)

#######################
### Transfer to Oak ###
#######################

flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)