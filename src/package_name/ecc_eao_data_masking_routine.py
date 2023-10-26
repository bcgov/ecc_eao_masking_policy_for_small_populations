# ================================================================================================#
#                                                                                                 #
#                                              Data Masking                                       #
#                                                                                                 #
# ------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Create Date: 2023.07.04                                                                         #
# Author: Okan K. Orhan, okan.orhan@gov.bc.ca                                                     #
# Description: This code apply masking for chosen data files                                      #
#                                                                                                 #
# ------------------------------------------------------------------------------------------------#
# Summary of Changes:                                                                             #
#                                                                                                 #
# Date(yyyy-mm-dd)  Author                   Email                   Comments                     #
# ----------        -----------------------  ----------------------  -------------------------    #
# 2023-08-25        Matthew Hall             Matthew.1.Hall          Fixing typings, removed      #
#                                            @gov.bc.ca              unsedlibraries, added        #
#                                                                    docstrings                   #
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
from terminal_interactions import OutputClass, InputClass

def get_csv_files(raw_data: pd.DataFrame, dir_path: str, file_name: str) -> None:
    '''
    Function to generate CSV file from pandas DataFrame

    Args:
        raw_data (pd.DataFrame): _description_
        dir_path (str): _description_
        file_name (str): _description_
    '''
    # Building full file path
    file_path = f'{dir_path}/{file_name}'

    # Generating CSV file
    OutputClass.process(f'Generating {file_name}')
    raw_data.to_csv(file_path, index=False, header=True, mode='w')
    OutputClass.success(f'{file_path} is generated')


