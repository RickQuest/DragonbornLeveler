import os

class AppDataManager:
    def __init__(self, app_name):
        # Initialize the app-specific directory in AppData\Local
        self.local_app_data = os.environ['LOCALAPPDATA']
        self.app_directory = os.path.join(self.local_app_data, app_name)

        # Create the base app directory if it doesn't exist
        if not os.path.exists(self.app_directory):
            os.makedirs(self.app_directory)

    def get_file_path(self, relative_path):
        """
        Returns the full path for a file inside the app directory,
        and ensures that any necessary subdirectories are created.
        """
        # Construct the full path, including any subdirectories
        full_path = os.path.join(self.app_directory, relative_path)

        # Ensure the subdirectories are created if they don't exist
        subfolder_path = os.path.dirname(full_path)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        return full_path

    def save_file(self, filename, content, subfolder=None):
        """ Saves content to a file in the app directory or a subfolder """
        file_path = self.get_file_path(os.path.join(subfolder or '', filename))
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"File saved: {file_path}")
        return file_path

    def read_file(self, filename):
        """ Reads the content from a file in the app directory """
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            raise FileNotFoundError(f"{filename} does not exist in {self.app_directory}")

    def delete_file(self, filename):
        """ Deletes a file from the app directory """
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File deleted: {file_path}")
        else:
            raise FileNotFoundError(f"{filename} does not exist in {self.app_directory}")

    def list_files(self):
        """ Lists all files in the app directory """
        return os.listdir(self.app_directory)


# Create the global instance of AppDataManager for the app
app_data_manager = AppDataManager('DragonbornLeveler')