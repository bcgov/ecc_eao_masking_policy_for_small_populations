# ================================================================================================#
#                                                                                                 #
#                       ECC EAO Masking Policy for Small Populations                              #
#                                                                                                 #
# ------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Create Date: 2023.10.26                                                                         #
# Author: Okan K. Orhan, okan.orhan@gov.bc.ca                                                     #
# Description: This routine applies masking for chosen data files                                 #
#                                                                                                 #
# ================================================================================================#

'''
Module providing masking capabilities for a chosen data file.
'''
# Standard libraries
import heapq
import os
import itertools
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import numpy as np

# User-defined libraries
from masking_policy_for_small_populations_lib import terminal_interactions

class GlobalMaskingPol:
    '''
        Class to define current masking limits
    '''
    def __init__(self) -> None:
        self.gmp_msk_max = 9
        self.gmp_msk_min = 1

def import_unmasked_data(file_path:str = None) -> pd.DataFrame:
    '''
    Importing unmasked data from a CSV or XLSX file into a Pandas dataframe

    Args:
        file_path (str): full path to file
        unmasked_data (pd.DataFrame): unmasked data from file_path

    Returns:
        unmasked_data (pd.DataFrame): unmasked data
    '''   
    if file_path is None:
        OutputClass.process('Please select a source file')
        Tk().withdraw()
        file_path = askopenfilename(filetypes=[('Choose a CVS or XLSX File', '*.csv *.xlsx')])
    if os.path.splitext(file_path)[1] in ['.csv', '.CSV']:
        unmasked_data: pd.DataFrame = pd.read_csv(file_path)
    if os.path.splitext(file_path)[1] in ['.xlsx', '.XLSX']:
        sheet_name = InputClass.get_inp('Excel sheet name')
        unmasked_data: pd.DataFrame = pd.read_excel(file_path, sheetname = sheet_name)
    return file_path, unmasked_data    

def export_masked_data(masked_data: pd.DataFrame, input_file_path: str) -> None:
    '''
    Exporting masked data into a CSV or XLSX file

    Args:
        masked_data (pd.DataFrame): final masked data
        dir_path (str): directory path to save masked file
        file_name (str): file name for masked data
    '''
    OutputClass.process(f'Generating {os.path.basename(input_file_path)}')
    if os.path.splitext(input_file_path)[1] in ['.csv', '.CSV']:
        output_file_path = f'{os.path.splitext(input_file_path)[0]}_Masked.csv'
        masked_data.to_csv(output_file_path, index=False, header=True, mode='w')
    if os.path.splitext(input_file_path)[1] in ['.xlsx', '.XLSX']:
        output_file_path = f'{os.path.splitext(input_file_path)[0]}__Masked.xlsx'
        writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')
        masked_data.to_excel(writer, index=False)
        writer.close()
    OutputClass.success(f'{output_file_path} is generated!')

def get_partition_column_names(data_column_info_dict: dict) -> list[str]:
    '''
    Function to collect partition column names. Please see User_Guide.pdf for further information.

    Args:
        data_column_info_dict (dict): column info from soruce data

    Returns:
        partitition_column_names (list[str]): column names
    '''
    partition_column_names: list[str] = []
    
    OutputClass.info('''
                     A Partition Column is a column that divides the data into groups, 
                     where each group is separetely assessed for masking conditions. 
                     For example, "year" can be a Partition Column, where numbers for 
                     each year commonly subject to masking policy in itself.
                     ''')
    OutputClass.process('''Type a Partition Column Number and hit enter. Type done to finish.''')
    user_input: str = ''
    while user_input != 'done':
        user_input = InputClass.get_inp('Partition Column Number')
        if user_input.lower() != 'done':
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in partition_column_names:
                OutputClass.warning('Repeated column number!')
            else:
                partition_column_names.append(data_column_info_dict[user_input])

    return partition_column_names

