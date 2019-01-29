# Create JSON file for UpSet app
# Author: Michal Cupak, 2018

import json
import os.path
from os import chdir, remove
import glob

##########################################################################

# Parameter inputs
csvFileRelPath = "data/knime_data/simpsons_2.csv"
columnCounts = [1,1,0,6]	# string, integer, float, binary
datasetName = "Simpsons 2"
upsetPath = "D:/_proteomika/KNIME_metanodes/Applications/UpSet"
addOnlyThisDataset = True
removeActualDatasetAfterOpen = False

##########################################################################

# Csv parameters
default_index = 0	# default ... 0; for knime ... 1 (on index 0 is default rowID)
separator = "\t"	# "," or ";" or "\t"

# Other parameters
datasetsFileName = "datasets.json"
timeToWait = 30		# time to wait before removing actual dataset files (csv, json)

# Computed constants from parameters
knime_data_folder = os.path.dirname(csvFileRelPath)
name = os.path.splitext(os.path.basename(csvFileRelPath))[0]
csvFileAbsPath = os.path.join(upsetPath, csvFileRelPath)
jsonFileName = name + ".json"
jsonFileRelPath = os.path.join(knime_data_folder, jsonFileName)
jsonFileAbsPath = os.path.join(upsetPath, jsonFileRelPath)
upsetAppPath = os.path.join(upsetPath, "index.html")



def re_create_datasets_file(only_actual):
	# Re-Create datasets.json
	datasets_list = []

	if only_actual:
		datasets_list.append(jsonFileRelPath)

	else:
		chdir(upsetPath)
		glob_path = os.path.join(knime_data_folder, "*.json")
		json_files_list = glob.glob(glob_path)
		json_files_list.sort()

		if (jsonFileRelPath in json_files_list):
			datasets_list.append(jsonFileRelPath)

		for json_file in json_files_list:
			if json_file != jsonFileRelPath:
				datasets_list.append(json_file)


	datasetsPath = os.path.join(upsetPath, datasetsFileName)
	with open(datasetsPath, "w") as fp2:
		json.dump(datasets_list, fp2)





if __name__ == '__main__':



	# JSON Data
	data = {
		"file": csvFileRelPath,
		"name": datasetName,
		"header": 0,
		"separator": separator,
		"skip": 0,
		"author": "MU Proteomics Group",
		"description": "",
		"source": "",
		"meta": []
	}


	index = default_index
	# Meta -> ID + strings
	for x in range(columnCounts[0]):
		if (index == default_index):
			meta_type = "id"
		else:
			meta_type = "string"
		data["meta"].append({ "type": meta_type, "index": index})
		index = index+1

	# Meta -> Integers
	for x in range(columnCounts[1]):
		data["meta"].append({ "type": "integer", "index": index})
		index = index+1

	# Meta -> Floats
	for x in range(columnCounts[2]):
		data["meta"].append({ "type": "float", "index": index})
		index = index+1

	# Sets
	binary_set_start = default_index + columnCounts[0] + columnCounts[1] + columnCounts[2]
	binary_set_end = binary_set_start + columnCounts[3] - 1
	data["sets"] = [
		{ "format": "binary", "start": binary_set_start, "end": binary_set_end}
	]




	# Create JSON file
	with open(jsonFileAbsPath, "w") as fp:
		json.dump(data, fp)


	# Re-create datasets.json
	re_create_datasets_file(addOnlyThisDataset)



	# Open UpSet in Firefox
	import webbrowser
	url = "file://" + upsetAppPath
	webbrowser.get("firefox").open_new(url)



	# Remove actual csv and json file
	if removeActualDatasetAfterOpen:
		print("Sleep before removing actual dataset files for " + str(timeToWait) + "s")
		import time
		for x in range(timeToWait):
			time.sleep(1)
			print(".", end="")
		print()
		if os.path.exists(jsonFileAbsPath):
			remove(jsonFileAbsPath)
		if os.path.exists(csvFileAbsPath):
			remove(csvFileAbsPath)
		re_create_datasets_file(False)



	# End
	print("True")
