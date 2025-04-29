import os
import shutil
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


ORIGINAL_FOLDER = "/Users/anshulshukla/Downloads/lbmaske"
NEW_FOLDER = "/Users/anshulshukla/Downloads/process_data"
BACKUP_FOLDER = "/Users/anshulshukla/Downloads/process_data_backup"

def rename_folder_and_images():
    
    if not os.path.exists(ORIGINAL_FOLDER):
        logger.error(f"Original folder {ORIGINAL_FOLDER} does not exist.")
        return

    
    if not os.path.exists(NEW_FOLDER):
        try:
            shutil.move(ORIGINAL_FOLDER, NEW_FOLDER)
            logger.info(f"Renamed folder from {ORIGINAL_FOLDER} to {NEW_FOLDER}")
        except PermissionError:
            logger.error(f"Permission denied when renaming folder. Try running with 'sudo' or adjust permissions with 'chmod -R u+w {ORIGINAL_FOLDER}'")
            return
        except Exception as e:
            logger.error(f"Failed to rename folder: {e}")
            return
    else:
        logger.info(f"Folder {NEW_FOLDER} already exists. Proceeding with renaming files.")

    
    if not os.path.exists(BACKUP_FOLDER):
        try:
            shutil.copytree(NEW_FOLDER, BACKUP_FOLDER)
            logger.info(f"Backup created at {BACKUP_FOLDER}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return
    else:
        logger.info(f"Backup folder {BACKUP_FOLDER} already exists. Proceeding with renaming.")

    
    image_files = [f for f in os.listdir(NEW_FOLDER) if f.lower().endswith('.png')]
    if not image_files:
        logger.warning(f"No .png files found in {NEW_FOLDER}")
        return

   
    image_files.sort()
    logger.info(f"Found {len(image_files)} .png files: {image_files}")

    
    for index, filename in enumerate(image_files, start=1):
        old_path = os.path.join(NEW_FOLDER, filename)
        new_filename = f"report{index}.png"
        new_path = os.path.join(NEW_FOLDER, new_filename)

        try:
            
            if os.path.exists(new_path):
                logger.warning(f"Skipping {new_filename} as it already exists.")
                continue
            
            
            shutil.move(old_path, new_path)
            logger.info(f"Renamed {filename} to {new_filename}")
        except PermissionError:
            logger.error(f"Permission denied when renaming {filename}. Try 'chmod u+w {old_path}' or run with 'sudo'.")
        except Exception as e:
            logger.error(f"Failed to rename {filename} to {new_filename}: {e}")

    logger.info("Renaming completed successfully!")

if __name__ == "__main__":
    logger.info(f"Starting image and folder renaming process for {ORIGINAL_FOLDER}")
    rename_folder_and_images()
    logger.info("Process finished.")