def get_subcategory_column_names(data_column_info_dict: dict,
                                partition_column_names: list) -> list[str]:
    '''
    Function to collect subcategory column names. Please see User_Guide.pdf for further information.

    Args:
        partition_column_names (list): column names
        data_column_info_dict (dict): column info from soruce data

    Returns:
        subcategory_column_names (list[str]): column names
    '''
    subcategory_column_names: list[str] = []
    OutputClass.info('''
                     Subcategory Column is a column that has options for a category in data. 
                     For examples, "gender" is commonly a Subcategory Colum with options such as "Men", "Women", "Non-Binary", "All". 
                     Thus, the masking rotuine will assess the masking conditions among values of a given 
                     Subcategory Column for each combinations of remaining Subcategory Columns. 
                     This ensures that a data, whcih should be masked, cannot be revealed thorugh simple subtraction using "All" value.''')
    OutputClass.process('''Type a Subcategory Column Number and hit enter. Type done to finish''')
    user_input: str = ''
    while user_input != 'done':
        user_input = InputClass.get_inp('Subcategory Column Number')
        if user_input.lower() != 'done':
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in subcategory_column_names:
                OutputClass.warning('Repeated column number!')
            elif data_column_info_dict[user_input] in partition_column_names:
                OutputClass.warning('Column in Partitions Column List!')
            else:
                subcategory_column_names.append(data_column_info_dict[user_input])
    return subcategory_column_names

def get_measure_column_names(data_column_info_dict: dict,
                                partition_column_names: list,
                                subcategory_column_names: list) -> (str, list[str]):
    '''
    Function to collect measure column names. Please see User_Guide.pdf for further information.

    Args:
        partition_column_names (list): column names
        subcategory_column_names (list): column names
        data_column_info_dict (dict): column info from soruce data

    Returns:
        measure_columns_relation_type (str): column relation type
        measure_column_names (list[str]): column names
    '''
    measure_column_names: list[str] = []
    OutputClass.info('''
                     Measure Column is a column that containg actual headcounts and will be used to assess 
                     the masking conditions and be masked if these conditions are met. 
                     There can be multiple Measure Columns, which can be independent or related through a relation.
                     ''')
    OutputClass.info('''
                     Measure Columns Relation Type defines relation between Measure Columns 
                     for cross-assessment the masking conditions to avoid indirect violation of the masking policy.
                     ''')
    measure_columns_realtion_type = InputClass.get_option('Options for Measure Columns Relation Type','Relation Type',\
                        {'0':'No Relation -> No Measure Columns are used to obtain another column.',
                         '1':'Rate -> Two Measure Columns are used to calculate a rate column.',
                         '2':'Sum -> Sum of two or more Measure Columns is presented in another column.'})
    
    
    if measure_columns_realtion_type == '0':
        user_input: str = ''
        while user_input != 'done':
            user_input = InputClass.get_inp('Measure Column Number')
            if user_input.lower() != 'done':
                if user_input not in list(data_column_info_dict)[0:]:
                    OutputClass.warning('Invalid column number!')
                elif data_column_info_dict[user_input] in measure_column_names:
                    OutputClass.warning('Repeated column number!')
                elif data_column_info_dict[user_input] in partition_column_names \
                    or data_column_info_dict[user_input] in subcategory_column_names:
                    OutputClass.warning('Column in Partition Columns List or Subcategory Columns List!')
                else:
                    measure_column_names.append(data_column_info_dict[user_input])
            
    if measure_columns_realtion_type == '1':
        user_input: str = ''
        while True:
            user_input = InputClass.get_inp('Numerator Column Number') 
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in partition_column_names \
                or data_column_info_dict[user_input] in subcategory_column_names:
                OutputClass.warning('Column in Partition Columns List or Subcategory Columns List!')
            else:
                measure_column_names.append(data_column_info_dict[user_input])
                break
        user_input: str = '' 
        while True:
            user_input = InputClass.get_inp('Denominator Column Number') 
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in measure_column_names:
                OutputClass.warning('It is already Numarator Column Number!')
            elif data_column_info_dict[user_input] in partition_column_names \
                or data_column_info_dict[user_input] in subcategory_column_names:
                OutputClass.warning('Column in Partition Columns List or Subcategory Columns List!')
            else:
                measure_column_names.append(data_column_info_dict[user_input])
                break
                
    if measure_columns_realtion_type == '2':
        user_input: str = ''
        while True:
            user_input = InputClass.get_inp('Sum Column Number') 
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in partition_column_names \
                or data_column_info_dict[user_input] in subcategory_column_names:
                OutputClass.warning('Column in Partition Columns List or Subcategory Columns List!')
            else:
                measure_column_names.append(data_column_info_dict[user_input])
                break
        user_input: str = '' 
        OutputClass.process('Type a Element Column Number and hit enter. Type done to finish.')
        while user_input != 'done':
            user_input = InputClass.get_inp('Element Column Numbers')
            if user_input.lower() != 'done':
                if user_input not in list(data_column_info_dict)[0:]:
                    OutputClass.warning('Invalid column number!')
                elif data_column_info_dict[user_input] in measure_column_names:
                    OutputClass.warning('Repeated column number!')
                elif data_column_info_dict[user_input] in partition_column_names \
                    or data_column_info_dict[user_input] in subcategory_column_names:
                    OutputClass.warning('Column in Partition or Subcategory Column List!')
                else:
                    measure_column_names.append(data_column_info_dict[user_input])      

    return measure_columns_realtion_type, measure_column_names

