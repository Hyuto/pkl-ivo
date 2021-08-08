import os, json
import logging, string
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm.auto import tqdm
from utils import check_dir

PUNC_WHITESPACE = str.maketrans(string.punctuation,
                                ' ' * len(string.punctuation))
DIGITS_WHITESPACE = str.maketrans(string.digits, ' ' * len(string.digits))


class Data:
    def __init__(self, path, config):
        self.path = path
        self.config = config

    def _read_dataset(self):
        """ Reading CSV Data """
        if os.path.isfile(self.path):
            logging.info(f'Loading dataset from file {self.path}')
            data = pd.read_csv(self.path)
        elif os.path.isdir(self.path):
            logging.info(f'Loading dataset from directory {self.path}')
            names = [os.path.join(self.path, x) for x in os.listdir(self.path)]
            data = pd.concat([pd.read_csv(x) for x in names])
        else:
            raise NotImplementedError('Error di file datanya')
        return data

    @staticmethod
    def _get_info(data, nan_desc=None):
        """ Print datasetn info """
        logging.info('Sukses loading data!')
        print(data.head())
        print()

        logging.info('Dataset Information')
        print(
            f'   *  Rentang Tanggal : {data.datetime.min().strftime("%d %b %Y")} - '
            + f'{data.datetime.max().strftime("%d %b %Y")}')
        print(f'   *  N data          : {data.shape[0]}')
        if type(nan_desc) == pd.Series:
            print('   *  Data hilang')
            print('\n'.join([
                f'      ~  {x[0]} : {x[1]}' for x in nan_desc.items()
                if x[0] != 'datetime'
            ]))
        elif type(nan_desc) == int:
            print(f'   *  N NaN           : {nan_desc.values.sum()}')
        print()

    def generate_dataset(self):
        """ Generate forecasting dataset """
        logging.info('Generating forecasting data')
        data = self._read_dataset()  # read csv

        # Preprocess data
        columns = ['datetime', 'sentiment']
        logging.info('Preprocess Data!')
        data['datetime'] = data['date'] + ' ' + data['time']
        data = data[columns]
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.sort_values(by=['datetime'], inplace=True)
        data.dropna(inplace=True)

        # Grouping by datetime
        if self.config['groupby'] == 'hour':
            grouping = [
                data['datetime'].dt.date, data['datetime'].dt.hour, 'sentiment'
            ]
            freq = 'H'
        elif self.config['groupby'] == 'day':
            grouping = [data['datetime'].dt.date, 'sentiment']
            freq = 'D'
        else:
            raise NotImplementedError('Config Error ! [groupby]')

        sentiments = ['negative', 'neutral', 'positive']
        data_baru = data.groupby(grouping).count()

        # Create new dataframe with forecast format
        data = pd.DataFrame({
            'datetime':
            pd.date_range(datetime.strptime(self.config['period']['start'],
                                            '%d/%m/%Y'),
                          datetime.strptime(self.config['period']['stop'],
                                            '%d/%m/%Y'),
                          freq=freq)
        })

        for sentiment in tqdm(sentiments):
            data_sentiment = data_baru.loc[
                [True if sentiment in x else False for x in data_baru.index], ]
            if self.config['groupby'] == 'hour':
                date = [
                    datetime(year=x[0].year,
                             month=x[0].month,
                             day=x[0].day,
                             hour=x[1]) for x in data_sentiment.index
                ]
            elif self.config['groupby'] == 'day':
                date = [
                    datetime(year=x[0].year, month=x[0].month, day=x[0].day)
                    for x in data_sentiment.index
                ]
            else:
                raise NotImplementedError('Config Error ! [groupby]')
            temp = pd.DataFrame({
                'datetime':
                date,
                sentiment:
                data_sentiment.to_numpy().flatten().astype('float32')
            })
            data = data.merge(temp, on='datetime', how='left')
        print()

        # Handle missing data
        nan_desc = data.isna().sum()
        for sentiment in sentiments:
            if self.config['handle-missing'] == 'mean':
                fill = data[sentiment].mean()
            elif self.config['handle-missing'] == 'median':
                fill = data[sentiment].median()
            elif type(self.config['handle-missing']) in [int, float]:
                fill = self.config['handle-missing']
            else:
                raise NotImplementedError('Config Error ! [handle-missing]')

            data[sentiment] = data[sentiment].fillna(fill)

        self._get_info(data, nan_desc)  # print info

        # Export
        logging.info('Exporting data')
        filename = f'Forecast Data_{data.datetime.min().strftime("%d %b %Y")} - ' + \
                   f'{data.datetime.max().strftime("%d %b %Y")}.csv'
        status, path = check_dir(filename)
        if status:
            data.to_csv(path, index=False)

        return data

    def read_forecast_data(self):
        logging.info('Reading forecasting data')
        data = self._read_dataset()

        data_format = ['datetime', 'negative', 'neutral', 'positive']
        if list(data.columns) != data_format:
            raise NotImplementedError('Format dataset salah! Tolong gunakan ' +
                                      'data hasil generate dari script')

        logging.info('Preprocess Data!')
        data['datetime'] = pd.to_datetime(data['datetime'])
        data.sort_values(by=['datetime'], inplace=True)

        self._get_info(data)

        return data

    @staticmethod
    def preprocess_text_data(s):
        s = s.lower()
        s = s.translate(DIGITS_WHITESPACE)
        s = s.translate(PUNC_WHITESPACE)
        s = ' '.join(s.split())
        return s

    def read_ocean_emotion_data(self):
        # Read dataset
        data = self._read_dataset()[['date', 'message']]

        # Preprocess Dataset
        data['date'] = pd.to_datetime(data['date'])
        data.sort_values(by=['date'], inplace=True)
        data.rename(columns={'date': 'datetime'}, inplace=True)
        nan_desc = data.isna().sum()
        data.dropna(inplace=True)
        data['message'] = data['message'].apply(
            lambda x: self.preprocess_text_data(x))

        self._get_info(data, nan_desc)

        return data
