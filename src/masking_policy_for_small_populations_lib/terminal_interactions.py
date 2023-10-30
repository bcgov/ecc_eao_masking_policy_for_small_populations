'''
_summary_

Returns:
    _type_: _description_
'''

import sys
from getpass import getpass
class InputClass:
    '''
    _summary_

    Returns:
        _type_: _description_
    '''
    horizontal_line_length: int = 81
    horizontal_line_char: str = '+'
    horizontal_line: str = f'{horizontal_line_length*horizontal_line_char}'

    # --> Standard input dun function
    @staticmethod
    def get_inp(text: str) -> str:
        '''
        _summary_

        Args:
            text (str): _description_

        Returns:
            str: _description_
        '''
        user_inp: str = input('\nACTION --> ' + text + ':  ').lower()
        print(InputClass.horizontal_line)
        return user_inp

    @staticmethod
    def get_passwd(text: str) -> str:
        '''
        _summary_

        Args:
            text (str): _description_

        Returns:
            str: _description_
        '''
        user_inp: str = getpass('\nACTION --> ' + text + ':  ')
        print(InputClass.horizontal_line)
        return user_inp

    @staticmethod
    def get_boolen(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        user_inp: str = input('\nACTION --> ' + text + '? (y/n):  ').lower()
        while user_inp not in ['y', 'n']:
            OutputClass.warning('Invalid choice, try again!')
            user_inp = input('\nACTION --> ' + text + '? (y/n):  ').lower()
        if user_inp == 'y':
            print(InputClass.horizontal_line)
        if user_inp == 'n':
            print('\n---> Terminated!\n')
            print(InputClass.horizontal_line)
            sys.exit()

    @staticmethod
    def get_boolen_opt(text: str) -> bool:
        '''
        _summary_

        Args:
            text (str): _description_

        Returns:
            bool: _description_
        '''
        user_input: str = input('\nACTION --> ' + text + '? (y/n):  ').lower()
        while user_input not in ['y', 'n']:
            OutputClass.warning('Invalid choice, try again!')
            user_input = input('\nACTION --> ' + text + '? (y/n):  ').lower()
        return user_input == 'y'

    @staticmethod
    def get_option(info_text: str, action_text: str, options: dict) -> str:
        '''
        _summary_

        Args:
            info_text (str): _description_
            action_text (str): _description_
            options (dict): _description_

        Returns:
            str: _description_
        '''
        OutputClass.info(info_text)
        print('\n'+'\n'.join((' : '.join(item) for item in options.items())))
        user_input: str = input('\nACTION --> ' + action_text + ':  ').lower()
        print(InputClass.horizontal_line)
        while user_input not in list(options)[0:]:
            OutputClass.warning('Invalid choice, try again!')
            user_input = input('\nACTION --> ' + action_text + ':  ').lower()
        return user_input

class OutputClass:
    '''
    _summary_
    '''

    def __init__(self) -> None:
        print('\n\n'
              '#===============================================================================#\n'
              '#                                                                               #\n'
              '#                      Ministry of Education and Child Care                     #\n'
              '#                          Education Analytics Office                           #\n'
              '#                                                                               #\n'
              '#            Contact Information : EDUC.SystemPerformance@gov.bc.ca             #\n'
              '#                                                                               #\n'
              '#-------------------------------------------------------------------------------#\n'
              '#                                                                               #\n'
              '#          Welcome to Masking Policy for Small Populations Rotuine!             #\n'
              '#                                                                               #\n'
              '#                                  Version 1.0                                  #\n'
              '#                                                                               #\n'
              '#===============================================================================#\n'
              )

    @staticmethod
    def process(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\nPROCESS --> ' + text + '...')

    @staticmethod
    def action_vis(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\nACTION --> '+text + ':  ')

    @staticmethod
    def info(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\nINFO --> ' + text)

    @staticmethod
    def banner(text_in: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\n=================================================================================')
        print(f'{text_in.upper(): ^10}')
        print('=================================================================================\n')

    @staticmethod
    def success(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\nDONE --> ' + text + ' ---> Job Done!\n')
        print('---------------------------------------------------------------------------------')

    @staticmethod
    def error(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        sys.exit('\nERROR --> ' + text + ' ---> Failed! \n')

    @staticmethod
    def warning(text: str) -> None:
        '''
        _summary_

        Args:
            text (str): _description_
        '''
        print('\nWARNING --> ' + text)