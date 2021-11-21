# import of useful packages for building the project
from functools import partial
from tkinter import filedialog
import tkinter as tk
import pandas as pd
import numpy as np
import statistics
import re
import os

# global variables with search keywords
QUESTION_GRADES_REFERENCE = 'valor da questão'
QUESTION_WEIGHTS_REFERENCE = 'taxa de acerto'
NAME_REFERENCE = 'aluno'

class extract_jupyter():
    '''extracting values from jupyter files'''

    def __init__(self, name_ref = NAME_REFERENCE, weights_ref = QUESTION_WEIGHTS_REFERENCE, grades_ref = QUESTION_GRADES_REFERENCE):
        '''
        class constructor
        
        Args:
            name_ref (str) --> keyword for name search
            weights_ref(str) --> keyword to search for hit rates
            grades_ref(str) --> keyword to search for the weights of each note
        '''

        self.name_ref = name_ref
        self.weights_ref = weights_ref
        self.grades_ref = grades_ref

    def ask_for_directory(self):
        '''
        find a directory via graphical interface
        
        Returns:
            path_dir (str) --> directory path
        '''

        root = tk.Tk()
        root.withdraw()

        return filedialog.askdirectory()


    def load_jupyter(self, path_file):
        '''
        load a jupyter file on a string

        Args:
            path_file(str) --> path where jupyter file is located

        Returns:
            jupyter_file (str) --> string with the jupyter file information
        '''

        data = open(path_file, mode = 'r', encoding = 'utf-8')
        jupyter_file = data.read()
        data.close()

        return jupyter_file.lower()

    def find_all_occurrences_index(self, string, sub_string):
        '''
        returns the index of all occurrences from a keyword

        Args:
            string (int) --> string with the jupyter file information
            sub_string (str) --> keyword for search
        
        Returns:
            index_list (list) --> llist with the initial indexes of the keywords found in the file
        '''

        return [sub_init.start() for sub_init in re.finditer(sub_string, string)]

    def get_values(self, string, list_index, max_lenght):
        '''
        returns sub strings from reference indices

        Args:
            string (str) --> string with the jupyter file information
            list_index (list) --> list with the initial indexes of the keywords found
            max_lenght (int) --> maximum string length to be returned
        
        Returns:
            values (list) --> list with found substrings
        '''

        values = list()
        for index in list_index:
            values.append(string[index:(index + max_lenght)])
        
        return values

    def get_files_in_dir(self, path_dir, extension, excesion = ''):
        '''
        find files found in a directory
        
        Args:
            path_dir (str) --> reference directory path
            extension (str) --> extension of files to be found
            excesion (str) --> exception file to be disregarded
        
        Returns:
            ipynb_files (list) --> list of valid files found
        '''

        list_files, ipynb_files = os.listdir(path_dir), list()
        for files in list_files:
            if files.find(extension) != -1 and files.find(excesion) <= 0: 
                ipynb_files.append(path_dir + '/' + files)

        return ipynb_files 

    def adjust_names(self, name_string):
        '''
        refines the name string to obtain the information without noise

        Args:
            name_string (str) --> noisy string containing student names
        Returns:
            name (str) --> student's name
        '''

        try:
            name = name_string.split(':')[1].split('"')[0]
            if name[0].isspace(): name = name[1:]
            if name == '': name = 'Desconhecido'
            return name.title()
        except:
            name = 'Desconhecido'
            return name

    def adjust_weight(self, weight_string, str_confirmation, weights = True): 
        '''
        refines the string with student grade weights and rates

        Args:
            weight_string (str) --> string with student grades or rates and noise
            str_confirmation (str) --> confirmation string to see if the parsing string is valid
            weights (bool) --> flag para identification of obtaining fees or question notes
        Returns:
            weight (float or str) --> student grade or rate
        '''
        
        if weight_string.find(str_confirmation) >= 0:
            weight = [int(word) for word in list(weight_string) if word.isdigit()]
            if len(weight) <= 0: 
                weight = ''
            elif len(weight) >= 2:
                weight = ''.join([str(value) for value in weight])
                weight = int(weight) / (10 ** (len(weight) - 1))
            else: 
                weight = weight[0]

            try:
                if weights:
                    if weight > 1.0 or weight < 0.0: weight = ''
            except:
                pass 
        else:
            weight = ''

        return weight 

    def extract_information(self, path_file):
        '''
        extract student information from a jupyter file

        Args:
            path_file (str) --> jupyter file path
        Returns:
            path_file (str) --> name of the file under analysis
            name (str) --> student's name
            grades (list) --> question weights
            weights (list) --> student hit rates
        '''

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
    '''organizes the information extracted from jupyter into an excel table'''

    def __init__(self, name_ref = NAME_REFERENCE, weights_ref = QUESTION_WEIGHTS_REFERENCE, grades_ref = QUESTION_GRADES_REFERENCE):
        '''
        class constructor

        Args:
            archives (list) --> jupyter file name list
            names (list) --> list with student names
            grades (list) --> list with the weights of each of the questions
            weights (list) --> list of student success rates
        '''
        
        super().__init__(name_ref = name_ref, weights_ref = weights_ref, grades_ref = grades_ref)
        self.archives = list()
        self.names = list()
        self.grades = list()
        self.weights = list()
    
    def set_value(self, values):
        '''
        sets the values obtained by the 'extract_information' method as attributes of the class

        Args:
            values (list) --> list of values obtained by mapping the method 'extract_information'
        '''

        self.archives.append(values[0])
        self.names.append(values[1])
        self.grades.append(values[2])
        self.weights.append(values[3])
    
    def set_values(self, values):
        '''
        sets various values obtained by the 'extract_information' method as class attributes

        Args:
            values (list) --> list of values obtained by mapping the method 'extract_information'
        '''

        _ = list(map(self.set_value, values))

    def get_mode(self):
        '''
        mode of the number of questions evaluated

        Returns:
            grades_mode (int) --> mode of the amount of questions
        '''

        grades_count = list()
        for grades in self.grades:
            grades_count.append(len(list(filter(lambda element: element != '', grades))))
        
        return statistics.mode(grades_count)
    
    def make_data(self, name = 'notas-alunos.xlsx'):
        '''
        adds the information extracted from the jupyter file into an excel file

        Args:
            name (str) --> name of the file to be generated
        '''
        
        grades_mode, data = self.get_mode(), dict()

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
            print('Tabela gerada com sucesso.')
        except Exception as e:
            print(e)
            print('Um erro ocorreu. Lamentamos o ocorrido.')
            
