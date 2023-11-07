# Orshak Ivan, 02.06.2022
import CashMachine
import argparse


def get_initial_data():
    """This function processes the arguments accepted by the program launching via the cmd"""
    parser = argparse.ArgumentParser()
    # To add arguments use '->py main.py -cash_state _args_'
    # Arguments style should be fit arguments for CashMachine.put_cash method
    # For example: -cash_state 'RUB500:1, USD100:2'
    parser.add_argument("-cash_state", default='')

    return parser.parse_args()


def main():
    # Input arguments string
    cash_state = get_initial_data().cash_state

    atm = CashMachine.CashMachine()
    atm.power_on(cash_state)


if __name__ == '__main__':
    main()
