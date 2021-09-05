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
        result_data = {}
        range_time = pd.date_range(
            datetime.strptime(config["period"]["start"], "%d/%m/%Y"),
            datetime.strptime(config["period"]["stop"], "%d/%m/%Y"),
            freq="M",
        )
        data = self.data.copy()
        for i, x in enumerate(tqdm(range_time.values)):
            temp_data = data.loc[data["datetime"] <= x]
            temp_result = {}
            temp_result_data = {}
            for key, value in self.keywords.items():
                patterns = [fr"\b{x}\b" for x in value]
                patterns = fr'{"|".join(patterns)}'
                search = [
                    [re.findall(patterns, x[0]), *x.tolist()]
                    for x in temp_data[
                        ["message", "url", "comments", "likes", "shares", "views"]
                    ].values
                    if len(re.findall(patterns, x[0])) > 0
                ]
                temp_result[key] = sum([len(x[0]) for x in search])
                temp_result_data[key] = {
                    "message": [x[1] for x in search],
                    "filtered": [" ".join(x[0]) for x in search],
                    "url": [x[2] for x in search],
                    "comments": [x[3] for x in search],
                    "likes": [x[4] for x in search],
                    "shares": [x[5] for x in search],
                    "views": [x[6] for x in search],
                }
            result[datetime.strptime(str(range_time.month[i]), "%m").strftime("%B")] = temp_result
            result_data[
                datetime.strptime(str(range_time.month[i]), "%m").strftime("%B")
            ] = temp_result_data
            data = data.loc[data["datetime"] > x]
        print()

        logging.info("Hasil")
        for m in result:
            print(m)
            total = sum(result[m].values())
            for key, value in result[m].items():
                if total > 0:
                    print(f"   *  {key} : {value} ({round(value / total * 100, 2)}%)")
                else:
                    print(f"   *  {key} : {value} (0%)")
            print()
        print()

        if export:
            logging.info(f"Exporting data")
            export_summary = {"bulan": [], self.analisis: [], "jumlah": [], "persentase": []}
            export_data = {
                "bulan": [],
                self.analisis: [],
                "message": [],
                "filtered": [],
                "url": [],
                "comments": [],
                "likes": [],
                "shares": [],
                "views": [],
            }

            for m in result:
                export_summary["bulan"] += [m for i in range(len(result[m]))]
                total = sum(result[m].values())
                export_summary[self.analisis] += list(result[m].keys())
                export_summary["jumlah"] += list(result[m].values())
                export_summary["persentase"] += [
                    round(value / total * 100, 4) if total > 0 else 0
                    for value in result[m].values()
                ]

            for m in result_data:
                for sub in result_data[m]:
                    export_data["message"] += result_data[m][sub]["message"]
                    export_data["filtered"] += result_data[m][sub]["filtered"]
                    export_data["url"] += result_data[m][sub]["url"]
                    export_data["comments"] += result_data[m][sub]["comments"]
                    export_data["likes"] += result_data[m][sub]["likes"]
                    export_data["shares"] += result_data[m][sub]["shares"]
                    export_data["views"] += result_data[m][sub]["views"]
                    export_data[self.analisis] += [sub] * len(result_data[m][sub]["message"])
                    export_data["bulan"] += [m] * len(result_data[m][sub]["message"])

            sheet1 = pd.DataFrame(export_summary)
            sheet2 = pd.DataFrame(export_data)

            filename = (
                f'{self.analisis.upper()}_{self.data.datetime.min().strftime("%d %b %Y")} - '
                + f'{self.data.datetime.max().strftime("%d %b %Y")}.xlsx'
            )

            status, path = check_dir(filename)
            if status:
                writer = pd.ExcelWriter(path, engine="xlsxwriter")
                sheet1.to_excel(writer, sheet_name="summary", index=False)
                sheet2.to_excel(writer, sheet_name="data", index=False)
                writer.save()