def main():
    '''main function of the project'''

    fun_utils, csv_utils = extract_jupyter(), organize_csv()
    print('=== Gerador de Notas - Introdução ao Processamento de Imagens Digitais ===')
    print('\nObservações Importantes:\n--')
    print('1. Todos os arquivos devem estar adicionados em um diretório (sem subdiretórios).')
    print('2. Verifique se o nome do aluno, o valor e a taxa das questões estão preenchidos.')
    print('3. Verifique se os valores das questões estão consistentes na tabela de Excel gerada.')
    print('4. As taxas de acertos são notas que variam de 0 a 1.')
    os.system('pause'), os.system('cls')

    print('Selecione o diretório com os laboratórios...')
    path_dir = fun_utils.ask_for_directory()
    os.system('cls')

    try:
        files = fun_utils.get_files_in_dir(path_dir = path_dir, extension = '.ipynb', excesion = 'checkpoints')
        results = map(fun_utils.extract_information, files)
        csv_utils.set_values(list(results))
    except:
        print('Não foi possível localizar o diretório.')
        os.system('pause')
        return

    print('Laboratórios encontrados:\n--')
    for index, archive in enumerate(csv_utils.archives):
        print('{} ==> {}'.format(index + 1, archive))
    print('--\n{} Laboratórios encontrados.'.format(len(csv_utils.archives)))
    os.system('pause'), os.system('cls')

    print('Selecione o diretório onde será salvo a tabela...')
    table_dir = fun_utils.ask_for_directory()
    os.system('cls')
    csv_utils.make_data(name = table_dir + '/notas-alunos.xlsx')
    os.system('pause')

if __name__ == '__main__':
    main()