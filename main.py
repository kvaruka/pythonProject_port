# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import os
import time
import os

import self as self
# packet
from t_tech.invest import Client, GetOperationsByCursorRequest
from t_tech.invest.sandbox.client import SandboxClient
from datetime import date
from datetime import datetime
import csv
import pandas as pd

# my customer library
from inv_cls import inv_port, inv_db

# Указываем gRPC использовать скачанный файл сертификата
#os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = (
#    "/Users/kvaruka/PycharmProjects/sert/russian_ca.pem"
#)
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = (
    "/Users/kvaruka/PycharmProjects/sert/russiantrustedca2024.pem"
)

def gen_analise_port():
    a = inv_port('Broker')
    a.porfolio_total_inf()

def main_from_tink():
    a = inv_port('Broker')
    a.get_porfolio_pandas() # read tinkoff
    #a.read_data_f() # get data from file
    #a.out_csv_port()

    a.sort_portfolio() # вывод в файл
    a.porfolio_total_inf()
    #a.bonds_sort() # расширенная инф по облигациям в портфеле

def test_cl(): # 02/02/2026
    print("test")

def main():
    print("main")
    # Var1 total
    #gen_analise_port()

    # Var2 positions
    main_from_tink()

    # test_class
    #a = inv_db()
    #a.temp_test_cls()
    #a.get_op_by_cursor()

    #a = inv_port('Broker')
    #a.get_porfolio_pandas() # read tinkoff
    #a.read_data_f() # get data from file
    #a.out_csv_port()
    #a.sort_portfolio() # analyse
    #a.print_port()

    #a = inv_port('Broker')
    #a.get_porfolio_pandas() # read tinkoff
    #a.read_data_f() # get data from file
    #a.out_csv_port()
    #a.sort_portfolio() # analyse
    #a.print_port()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    print_hi('PyCharm')



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
