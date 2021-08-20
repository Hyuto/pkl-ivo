import os, json, re
import logging, string
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from tqdm.auto import tqdm

PUNC_WHITESPACE = str.maketrans(string.punctuation, " " * len(string.punctuation))
DIGITS_WHITESPACE = str.maketrans(string.digits, " " * len(string.digits))


class Data:
    def __init__(self, path, config):
        self.path = path
        self.config = config

    def _read_dataset(self):
        """Reading CSV Data"""
        if os.path.isfile(self.path):
            logging.info(f"Loading dataset from file {self.path}")
            data = pd.read_csv(self.path)
        elif os.path.isdir(self.path):
            logging.info(f"Loading dataset from directory {self.path}")
            names = [os.path.join(self.path, x) for x in os.listdir(self.path)]
            data = pd.concat([pd.read_csv(x) for x in names])
        else:
            raise NotImplementedError("Error di file datanya")
        return data

    @staticmethod
    def _get_info(data, nan_desc=None):
        """Print datasetn info"""
        logging.info("Sukses loading data!")
        print(data.head())
        print()

        logging.info("Dataset Information")
        print(
            f'   *  Rentang Tanggal : {data.datetime.min().strftime("%d %b %Y")} - '
            + f'{data.datetime.max().strftime("%d %b %Y")}'
        )
        print(f"   *  N data          : {data.shape[0]}")
        if type(nan_desc) == pd.Series:
            print("   *  Data hilang")
            print(
                "\n".join(
                    [f"      ~  {x[0]} : {x[1]}" for x in nan_desc.items() if x[0] != "datetime"]
                )
            )
        elif type(nan_desc) == int:
            print(f"   *  N NaN           : {nan_desc.values.sum()}")
        print()

    @staticmethod
    def find(x, patterns):
        try:
            return True if re.findall(patterns, x, flags=re.IGNORECASE) != [] else False
        except:
            return False

    def generate_dataset(self, filters=None):
        """Generate forecasting dataset"""
        logging.info("Generating forecasting data")
        data = self._read_dataset()  # read csv

        if filters:
            logging.info("Filtering Data")
            print("   *  Keywords :")
            for i, x in enumerate(filters.split(",")):
                print(f"      {i + 1}.  {x}")

            patterns = [fr"\b{x}\b" for x in filters.split(",")]
            patterns = fr'{"|".join(patterns)}'
            data = data.loc[data["message"].apply(lambda x: self.find(x, patterns))]

        # Preprocess data
        columns = ["datetime", "sentiment"]
        logging.info("Preprocess Data!")
        data["datetime"] = data["date"] + " " + data["time"]
        data = data[columns]
        data["datetime"] = pd.to_datetime(data["datetime"])
        data.sort_values(by=["datetime"], inplace=True)
        data.dropna(inplace=True)

        # Grouping by datetime
        grouping = [data["datetime"].dt.date, data["datetime"].dt.hour, "sentiment"]
        freq = "H"

        sentiments = ["negative", "neutral", "positive"]
        data_baru = data.groupby(grouping).count()

        # Create new dataframe with forecast format
        data = pd.DataFrame(
            {
                "datetime": pd.date_range(
                    datetime.strptime(
                        self.config["period"]["start"] + " 00:00:00", "%d/%m/%Y %H:%M:%S"
                    ),
                    datetime.strptime(
                        self.config["period"]["stop"] + " 23:59:59", "%d/%m/%Y %H:%M:%S"
                    ),
                    freq=freq,
                )
            }
        )

        for sentiment in tqdm(sentiments):
            data_sentiment = data_baru.loc[
                [True if sentiment in x else False for x in data_baru.index],
            ]
            date = [
                datetime(year=x[0].year, month=x[0].month, day=x[0].day, hour=x[1])
                for x in data_sentiment.index
            ]
            temp = pd.DataFrame(
                {"datetime": date, sentiment: data_sentiment.to_numpy().flatten().astype("float32")}
            )
            data = data.merge(temp, on="datetime", how="left")
        print()

        # Grouping by datetime
        if self.config["groupby"] == "hour":
            pass
        elif self.config["groupby"] == "day":
            data = data.resample("D", on="datetime").sum()
        elif self.config["groupby"] == "week":
            day = data["datetime"][0] + timedelta(days=6)
            data = data.resample(f"W-{day.strftime('%a')}", on="datetime").sum()
        else:
            raise NotImplementedError("Config Error ! [groupby]")

        # Handle missing data
        nan_desc = data.isna().sum()
        for sentiment in sentiments:
            data[sentiment] = data[sentiment].fillna(0)

        data.reset_index(inplace=True)
        data = data[["datetime", "negative", "neutral", "positive"]]
        data = data.loc[
            data["datetime"] <= datetime.strptime(self.config["period"]["stop"], "%d/%m/%Y")
        ]
        data["total"] = data[["negative", "neutral", "positive"]].sum(axis=1)

        self._get_info(data, nan_desc)  # print info

        return data

    def read_forecast_data(self):
        logging.info("Reading forecasting data")
        data = self._read_dataset()

        data_format = ["datetime", "negative", "neutral", "positive", "total"]
        if list(data.columns) != data_format:
            raise NotImplementedError(
                "Format dataset salah! Tolong gunakan " + "data hasil generate dari script"
            )

        logging.info("Preprocess Data!")
        data["datetime"] = pd.to_datetime(data["datetime"])
        data.sort_values(by=["datetime"], inplace=True)

        self._get_info(data)

        return data

    @staticmethod
    def preprocess_text_data(s):
        s = s.lower()
        s = s.translate(DIGITS_WHITESPACE)
        s = s.translate(PUNC_WHITESPACE)
        s = " ".join(s.split())
        return s

    def read_ocean_emotion_data(self):
        # Read dataset
        data = self._read_dataset()[["date", "message"]]

        # Preprocess Dataset
        data["date"] = pd.to_datetime(data["date"])
        data.sort_values(by=["date"], inplace=True)
        data.rename(columns={"date": "datetime"}, inplace=True)
        nan_desc = data.isna().sum()
        data.dropna(inplace=True)
        data["message"] = data["message"].apply(lambda x: self.preprocess_text_data(x))

        data = data.loc[
            (data["datetime"] >= datetime.strptime(self.config["period"]["start"], "%d/%m/%Y"))
            & (data["datetime"] <= datetime.strptime(self.config["period"]["stop"], "%d/%m/%Y"))
        ]

        self._get_info(data, nan_desc)

        return data
