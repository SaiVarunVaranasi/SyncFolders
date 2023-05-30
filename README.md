# SyncFolders

# SyncFolders

`SyncFolders` is a Python script that synchronizes files and folders between a source folder and a replica folder. It compares the contents of the two folders and performs the necessary operations to ensure that both folders are in sync. It is a one way sync i.e the changes in source folder will be applied to replica folder but the changes to replica folder will not reflect in source folder.

## Features

- Copies new files from the source folder to the replica folder.
- Copies new folders and their contents from the source folder to the replica folder.
- Removes deleted files from the replica folder.
- Removes deleted folders and their contents from the replica folder.
- Updates modified files in the replica folder.

## Usage

Run the script:

	python sync_folders.py [source_folder] [replica_folder] [sync_time] [log_path]
	

- source_folder: Path to the source folder.
- replica_folder: Path to the replica folder.
- sync_time: Synchronization interval in **_seconds_**.
- log_path: Path to the log file.


## Logging

The script logs the following information to the specified log file:

- Program start time
- Source folder path
- Replica folder path
- Synchronization interval
- Log file path
- Modified or created files and folders
- Removed files and folders


