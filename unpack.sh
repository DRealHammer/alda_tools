#!/bin/bash

# go into the working dir
cd $1
work_dir=$(pwd)

# process every folder
processed_folders=0
for subdir in */
do
	
	#echo $subdir that we enter
	# go in the folder
	cd $subdir
	#echo current folder: $subdir

	# unzip every zip file and remove the zip
	
	for zip in *.zip
	do
		#echo current zip: $zip
		bsdtar -xf $zip
		rm $zip

		# possibly remove a macosx file if present
		if [[ -d __MACOSX ]]
		then
			rm -r "__MACOSX"
		fi
	done

	#echo now working on the folders inside the directory

	# go in every unpacked folder and move the files in the subdir folder
	for submission in */
	do
		
		#echo checking if $submission exists in the folder
		#echo files:
		#ls
		#echo ----

		if [[ "$submission" == /* ]]
		then
			continue
		fi

		# sanity check bc students use spaces in the folder names
		if [[ -d "$submission" ]]
		then
			#echo "\t" $submission that we enter 
			mv "$submission"/* .
			rm -r "$submission"
		fi
	done

	# go back to the working dir for the next folder
	cd $work_dir
	processed_folders=$(expr $processed_folders + 1)
done

echo "=> Processed" $processed_folders folders

# now work on the pure zip files
cd $work_dir
processed_zips=0
for zip in *.zip
do
	clean_name=$(basename -s .zip $zip)
	mkdir $clean_name
	mv $zip $clean_name
	cd $clean_name
	bsdtar -xf $zip
	rm $zip
	if [[ -d __MACOSX ]];
	then
		rm -r "__MACOSX"
	fi
	cd $work_dir
	processed_zips=$(expr $processed_zips + 1)
done

echo "=> Processed" $processed_zips "single zip files"
