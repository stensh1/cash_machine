# Orshak Ivan, 02.06.2022
import os
import hashlib
from ctypes import windll, create_string_buffer


def get_console_size():
    """This function gets the terminal parameters for centering text"""
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
    else:
        sizex = 80

    return sizex


class CashMachine:
    """Main class"""

    def __init__(self):
        """Constructor"""
        self.cash = {'RUB': {}, 'EUR': {}, 'USD': {}}
        self.is_active = 0
        self.is_auth = 0
        self.users = {}
        self.info = 'Dear user, there are several things you can do:\n' \
                    '- To show available banknotes type "status".\n' \
                    '    Everything after this command will be ignored.\n' \
                    '- To put your money on your card type "put"\n' \
                    '    and banknotes that you want to put in the format CURRENCY_CODE + VALUE:QUANTITY\n' \
                    '    For example: "put USD100:2" - to put in two hundred dollar bills.\n' \
                    '    Moreover, you can put banknotes of different currencies and values at the same time.\n' \
                    '    For this one use "," between banknotes: "put USD100:2, EUR100:5"\n' \
                    '- To withdraw money from your account type "withdraw" with currency code and value.\n' \
                    '    For example: "withdraw USD:155" - to get 155 dollars.\n' \
                    '    NOTICE: Only one currency can be withdrawn at a time.\n' \
                    '- To sign out your account type "exit".\n' \
                    '- To switch off machine type "off".'
        self.db = open('users.dat', 'a+')
        self.user_name = ''
        self.user_balance = {}

    def __del__(self):
        return 0

    def power_on(self, initial_state):
        self.is_active = 1
        self.put_cash(initial_state)

        # The main program loop
        while self.is_active:
            # We need to reopen data file to check new updates
            self.db = open('users.dat', 'r+')
            db_data = self.db.read().split(':')

            for i in range(0, len(db_data) - 1, 2):
                self.users[db_data[i]] = db_data[i + 1]

            self.console_draw('Authorization', self.authorization())
            os.system('pause')
            self.user_handler()
        else:
            self.power_off()

        return

    def power_off(self):
        self.db.close()
        os.system('cls')
        self.__del__()

    def console_draw(self, *args):
        width = get_console_size()
        title = args[0].center(width)
        bank_name = 'Welcome, ' + self.user_name + '!' + '----------\n'.rjust(width - len(self.user_name) - 10) + \
                    '|Sbebrank|\n'.rjust(width) + '----------\n'.rjust(width)

        os.system('cls')

        print(bank_name)
        print("Type 'off' to shutdown\n")
        print('-' * width)

        if self.is_auth:
            print('Your balance is:\n' + 'RUB' + '--->' + str(self.user_balance['RUB']) + '\n' + 'EUR' + '--->' +
                  str(self.user_balance['EUR']) + '\n' + 'USD' + '--->' + str(self.user_balance['USD']) + '\n')
            print("To get help with available command type 'help'")
            print('-' * width)

        print(title)

        if len(args) > 1:
            print(args[1])

        return

    def authorization(self):
        self.console_draw('Authorization')

        login = input('Enter your login:')

        if login == 'off':
            self.is_active = 0
            return 'Shutting down...'

        if login in self.users:
            # Authorization part
            # Encode is required for md5 hashing
            pswd = input('Enter your password:').encode()

            if hashlib.md5(pswd).hexdigest() == self.users[login]:
                self.is_auth = 1
                self.user_name = login

                # Uploading user data from a file
                f = open(self.user_name + '.dat', 'r')
                # We do not need to check the input data from the file,
                # because the rules for these internal files are set by us
                # RULE: CURRENCY_CODE:VALUE, CURRENCY_CODE:VALUE, ....
                balance = f.read().split(',')

                if len(balance) > 1:
                    # Got some data
                    for i in balance:
                        self.user_balance[i.split(':')[0]] = i.split(':')[1]
                else:
                    # User's file is empty
                    self.user_balance = {'RUB': 0, 'EUR': 0, 'USD': 0}

                return 'You have been successfully authorized.'
            else:
                return 'Wrong password.'
        else:
            # Registration part
            self.console_draw('Ooops...', 'You are not in our system\n--->Do you want to sign up?')

            if input('y/n: ') == 'y':
                self.console_draw('Registration')
                pswd = input('Create your password:').encode()
                # Saving new user
                self.db.write(login + ':' + hashlib.md5(pswd).hexdigest() + ':')
                self.db.close()
                # We need to create an empty new user's file,
                # because we are opening it in authorization part with parameter 'r'
                # NOTICE: Files, unlike usernames, are not case sensitive!
                f = open(login + '.dat', 'a+')

                return 'Registration completed.'

    def user_handler(self):
        if self.is_active:
            # 'user is logged in' loop
            while self.is_auth:
                self.console_draw('Please, type any command')
                command = input('Type command:')
                command = command.split()

                # str must be not NULL
                if command:
                    if command[0] == 'status':
                        self.console_draw('Available banknotes:', self.cash_status(self.cash))
                    elif command[0] == 'withdraw':
                        self.console_draw('Result:', self.withdraw_cash(''.join(command[1:])))
                    elif command[0] == 'put':
                        self.console_draw('Result:', self.put_cash(''.join(command[1:])))
                    elif command[0] == 'help':
                        self.console_draw('Usage', self.info)
                    elif command[0] == 'exit':
                        self.console_draw('Are you sure?')
                        if input('y/n: ') == 'y':
                            self.is_auth = 0
                    elif command[0] == 'off':
                        self.console_draw('Are you sure?')
                        if input('y/n: ') == 'y':
                            self.is_auth = 0
                            self.is_active = 0
                    else:
                        self.console_draw('Unknown command!')

                    os.system('pause')
            else:
                # Saving user data into a file
                if self.user_balance:
                    f = open(self.user_name + '.dat', 'w')
                    f.write('RUB:' + str(self.user_balance['RUB']) + ',EUR:' + str(self.user_balance['EUR']) +
                            ',USD:' + str(self.user_balance['USD']))
                    f.close()

    def withdraw_cash(self, cash_status):
        banknotes_out = {}
        banknote_counter = 0
        output = ''
        value = 0

        if cash_status:
            sum_out = cash_status.split(':')

            if len(sum_out) == 2:
                if sum_out[1].isdigit():
                    sum_out[1] = int(sum_out[1])
                    value = sum_out[1]
                else:
                    return 'Withdraw value syntax error.'
            else:
                return 'Withdraw value syntax error.'
        else:
            return 'No banknotes found.'

        if sum_out[0] in self.cash:
            if sum_out[1] > int(self.user_balance[sum_out[0]]):
                return 'Your balance is less than the request.'

            d = self.cash[sum_out[0]]
            d = dict(sorted(d.items(), key=lambda x: int(x[0]), reverse=True))
        else:
            return 'No such currency in cash machine.'

        for i in d:
            if sum_out[1] != 0:
                while sum_out[1] >= int(i) and d[i] > 0:
                    sum_out[1] -= int(i)
                    d[i] -= 1
                    banknote_counter += 1
                    banknotes_out[i] = banknote_counter
            else:
                break

            banknote_counter = 0

        if sum_out[1] == 0:
            self.cash[sum_out[0]] = d
            self.user_balance[sum_out[0]] = int(self.user_balance[sum_out[0]]) - value

            for i in banknotes_out:
                output += sum_out[0] + str(i) + ' - ' + str(banknotes_out[i]) + '\n'

            return 'Take your money: ' + output
        else:
            return 'Unable to withdraw amount.'

    def get_banknotes(self, cash_status):
        # А sub-method for forming a correct dictionary of bills and verifying input banknotes data
        banknotes = dict()

        if cash_status:
            cash = str(cash_status).replace(" ", "").split(',')

            for i in range(0, len(cash)):
                banknote = cash[i].split(':')

                if len(banknote) > 1:
                    if banknote[1].isdigit():
                        banknotes[banknote[0]] = int(banknote[1])
                    else:
                        return banknotes, 'Banknote value syntax error.'
                else:
                    return banknotes, 'Banknote syntax error.'

            return banknotes, 0
        else:
            return banknotes, 'No banknotes found.'

    def put_cash(self, cash_status):
        # For methods put_cash, withdraw_cash and get_banknotes it would be better to use errors handler
        # But this case is too small to use separate handling method
        banknotes_in, err = self.get_banknotes(cash_status)
        temp = 0

        if err == 0:
            for i in banknotes_in:
                if len(i) > 3:
                    if i[0:3] in self.cash and i[3:].isdigit():
                        if i[3:] in self.cash[i[0:3]]:
                            # If this banknote already exist, save value
                            temp = int(self.cash[i[0:3]][i[3:]])

                        # Update cash in ATM
                        self.cash[i[0:3]][i[3:]] = int(banknotes_in[i]) + temp

                        if self.user_balance:
                            # Update user balance
                            temp = int(self.user_balance[i[0:3]])
                            self.user_balance[i[0:3]] = int(banknotes_in[i]) * int(i[3:]) + temp
                    else:
                        return 'No such currency.'
                else:
                    return 'Value syntax error.'
        else:
            return err

        return 'Your account has been successfully funded.\n'

    def cash_status(self, account):
        # Getting balance from dictionary of banknotes
        # {'RUB': {}, 'USD': {}, 'EUR': {}} formatting to '-->CUR(VAL) - NUM_OF_BANKNOTES'
        status = ''

        for key in account:
            for i in account[key]:
                status += '--> ' + key + '(' + i + ') - ' + str(account[key][i]) + '\n'

        if status:
            return status
        else:
            return 'No money.'
