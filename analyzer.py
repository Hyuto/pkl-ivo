import os, re, json, logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.auto import tqdm


class Analyzer:
    def __init__(self, data, analisis):
        self.analisis = analisis
        with open('keywords.json') as reader:
            self.keywords = json.load(reader)[analisis]
        self.data = data

    def _check_dir(self, filename):
        if not os.path.isdir('./output'):
            os.mkdir('./output')

        if os.path.isfile(f'./output/{filename}'):
            logging.warning('Terdapat file lama!')
            user = input('   *  Overwrite? [y/n] ')
            print()
            if user.lower() == 'y':
                return True
            elif user.lower() == 'n':
                return False
            else:
                raise NotImplementedError('Input error!')
        return True

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
            df = pd.DataFrame({
                self.analisis:
                result.keys(),
                'jumlah':
                result.values(),
                'persentase': [x / total * 100 for x in result.values()]
            })

            filename = f'{self.analisis.upper()}_{self.data.date.min().strftime("%d %b %Y")} - ' + \
                       f'{self.data.date.max().strftime("%d %b %Y")}.csv'

            if self._check_dir(filename):
                df.to_csv(f'./output/{filename}', index=False)
                logging.info(f'Exported to "output/{filename}"')
