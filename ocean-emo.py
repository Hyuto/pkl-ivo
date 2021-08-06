import os, argparse, logging
import string, re, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.auto import tqdm

PUNC_WHITESPACE = str.maketrans(string.punctuation,
                                ' ' * len(string.punctuation))
DIGITS_WHITESPACE = str.maketrans(string.digits, ' ' * len(string.digits))


def preprocess(s):
    s = s.lower()
    s = s.translate(DIGITS_WHITESPACE)
    s = s.translate(PUNC_WHITESPACE)
    s = ' '.join(s.split())
    return s


def read_dataset(path):
    # Read Dataset
    if os.path.isfile(path):
        logging.info(f'Loading dataset from file {path}')
        data = pd.read_csv(path)[['date', 'message']]
    elif os.path.isdir(path):
        logging.info(f'Loading dataset from directory {path}')
        names = [os.path.join(path, x) for x in os.listdir(path)]
        data = pd.concat([pd.read_csv(x) for x in names])[['date', 'message']]
    else:
        raise OSError('Error di file datanya')

    # Preprocess Dataset
    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by=['date'], inplace=True)
    nan_desc = data.isna().sum()
    data.dropna(inplace=True)
    data['message'] = data['message'].apply(lambda x: preprocess(x))

    logging.info('Sukses loading data!')
    print(data.head())
    print()

    logging.info('Dataset Information')
    print(f'Rentang Tanggal : {data.date.min()} - {data.date.max()}')
    print(f'N data          : {data.shape[0]}')
    print(f'N NaN           : {nan_desc.values.sum()}')
    print()

    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script untuk melakukan analisis & OCEAN")
    parser.add_argument(
        "-p",
        "--path",
        help="Path ke data atau direktori tempat penyimpanan data",
        type=str,
        required=True)
    parser.add_argument(
        "-a",
        "--analysis",
        help="Tipe analisis yang digunakan 'emotion' atau 'ocean'",
        type=str)

    args = parser.parse_args()
    logging.basicConfig(format='[ %(levelname)s ] %(message)s',
                        level=logging.INFO)

    data = read_dataset(args.path)

    if args.analysis:
        with open('keywords.json') as reader:
            keywords = json.load(reader)