def apply_full_masking(raw_data: pd.DataFrame, mask_string: str = 'Msk',
                       partition_column_numbers: list | None = None,
                       subcategory_column_numbers: list | None = None,
                       measure_column_relation_type: str | None = None,
                       measure_column_numbers: list | None = None,
                       additional_masking_column_flag: bool = False,
                       additional_masking_column_numbers: list | None = None
                       ) -> pd.DataFrame:
    '''
    _summary_

    Args:
        unmsk_data (pd.DataFrame): _description_
        msk_string (str, optional): _description_. Defaults to 'Msk'.
        part_col_nums (list | None, optional): _description_. Defaults to None.
        scat_col_nums (list | None, optional): _description_. Defaults to None.
        mea_col_rel_type (str | None, optional): _description_. Defaults to None.
        mea_col_nums (list | None, optional): _description_. Defaults to None.
        add_msk_col (bool, optional): _description_. Defaults to False.
        add_msk_col_nums (list | None, optional): _description_. Defaults to None.

    Returns:
        pd.DataFrame: _description_
    '''
    gmp_msk_max: int = 9
    gmp_msk_min: int = 1

    # Collecting column numbers and names
    data_columns: dict[str, str] = {}
    tind = 1
    for col in raw_data.columns:
        data_columns[str(tind)] = col
        tind += 1

    if (partition_column_numbers is None or
        subcategory_column_numbers is None or
            measure_column_numbers is None):
        OutputClass.info('Unmasked Data Columns')
        print('\n'+'\n'.join((' : '.join(item)
              for item in data_columns.items()))+'\n')

    # Partition Column Names
    partition_column_names: list[str] = get_partition_column_names(
        partition_column_numbers, data_columns)

    # Subcategory Column Names
    subcategory_column_names: list[str] = get_subcategory_column_names(
        subcategory_column_numbers, data_columns, partition_column_names)

    # Measure Column Names
    mea_col_names: list[str] = []
    if measure_column_relation_type is None:
        OutputClass.info('''Measure Column is a integer number column, for which conditions of
                      masking will be assessed. For example, "writer_count" is generally a 
                      Measure Column, whose values will be compared with global masking 
                      conditions.''')
        OutputClass.info('''Relation of Measure Columns to relevant calculated column(s) is required
                      to ensure not to under- or over- masking. For example, if a
                      "pariticipation_rate" is present, it relates "writer_count" to
                      "expected_count". Thus, one needs to mask "expected_count" if "writer_count"
                      is needed to be masked regardless its value.''')
        options: dict[str, str] = {
            '0': 'No Relation -> No Measure Columns are used to obtain another column.',
            '1': 'Rate -> Two Measure Columns are used to calculate a rate column.',
            '2': 'Sum -> Sum of two or more Measure Columns is presented in another column.'}
        topt: str = InputClass.get_option(
            'Options for Relation Type', 'Relation Type', options)
        OutputClass.info(
            'Type a Measure Column Number and hit enter. Type done to finish.')
        if topt == '0':
            user_input: str = ''
            while user_input != 'done':
                user_input = InputClass.get_inp('Measure Column Number')
                if user_input.lower() != 'done':
                    if user_input not in list(data_columns)[0:]:
                        OutputClass.warning('Invalid column number!')
                    elif data_columns[user_input] in subcategory_column_names:
                        OutputClass.warning('Repeated column number!')
                    elif (data_columns[user_input] in partition_column_names or
                          data_columns[user_input] in subcategory_column_names):
                        OutputClass.warning(
                            'Column in Partition or Subcategory Column List!')
                    else:
                        mea_col_names.append(data_columns[user_input])

        if topt == '1':
            while True:
                user_input = InputClass.get_inp('Numerator Column Number')
                if data_columns[user_input] not in mea_col_names:
                    OutputClass.warning('Invalid column number!')
                else:
                    mea_col_names.append(data_columns[user_input])
                    break

            while True:
                user_input = InputClass.get_inp('Denominator Column Number')
                if data_columns[user_input] not in mea_col_names:
                    OutputClass.warning('Invalid column number!')
                else:
                    mea_col_names.append(data_columns[user_input])
                    break

        if topt == '2':
            mea_col_names: list[str] = []
            while True:
                user_input = InputClass.get_inp('Sum Column Number')
                if user_input not in list(data_columns)[0:]:
                    OutputClass.warning('Invalid column number!')
                else:
                    mea_col_names.append(data_columns[user_input])
                    break

            OutputClass.info(
                'Type Element Columns and hit enter. Type done to finish.')
            user_input = ''
            while user_input != 'done':
                user_input = InputClass.get_inp('Element Column Numbers')
                if user_input.lower() != 'done':
                    if user_input not in list(data_columns)[0:]:
                        OutputClass.warning('Invalid column number!')
                    elif data_columns[user_input] in subcategory_column_names:
                        OutputClass.warning('Repeated column number!')
                    elif (data_columns[user_input] in partition_column_names or
                          data_columns[user_input] in subcategory_column_names):
                        OutputClass.warning(
                            'Column in Partition or Subcategory Column List!')
                    else:
                        mea_col_names.append(data_columns[user_input])

        if InputClass.get_boolen_opt('Additional columns to mask'):
            additional_masking_column_flag = True
    else:
        if measure_column_numbers is not None:
            for user_input in measure_column_numbers:
                mea_col_names.append(data_columns[user_input])

    # Masking Column Names
    add_msk_col_names: list[str] = []
    if additional_masking_column_flag is True:
        if subcategory_column_numbers is None:
            OutputClass.info(
                'Type a Additional Masking Column Number and hit enter. Type done to finish.')
            user_input = ''
            while user_input != 'done':
                user_input = InputClass.get_inp('Masking Column Number')
                if user_input.lower() != 'done':
                    if user_input not in list(data_columns)[0:]:
                        OutputClass.warning('Invalid column number!')
                    elif data_columns[user_input] in subcategory_column_names:
                        OutputClass.warning('Repeated column number!')
                    elif (data_columns[user_input] in partition_column_names or
                          user_input in subcategory_column_names):
                        OutputClass.warning(
                            'Column in Partition Column List or Subcategory Column List!')
                    else:
                        add_msk_col_names.append(data_columns[user_input])
        else:
            if additional_masking_column_numbers is not None:
                for user_input in additional_masking_column_numbers:
                    add_msk_col_names.append(data_columns[user_input])

    # Three set of masking condition will be evaluated.
    # Distinct index and column numbers will be collected into a dict.

    msk_data_ind_col_dict: dict[int, list] = {}

    # 1) Simple masking procedure
    for tind in raw_data.index.values:
        msk_data_ind_col_dict[tind] = []
        for tcol in mea_col_names + add_msk_col_names:
            # tnum:int = raw_data.loc[tind, tcol]
            tnum = raw_data.iloc[tind, raw_data.columns.get_loc(tcol)]
            if tnum >= gmp_msk_min and tnum <= gmp_msk_max:
                msk_data_ind_col_dict[tind].append(tcol)

    # 2) Vertical masking procedure for subcategories

    # Unique combination of fields for Unique Idenifying Columns
    partition_column_distinct_row_list = list(
        raw_data[partition_column_names].drop_duplicates().reset_index(drop=True).values)

    # Subsets of Subcategory Column Numbers with one less element
    if len(subcategory_column_names) >= 1:

        subcategory_column_names_subset = list(itertools.combinations(
            subcategory_column_names, len(subcategory_column_names)-1))

        # Looping over data partitions
        for partition_column_distinct_row in partition_column_distinct_row_list:
            partition_column_data: pd.DataFrame = raw_data.copy()

            # Looping over part_dis_row_list to choose partition from original dataframe
            partition_column_data2: pd.DataFrame = pd.DataFrame()
            for enum_i, item in enumerate(partition_column_names):
                partition_column_data2: pd.DataFrame = partition_column_data.loc[
                    partition_column_data[item] == partition_column_distinct_row[enum_i]]

            # Looping over distinct remaining combination of
            # subcategories for a given subcategory
            for subcategory_column_name in subcategory_column_names_subset:
                subcategory_column_name_list = list(subcategory_column_name)
                subcategory_distinct_row_list: pd.DataFrame = partition_column_data2[subcategory_column_name_list].drop_duplicates(
                ).reset_index(drop=True).values.tolist()

                # Looping over distinct values of combination of subcategories
                for subcategory_distinct_row in subcategory_distinct_row_list:
                    scat_data: pd.DataFrame = partition_column_data2.copy()
                    for item in range(len(subcategory_distinct_row)):
                    # for j, item2 in enumerate(sdr):
                        scat_data = scat_data.loc[scat_data[subcategory_column_name[item]]
                                                  == subcategory_distinct_row[item]]

                    for tcol in mea_col_names:
                        tcond = True
                        while tcond:
                            try:
                                tvals = scat_data[tcol].values
                                tinds = scat_data.index.values
                                n2mins = heapq.nsmallest(
                                    2, [i for i in tvals if i != 0])
                                n1min: int = min(n2mins)
                                if n1min <= gmp_msk_max:
                                    for item in range(len(tinds)):
                                        tval = tvals[item]
                                        tind = tinds[item]
                                        if tval in n2mins:
                                            if tcol not in msk_data_ind_col_dict[tind]:
                                                msk_data_ind_col_dict[tind].append(
                                                    tcol)
                                break
                            except ValueError:
                                tcond = False

    # 3) Horizontal masking procedure for measure column relations
    if measure_column_relation_type == '1':
        for tind in raw_data.index.values:
            tcond = True
            while tcond:
                try:
                    tvals: pd.DataFrame = raw_data.loc[tind, mea_col_names]
                    n1min = min([i for i in tvals if i != 0])
                    if n1min <= gmp_msk_max:
                        for tcol in mea_col_names:
                            if tcol not in msk_data_ind_col_dict[tind]:
                                msk_data_ind_col_dict[tind].append(tcol)
                    break
                except ValueError:
                    tcond = False

    if measure_column_relation_type == '2':
        for tind in raw_data.index.values:
            tcond = True
            while tcond:
                try:
                    tvals = raw_data.loc[tind, mea_col_names]
                    n2mins = heapq.nsmallest(2, [i for i in tvals if i != 0])
                    n1min = min(n2mins)
                    if n1min <= gmp_msk_max:
                        for tcol in mea_col_names:
                            tval = raw_data.loc[tind, tcol]
                            if tval in n2mins:
                                if tcol not in msk_data_ind_col_dict[tind]:
                                    msk_data_ind_col_dict[tind].append(tcol)
                    break
                except ValueError:
                    tcond = False

    for tind, tcols in msk_data_ind_col_dict.items():
        if len(tcols) > 0:
            if len(add_msk_col_names) > 0:
                tcols += add_msk_col_names
            raw_data.loc[tind, list(set(tcols))] = mask_string

    return raw_data


