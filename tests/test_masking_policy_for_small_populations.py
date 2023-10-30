'''
    _summary_
'''
import os
from typing import Any, Iterator
from _pytest.monkeypatch import MonkeyPatch
from csv_diff import load_csv, compare
import pandas as pd
import masking_policy_for_small_populations
#import terminal_interaction

def test_full_run(monkeypatch: MonkeyPatch) -> None:
    '''
    Test the full run

    Args:
        monkeypatch (_type_): _description_
    '''
    

    # Measure Column Relation Type: 0 --> No relation.
    
    def mock_return_0() -> str:
        file_path = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_0.csv'
        unmasked_data: pd.DataFrame = pd.read_csv(file_path)
        return file_path, unmasked_data
    monkeypatch.setattr('masking_policy_for_small_populations.import_unmasked_data',  mock_return_0)


    responses: list[str] = []
    responses.append('1')
    responses.append('2')
    responses.append('3')
    responses.append('done')
    responses.append('4')
    responses.append('5')
    responses.append('6')
    responses.append('done')
    responses.append('0')
    responses.append('7')
    responses.append('8')
    responses.append('9')
    responses.append('done')
    response_iterator: Iterator[str] = iter(responses)
    monkeypatch.setattr('builtins.input', lambda msg: next(response_iterator))
    masking_policy_for_small_populations.main_loop()
    
    infile_01_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_0_Masked.csv'
    infile_02_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_0_Masked_Actual.csv'
    
    with open(infile_01_filename,'r', encoding='utf-8') as infile_01:
        with open(infile_02_filename,'r', encoding='utf-8') as infile_02:
            diff:dict[str, list[Any]] = compare(
                load_csv(infile_01),
                load_csv(infile_02)
            )
            print(diff)

    # Measure Column Relation Type: 1 --> Rate.
    
    def mock_return_1() -> str:
        file_path = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_1.csv'
        unmasked_data: pd.DataFrame = pd.read_csv(file_path)
        return file_path, unmasked_data
    monkeypatch.setattr('masking_policy_for_small_populations.import_unmasked_data',  mock_return_1)


    responses: list[str] = []
    responses.append('1')
    responses.append('2')
    responses.append('3')
    responses.append('done')
    responses.append('4')
    responses.append('5')
    responses.append('6')
    responses.append('done')
    responses.append('1')
    responses.append('7')
    responses.append('8')
    response_iterator: Iterator[str] = iter(responses)
    monkeypatch.setattr('builtins.input', lambda msg: next(response_iterator))
    masking_policy_for_small_populations.main_loop()
    
    infile_01_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_1_Masked.csv'
    infile_02_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_1_Masked_Actual.csv'
    
    with open(infile_01_filename,'r', encoding='utf-8') as infile_01:
        with open(infile_02_filename,'r', encoding='utf-8') as infile_02:
            diff:dict[str, list[Any]] = compare(
                load_csv(infile_01),
                load_csv(infile_02)
            )
            print(diff)


    # Measure Column Relation Type: 2 --> Sum.
    
    def mock_return() -> str:
        file_path = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_2.csv'
        unmasked_data: pd.DataFrame = pd.read_csv(file_path)
        return file_path, unmasked_data
    monkeypatch.setattr('masking_policy_for_small_populations.import_unmasked_data',  mock_return)


    responses: list[str] = []
    responses.append('1')
    responses.append('2')
    responses.append('3')
    responses.append('done')
    responses.append('4')
    responses.append('5')
    responses.append('6')
    responses.append('done')
    responses.append('2')
    responses.append('10')
    responses.append('7')
    responses.append('8')
    responses.append('9')
    responses.append('done')
    response_iterator: Iterator[str] = iter(responses)
    monkeypatch.setattr('builtins.input', lambda msg: next(response_iterator))
    masking_policy_for_small_populations.main_loop()
    
    infile_01_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_2_Masked.csv'
    infile_02_filename:str = f'{os.getcwd()}/tests/dummy_data_mea_col_rel_2_Masked_Actual.csv'
    
    with open(infile_01_filename,'r', encoding='utf-8') as infile_01:
        with open(infile_02_filename,'r', encoding='utf-8') as infile_02:
            diff:dict[str, list[Any]] = compare(
                load_csv(infile_01),
                load_csv(infile_02)
            )
            print(diff)