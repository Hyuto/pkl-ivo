import os, re, json, logging
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from utils import check_dir
from datetime import datetime


class Analyzer:
    def __init__(self, data, analisis):
        self.analisis = analisis
        with open("keywords.json") as reader:
            self.keywords = json.load(reader)[analisis]
        self.data = data

    def analyse(self, export, config):
        result = {}
        range_time = pd.date_range(
            datetime.strptime(config["period"]["start"], "%d/%m/%Y"),
            datetime.strptime(config["period"]["stop"], "%d/%m/%Y"),
            freq="M",
        )
        data = self.data.copy()
        for i, x in enumerate(tqdm(range_time.values)):
            temp_data = data.loc[data["datetime"] <= x]
            temp_result = {}
            for key, value in self.keywords.items():
                patterns = [fr"\b{x}\b" for x in value]
                patterns = fr'{"|".join(patterns)}'
                count = [len(re.findall(patterns, x)) for x in temp_data.message.values]
                temp_result[key] = sum(count)
            result[datetime.strptime(str(range_time.month[i]), "%m").strftime("%B")] = temp_result
            data = data.loc[data["datetime"] > x]
        print()

        logging.info("Hasil")
        for m in result:
            print(m)
            total = sum(result[m].values())
            for key, value in result[m].items():
                print(f"   *  {key} : {value} ({round(value / total * 100, 2)}%)")
            print()
        print()

        if export:
            logging.info(f"Exporting data")
            export_data = {"bulan": [], self.analisis: [], "jumlah": [], "persentase": []}

            for m in result:
                export_data["bulan"] += [m for i in range(len(result[m]))]
                total = sum(result[m].values())
                export_data[self.analisis] += list(result[m].keys())
                export_data["jumlah"] += list(result[m].values())
                export_data["persentase"] += [
                    round(value / total * 100, 4) for value in result[m].values()
                ]

            df = pd.DataFrame(export_data)

            filename = (
                f'{self.analisis.upper()}_{self.data.datetime.min().strftime("%d %b %Y")} - '
                + f'{self.data.datetime.max().strftime("%d %b %Y")}.csv'
            )

            status, path = check_dir(filename)
            if status:
                df.to_csv(path, index=False)