def get_subcategory_column_names(subcategory_column_numbers,
                                 data_col_dict, partition_column_names) -> list[str]:
    '''
    _summary_

    Args:
        subcategory_column_numbers (_type_): _description_
        data_col_dict (_type_): _description_
        partition_column_names (_type_): _description_

    Returns:
        list[str]: _description_
    '''
    subcategory_column_names: list[str] = []
    if subcategory_column_numbers is None:
        OutputClass.info('''Subcategory Column is a column, used for masking assessment among its
                         possible options for every combination of other Subcategory Column(s).
                         For example, "gender" is generally a Subcategory Column, for which "All",
                         "Male" and "Female" selection would be assessed for masking for each
                         combination of other Subcategory Column(s) such as "indegenous",
                         "on_reverse" etc.''')
        OutputClass.info(
            'Type a Subcategory Column Number and hit enter. Type done to finish.')
        user_input: str = ''
        while user_input != 'done':
            user_input = InputClass.get_inp('Subcategory Column Number')
            if user_input.lower() != 'done':
                if user_input not in list(data_col_dict)[0:]:
                    OutputClass.warning('Invalid column number!')
                elif data_col_dict[user_input] in subcategory_column_names:
                    OutputClass.warning('Repeated column number!')
                elif data_col_dict[user_input] in partition_column_names:
                    OutputClass.warning('Column in Partition Column List!')
                else:
                    subcategory_column_names.append(data_col_dict[user_input])
    else:
        for user_input in subcategory_column_numbers:
            subcategory_column_names.append(data_col_dict[user_input])
    return subcategory_column_names


