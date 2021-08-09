import os, argparse
import json, logging
import numpy as np
import pandas as pd

import matplotlib

# set backend to non GUI
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import Data
from utils import get_project_dir

import pmdarima as pm
from pmdarima import model_selection
from sklearn.metrics import *


def forecast(data, config, interval):
    name = (
        f'Forecast_{data.datetime.min().strftime("%d %b %Y")} - '
        + f'{data.datetime.max().strftime("%d %b %Y")}'
    )
    project_dir = get_project_dir(name)

    sentiments = ["negative", "neutral", "positive"]
    for sentiment in sentiments:
        logging.info(f"Forecasting {sentiment} (ARIMA)")
        train, test = model_selection.train_test_split(
            data[sentiment].values, test_size=config["n-test"]
        )

        model = pm.auto_arima(train, **config["ARIMA"])

        if not config["ARIMA"]["trace"]:
            print(f"   *  Best Model : {model}")

        preds, conf_int = model.predict(n_periods=test.shape[0], return_conf_int=True)

        logging.info("Performance")
        print(f"   *  Test RMSE : {round(np.sqrt(mean_squared_error(test, preds)), 2)}")
        print(f"   *  Test MAPE : {round(mean_absolute_percentage_error(test, preds) * 100, 2)}%")
        print()

        model.update(test)

        preds, conf_int = model.predict(n_periods=config["n-predict"], return_conf_int=True)
        if interval == "day":
            i = "D"
        elif interval == "hour":
            i = "h"
        else:
            raise NotImplementedError("Config Error ! [groupby]")

        preds_axis = [
            data["datetime"].values[-1] + np.timedelta64(x, i)
            for x in range(1, config["n-predict"] + 1)
        ]

        plt.figure(figsize=(10, 5))
        plt.plot(data["datetime"].values, train.tolist() + test.tolist(), alpha=0.75)
        plt.plot(preds_axis, preds, alpha=0.75)
        plt.fill_between(preds_axis, conf_int[:, 0], conf_int[:, 1], alpha=0.1, color="g")
        plt.title(f"{sentiment.title()} forecasts", fontsize=20)
        plt.xticks(rotation=90)
        plt.xlabel("Date")
        plt.savefig(os.path.join(project_dir, f"ARIMA-{sentiment}.png"), bbox_inches="tight")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk melakukan forecasting")
    parser.add_argument(
        "-p",
        "--path",
        help="Path ke data atau direktori tempat penyimpanan data",
        type=str,
        required=True,
    )
    parser.add_argument("-g", "--generate", help="Generate forecasting data", action="store_true")
    parser.add_argument(
        "-a", "--analyze", help="Melakukan forecasting terhadap data", action="store_true"
    )
    parser.add_argument("-e", "--export", help="Export hasil ke csv", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO)

    logging.info('Getting config from "./config.json"')
    with open("./config.json") as reader:
        config = json.load(reader)

    datagen = Data(args.path, config["data"]["forecast"])

    if args.generate:
        data = datagen.generate_dataset()

    if args.analyze:
        data = datagen.read_forecast_data()
        forecast(data, config["forecast"], config["data"]["forecast"]["groupby"])

    logging.info("Done !")
