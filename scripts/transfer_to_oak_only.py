import dataflow as flow
import sys
import os

def main():
	folder = '20200207-sez'
	full_target = 'F:/FTP_IMPORTS' + '/' + folder
	#oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
	oak_target = 'X:/data/Ashley2/imports'
	extensions_for_oak_transfer = ['.nii', '.csv', '.xml', 'json'] # last 4 chars

	flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)

if __name__ == '__main__':
	main()