def get_partition_column_names(column_numbers: list[str] | None, data_col_dict) -> list[str]:
    '''
    _summary_

    Args:
        partition_column_numbers (_type_): _description_
        data_col_dict (_type_): _description_

    Returns:
        list[str]: _description_
    '''
    partition_column_names: list[str] = []
    if column_numbers is None:
        OutputClass.info('''Partition Column is a column, used for partitioning data into blocks,
                      for which masking conditions are independetly assessed.
                      For example, "school_year" is generally a Partition Column, for which masking
                      would be independently applied for each given shcool year.''')
        OutputClass.info(
            'Type a Partition Column Number and hit enter. Type done to finish.')
        user_input: str = ''
        while user_input != 'done':
            user_input = InputClass.get_inp('Partition Column Number')
            if user_input.lower() != 'done':
                if user_input not in list(data_col_dict)[0:]:
                    OutputClass.warning('Invalid column number!')
                elif data_col_dict[user_input] in partition_column_names:
                    OutputClass.warning('Repeated column number!')
                else:
                    partition_column_names.append(data_col_dict[user_input])
    else:
        for user_input in column_numbers:
            partition_column_names.append(data_col_dict[user_input])
    return partition_column_names


def main_loop() -> None:
    '''
    Main program execution
    '''
    OutputClass()
    OutputClass.banner('''This routine is a limited version of masking policy moduls in
                    Data Analytics Engine to be used indepdendently. Thus, it has 
                    limited capacity, only working directly on a CSV file.''')
    Tk().withdraw()
    infile: str = get_csv_file()
    raw_data: pd.DataFrame = pd.read_csv(infile)
    raw_data = raw_data.copy()
    raw_data = apply_full_masking(raw_data)
    masked_data: pd.DataFrame = raw_data.copy()
    for row_index in masked_data.index.values:
        for column_index in masked_data.columns:
            if raw_data.loc[row_index, column_index] == 'Msk':
                masked_data.loc[row_index, column_index] = 'Msk'

    dir_path: str = os.path.dirname(infile)
    file_name: str = f'{os.path.splitext(os.path.basename(infile))[0]}_Msk.csv'
    get_csv_files(masked_data, dir_path, file_name)


def get_csv_file() -> str:
    '''
    _summary_

    Returns:
        str: _description_
    '''
    return askopenfilename(filetypes=[('Choose CVS File', '*.csv')])


# Program entry point
if __name__ == '__main__':
    main_loop()
