from functools import partial
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import numpy as np
import statistics
import re
import os

QUESTION_GRADES_REFERENCE = 'valor da questão'
QUESTION_WEIGHTS_REFERENCE = 'taxa de acerto'
NAME_REFERENCE = 'aluno'

class extract_jupyter():

    def __init__(self, name_ref = NAME_REFERENCE, weights_ref = QUESTION_WEIGHTS_REFERENCE, grades_ref = QUESTION_GRADES_REFERENCE):

        self.name_ref = name_ref
        self.weights_ref = weights_ref
        self.grades_ref = grades_ref

        return 

    def ask_for_directory(self):

        root = tk.Tk()
        root.withdraw()

        return filedialog.askdirectory()


    def load_jupyter(self, path_file):

        data = open(path_file, mode = 'r', encoding = 'utf-8')
        jupyter_file = data.read()
        data.close()

        return jupyter_file.lower()

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

        try:
            name = name_string.split(':')[1].split('"')[0]
            if name[0].isspace(): name = name[1:]
            if name == '': name = 'Desconhecido'
            return name.title()
        except:
            name = 'Desconhecido'
            return name

    def adjust_weight(self, weight_string, str_confirmation, weights = True): 
        
        if weight_string.find(str_confirmation) >= 0:
            weight = [int(word) for word in list(weight_string) if word.isdigit()]
            if len(weight) > 2 or len(weight) <= 0: weight = ''
            elif len(weight) == 2: weight = int(str(weight[0]) + str(weight[1])) / 10
            else: weight = weight[0]

            try:
                if weights:
                    if weight > 1.0 or weight < 0.0: weight = ''
            except:
                pass 
        else:
            weight = ''

        return weight 

    def extract_information(self, path_file):

        jupyter_file = self.load_jupyter(path_file = path_file)
        name = self.find_all_occurrences_index(string = jupyter_file, sub_string = self.name_ref)
        grades = self.find_all_occurrences_index(string = jupyter_file, sub_string = self.grades_ref)
        weights = self.find_all_occurrences_index(string = jupyter_file, sub_string = self.weights_ref)
        name = self.get_values(string = jupyter_file, list_index = name, max_lenght = 100)
        grades = self.get_values(string = jupyter_file, list_index = grades, max_lenght = 25)
        weights = self.get_values(string = jupyter_file, list_index = weights, max_lenght = 25)
        partial_adjust_weights = partial(self.adjust_weight, str_confirmation = 'taxa de acerto:')
        partial_adjust_grades = partial(self.adjust_weight, str_confirmation = 'valor da questão:', weights = False)
        
        return path_file.split('/')[-1], self.adjust_names(name[0]), list(map(partial_adjust_grades, grades)), list(map(partial_adjust_weights, weights)) 

class organize_csv(extract_jupyter):

    def __init__(self, name_ref = NAME_REFERENCE, weights_ref = QUESTION_WEIGHTS_REFERENCE, grades_ref = QUESTION_GRADES_REFERENCE):
        
        super().__init__(name_ref = name_ref, weights_ref = weights_ref, grades_ref = grades_ref)
        self.archives = list()
        self.names = list()
        self.grades = list()
        self.weights = list()

        return
    
    def set_value(self, values):

        self.archives.append(values[0])
        self.names.append(values[1])
        self.grades.append(values[2])
        self.weights.append(values[3])

        return 
    
    def set_values(self, values):

        _ = list(map(self.set_value, values))

        return 

    def get_mode(self):

        grades_count = list()
        for grades in self.grades:
            grades_count.append(len(list(filter(lambda element: element != '', grades))))
        
        return statistics.mode(grades_count)

    
    def make_data(self, name = 'notas-alunos.xlsx'):
        
        grades_mode = self.get_mode()
        data = dict()

        data['Arquivo'], data['Nome'], data['Nota'] = list(), list(), list()
        for index in range(0, grades_mode):
            data['Taxa ' + str(index + 1)], data['Valor ' + str(index + 1)] = list(), list()

        for index in range(0, len(self.archives)):
            weights = list(filter(lambda element: element != '', self.weights[index]))
            grades = list(filter(lambda element: element != '', self.grades[index]))

            if len(weights) == len(grades):
                data['Arquivo'].append(self.archives[index])
                data['Nome'].append(self.names[index])
                data['Nota'].append(np.sum(np.array(weights) * np.array(grades)))


                for item in range(0, len(grades)):
                    data['Taxa ' + str(item + 1)].append(weights[item]) 
                    data['Valor ' + str(item + 1)].append(grades[item])
                
            else:
                os.system('cls')
                print('Problema ao computar a nota de {}.'.format(self.archives[index]))
                os.system('pause')
        
        try:
            dataframe = pd.DataFrame(data)
            dataframe.to_excel(name, index = False)
            return True
        except:
            os.system('cls')
            print('Erro ao gerar o dataframe.')
            os.system('pause')
            return False

def main():

    fun_utils, csv_utils = extract_jupyter(), organize_csv()
    print('=== Gerador de Notas - Int. PDI 2021.1 ===')
    print('\nObservações Importantes:\n--')
    print('1. Todos os arquivos devem estar adicionados em um diretório (sem subpastas).')
    print('2. Verifique se o nome do aluno, o valor e a taxa das questões estão preenchidos.')
    print('3. Verifique se os valores das questões estão consistentes na tabela de Excel gerada.')
    print('4. As taxas de acertos são notas que variam de 0 a 1.')
    os.system('pause')
    os.system('cls')

    print('Selecione o diretório com os laboratórios...')
    path_dir = fun_utils.ask_for_directory()
    os.system('cls')

    files = fun_utils.get_files_in_dir(path_dir = path_dir, extension = '.ipynb', excesion = 'checkpoints')
    results = map(fun_utils.extract_information, files)
    csv_utils.set_values(list(results))

    print('Laboratórios encontrados:\n--')
    for index, archive in enumerate(csv_utils.archives):
        print('{} ==> {}'.format(index + 1, archive))
    os.system('pause')
    os.system('cls')

    print('Selecione o diretório onde será salvo a tabela...')
    table_dir = fun_utils.ask_for_directory()
    state = csv_utils.make_data(name = table_dir + '/notas-alunos.xlsx')
    os.system('cls')
    if state:
        print('Tabela gerada com sucesso. Verifique os dados gerados.')
    else:
        print('Um erro impediu que a tabela fosse gerada. Verifique os laboratórios')
    os.system('pause')

    return


if __name__ == '__main__':
    main()

