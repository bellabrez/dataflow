import dataflow as flow
full_target = 'F:/ftp_imports/20200130'

flow.convert_raw_to_tiff(full_target)

#########################################
### Convert tiff to nii or tiff stack ###
#########################################

if convert_to in ['.nii', 'nii', 'nifti']:
    flow.start_convert_tiff_collections(full_target)
elif convert_to in ['.tiff', 'tiff', '.tif', 'tif']:
    flow.convert_tiff_collections_to_stack(full_target)
else:
    print('{} is an invalid convert_to variable from metadata.'.format(convert_to))

#######################
### Transfer to Oak ###
#######################

flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)