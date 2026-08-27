
import time
import os
import self as self
# packet
from t_tech.invest         import Client, GetOperationsByCursorRequest
from t_tech.invest.sandbox.client import SandboxClient
from t_tech.invest.utils   import now
from t_tech.invest.schemas import AssetsRequest
from t_tech.invest.schemas         import InstrumentStatus
from t_tech.invest.schemas import GetBondEventsRequest # Добавить это
from datetime import date
from datetime import datetime
import csv
import pandas as pd
import sqlite3
import  pickle

from datetime import timedelta
#  класс главный
#class inv_main:
#    def __init__(self):
import time
import json
#start_time = time.perf_counter()  # Точка старта
# Ваш код здесь
#sum(range(10**7))
#end_time = time.perf_counter()    # Точка финиша
#print(f"Время выполнения: {end_time - start_time:.4f} сек.")

class inv_port:
    type = 'Broker'
    token = ''
    def __init__(self,type):
        def get_date_fname():
            time = datetime.now()
            t1 = time.time().strftime("%Hh_%Mm_%Ss")
            today = date.today()
            d1 = today.strftime("%Y_%m_%d")
            fname = '_' + d1 + "_" + t1
            return fname
        self.token = os.environ.get('TOKEN')
        # t.J8_iIGhyaETFSdAbHvcsSqJdr4uv_1I6VPi9spzXhXGrna1zhI_nLsAXVFm8dJeCAdgmhvXDmoVwqp6s8XSong
        print(self.token)
        if  type == 'IIS':
            self.type = 'IIS'
        self.fname = get_date_fname()
        self.fname_etf = self.type  + self.fname + '_etf' + '.csv'
        self.fname_share = self.type  + self.fname + '_share' +   '.csv'
        self.fname_bond = self.type  + self.fname + '_bond' + '.csv'
        self.fname = self.type + self.fname + '.csv'
        self.fname_total = self.type + self.fname + '_total' + '.csv'

        self.fname_in = 'port.csv' # in file name with portfolio

        self.fname_csv = self.fname
        self.fname_ext_csv = self.fname

        self.figi_info_short = {} #  словарь списков figi/name/ticker/type

        self.port_type = {
            'ticker':[],     # added
            'name':[],      # name
            'average_position_price_curr': [],
            'average_position_price':[], # Money curr
            'average_position_price_fifo_curr': [],
            'average_position_price_fifo':[], # Money  curr
            'average_position_price_pt':[], # Money   _no_curr
            'blocked':[],
            'blocked_lots':[],
            'current_nkd_curr': [],
            'current_nkd':[], # Money curr
            'current_price_curr': [],
            'current_price':[], # Money curr
            'expected_yield':[],
            'expected_yield_fifo':[],
            'figi':[],
            'instrument_type':[],
            'instrument_uid':[],
            'position_uid':[],
            'quantity':[],
            'quantity_lots':[],
            'var_margin_curr': [],
            'var_margin':[] # Money curr
        }
        self.port_type_ext = {
            'ticker':[],     # added
            'name':[],      # name
            'quantity':[],
            'current_price_curr':[],
            'current_price':[],  # Money curr
            'current_amount':[], # current amount
            'average_position_price_curr':[],
            'average_position_price': [],  # Money curr
            'average_amount':[], # spent for position
            'delta':[], # Прибыль/Убыток
            'average_position_price_fifo_curr': [],
            'average_position_price_fifo': [],  # Money  curr

            'average_position_price_pt':[], # Money   _no_curr
            'blocked':[],
            'blocked_lots':[],
            'current_nkd_curr': [],
            'current_nkd':[], # Money curr
            'expected_yield':[],
            'expected_yield_fifo':[],
            'figi':[],
            'instrument_type':[],
            'instrument_uid':[],
            'position_uid':[],
            'quantity_lots':[],
            'var_margin_curr': [],
            'var_margin':[] # Money curr
        }
        self.port_total = {
            'Name_pos': [],  # Total_etf
            'curr':[],
            'amount': [],      # name
            'date':[],
            'curr_amount':[],
            'avr_amount': [],
            'delta':[]
        }
        self.pd_port = pd.DataFrame(self.port_type)              # Pandas Portfolio from Tinkoff
        self.pd_port_ext = pd.DataFrame(self.port_type_ext)      # Pandas Portfolio + extra colunms
        self.pd_port_total = pd.DataFrame(self.port_total)       # Pandas Portfolio total

        # inf_table
        self.pd_ref_shares  = pd.DataFrame()    # полный справочник по акциям
        self.pd_ref_bonds = pd.DataFrame()      # полный справочник по облигациям
        self.pd_ref_etfs = pd.DataFrame()       # полный справочник по фондам


    def ini_ref(self,mode = ''):
        if mode=='RT' or mode=='RTF' or mode == '': # read from Tinkoff
            if self.figi_info_short == {}:
                # all_data = []
                #if token == '':
                token = self.token
                with Client(token) as client:
                    # 1. Получаем списки разных типов инструментов
                    # InstrumentStatus.BASE — только те, что доступны для торговли сейчас
                    self.shares = client.instruments.shares(
                        instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                    self.bonds = client.instruments.bonds(
                        instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                    # etfs = client.instruments.etfs(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments
                    self.etfs = client.instruments.etfs(
                        instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments

                    # 2. Объединяем и извлекаем нужные поля
                    self.figi_info_short = {
                        instr.figi: {
                            'name': instr.name,
                            'ticker': instr.ticker,
                            'type': type(instr).__name__
                        }
                        for instr in (self.shares + self.bonds + self.etfs)
                    }
                    self.pd_ref_shares = pd.DataFrame(self.shares)
                    self.pd_ref_bonds = pd.DataFrame(self.bonds)
                    #self.pd_ref_bonds.info()
                    self.pd_ref_etfs = pd.DataFrame(self.etfs)

            if mode == 'RTF':
                with open("figi_info_short.pkl", "wb") as file:
                    pickle.dump(self.figi_info_short, file)
                self.pd_ref_shares.to_json("pd_ref_shares.json", orient='records', force_ascii=False, indent=4)
                self.pd_ref_bonds.to_json("pd_ref_bonds.json", orient='records', force_ascii=False, indent=4)
                self.pd_ref_etfs.to_json("pd_ref_etfs.json", orient='records', force_ascii=False, indent=4)

                #self.pd_ref_shares.to_pickle("pd_ref_shares.pkl")
                #self.pd_ref_bonds.to_pickle("pd_ref_bonds.pkl")
                #self.pd_ref_etfs.to_pickle("pd_ref_etfs.pkl")

                #with open('pd_ref_shares.pkl', 'wb') as file:
                #    pickle.dump(self.pd_ref_shares, file)
                #with open('pd_ref_bonds_ref.pkl', 'wb') as file:
                #    pickle.dump(self.pd_ref_bonds, file)
                #with open('pd_ref_etfs.pkl', 'wb') as file:
                #    pickle.dump(self.pd_ref_etfs, file)

        # with open("figi_info_short.pkl", "rb") as file:
        #    self.figi_info_short = pickle.load(file)

        elif mode=='RF': # read from Files pickle
            with open("figi_info_short.pkl", "rb") as file:
                self.figi_info_short = pickle.load(file)
            self.pd_ref_shares = pd.read_json("pd_ref_shares.json")
            self.pd_ref_bonds = pd.read_json("pd_ref_bonds.json")
            self.pd_ref_etfs = pd.read_json("pd_ref_etfs.json")
            #with open("pd_ref_shares.pkl", "rb") as file:
            #    self.pd_ref_shares = pickle.load(file)
            #with open("pd_ref_bonds_ref.pkl", "rb") as file:
            #    self.pd_ref_bonds_ref = pickle.load(file)
            #with open("pd_ref_etfs.pkl", "rb") as file:
            #    self.pd_ref_etfs = pickle.load(file)


    def read_data_f(self):
        self.data_in_f = pd.read_csv(self.fname_in, keep_default_na=False)
        self.df_in_f = pd.DataFrame(self.data_in_f, columns=
                ['ticker', 'name', 'average_position_price_curr', 'average_position_price',
            'average_position_price_fifo_curr', 'average_position_price_fifo', # Money  curr
            'average_position_price_pt', # Money   _no_curr
            'blocked',
            'blocked_lots',
            'current_nkd_curr',
            'current_nkd', # Money curr
            'current_price_curr',
            'current_price', # Money curr
            'expected_yield',
            'expected_yield_fifo',
            'figi',
            'instrument_type',
            'instrument_uid',
            'position_uid',
            'quantity',
            'quantity_lots',
            'var_margin_curr',
            'var_margin']  )
        print(self.df_in_f)
        self.pd_port = self.df_in_f

    def get_porfolio(self):
        # конструкция сомнительная
        print("get_porfolio")
        with Client(self.token) as client:
            client_test = client
            tariff = client.users.get_user_tariff()
            accounts = client.users.get_accounts()
            if self.type == 'IIS':
                account_id = accounts.accounts[1].id
            else:
                account_id = accounts.accounts[0].id
            portf = client.operations.get_portfolio(account_id=account_id)
            return portf
    def get_figi_info(self, figi, token=''): # новая версия кода
        # метод создает справочник self.figi_info_short


        if self.figi_info_short == {}:
            self.ini_ref(mode='RT')   # read Tinkoff
            #self.ini_ref(mode='RTF') # read Tinkoff Save File
            #self.ini_ref(mode='RF')  # read File
        res = self.figi_info_short.get(figi, {'figi': figi, 'name': '-', 'ticker': '-', 'type': '-'})
        return res
    '''def get_figi_info(self, figi, token=''): # новая версия кода
        # метод создает справочник self.figi_info_short
        #
        #with open("figi_info_short.pkl", "wb") as file:
        #    pickle.dump(self.figi_info_short, file)
        #with open("figi_info_short.pkl", "rb") as file:
        #    self.figi_info_short = pickle.load(file)

        if self.figi_info_short == {}:
            # all_data = []
            start_time = time.perf_counter()  # Точка старта
            if token == '':
                token = self.token
            with Client(token) as client:
                # 1. Получаем списки разных типов инструментов
                # InstrumentStatus.BASE — только те, что доступны для торговли сейчас
                self.shares = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                self.bonds = client.instruments.bonds(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                #etfs = client.instruments.etfs(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments
                self.etfs = client.instruments.etfs(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
                #with open("shares.pkl", "wb") as file:
                #   pickle.dump(self.shares, file)
               # with open("bonds.pkl", "wb") as file:
               #     pickle.dump(self.bonds, file)
               # with open("etf.pkl", "wb") as file:
               #     pickle.dump(self.etfs, file)

                end_time = time.perf_counter()  # Точка финиша

                print(f"Время выполнения get_figi_info  заполн спр: {end_time - start_time:.4f} сек.")
                # 2. Объединяем и извлекаем нужные поля
                self.figi_info_short = {
                    instr.figi: {
                        'name': instr.name,
                        'ticker': instr.ticker,
                        'type': type(instr).__name__
                    }
                    for instr in (self.shares + self.bonds + self.etfs)
                }
                #with open("figi_info_short.pkl", "wb") as file:
                #     pickle.dump(self.figi_info_short, file)
            #end_time = time.perf_counter()  # Точка финиша

        res = self.figi_info_short.get(figi, {'figi': figi, 'name': '-', 'ticker': '-', 'type': '-'})
         #print(res.get('name')) # пример использования
        return res'''

#    def get_figi_info_pos(self, instr_query): # удалено т.к. медленно
#        with Client(self.token) as client:
#            client_test = client
#            accounts = client.users.get_accounts()
#            account_id = accounts.accounts[0].id
#            inst = client.instruments
#            finst = inst.find_instrument(query=instr_query)
#            res_pos = 0
#            for figi_pos in finst.instruments:
#                if figi_pos.figi == instr_query:
#                    res_pos = figi_pos
#                    break
#            return res_pos
    def get_porfolio_pandas(self): # fill self.pd_port
        print('<<< beg get_porfolio_pandas')
        start_time = time.perf_counter()  # Точка старта
        # Ваш код здесь
        # sum(range(10**7))
        portfolio = self.get_porfolio()
        #print(portfolio)
        port_positions = portfolio.positions
        step = 0
        for port_pos in port_positions:
            #print(port_pos)
            #print(dir(port_pos))

            #print('port_pos.figi',port_pos.figi)
            if port_pos.figi == '':
                continue

            #print('figi_pos', figi_pos.figi)
            figi_pos = self.get_figi_info(port_pos.figi)

            #print(figi_pos.name)
            #print(figi_pos.get('name'))

            self.pd_port.loc[len(self.pd_port.index)] = [
                #figi_pos.ticker,
                #figi_pos.name,
                figi_pos.get('ticker'),
                figi_pos.get('name'),
                port_pos.average_position_price.currency,
                port_pos.average_position_price.units + port_pos.average_position_price.nano/1000000000,
                port_pos.average_position_price_fifo.currency,
                port_pos.average_position_price_fifo.units + port_pos.average_position_price_fifo.nano/1000000000,
                port_pos.average_position_price_pt.units + port_pos.average_position_price_pt.nano / 1000000000,
                port_pos.blocked,
                port_pos.blocked_lots.units + port_pos.blocked_lots.nano / 1000000000,
                port_pos.current_nkd.currency, #money
                port_pos.current_nkd.units + port_pos.current_nkd.nano / 1000000000,
                port_pos.current_price.currency, # money
                port_pos.current_price.units + port_pos.current_price.nano / 1000000000,
                port_pos.expected_yield.units + port_pos.expected_yield.nano / 1000000000,
                port_pos.expected_yield_fifo.units + port_pos.expected_yield_fifo.nano / 1000000000,
                port_pos.figi,
                port_pos.instrument_type,
                port_pos.instrument_uid,
                port_pos.position_uid,
                port_pos.quantity.units + port_pos.quantity.nano / 1000000000,
                port_pos.quantity_lots.units + port_pos.quantity_lots.nano / 1000000000,
                port_pos.var_margin.currency, # money
                port_pos.var_margin.units + port_pos.var_margin.nano / 1000000000
            ]

            #step = step + 1
            #print(step)
            #if step == 98:
                #break
             #   print("sleep 61 sec")
             #   time.sleep(61)
                #step = 0
        #print(self.pd_port)
        #self.out_csv_port()
        end_time = time.perf_counter()    # Точка финиша
        print(f"Время выполнения get_portfolio_pandas: {end_time - start_time:.4f} сек.")
        print('>>> end get_porfolio_pandas')
    def bond_detail(self):
        figi = 'TCS00A109551'
        figi = 'TCS00A10B4K3' # oferta 2
        figi = 'TCS00A105VU7'  # oferta 2
        TOKEN = self.token
        with Client(TOKEN) as client:
            # Указываем временной интервал (например, от сегодня до конца года)
            to_date = datetime.now() + timedelta(days=365)

            coupons = client.instruments.get_bond_coupons(
                figi=figi,
                from_=datetime.now(),
                to=to_date
            )

            #coupons.events.sort(k)
            print(type(coupons))
            print(type(coupons.events))
            coupons.events.sort(key=lambda x: x.coupon_date, reverse=False)
            for coupon in coupons.events:
                print(f"Дата выплаты: {coupon.coupon_date}")
                # Сумма купона на 1 бумагу (объект MoneyValue или Quotation)
                amount = coupon.pay_one_bond.units + coupon.pay_one_bond.nano / 1e9
                print(f"Размер купона: {amount} {coupon.pay_one_bond.currency}")
                print(f"Купонный период/число: {coupon.coupon_period}/{coupon.coupon_number}")
                break

            events = client.instruments.get_bond_events(
                request=GetBondEventsRequest(
                    instrument_id=figi,
                    from_=datetime.now(),
                    to=to_date
                )
            )
            events.events.sort(key=lambda x: x.event_date, reverse=False)
            for event in events.events:
                #print(f"Тип события, дата события: {event.event_type.name}, {event.event_date}")
                #print(f"Стоимость операции {event.value.units + event.value.nano / 1000000000} <UNK>")
                #print(f"coupon_interest_rate{event.coupon_interest_rate.units + event.coupon_interest_rate.nano / 1000000000}")
                #print(event)

                # Предположим, ваш объект называется event
                print(f"--- Событие №{event.event_number} ---{event.event_type.name}")
                print(f"Дата события: {event.event_date.strftime('%d.%m.%Y')}")
                print(f"Дата выплаты: {event.pay_date.strftime('%d.%m.%Y')}")
                print(
                    f"Выплата:      {event.pay_one_bond.units + event.pay_one_bond.nano / 1e9:.2f} {event.pay_one_bond.currency.upper()}")
                print(
                    f"Ставка:       {event.coupon_interest_rate.units + event.coupon_interest_rate.nano / 1e9}% ({event.operation_type})")
                print(f"Период:       {event.coupon_period} дней")
                print(f"Примечание:  {event.note}")

                print(f"Дата для уч: {event.fix_date.strftime('%d.%m.%Y')}")
    def bonds_sort(self): # создание Pandas для расширенной информации по облигациям в портфеле
        self.bond_detail()
        #return
        #ticker/name/quantity/current_price_curr/current_price/current_amount/average_position_price_curr/average_position_price
        #average_amount/delta/nkd

        #Купон %/Кол - во выплат/
        #Погашение (дата)/Купон/Номинал/Амортизация/Оферта/Дата оферты/СтавкаСрПозиция/СтавкаТекЦена
        #Сумма НКД/Процент ИзмЦены/Доходность к погашению Тинькофф/Доходность к оферте Тинькофф

        def get_info(row):
            # Представим, что здесь сложная логика или поиск в словаре
            #if row['figi'] == 'BBG004730N88':
            #    return 'Сбербанк', 'SBER', '1'
            r_current_amount = row['current_price'] * row['quantity']
            r_average_amount = row['average_position_price'] * row['quantity']  #'average_amount':[],  # spent for position
            #r_delta =  row['current_price'] * row['quantity'] - row['average_position_price'] * row['quantity'], # delta
            r_delta = r_current_amount - r_average_amount
            return r_current_amount, r_average_amount, r_delta

        # Обновляем два столбца сразу
        #df[['name', 'ticker']] = df.apply(lambda r: get_info(r), axis=1, result_type='expand')
        self.pd_port_bond =pd.DataFrame(columns=self.pd_port)# create a frame

        self.pd_port_bond = self.pd_port[self.pd_port['instrument_type'] == 'bond'].copy() # create a stock pandas


        self.pd_port_bond[['current_amount', 'average_amount', 'delta_amount']] = self.pd_port_bond.apply(lambda r:get_info(r), axis=1, result_type='expand')


        # добавляем вычисляемые столбцы

        self.pd_port_bond1 = self.pd_port[self.pd_port['instrument_type'] == 'bond'].copy()  # create a stock pandas
        self.pd_port_bond1['current_amount'] = self.pd_port_bond1['current_price'] * self.pd_port_bond1['quantity']
        self.pd_port_bond1['average_amount'] = self.pd_port_bond1['average_position_price'] * self.pd_port_bond1['quantity']
        self.pd_port_bond1['delta_amount'] = self.pd_port_bond1['current_amount'] - self.pd_port_bond1['average_amount']

        # Создать фрейм из списка
        #self.pd_bonds_ref = pd.DataFrame(self.bonds)

        # cоздаем индекс
        #self.pd_bonds_ref = self.pd_bonds_ref.set_index('figi', drop=False)
        #self.pd_bonds_ref = self.pd_bonds_ref.sort_index()
        self.pd_ref_bonds.info()
        # добавляем колонки по индексу
        self.pd_port_bond_ext = self.pd_port_bond.merge(self.pd_ref_bonds[['figi','call_date']], on='figi', how='left')
        self.pd_port_bond_ext['call_date'] = self.pd_port_bond_ext['call_date'].dt.date
        self.pd_port_bond_ext.sort_values(by=['current_amount'], ascending=True, inplace=True)

        #print(self.pd_port_bond_ext)
        #self.pd_port_bond_ext.info()
        #print(self.pd_port_bond_ext[['figi','ticker', 'name', 'current_nkd','call_date']])
        print(self.pd_port_bond_ext[['figi', 'ticker', 'call_date', 'name']].to_string())


        # out
        #self.pd_bonds_ref.to_csv(
        #    self.fname_bond,
        #    sep = ',',
        #    encoding='utf-8-sig',  # Сигнатура UTF-8, чтобы Excel сразу понял кодировку
        #    index=False)

        #df.to_csv(
        #    'data_for_excel.csv',
        #    sep=';',  # Точка с запятой — стандарт для Excel в РФ
        #    encoding='utf-8-sig',  # Сигнатура UTF-8, чтобы Excel сразу понял кодировку
        #    index=False
        #)

    def sort_portfolio2(self):
        # версия оптимизированная версия sort_portfolio
        print("<<< beg sort portfolio2")

        # Список типов инструментов и соответствующих им имён файлов для экспорта
        instrument_types = {
            'share': self.fname_share,
            'etf':   self.fname_etf,
            'bond':  self.fname_bond
        }

        for inst_type, filename in instrument_types.items():
            # 1. Фильтруем исходный портфель по типу и валюте (рубли)
            df_filtered = self.pd_port[
                (self.pd_port['instrument_type'] == inst_type) &
                (self.pd_port['current_price_curr'] == 'rub')
                ].copy()

            if df_filtered.empty:
                continue

            # 2. Векторные расчеты без циклов (работают мгновенно)
            #Текущая стоимость
            df_filtered['current_amount'] = df_filtered['current_price'] * df_filtered['quantity']          #
            #Стоимость покупки
            df_filtered['average_amount'] = df_filtered['average_position_price'] * df_filtered['quantity'] #
            #Разница + прибыль - убыток
            df_filtered['delta'] = df_filtered['current_amount'] - df_filtered['average_amount']

            # 3. Сортировка по убыванию стоимости
            self.pd_print = df_filtered.sort_values('current_amount', ascending=False).reset_index(drop=True)

            # 4. Вывод и сохранение результатов
            #self.print_port()
            self.pd_port_ext = self.pd_print
            self.fname_ext_csv = filename

            self.out_csv_port_ext()


            # Фильтруем по двум условиям и берем конкретный столбец
            total_rub_xxxx = df_filtered.loc[
                (self.pd_port['instrument_type'] == inst_type) &
                (self.pd_port['current_price_curr'] == 'rub'),
                'current_amount'
            ].sum()

            print(inst_type)
            print(total_rub_xxxx)

        self.all_inst = []
        print(">>> end sort portfolio")



    def sort_portfolio(self):
        print("<<<< beg sort portfolio")
        # share  Stocks
        self.pd_port_share =pd.DataFrame(columns=self.pd_port)# create a frame
        self.pd_port_share = self.pd_port.loc[self.pd_port['instrument_type'] == 'share'] # create a stock pandas

        #self.pd_port_ext = pd.DataFrame(self.port_type)  # Pandas Portfolio + extra colunms
        # copy to extended pandas
        # dell rows from pd_port_ext
        self.pd_port_ext = pd.DataFrame(self.port_type_ext) # Pandas Portfolio + extra colunms
        #print(self.pd_port_ext)
        '''[ticker, name, average_position_price_curr, average_position_price, average_position_price_fifo_curr,
                 average_position_price_fifo, average_position_price_pt, blocked, blocked_lots, current_nkd_curr,
                 current_nkd, current_price_curr, current_price, expected_yield, expected_yield_fifo, figi,
                 instrument_type, instrument_uid, position_uid, quantity, quantity_lots, var_margin_curr, var_margin]
        '''
        for index, row in self.pd_port_share.iterrows():
            self.pd_port_ext.loc[len(self.pd_port_ext.index)] = [
                row['ticker'],
                row['name'],
                row['quantity'],
                row['current_price_curr'],
                row['current_price'],
                row['current_price'] * row['quantity'],  # 'current_amount': [],
                row['average_position_price_curr'],
                row['average_position_price'],
                row['average_position_price'] * row['quantity'],  #'average_amount':[],  # spent for position
                row['current_price'] * row['quantity'] - row['average_position_price'] * row['quantity'], # delta
                row['average_position_price_fifo_curr'],
                row['average_position_price_fifo'],
                row['average_position_price_pt'],
                row['blocked'],
                row['blocked_lots'],
                row['current_nkd_curr'],
                row['current_nkd'],
                row['expected_yield'],
                row['expected_yield_fifo'],
                row['figi'],
                row['instrument_type'],
                row['instrument_uid'],
                row['position_uid'],
                row['quantity_lots'],
                row['var_margin_curr'],
                row['var_margin']
                ]
        #self.pd_port.groupby(['instrument_type']).sum([])


        # currency

        self.pd_print = self.pd_port_ext.sort_values('current_amount',ascending=False)
        #self.pd_print = self.pd_port_ext
        self.pd_print = self.pd_print.loc[self.pd_print['current_price_curr'] == 'rub']
        self.pd_print = self.pd_print.reset_index(drop=True)
        self.print_port()
        self.pd_port_ext = self.pd_print
        self.fname_ext_csv = self.fname_share
        self.out_csv_port_ext()

        # ETF
        self.pd_port_etf =pd.DataFrame(columns=self.pd_port)# create a frame
        self.pd_port_etf = self.pd_port.loc[self.pd_port['instrument_type'] == 'etf'] # create a stock pandas
        #self.pd_port_ext.drop()
        print(self.pd_port_ext)
        self.pd_port_ext = pd.DataFrame(self.port_type_ext)  # Pandas Portfolio + extra colunms
        # copy to extended pandas
        print(self.pd_port_ext)
        '''[ticker, name, average_position_price_curr, average_position_price, average_position_price_fifo_curr,
                 average_position_price_fifo, average_position_price_pt, blocked, blocked_lots, current_nkd_curr,
                 current_nkd, current_price_curr, current_price, expected_yield, expected_yield_fifo, figi,
                 instrument_type, instrument_uid, position_uid, quantity, quantity_lots, var_margin_curr, var_margin]
        '''
        for index, row in self.pd_port_etf.iterrows():
            self.pd_port_ext .loc[len(self.pd_port_ext.index)] = [
                row['ticker'],
                row['name'],
                row['quantity'],
                row['current_price_curr'],
                row['current_price'],
                row['current_price'] * row['quantity'],  # 'current_amount': [],
                row['average_position_price_curr'],
                row['average_position_price'],
                row['average_position_price'] * row['quantity'],  #'average_amount':[],  # spent for position
                row['current_price'] * row['quantity'] - row['average_position_price'] * row['quantity'], # delta
                row['average_position_price_fifo_curr'],
                row['average_position_price_fifo'],
                row['average_position_price_pt'],
                row['blocked'],
                row['blocked_lots'],
                row['current_nkd_curr'],
                row['current_nkd'],
                row['expected_yield'],
                row['expected_yield_fifo'],
                row['figi'],
                row['instrument_type'],
                row['instrument_uid'],
                row['position_uid'],
                row['quantity_lots'],
                row['var_margin_curr'],
                row['var_margin']
                ]

        #self.pd_port.groupby(['instrument_type']).sum([])
        # bond
        # etf
        # currency
        self.pd_print = self.pd_port_ext.sort_values('current_amount',ascending=False)
        #self.pd_print = self.pd_port_ext
        self.pd_print = self.pd_print.loc[self.pd_print['current_price_curr'] == 'rub']
        self.pd_print = self.pd_print.reset_index(drop=True)
        self.print_port()
        self.fname_ext_csv = self.fname_etf
        self.pd_port_ext = self.pd_print
        self.out_csv_port_ext()
        self.all_inst = []


        # 3 BONDS
        self.pd_port_bond =pd.DataFrame(columns=self.pd_port)# create a frame
        self.pd_port_bond = self.pd_port.loc[self.pd_port['instrument_type'] == 'bond'] # create a stock pandas
        #self.pd_port_ext.drop()
        print(self.pd_port_ext)
        self.pd_port_ext = pd.DataFrame(self.port_type_ext)  # Pandas Portfolio + extra colunms
        # copy to extended pandas
        print(self.pd_port_ext)
        '''[ticker, name, average_position_price_curr, average_position_price, average_position_price_fifo_curr,
                 average_position_price_fifo, average_position_price_pt, blocked, blocked_lots, current_nkd_curr,
                 current_nkd, current_price_curr, current_price, expected_yield, expected_yield_fifo, figi,
                 instrument_type, instrument_uid, position_uid, quantity, quantity_lots, var_margin_curr, var_margin]
        '''
        for index, row in self.pd_port_bond.iterrows():
            self.pd_port_ext .loc[len(self.pd_port_ext.index)] = [
                row['ticker'],
                row['name'],
                row['quantity'],
                row['current_price_curr'],
                row['current_price'],
                row['current_price'] * row['quantity'],  # 'current_amount': [],
                row['average_position_price_curr'],
                row['average_position_price'],
                row['average_position_price'] * row['quantity'],  #'average_amount':[],  # spent for position
                row['current_price'] * row['quantity'] - row['average_position_price'] * row['quantity'], # delta
                row['average_position_price_fifo_curr'],
                row['average_position_price_fifo'],
                row['average_position_price_pt'],
                row['blocked'],
                row['blocked_lots'],
                row['current_nkd_curr'],
                row['current_nkd'],
                row['expected_yield'],
                row['expected_yield_fifo'],
                row['figi'],
                row['instrument_type'],
                row['instrument_uid'],
                row['position_uid'],
                row['quantity_lots'],
                row['var_margin_curr'],
                row['var_margin']
                ]

        #self.pd_port.groupby(['instrument_type']).sum([])
        # bond
        # etf
        # currency
        self.pd_print = self.pd_port_ext.sort_values('current_amount',ascending=False)
        #self.pd_print = self.pd_port_ext
        self.pd_print = self.pd_print.loc[self.pd_print['current_price_curr'] == 'rub']
        self.pd_print = self.pd_print.reset_index(drop=True) # обновление нумерации после фильтрации
        self.print_port()
        self.fname_ext_csv = self.fname_bond
        self.pd_port_ext = self.pd_print
        self.out_csv_port_ext()
        print(">>>> end sort portfolio")
    def print_port(self):
        for index, row in self.pd_print.iterrows():
            print(index, row['ticker'], row['name'], row['figi'],row['instrument_type'],"{:.2f}".format(row['current_amount']),"{:.2f}".format(row['delta']) )
    def out_csv_port_ext(self):
        #fname_ext = 'share' + self.fname


        fname_ext = self.fname_ext_csv

        print('out_csv_port_ext: out file ->', fname_ext)

        #return # temp for test

        with open(fname_ext, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    # quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #spamwriter.writerow(
            #    [''])
            spamwriter.writerow(
                [
                    'ticker',  # added
                    'name',  # name
                    'quantity',
                    'current_price_curr',
                    'current_price',  # Money curr
                    'current_amount',  # current amount
                    'average_position_price_curr',
                    'average_position_price',  # Money curr
                    'average_amount',  # spent for position
                    'delta',  # Прибыль/Убыток
                    'nkd' # nkd for bonds
            ]) # Money curr

            #        print(dir(row['accrued_int']))
            for index, row in self.pd_port_ext.iterrows():
                spamwriter.writerow([
                    row['ticker'],
                    row['name'],
                    row['quantity'],
                    row['current_price_curr'],
                    row['current_price'],  # Money curr
                    "{:.2f}".format(row['current_amount']),  # current amount
                    row['average_position_price_curr'],
                    row['average_position_price'],  # Money curr
                    "{:.2f}".format(row['average_amount']),#row['average_amount'],  # spent for position
                    "{:.2f}".format(row['delta']), # row['delta']  # Прибыль/Убыток
                    row['current_nkd']
                ])
    def out_csv_port(self):
        #data = pd.read_csv(fname, keep_default_na=False)
        with open(self.fname, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    # quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #spamwriter.writerow(
            #    [''])
            spamwriter.writerow(
                ['ticker', 'name', 'average_position_price_curr', 'average_position_price',
            'average_position_price_fifo_curr',             'average_position_price_fifo', # Money  curr
            'average_position_price_pt', # Money   _no_curr
            'blocked',
            'blocked_lots',
            'current_nkd_curr',
            'current_nkd', # Money curr
            'current_price_curr',
            'current_price', # Money curr
            'expected_yield',
            'expected_yield_fifo',
            'figi',
            'instrument_type',
            'instrument_uid',
            'position_uid',
            'quantity',
            'quantity_lots',
            'var_margin_curr',
            'var_margin']) # Money curr

            #        print(dir(row['accrued_int']))
            for index, row in self.pd_port.iterrows():
                spamwriter.writerow([
                    row['ticker'],
                    row['name'],
                    row['average_position_price_curr'],
                    row['average_position_price'],
                    row['average_position_price_fifo_curr'],
                    row['average_position_price_fifo'],
                    row['average_position_price_pt'],
                    row['blocked'],
                    row['blocked_lots'],
                    row['current_nkd_curr'],
                    row['current_nkd'],
                    row['current_price_curr'],
                    row['current_price'],
                    row['expected_yield'],
                    row['expected_yield_fifo'],
                    row['figi'],
                    row['instrument_type'],
                    row['instrument_uid'],
                    row['position_uid'],
                    row['quantity'],
                    row['quantity_lots'],
                    row['var_margin_curr'],
                    row['var_margin']
                ])
        #self.fname
    def porfolio_total_inf(self):
        print('<< beg porfolio_total_inf')

        portfolio = self.get_porfolio()
        print('Share', portfolio.total_amount_shares.currency, portfolio.total_amount_shares.units + portfolio.total_amount_shares.nano/1000000000)
        print('Bonds', portfolio.total_amount_bonds.currency, portfolio.total_amount_bonds.units + portfolio.total_amount_bonds.nano/1000000000)
        print('ETF', portfolio.total_amount_etf.currency, portfolio.total_amount_etf.units + portfolio.total_amount_etf.nano/1000000000)
        print('curr', portfolio.total_amount_currencies.currency, portfolio.total_amount_currencies.units + portfolio.total_amount_currencies.nano/1000000000)
        print('all', portfolio.total_amount_portfolio.currency, portfolio.total_amount_portfolio.units + portfolio.total_amount_portfolio.nano/1000000000)

        #'Name_pos': [],  # Total_etf
        #'curr': [],
        #'amount': [],  # name
        #'date': []

        today = date.today()
        d1 = today.strftime("%d.%m.%Y")

# Для вычислений по портфелю вручную по позициям
        df_filtered = self.pd_port[
            #(self.pd_port['instrument_type'] == 'share') &
            (self.pd_port['current_price_curr'] == 'rub')
            ].copy()
        # 2. Векторные расчеты без циклов (работают мгновенно)
        # Текущая стоимость
        df_filtered['current_amount'] = df_filtered['current_price'] * df_filtered['quantity']  #
        # Стоимость покупки
        df_filtered['average_amount'] = df_filtered['average_position_price'] * df_filtered['quantity']  #
        # Разница + прибыль - убыток
        df_filtered['delta'] = df_filtered['current_amount'] - df_filtered['average_amount']

        total_rub_curr_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'share') &
            (self.pd_port['current_price_curr'] == 'ru'),
            'current_amount'
        ].sum()
        total_rub_average_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'share') &
            (self.pd_port['average_position_price_curr'] == 'rub'),
            'average_amount'
        ].sum()
        delta = total_rub_curr_amount - total_rub_average_amount

        self.pd_port_total.loc[len(self.pd_port_total.index)] = [
            'Share',
            portfolio.total_amount_shares.currency,
            portfolio.total_amount_shares.units + portfolio.total_amount_shares.nano/1000000000, # amount
            d1,
            total_rub_curr_amount,
            total_rub_average_amount,
            delta,
        ]

        total_rub_curr_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'bond') &
            (self.pd_port['current_price_curr'] == 'rub'),
            'current_amount'
        ].sum()
        total_rub_average_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'bond') &
            (self.pd_port['average_position_price_curr'] == 'rub'),
            'average_amount'
        ].sum()
        delta = total_rub_curr_amount - total_rub_average_amount

        self.pd_port_total.loc[len(self.pd_port_total.index)] = [
            'Bonds',
            portfolio.total_amount_bonds.currency,
            portfolio.total_amount_bonds.units + portfolio.total_amount_bonds.nano/1000000000, # amount
            d1,
            total_rub_curr_amount,
            total_rub_average_amount,
            delta,
        ]

        total_rub_curr_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'etf') &
            (self.pd_port['current_price_curr'] == 'rub'),
            'current_amount'
        ].sum()
        total_rub_average_amount = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'etf') &
            (self.pd_port['average_position_price_curr'] == 'rub'),
            'average_amount'
        ].sum()
        delta =  total_rub_curr_amount - total_rub_average_amount

        self.pd_port_total.loc[len(self.pd_port_total.index)] = [
            'ETF',
            portfolio.total_amount_etf.currency,
            portfolio.total_amount_etf.units + portfolio.total_amount_etf.nano/1000000000, # amount
            d1,
            total_rub_curr_amount,
            total_rub_average_amount,
            delta,
        ]
        self.pd_port_total.loc[len(self.pd_port_total.index)] = [
            'curr',
            portfolio.total_amount_currencies.currency,
            portfolio.total_amount_currencies.units + portfolio.total_amount_currencies.nano/1000000000, # amount
            d1,
            1,
            1,
            0
        ]
        self.pd_port_total.loc[len(self.pd_port_total.index)] = [
            'Total',
            portfolio.total_amount_portfolio.currency,
            portfolio.total_amount_portfolio.units + portfolio.total_amount_portfolio.nano/1000000000, # amount
            d1,
            1,
            1,
            1
        ]

        print(self.pd_port_total)


        print("calculate fact itogo:")


        # Var2
        df_filtered = self.pd_port[
            #(self.pd_port['instrument_type'] == 'share') &
            (self.pd_port['current_price_curr'] == 'rub')
            ].copy()

        # 2. Векторные расчеты без циклов (работают мгновенно)
        # Текущая стоимость
        df_filtered['current_amount'] = df_filtered['current_price'] * df_filtered['quantity']  #
        # Стоимость покупки
        df_filtered['average_amount'] = df_filtered['average_position_price'] * df_filtered['quantity']  #
        # Разница + прибыль - убыток
        df_filtered['delta'] = df_filtered['current_amount'] - df_filtered['average_amount']

        total_rub_xxxx = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'share') &
            (self.pd_port['current_price_curr'] == 'rub'),
            'current_amount'
        ].sum()

        #money = total_rub_xxxx
        # Сначала округляем до 2 знаков, затем меняем '.' на ','
        total_rub_xxxx = f"{total_rub_xxxx:.2f}".replace('.', ',')
        print("var2 total_rub_share:", total_rub_xxxx)

        total_rub_xxxx = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'bond') &
            (self.pd_port['current_price_curr'] == 'rub'),
            'current_amount'
        ].sum()

        # Сначала округляем до 2 знаков, затем меняем '.' на ','
        total_rub_xxxx = f"{total_rub_xxxx:.2f}".replace('.', ',')
        print("var2 total_rub_bond:", total_rub_xxxx)


        total_rub_xxxx = df_filtered.loc[
            (self.pd_port['instrument_type'] == 'etf') &
            (self.pd_port['current_price_curr'] == 'rub'),
            'current_amount'
        ].sum()
        money = total_rub_xxxx
        # Сначала округляем до 2 знаков, затем меняем '.' на ','
        total_rub_xxxx = f"{total_rub_xxxx:.2f}".replace('.', ',')
        print("var2 total_rub_etf:", total_rub_xxxx)

        ## Сначала разделяем подчеркиванием, а затем меняем его на пробел
        #formatted = f"{money:_.2f}".replace("_", " ")
        #print("var2 total_rub_xxxx:", formatted)

        #total_rub_xxxx = df_filtered.loc[
        #    (self.pd_port['instrument_type'] == 'bond') &
        #    (self.pd_port['current_price_curr'] == 'rub'),
        #    'current_amount'
        #].sum()
        #money = total_rub_xxxx
        ## Сначала разделяем подчеркиванием, а затем меняем его на пробел
        #formatted = f"{money:_.2f}".replace("_", " ")
        #print("var2 total_rub_bond:", formatted)

        #total_rub_xxxx = df_filtered.loc[
        #    (self.pd_port['instrument_type'] == 'etf') &
        #    (self.pd_port['current_price_curr'] == 'rub'),
        #    'current_amount'
        #].sum()
        #money = total_rub_xxxx
        ## Сначала разделяем подчеркиванием, а затем меняем его на пробел
        #formatted = f"{money:_.2f}".replace("_", " ")
        #print("var2 total_rub_ETF:", formatted)

        #print(self.pd_port_total)


        #portfolio.total_amount_etf
        #print(portfolio.)

 # port_pos.average_position_price.units + port_pos.average_position_price.nano/1000000000,

   #fname_ext = 'share' + self.fname
        fname_ext = self.fname_total
        with open(fname_ext, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    # quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #spamwriter.writerow(
            #    [''])
            spamwriter.writerow(
                [
                    'act',  # added
                    'curr',  # name
                    'amount',
                    'date',
                    'curr_amount',
                    'avr_amount',
                    'delta'
                ]) # Money curr

            #        print(dir(row['accrued_int']))
            for index, row in self.pd_port_total.iterrows():
                spamwriter.writerow([
                    row['Name_pos'],
                    row['curr'],
                    row['amount'],
                    row['date'],
                    f"{row['curr_amount']:.2f}",
                    f"{row['avr_amount']:.2f}",
                    f"{row['delta']:.2f}"
                ])

    print('>> end porfolio_total_inf')
#class  inv_operations:
#    def __init__(self):
# cl_tinv_db - класс для сохранения данных в DB

class inv_db:
    #  save data from tinkoff to DB
    def __init__(self,account_id = '0'):
        def cr_tab_toperations_sql(self):
            """
            :param self:
            :return: # SQL запроса на создание таблицы
            """

            cr_tab_sql = '''
            CREATE TABLE IF NOT EXISTS toperations (
            cursor               TEXT,                            
            broker_account_id    TEXT,
            id                   TEXT,
            parent_operation_id  TEXT,
            name                 TEXT,
            date_msk             TEXT,             
            time_msk             TEXT,             
            type                 TEXT,             
            type_txt             TEXT,             
            description          TEXT,             
            state                TEXT,             
            instrument_uid       TEXT,             
            figi                 TEXT,             
            instrument_type      TEXT,             
            instrument_kind      TEXT,             
            position_uid         TEXT,             
            payment              TEXT,             
            price                TEXT,             
            commission           TEXT,             
            yield                TEXT,             
            yield_relative       TEXT,             
            accrued_int          TEXT,             
            quantity             TEXT,             
            quantity_rest        TEXT,             
            quantity_done        TEXT,             
            cancel_time_msk      TEXT, 
            cancel_date_msk      TEXT, 
            cancel_reason        TEXT,             
            trades_info          TEXT,             
            asset_uid            TEXT,
            child_operations     TEXT                                                                                         
            )
            '''
            return cr_tab_sql
        self.token = os.environ.get('TOKEN')
        self.account_id = account_id
        print('Счет по умолчанию')
        if self.account_id == '0':
            print('Будет выбран первый счет')
        self.cr_tab_toperations_sql = cr_tab_toperations_sql(self) # SQL запрос на создание таблицы toperations

        self.figi_info_short = {}

        # Types for Pandas and for SQL tab
        self.toperations = {
            'cursor':[],
            'broker_account_id':[],
            'id':[],
            'parent_operation_id':[],
            'name':[],
            'date_msk':[],
            'time_msk':[],
            'type':[],
            'type_txt':[],
            'description':[],
            'state':[],
            'instrument_uid':[],
            'figi':[],
            'instrument_type':[],
            'instrument_kind':[],
            'position_uid':[],
            'payment':[],
            'price':[],
            'commission':[],
            'yield':[],
            'yield_relative':[],
            'accrued_int':[],
            'quantity':[],
            'quantity_rest':[],
            'quantity_done':[],
            'cancel_time_msk':[],
            'cancel_date_msk':[],
            'cancel_reason':[],
            'trades_info':[],    # здесь массив операций дополнительных
            'asset_uid':[],
            'child_operations':[],
            'fin_day':[]         # запись операций после заверщения дня
        }

    def op_to_db_upd(self):
        # дополнительно
        print('<UNK> <UNK> <UNK> <UNK>')
        #with Client(token) as client:
        #    accounts = client.users.get_accounts()
        #    account_id = accounts.accounts[0].id
        #    acc_id = account_id
        #    print(accounts.accounts[0])
        # сохраняем операции в DB
        #for operation in self.cr_tab_toperations_sql

    def get_op_by_cursor(self,token = '') -> pd.DataFrame:
        # дополнительно параметры account_id, dates
        if token == '':
            token = self.token
        with Client(token) as client:
            accounts = client.users.get_accounts()
            account_id = accounts.accounts[0].id
            acc_id = account_id
            opened_date = accounts.accounts[0].opened_date  # portfoilio open date
            def get_request(cursor=""):
                return GetOperationsByCursorRequest(
                    account_id=account_id,
                    from_=now() - timedelta(days=10000),
                    to=now() - timedelta(days=0),
                    # instrument_id="BBG004730N88",
                    cursor=cursor,
                    limit=1000,
                )

            #self.toperations = []
            new_ops = []
            df = pd.DataFrame(self.toperations)
            pack = 0
            operations = client.operations.get_operations_by_cursor(get_request())
            while True:
                print(f'Pack {pack}')
                pack += 1
                for op in operations.items:
                    new_ops.append({
                        'id': op.id,
                        'date': op.date,
                        'type': op.type.name,
                        'figi': op.figi,
                        'payment': op.payment.units + op.payment.nano / 1e9,
                        'currency': op.payment.currency,
                        'description': op.description
                    })
                    # Просто пушим в список
                    #self.toperations.append(new_operation)

                if  not operations.has_next: # выходим из цикла
                    break

                request = get_request(cursor=operations.next_cursor)
                operations = client.operations.get_operations_by_cursor(request)

#            # 3. Сохраняем новые данные
            if new_ops:
                new_df = pd.DataFrame(new_ops)
#                # Используем метод, чтобы избежать дубликатов по ID (если нужно)
#                new_df.to_sql(table_name, conn, if_exists='append', index=False)
#                print(f"Загружено операций: {len(new_df)}")

                connection = sqlite3.connect('my_database.db')
                cursor = connection.cursor()
                new_df.to_sql('oper_lite_all', connection, if_exists='append', index=False)
                print(f"Загружено операций: {len(new_df)}")

            # 4. Возвращаем результат
#            full_df = pd.read_sql(f"SELECT * FROM {table_name} ORDER BY date", conn, parse_dates=['date'])
#            conn.close()
            return new_df



        print('<UNK> <UNK> <UNK> <UNK> <UNK>')
        #df1 = pd.DataFrame(self.toperations)
        df1 = pd.DataFrame(self.test_qwe)
        return df1
        #return pd.DataFrame(self.toperations['cursor'])
    def save_op_db(self, df: pd.DataFrame):
        df.loc[len(df.index)] = [
            '-',  # No ticker found
        ]
        print(df)


# beg test part
    def get_figi_info(self, figi,token = ''):
        # метод создает справочник self.figi_info_short
        #
        if self.figi_info_short == {}:
            #all_data = []
            if token == '':
                token = self.token
            with Client(token) as client:
                # 1. Получаем списки разных типов инструментов
                # InstrumentStatus.BASE — только те, что доступны для торговли сейчас
                shares = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments
                bonds = client.instruments.bonds(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments
                etfs = client.instruments.etfs(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE).instruments

                # 2. Объединяем и извлекаем нужные поля
                self.figi_info_short = {
                    instr.figi: {
                        'name': instr.name,
                        'ticker': instr.ticker,
                        'type': type(instr).__name__
                    }
                    for instr in (shares + bonds + etfs)
                }
                #print(self.figi_info_short)

        res2 = self.figi_info_short.get(figi, {'figi': figi,'name':'-','ticker':'-','type':'-'})
            #res1 = {'figi': figi,
            #        'name':  self.figi_info_short.get(figi),
            #        'ticker': res['ticker'],
            #        'type': type(res).__name__}
            #print(by_uid.get('Анн1а', {}).get("возраст", "not found"))
        #print(res2.get('name','name not found'))

        #print(type(self.figi_info_short))
        #self.figi_info_short = {}
        res2 = self.figi_info_short.get(figi, {'figi': figi, 'name': '-', 'ticker': '-', 'type': '-'})
        #print(res2.get('name', 'name not found'))
        return res2

    def get_assets(self,token = ''):
        if token == '':
            token = self.token
        with Client(token) as client:
            accounts = client.users.get_accounts()
            account_id = accounts.accounts[0].id
            acc_id = account_id
            opened_date = accounts.accounts[0].opened_date  # portfoilio open date
            assets = client.instruments.get_assets(request=AssetsRequest())
            #assets = client.instruments.get_assets(
            print(dir(assets))
            print(type(assets))
            print(len(assets.assets))
            for asset in assets.assets:
                #asset.
                for inst in asset.instruments:
                    if asset.type == 100:
                        print(f'Ticker instrument_type  check ! {inst.ticker},{inst.instrument_type}')
                    if inst.ticker == 'TSOX':
                    #if inst.ticker == 'TMON@':
                        print("FOUND")
                        print(f'asset.uid{asset.uid}')
                        print(f'AssetInstrument.uid UID-идентификатор инструмента. {inst.uid}')
                        print(f'AssetInstrument.position_uid ID позиции. {inst.position_uid}')
                        print(f'Ticker instrument_type asset.type {inst.ticker}, {inst.instrument_type}, {asset.type}, {asset.type.name}')
                        print(dir(inst.instrument_type))
                        print(type(inst.instrument_type))
                        if inst.instrument_type == 2:
                            print(f'Ticker instrument_type = 2 {inst.ticker}, {inst.instrument_type}')


                #l1 = len(asset.instruments)
                #if l1 >1:
                #    print(asset.name)
                #    for inst in asset.instruments:
                #        print(inst.figi)
                #        print(inst.ticker)
            etfs = client.instruments.etfs(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL)

            print(f'Записей ETFS {len(etfs.instruments)}')

            for etf in etfs.instruments:
                if etf.ticker == 'TSOX':
                    print(f'ETFS {etf.ticker}, {etf.name}, {etf.figi}')
            #for etf in etfs.etfs:
            shares = client.instruments.shares()
            print(f'Записей shares {len(shares.instruments)}')
            bonds = client.instruments.bonds()
            print(f'Записей bonds {len(bonds.instruments)}')
            Currencies = client.instruments.currencies()
            print(f'Записей Currencies {len(Currencies.instruments)}')

            # BBG004731032 - figi
            # Создаем индекс "на лету"
            shares_figi = {i.figi: i for i in shares.instruments}
            # Мгновенно достаем нужное
            item = shares_figi.get("BBG004731032")
            print(item)
            #print(item, item.name)


    def temp_test_cls(self):
        a = 1
        self.get_assets()
        #t1 = {}
        #t1 = self.get_figi_info('BBG004731032')
        #print(t1.get('name'))
        #t1 = self.get_figi_info('BBG000BBCQD7')
        #print(t1.get('name'))
#        self.get_assets()
#        specific_date = datetime(year=2024, month=12, day=25, hour=10, minute=30)
#        print(specific_date)
##        print(specific_date.date())
#        print(specific_date.time())
#        to = now() - timedelta(days=0)
#        print(to)


        #df = self.get_op_by_cursor()
        #self.save_op_db(df)
        #self.test_qwe[]

# end test part