def get_additional_masking_column_names(data_column_info_dict: dict,
                                partition_column_names: list,
                                subcategory_column_names: list,
                                measure_column_names: list) -> list[str]:
    '''
    Function to collect additionan masking column names. Please see User_Guide.pdf for further information.

    Args:
        partition_column_names (list): column names
        subcategory_column_names (list): column names
        measure_column_names (list): column names
        data_column_info_dict (dict): column info from soruce data

    Returns:
        additional_masking_column_names (list[str]): column names
    '''
    additional_masking_column_names: list[str] = []
    OutputClass.info('''Additional Masking Column is a column, whcih will be masked if any of Measure Column in a given row
                        is alrecy masked.''')
    OutputClass.info('Type a Additional Masking Column Number and hit enter. Type done to finish.')
    user_input: str = ''
    while user_input != 'done':
        user_input = InputClass.get_inp('Additional Masking Column Number')
        if user_input.lower() != 'done':
            if user_input not in list(data_column_info_dict)[0:]:
                OutputClass.warning('Invalid column number!')
            elif data_column_info_dict[user_input] in subcategory_column_names:
                OutputClass.warning('Repeated column number!')
            elif data_column_info_dict[user_input] in partition_column_names \
                or data_column_info_dict[user_input] in subcategory_column_names \
                or data_column_info_dict[user_input] in measure_column_names:
                OutputClass.warning('Column in Partition Columns List or Subcategory Columns List or Measure Columns List!')
            else:
                additional_masking_column_names.append(data_column_info_dict[user_input])
    return additional_masking_column_names

