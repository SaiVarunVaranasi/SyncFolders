import sys
import logging
import datetime
import os
import time

class SyncFolders:
    def __init__(self,
                 sourceFolder=None,
                 replicaFolder=None,
                 sync=None,
                 logpath=None):
        self.src = self.modify_paths(sourceFolder) or self.modify_paths(r"C:\Users\varan\OneDrive\Desktop\TestFolder\Source")
        self.rep = self.modify_paths(replicaFolder) or self.modify_paths(r"C:/Users/varan/OneDrive/Desktop/TestFolder/Replica")
        self.sync = sync or "120"
        self.logpath = self.modify_paths(logpath) or self.modify_paths(r"C:/Users/varan/OneDrive/Desktop/TestFolder/log.txt")

        logging.basicConfig(filename=self.logpath, level=logging.DEBUG)
        self.log_initial_parameters()
        self.compare_files_and_folders()
        self.recursive_execution(self.sync)

    def modify_paths(self, path):
        if path is not None:
            path=path.replace('\\', '/').replace('//', '/')
            print(f"Path modified:{path}")
            return path
            
        else:
            return None
        
        

    def log_initial_parameters(self):
        current_time = datetime.datetime.now()
        logging.info(f"Program started at: {current_time}")
        logging.info(f"Source Folder: {self.src}")
        logging.info(f"Destination folder: {self.rep}")
        logging.info(f"Synchronization interval: {self.sync}")
        logging.info(f"Log Path: {self.logpath}")

    def get_files_and_folders(path):
        files = []
        folders = []

        for root, dirs, files_list in os.walk(path):
            for file in files_list:
                files.append(os.path.join(root, file))
            for folder in dirs:
                folders.append(os.path.join(root, folder))

        return files, folders

    def copyFiles(self,files):
        files_copied=[]
        if files:
            for file in files:
                src_path= self.modify_paths(os.path.join(self.src,file.replace("\\","",1)))
                rep_path= self.modify_paths(os.path.join(self.rep,file.replace("\\","",1)))
                os.makedirs(os.path.dirname(rep_path), exist_ok=True)
                with open(src_path, 'rb') as source_file, open(rep_path, 'wb') as destination_file:
                    destination_file.write(source_file.read())
                files_copied.append({'file':file,'src_location':src_path,'rep_location':rep_path})    
        return files_copied
    
    def copyFolders(self, folders, src_path, rep_path):
        folders_copied = []
        if folders:
            for folder in folders:
                src_folder_path = self.modify_paths(os.path.join(src_path, folder.replace("\\","",1)))
                dest_folder_path = self.modify_paths(os.path.join(rep_path, folder.replace("\\","",1)))
                if os.path.isdir(src_folder_path):
                    os.makedirs(dest_folder_path, exist_ok=True)
                    subfolders = os.listdir(src_folder_path)
                    subfolders_copied = self.copyFolders(subfolders, src_folder_path, dest_folder_path)
                    folders_copied.extend(subfolders_copied)
                else:
                    src_file_path = src_folder_path
                    dest_file_path = dest_folder_path
                    with open(src_file_path, 'rb') as src_file, open(dest_file_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                folders_copied.append({'folder': os.path.basename(folder),'src_location': src_folder_path, 'rep_location': dest_folder_path})
        return folders_copied



    
    def removeFolder(self,path):
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

    def UpdateModifiedFiles(self,files):
        files_modified=[]
        if files:
            for file in files:
                src_path= self.modify_paths(os.path.join(self.src,file.replace("\\","",1)))
                rep_path= self.modify_paths(os.path.join(self.rep,file.replace("\\","",1)))
                src_modified = os.path.getmtime(src_path)
                rep_modified = os.path.getmtime(rep_path)
                
                if src_modified>rep_modified:
                    os.remove(rep_path)
                    self.copyFiles(list(file))
                    files_modified.append({'file':file,'src_location':src_path,'rep_location':rep_path})  
            
        return files_modified
    
    def UpdateModifiedFolders(self,folders,src_path,rep_path):
        folders_modified=[]
        if folders:
            for folder in folders:
                src_path= self.modify_paths(os.path.join(src_path,folder.replace("\\","",1)))
                rep_path= self.modify_paths(os.path.join(rep_path, folder.replace("\\","",1)))
                src_modified = os.path.getmtime(src_path)
                rep_modified = os.path.getmtime(rep_path)

                if src_modified>rep_modified:
                    self.removeFolder(rep_path)
                    self.copyFiles(list(folder))
                    folders_modified.append({'folder':folder,'src_location':src_path,'rep_location':rep_path})          
        return folders_modified

    def print_and_log_for_files(self,files,event=" "):
        count=len(files)
        print("-----------------------------------------------------------")
        print(f"{count} files have been {event}. Please find the details below:")
        logging.info(f"{count} files have been {event}. Please find the details below:")
        for i in files:
            name=i['file']
            src=i['src_location']
            rep=i['rep_location']
            print(f"File:{name}")
            print(f"Source folder location :{src}")
            print(f"Replica folder location :{rep}")
            print("-----------------------------------------------------------")
            logging.info(f"File:{name}")
            logging.info(f"Source folder location :{src}")
            logging.info(f"Replica folder location :{rep}")

    def print_and_log_for_folders(self,folders,event=" "):
            count=len(folders)
            print("-----------------------------------------------------------")
            print(f"{count} folders and their subfolders have been {event}. Please find the details below:")
            logging.info(f"{count} folders and their subfolders have been {event}. Please find the details below:")
            for folder_info in folders:
                name = folder_info['folder']
                src = folder_info['src_location']
                rep = folder_info['rep_location']
                print(f"Folder:{name}")
                print(f"Source folder location :{src}")
                print(f"Replica folder location :{rep}")
                print("-----------------------------------------------------------")
                logging.info(f"Folder:{name}")
                logging.info(f"Source folder location :{src}")
                logging.info(f"Replica folder location :{rep}")


    def compare_files_and_folders(self):
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


        src_files = [file.replace(self.src, '') for file in src_files]
        rep_files = [file.replace(self.rep, '') for file in rep_files]
        files_in_both_src_rep=list(set(src_files) & set(rep_files))

        src_folders = [folder.replace(self.src, '') for folder in src_folders]
        rep_folders = [folder.replace(self.rep, '') for folder in rep_folders]

        folders_in_both_src_rep = list(set(src_folders) & set(rep_folders))

        

        filesModified=self.UpdateModifiedFiles(files_in_both_src_rep)
        foldersModified=self.UpdateModifiedFolders(folders_in_both_src_rep,self.src,self.rep)

        folders_in_src_not_rep=list(set(src_folders)-set(rep_folders))
        files_in_src_not_rep=list(set(src_files)-set(rep_files))

        filesCopied=self.copyFiles(files_in_src_not_rep)
        foldersCopied=self.copyFolders(folders_in_src_not_rep,self.src,self.rep)
        print("---------------Files Created/Modified in Replica Folder--------------------------")
        self.print_and_log_for_files(filesModified,event="modified")
        self.print_and_log_for_files(filesCopied,event="copied")
        print("---------------Folders Created/Modified in Replica Folder--------------------------")
        self.print_and_log_for_folders(foldersModified,event="modified")
        self.print_and_log_for_folders(foldersCopied,event="copied")


    def recursive_execution(self,sync_time):
        while True:
            # Execute the program here
            SyncFolders(sourceFolder=self.src, replicaFolder=self.rep, sync=self.sync, logpath=self.logpath)
            
            # Wait for the specified sync time
            time.sleep(sync_time)

# Read command line arguments
arguments = sys.argv[1:]
source_folder = arguments[0] if arguments else None
replica_folder = arguments[1] if len(arguments) > 1 else None
sync_time = arguments[2] if len(arguments) > 2 else None
log_path = arguments[3] if len(arguments) > 3 else None

SyncFolders(sourceFolder=source_folder, replicaFolder=replica_folder,sync=sync_time,logpath=log_path)