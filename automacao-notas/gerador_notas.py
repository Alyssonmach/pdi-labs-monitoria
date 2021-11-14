from tkinter import filedialog
import tkinter as tk
import re
import os

NAME_REFERENCE = 'Aluno'
QUESTION_WEIGHTS_REFERENCE = 'Taxa de acerto'

class extract_jupyter():

    def __init__(self, name_ref = NAME_REFERENCE, question_ref = QUESTION_WEIGHTS_REFERENCE):

        self.name_ref = name_ref
        self.question_ref = question_ref

        return 

    def ask_for_directory(self):

        root = tk.Tk()
        root.withdraw()

        return filedialog.askdirectory()


    def load_jupyter(self, path_file):

        data = open(path_file, mode = 'r', encoding = 'utf-8')
        jupyter_file = data.read()
        data.close()

        return jupyter_file

    def find_all_occurrences_index(self, string, sub_string):

        return [sub_init.start() for sub_init in re.finditer(sub_string, string)]

    def get_values(self, string, list_index, max_lenght):

        values = list()
        for index in list_index:
            values.append(string[index:(index + max_lenght)])
        
        return values

    def get_files_in_dir(self, path_dir, extension, excesion = ''):

        list_files, ipynb_files = os.listdir(path_dir), list()
        for files in list_files:
            if files.find(extension) != -1 and files.find(excesion) <= 0: 
                ipynb_files.append(path_dir + '/' + files)

        return ipynb_files 

    def adjust_names(self, name_string):
        name = name_string.split(':')[1].split('"')[0]
        if name[0].isspace(): name = name[1:]

        return name

    def adjust_weight(self, weight_string): 
        
        weight = [int(word) for word in list(weight_string) if word.isdigit()]
        if len(weight) > 2 or len(weight) <= 0: weight = ''
        elif len(weight) == 2: weight = int(str(weight[0]) + str(weight[1])) / 10
        else: weight = weight[0]

        if weight > 1.0 or weight < 0.0: weight = ''

        return weight 

    def extract_information(self, path_file):

        jupyter_file = self.load_jupyter(path_file = path_file)
        names = self.find_all_occurrences_index(string = jupyter_file, sub_string = self.name_ref)
        weights = self.find_all_occurrences_index(string = jupyter_file, sub_string = self.question_ref)
        names = self.get_values(string = jupyter_file, list_index = names, max_lenght = 100)
        weights = self.get_values(string = jupyter_file, list_index = weights, max_lenght = 30)

        return list(map(self.adjust_names, names)), list(map(self.adjust_weight, weights)) 

def main():

    fun_utils = extract_jupyter()
    path_dir = fun_utils.ask_for_directory()
    files = fun_utils.get_files_in_dir(path_dir = path_dir, extension = '.ipynb', excesion = 'checkpoints')
    results = map(fun_utils.extract_information, files)
    name, weights = list(results)[0]
    print(name, weights)

    return

if __name__ == '__main__':
    main()

