import json
import os


class Config:
    def __init__(self, program_name):
        self.file_path = os.path.join(os.getenv('localappdata'), program_name, 'config.json')
        self.defaults_file_path = os.path.join(os.getenv('localappdata'), program_name, 'defaults.cnf')
        self.data = self.load_data()

    def load_data(self):
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(self.file_path):
            open(self.file_path, 'w').close()
            self.data = {"servers": []}
            self.save_data()
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def update_data(self, new_data):
        self.data.update(new_data)
        self.save_data()

    def save_data(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def set_defaults_file(self, passwd):
        with open(self.defaults_file_path, 'w') as file:
            file.writelines([
                "[client]\n",
                "password=" + str(passwd)+"\n",
            ])

    def get_defaults_file_path(self):
        return self.defaults_file_path