def apply_full_masking(unmasked_data: pd.DataFrame, 
                       masking_string: str = 'Msk',
                       partition_column_numbers: list | None = None,
                       subcategory_column_numbers: list | None = None,
                       measure_columns_relation_type: str | None = None,
                       measure_column_numbers: list | None = None,
                       additional_masking_column_flag: bool = False,
                       additional_masking_column_numbers: list | None = None
                       ) -> dict:
    '''
    Main function to determine indices to be masked.

    Args:
        unmasked_data (pd.DataFrame): unmasked data
        masking_string (str, optional): string to replace numner to be masked. Defaults to 'Msk'.
        partition_column_numbers (list | None, optional): partition columns (see User_Guide). Defaults to None.
        subcategory_column_numbers (list | None, optional): subcategory columns (see User_Guide). Defaults to None.
        measure_columns_relation_type (str | None, optional): _description_. Defaults to None.
        measure_column_numbers (list | None, optional): measure columns (see User_Guide). Defaults to None.
        additional_masking_column_flag (bool, optional): boolen for additional columns to be masked. Defaults to False.
        additional_masking_column_numbers (list | None, optional): additional columns to be masked (see User_Guide). Defaults to None.

    Returns:
        
    '''

    # Collecting column numbers and names
    data_column_info_dict:dict[str:str] = {}
    column_number_enum = 1
    for column_name_enum in unmasked_data.columns:
        data_column_info_dict[str(column_number_enum)] = column_name_enum
        column_number_enum += 1

    if partition_column_numbers is None or subcategory_column_numbers is None or measure_column_numbers is None:
        OutputClass.info('Unmasked Data Column Number and Names')
        print('\n'+'\n'.join((' : '.join(item) for item in data_column_info_dict.items()))+'\n')

    # Checking for empty columns
    for column_name_enum in unmasked_data.columns:
        if unmasked_data[column_name_enum].empty:
            OutputClass.error(f'{column_name_enum} is empty! Please correct the source file!') 

    # Partition Column Names
    partition_column_names:list[str] = []
    if partition_column_numbers is None:
        partition_column_names = get_partition_column_names(data_column_info_dict)
    else:
        for column_number_enum in partition_column_numbers:
            partition_column_names.append(data_column_info_dict[column_number_enum])

    # Subcategory Column Names
    subcategory_column_names:list[str] = []
    if subcategory_column_numbers is None or measure_columns_relation_type is None:
        subcategory_column_names = get_subcategory_column_names(data_column_info_dict, partition_column_names)
    else:
        for column_number in subcategory_column_numbers:
            subcategory_column_names.append(data_column_info_dict[column_number])

    # Measure Column Names
    measure_column_names:list[str] = []
    if measure_columns_relation_type is None:  
        measure_columns_relation_type, measure_column_names = get_measure_column_names(data_column_info_dict, 
                                                                                       partition_column_names, 
                                                                                       subcategory_column_names)        
    else:
        for column_number_enum in measure_column_numbers:
            measure_column_names.append(data_column_info_dict[column_number_enum])
        

    # Additional masking Column Names
    additional_masking_column_names:list[str] = []
    if additional_masking_column_flag is True:
        if additional_masking_column_numbers is None:
            additional_masking_column_names = get_additional_masking_column_names(data_column_info_dict,
                                                                                  partition_column_names,
                                                                                  subcategory_column_names,
                                                                                  measure_column_names)
        else:
            for column_number_enum in additional_masking_column_numbers:
                additional_masking_column_names.append(data_column_info_dict[column_number_enum])


    # Three set of masking condition will be evaluated.
    # Distinct index and column numbers will be collected into a dict.
    masked_cell_index:dict[int, list] = {}
    # 1) Simple masking procedure
    for row_index_enum in unmasked_data.index.values:
        masked_cell_index[row_index_enum] = []
        for column_name_enum in measure_column_names:
            temp_value = unmasked_data.loc[row_index_enum, column_name_enum]
            if temp_value not in [None, 'nan'] and \
                temp_value >= GlobalMaskingPol().gmp_msk_min \
                and temp_value <= GlobalMaskingPol().gmp_msk_max:
                masked_cell_index[row_index_enum].append(column_name_enum)
 
    # 2) Vertical masking procedure for subcategories
    # This routine requires at least one Subcategory Column
    if len(subcategory_column_names) >= 1:
        partition_column_values_comb = list(unmasked_data[partition_column_names].drop_duplicates().reset_index(drop = True).values)
        subcategory_column_names_subset_comb = list(itertools.combinations(subcategory_column_names, len(subcategory_column_names)-1))
        for partition_column_values in partition_column_values_comb:
            partioned_data= unmasked_data.copy()
            for partition_column_names_enum, partition_column_names_value in enumerate(partition_column_names):
                partioned_data = partioned_data.loc[partioned_data[partition_column_names_value] == partition_column_values[partition_column_names_enum]]          
            for subcategory_column_names_subset in subcategory_column_names_subset_comb:
                subcategory_column_values_subset_comb = list(unmasked_data[list(subcategory_column_names_subset)].drop_duplicates().reset_index(drop = True).values)
                for subcategoryu_column_values_subset in subcategory_column_values_subset_comb:
                    partioned_subcategoried_data = partioned_data.copy()
                    for subcategory_column_names_subset_enum, subcategory_column_names_subset_value in enumerate(subcategory_column_names_subset):
                        partioned_subcategoried_data = partioned_subcategoried_data.loc[partioned_subcategoried_data[subcategory_column_names_subset_value] == subcategoryu_column_values_subset[subcategory_column_names_subset_enum]]
                    temp_index_list = partioned_subcategoried_data.index.values
                    for column_name_enum in measure_column_names:
                        temp_cond = True
                        while temp_cond:
                            try:
                                temp_value_list = partioned_subcategoried_data[column_name_enum].values
                                n2mins = heapq.nsmallest(2, [i for i in temp_value_list if i != 0])
                                n1min= min(n2mins)
                                '''
                                temp_hist_list = list(itertools.chain.from_iterable([masked_cell_index.get(key) \
                                                                                            for key in partioned_subcategoried_data[column_name_enum].index]))
                                for temp_value_enum, temp_value in enumerate(temp_value_list):
                                    if column_name_enum in temp_hist_list and temp_value == n1min:
                                        masked_cell_index[temp_index_list[temp_value_enum]].append(column_name_enum)
                                '''                                                           
                                if n1min <= GlobalMaskingPol().gmp_msk_max:
                                    for temp_value_enum, temp_value in enumerate(temp_value_list):
                                        if n1min <= GlobalMaskingPol().gmp_msk_max:
                                            if temp_value in n2mins \
                                                and column_name_enum not in masked_cell_index[temp_index_list[temp_value_enum]]:
                                                masked_cell_index[temp_index_list[temp_value_enum]].append(column_name_enum)
                                break
                            except ValueError:
                                temp_cond = False
                            except TypeError:
                                temp_cond = False
        
    # 3) Horizontal masking procedure for measure column relations
    if measure_columns_relation_type == '1':
        for row_index_enum in unmasked_data.index.values:
            if len(set(measure_column_names).intersection(masked_cell_index[row_index_enum])) > 0:
                masked_cell_index[row_index_enum] += measure_column_names
            masked_cell_index[row_index_enum] = np.unique(np.array(masked_cell_index[row_index_enum])).tolist()
            temp_value_list =[]
            for column_name_enum in measure_column_names:
                if unmasked_data.loc[row_index_enum, column_name_enum] not in [None, 'nan']:
                    temp_value_list.append(unmasked_data.loc[row_index_enum, measure_column_names])
            if len(temp_value_list) >= 1:
                temp_cond = True
                while temp_cond:
                    try:                    
                        n1min = min(temp_value_list)
                        if n1min <= GlobalMaskingPol().gmp_msk_max and n1min >= GlobalMaskingPol().gmp_msk_min:
                            for column_name_enum in measure_column_names:
                                if column_name_enum not in masked_cell_index[row_index_enum]:
                                    masked_cell_index[row_index_enum].append(column_name_enum)
                        break
                    except ValueError:
                        temp_cond = False
                    except TypeError:
                        temp_cond = False

    if measure_columns_relation_type == '2':
        for row_index_enum in unmasked_data.index.values:
            if measure_column_names[0] in masked_cell_index[row_index_enum]:
                masked_cell_index[row_index_enum] += measure_column_names
            else:
                temp_value_list = []
                for column_name_enum in measure_column_names:
                    if unmasked_data.loc[row_index_enum, column_name_enum] not in [None, 'nan']:
                        temp_value_list.append(unmasked_data.loc[row_index_enum, column_name_enum])
                if len(temp_value_list) >= 2:
                    n2mins = heapq.nsmallest(2, [i for i in temp_value_list if i != 0])
                    if len(n2mins) == 2:
                        n1min= min(n2mins)
                        if len(set(measure_column_names).intersection(masked_cell_index[row_index_enum])) > 0:
                            for column_enum in measure_column_names:
                                if unmasked_data.loc[row_index_enum, column_enum] == n1min:
                                    masked_cell_index[row_index_enum].append(column_enum)
                        if n1min <= GlobalMaskingPol().gmp_msk_max: 
                            for column_enum in measure_column_names:
                                if unmasked_data.loc[row_index_enum, column_enum] in n2mins:
                                    masked_cell_index[row_index_enum].append(column_enum)
            masked_cell_index[row_index_enum] = np.unique(np.array(masked_cell_index[row_index_enum])).tolist()
                            
                        
    unmasked_data = unmasked_data.astype(str)
    for index_enum, column_list_enum in masked_cell_index.items():
        if len(column_list_enum) > 0:
            if len(additional_masking_column_names) > 0:
                column_list_enum += additional_masking_column_names
            unmasked_data.loc[index_enum, list(set(column_list_enum))] = masking_string
    return unmasked_data


def main_loop() -> None:
    '''
    Main program execution
    '''
    OutputClass()
    input_file_path, unmasked_data = import_unmasked_data()
    masked_data = apply_full_masking(unmasked_data)
    export_masked_data(masked_data, input_file_path)

# Program entry point
if __name__ == '__main__':
    main_loop()