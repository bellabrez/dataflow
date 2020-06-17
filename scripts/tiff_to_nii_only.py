import dataflow as flow
full_target = 'G:/ftp_imports/20200228/fly3/anat_0/TSeries-02282020-0943-002'
#full_target = 'F:/ftp_imports/20200210/fly2/anat_0/TSeries-02102020-1424-002'
flow.start_convert_tiff_collections(full_target)
