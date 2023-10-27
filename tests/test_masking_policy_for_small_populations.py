'''
    _summary_
'''
from typing import Any, Iterator
from _pytest.monkeypatch import MonkeyPatch
from csv_diff import load_csv, compare
import ecc_eao_data_masking_routine
import os

def test_full_run(monkeypatch: MonkeyPatch) -> None:
    '''
    Test the full run

    Args:
        monkeypatch (_type_): _description_
    '''
    def mock_return() -> str:
        return f'{os.getcwd()}/tests/dummy_data.csv'

    monkeypatch.setattr('ecc_eao_data_masking_routine.get_csv_file', mock_return)

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
    responses.append('n')
    response_iterator: Iterator[str] = iter(responses)
    monkeypatch.setattr('builtins.input', lambda msg: next(response_iterator))
    ecc_eao_data_masking_routine.main_loop()

    infile_01_filename:str = f'{os.getcwd()}/tests/dummy_data_Msk.csv'
    infile_02_filename:str = f'{os.getcwd()}/tests/dummy_data_Msk_Actual.csv'

    with open(infile_01_filename,'r', encoding='utf-8') as infile_01:
        with open(infile_02_filename,'r', encoding='utf-8') as infile_02:
            diff:dict[str, list[Any]] = compare(
                load_csv(infile_01),
                load_csv(infile_02)
            )
            print(diff)