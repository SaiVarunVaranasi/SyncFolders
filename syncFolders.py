import sys
import logging
import datetime
import os
import time

class SyncFolders:
     # Lists to store information about copied files, copied folders, removal lists
    files_copied=[]
    folders_copied = []
    folders_removal_list=[]
    files_removal_list=[]

    def __init__(self,
                 sourceFolder=None,
                 replicaFolder=None,
                 sync=None,
                 logpath=None):
        """
        Initializes the SyncFolders object with the provided parameters.

        Args:
            sourceFolder (str): Path to the source folder.
            replicaFolder (str): Path to the replica folder.
            sync (int): Synchronization interval in seconds.
            logpath (str): Path to the log file.

        """
        self.src = self.modify_paths(sourceFolder)
        self.rep = self.modify_paths(replicaFolder)
        self.sync = sync
        self.logpath = self.modify_paths(logpath)
        logging.basicConfig(filename=self.logpath, level=logging.DEBUG)
        self.log_initial_parameters()
        self.compare_files_and_folders()
        

    def modify_paths(self, path):
        """
        Modifies the provided path by replacing backslashes with forward slashes.

        Args:
            path (str): The path to be modified.

        Returns:
            str: The modified path.

        """
        if path is not None:
            path=path.replace('\\', '/').replace('//', '/')
            return path
            
        else:
            return None
        
        

    def log_initial_parameters(self):
        """
        Logs the initial parameters to the log file.

        """ 
        current_time = datetime.datetime.now()
        logging.info(f"Program started at: {current_time}")
        logging.info(f"Source Folder: {self.src}")
        logging.info(f"Destination folder: {self.rep}")
        logging.info(f"Synchronization interval: {self.sync}")
        logging.info(f"Log Path: {self.logpath}")

    def get_files_and_folders(self,path):
        """
        Retrieves the list of files and folders in the given path.

        Args:
            path (str): The path to retrieve files and folders from.

        Returns:
            tuple: A tuple containing two lists: files and folders.

        """
        files = []
        folders = []

        for root, dirs, files_list in os.walk(path):
            for file in files_list:
                files.append(os.path.join(root, file))
            for folder in dirs:
                folders.append(os.path.join(root, folder))

        return files, folders

    def copyFiles(self,files,src_path,rep_path,method):
        """
        Copies the specified files from the source path to the replica path.

        Args:
            files (list): A list of file names to be copied.
            src_path (str): The source path where the files are located.
            rep_path (str): The replica path where the files will be copied.
            method (str): The method used for copying the files.

        """
        try:
            if files:
                for file in files:
                    src_path_update= self.modify_paths(os.path.join(src_path,file.replace("\\","",1)))
                    rep_path_update= self.modify_paths(os.path.join(rep_path,file.replace("\\","",1)))
                    os.makedirs(os.path.dirname(rep_path_update), exist_ok=True)
                    with open(src_path_update, 'rb') as source_file, open(rep_path_update, 'wb') as destination_file:
                        destination_file.write(source_file.read())
                    self.files_copied.append({'file':file,'src_location':src_path_update,'rep_location':rep_path_update,'method':method})
        except OSError as e:
            print(f"Error copying folder'{file}' at '{src_path_update}': {e}")
   
    def copyFolders(self, folders, src_path, rep_path,method):
        """
        Copies the specified folders and their contents from the source path to the replica path.

        Args:
            folders (list): A list of folder names to be copied.
            src_path (str): The source path where the folders are located.
            rep_path (str): The replica path where the folders will be copied.
            method (str): The method used for copying the folders.

        """
        try:
            if folders:
                for folder in folders:
                    src_folder_path = self.modify_paths(os.path.join(src_path, folder.replace("\\","",1)))
                    dest_folder_path = self.modify_paths(os.path.join(rep_path, folder.replace("\\","",1)))
                    if os.path.isdir(src_folder_path):
                        os.makedirs(dest_folder_path, exist_ok=True)
                        self.folders_copied.append({'folder': os.path.basename(folder),'src_location': src_folder_path, 'rep_location': dest_folder_path,'method':method})
                        subfolders = os.listdir(src_folder_path)
                        self.copyFolders(subfolders, src_folder_path, dest_folder_path,"Copy")
                    else:
                        src_file_path = src_folder_path.replace(os.path.basename(folder), '')
                        dest_file_path = dest_folder_path.replace(os.path.basename(folder), '')
                        self.copyFiles([folder],src_file_path,dest_file_path,"Copy")
        except OSError as e:
            print(f"Error copying folder'{folder}' at '{src_folder_path}': {e}")

    def removeFolder(self,path):
        """
        Removes the specified folder and its contents.

        Args:
            path (str): The path of the folder to be removed.

        """
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    os.rmdir(dir_path)
            os.rmdir(path)
        except OSError as e:
            print(f"Error removing directory '{path}': {e}")

    def updateModifiedFiles(self,files,src_path,rep_path):
        """
        Updates the modified files by copying them from the source path to the replica path.

        Args:
            files (list): A list of file names to be checked for updates.
            src_path (str): The source path where the files are located.
            rep_path (str): The replica path where the files will be updated.

        """
        try:
            if files:
                for file in files:
                    src_path_updated= self.modify_paths(os.path.join(src_path,file.replace("\\","",1)))
                    rep_path_updated= self.modify_paths(os.path.join(rep_path,file.replace("\\","",1)))
                    src_last_modified = os.path.getmtime(src_path_updated)
                    rep_last_modified = os.path.getmtime(rep_path_updated)
                    
                    if src_last_modified>rep_last_modified:
                        os.remove(rep_path_updated)
                        
                        self.copyFiles([file],src_path_updated.replace(os.path.basename(file), ''),rep_path_updated.replace(os.path.basename(file), ''),"Modify")                 
        except OSError as e:
            print(f"Error modifying file'{file}' at '{src_path_updated}': {e}")
            
    def updateModifiedFolders(self,folders,src_path,rep_path):
        """
        Updates the modified folders by copying them from the source path to the replica path.

        Args:
            folders (list): A list of folder names to be checked for updates.
            src_path (str): The source path where the folders are located.
            rep_path (str): The replica path where the folders will be updated.

        """
        try:
            if folders:
                for folder in folders:
                    src_path_updated= self.modify_paths(os.path.join(src_path,folder.replace("\\","",1)))
                    rep_path_updated= self.modify_paths(os.path.join(rep_path, folder.replace("\\","",1)))
                    src_last_modified = os.path.getmtime(src_path_updated)
                    rep_last_modified = os.path.getmtime(rep_path_updated)

                    if src_last_modified>rep_last_modified:
                        self.removeFolder(rep_path_updated)
                        self.copyFolders([folder],src_path_updated,rep_path_updated,"Modify")
        except OSError as e:
            print(f"Error modifying folder'{folder}' at '{src_path_updated}': {e}")

    def removeDeletedFolders(self,folders,rep_path):
        """
        Removes the specified folders and their contents from the replica path.

        Args:
            folders (list): A list of folder names to be removed.
            rep_path (str): The replica path where the folders are located.

        """
        if folders:
            try:
                for folder in folders:
                    rep_path_updated= self.modify_paths(os.path.join(rep_path, folder.replace("\\","",1)))
                    self.removeFolder(rep_path_updated)
                    self.folders_removal_list.append({'folder': os.path.basename(folder),'location': rep_path_updated})
            except OSError as e:
                print(f"Error removing directory '{rep_path}': {e}")

    def removeDeletedFiles(self,files,rep_path):
        """
        Removes the specified files from the replica path.

        Args:
            files (list): A list of file names to be removed.
            rep_path (str): The replica path where the files are located.

        """
        if files:
            try:
                for file in files:
                        file_path = os.path.join(rep_path, file)
                        os.remove(file_path)
                        self.files_removal_list.append({'file': os.path.basename(file),'location': file_path})
            except OSError as e:
                print(f"Error removing directory '{rep_path}': {e}")


    def print_and_log_for_files(self,files):
        """
        Prints and logs the details of the modified or created files.

        Args:
            files (list): List of file information dictionaries.
                Each dictionary should contain the following keys: 'file', 'src_location', 'rep_location', 'method'.
        """
        count=len(files)
        print("-----------------------------------------------------------")
        print(f"{count} files have been Modified/Created. Please find the details below:")
        logging.info(f"{count} files have been Modified/Created. Please find the details below:")
        for file_info in files:
            name=file_info['file']
            src=file_info['src_location']
            rep=file_info['rep_location']
            method=file_info['method']
            print(f"File:{name}")
            print(f"Source folder location :{src}")
            print(f"Replica folder location :{rep}")
            print(f"Modified/Copied :{method}")
            print("-----------------------------------------------------------")
            logging.info(f"File:{name}")
            logging.info(f"Source folder location :{src}")
            logging.info(f"Replica folder location :{rep}")
            logging.info(f"Modified/Copied :{method}")

    def print_and_log_for_folders(self,folders):
            """
                Prints and logs the details of the modified or created folders.

                Args:
                    folders (list): List of folder information dictionaries.
                    Each dictionary should contain the following keys: 'folder', 'src_location', 'rep_location', 'method'.
            """

            count=len(folders)
            print("-----------------------------------------------------------")
            print(f"{count} folders and their subfolders have been Modified/Created. Please find the details below:")
            logging.info(f"{count} folders and their subfolders have been Modified/Created. Please find the details below:")
            for folder_info in folders:
                name = folder_info['folder']
                src = folder_info['src_location']
                rep = folder_info['rep_location']
                method=folder_info['method']
                print(f"Folder:{name}")
                print(f"Source folder location :{src}")
                print(f"Replica folder location :{rep}")
                print(f"Modified/Copied :{method}")
                print("-----------------------------------------------------------")
                logging.info(f"Folder:{name}")
                logging.info(f"Source folder location :{src}")
                logging.info(f"Replica folder location :{rep}")
                logging.info(f"Modified/Copied :{method}")

    def print_and_log_for_folders_removal(self,removedFolders):
            """
                Prints and logs the details of the removed folders.

                Args:
                    removedFolders (list): List of removed folder information dictionaries.
                    Each dictionary should contain the following keys: 'folder', 'location'.
            """
            count=len(removedFolders)
            print("-----------------------------------------------------------")
            print(f"{count} folders and their subfolders have been deleted. Please find the details below:")
            logging.info(f"{count} folders and their subfolders have been deleted. Please find the details below:")
            for folder_info in removedFolders:
                name = folder_info['folder']
                src = folder_info['location']
                print(f"Folder:{name}")
                print(f"Source folder location :{src}")
                print("-----------------------------------------------------------")
                logging.info(f"Folder:{name}")
                logging.info(f"Source folder location :{src}")

    def print_and_log_for_files_removal(self,removedfiles):
            """
            Prints and logs the details of the removed files.

            Args:
                removedfiles (list): List of removed file information dictionaries.
                    Each dictionary should contain the following keys: 'file', 'location'.
            """
            count=len(removedfiles)
            print("-----------------------------------------------------------")
            print(f"{count} folders and their subfolders have been deleted. Please find the details below:")
            logging.info(f"{count} folders and their subfolders have been deleted. Please find the details below:")
            for file_info in removedfiles:
                name = file_info['file']
                src = file_info['location']
                print(f"File:{name}")
                print(f"Source folder location :{src}")
                print("-----------------------------------------------------------")
                logging.info(f"Folder:{name}")
                logging.info(f"Source folder location :{src}")


    def compare_files_and_folders(self):
        """
        Compares the files and folders between the source and replica folders, performs necessary operations,
        and prints/logs the summary of actions taken.
        """
        src_files,src_folders=self.get_files_and_folders(self.src)
        rep_files,rep_folders=self.get_files_and_folders(self.rep)
        
        print(f"Files in Source Folder: {len(src_files)}")
        print(f"Folders in Source Folder: {len(src_folders)}")
        print(f"Files in Replica Folder: {len(rep_files)}")
        print(f"Folders in Replica Folder: {len(rep_folders)}")
        logging.info(f"Files in Source Folder: {len(src_files)}")
        logging.info(f"Folders in Source Folder: {len(src_folders)}")
        logging.info(f"Files in Replica Folder: {len(rep_files)}")
        logging.info(f"Folders in Replica Folder: {len(rep_folders)}")

        #Compare Folders:
        src_folders = [folder.replace(self.src, '') for folder in src_folders]
        rep_folders = [folder.replace(self.rep, '') for folder in rep_folders]
        
        
        #Check if these common folders have been updated and update if necessary
        folders_in_both_src_rep = list(set(src_folders) & set(rep_folders))
        self.updateModifiedFolders(folders_in_both_src_rep,self.src,self.rep)

        #Copy/Create the folders in replica
        folders_in_src_not_rep=list(set(src_folders)-set(rep_folders))
        self.copyFolders(folders_in_src_not_rep,self.src,self.rep,"Copy")

        #Remove the folders from replica
        folders_in_rep_not_src = list(set(rep_folders)-set(src_folders))
        self.removeDeletedFolders(folders_in_rep_not_src,self.rep)

        #get the updated list of files and folders so we can remove the already copied subfolders and files for further processing
        src_files1,src_folders1=self.get_files_and_folders(self.src)
        rep_files1,rep_folders1=self.get_files_and_folders(self.rep)

        #Compare files
        src_files1 = [file.replace(self.src, '') for file in src_files1]
        rep_files1 = [file.replace(self.rep, '') for file in rep_files1]

        
        #Check if these common files have been updated and update if necessary
        files_in_both_src_rep=list(set(src_files1) & set(rep_files1))
        self.updateModifiedFiles(files_in_both_src_rep,self.src,self.rep)

        #Copy/Create the files in replica
        files_in_src_not_rep=list(set(src_files1)-set(rep_files1))
        self.copyFiles(files_in_src_not_rep,self.src,self.rep,"Copy")

        #Remove the files from replica
        files_in_rep_not_src=list(set(rep_files1)-set(src_files1))
        self.removeDeletedFiles(files_in_rep_not_src,self.rep)


        print("---------------Files Created/Modified in Replica Folder--------------------------")
        self.print_and_log_for_files(self.files_copied)

        print("---------------Folders Created/Modified in Replica Folder--------------------------")
        self.print_and_log_for_folders(self.folders_copied)

        print("---------------Folders removed from Replica Folder--------------------------")
        self.print_and_log_for_folders_removal(self.folders_removal_list)

        print("---------------Files removed from Replica Folder--------------------------")
        self.print_and_log_for_folders_removal(self.files_removal_list)



def main():
    # Read command line arguments
    arguments = sys.argv[1:]
    source_folder = arguments[0] if arguments else None
    replica_folder = arguments[1] if len(arguments) > 1 else None
    sync_time = int(arguments[2]) if len(arguments) > 2 else 120
    log_path = arguments[3] if len(arguments) > 3 else None
    
    while True:
        #Clearing the lists before every rerun of code        
        SyncFolders.files_copied.clear()
        SyncFolders.folders_copied.clear()
        SyncFolders.folders_removal_list.clear()
        SyncFolders.files_removal_list.clear()
        SyncFolders(sourceFolder=source_folder, replicaFolder=replica_folder, sync=sync_time, logpath=log_path)
        
        # Print the Waiting time
        print(f"Waiting for {sync_time} seconds...")
        for remaining_time in range(sync_time, 0, -1):
            sys.stdout.write(f"\r{remaining_time} seconds remaining...")
            sys.stdout.flush()
            time.sleep(1)

        
        print()

if __name__ == "__main__":
    main()