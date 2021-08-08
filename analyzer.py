import os, re, json, logging
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from utils import check_dir


class Analyzer:
    def __init__(self, data, analisis):
        self.analisis = analisis
        with open('keywords.json') as reader:
            self.keywords = json.load(reader)[analisis]
        self.data = data

    def analyse(self, export):
        result = {}
        for key, value in tqdm(self.keywords.items()):
            patterns = [fr'\b{x}\b' for x in value]
            patterns = fr'{"|".join(patterns)}'
            count = [
                len(re.findall(patterns, x)) for x in self.data.message.values
            ]
            result[key] = sum(count)
        print()

        logging.info('Hasil')
        total = sum(result.values())
        for key, value in result.items():
            print(f'   *  {key} : {value} ({round(value / total * 100, 2)}%)')
        print()

        if export:
            logging.info(f'Exporting data')

            df = pd.DataFrame({
                self.analisis:
                result.keys(),
                'jumlah':
                result.values(),
                'persentase': [x / total * 100 for x in result.values()]
            })

            filename = f'{self.analisis.upper()}_{self.data.datetime.min().strftime("%d %b %Y")} - ' + \
                       f'{self.data.datetime.max().strftime("%d %b %Y")}.csv'

            status, path = check_dir(filename)
            if status:
                df.to_csv(path, index=False)
