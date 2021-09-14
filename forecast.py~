import os, argparse
import json, logging
import numpy as np
import pandas as pd
from datetime import datetime as dt

import matplotlib

# set backend to non GUI
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import Data
from utils import get_project_dir, check_dir

import pmdarima as pm
from pmdarima import model_selection
from sklearn.metrics import *


def forecast(data, config, interval, project_dir):
    sentiments = ["negative", "neutral", "positive", "total"]
    log_score = {}
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
        rmse = round(np.sqrt(mean_squared_error(test, preds)), 2)
        mape = round(mean_absolute_percentage_error(test, preds) * 100, 2)
        log_score[sentiment] = {"rmse": rmse, "mape": mape}
        print(f"   *  Test RMSE : {rmse}")
        print(f"   *  Test MAPE : {mape}%")
        print()

        model.update(test)

        preds, conf_int = model.predict(n_periods=config["n-predict"], return_conf_int=True)
        if interval == "day":
            i = "D"
        elif interval == "hour":
            i = "h"
        elif interval == "week":
            i = "W"
        else:
            raise NotImplementedError("Config Error ! [groupby]")

        preds_axis = [
            data["datetime"].values[-1] + np.timedelta64(x, i)
            for x in range(0, config["n-predict"] + 1)
        ]

        last_test = [test.tolist()[-1]]
        plt.figure(figsize=(10, 5))
        plt.plot(data["datetime"].values, train.tolist() + test.tolist(), alpha=0.75)
        plt.plot(preds_axis, last_test + preds.tolist(), alpha=0.75)
        plt.fill_between(
            preds_axis,
            last_test + conf_int[:, 0].tolist(),
            last_test + conf_int[:, 1].tolist(),
            alpha=0.1,
            color="g",
        )
        plt.title(f"{sentiment.title()} forecasts", fontsize=20)
        xlab = pd.date_range('2021/1/1','2021/11/1',freq='1MS')
        plt.xticks(ticks = xlab,
                   labels=list(map(lambda x: dt.strftime(x,'%d %b'), xlab)))
        plt.xlabel("Date")
        plt.savefig(os.path.join(project_dir, f"ARIMA-{sentiment}.png"), bbox_inches="tight")

    return log_score


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
    parser.add_argument("-f", "--filter", help="Filter data with keywords", type=str)
    parser.add_argument(
        "-a", "--analyze", help="Melakukan forecasting terhadap data", action="store_true"
    )
    parser.add_argument("-pr", "--prophet", help="Using Prophet", action="store_true")
    parser.add_argument("-e", "--export", help="Export performance to csv", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO)

    logging.info('Getting config from "./config.json"')
    with open("./config.json") as reader:
        config = json.load(reader)

    datagen = Data(args.path, config["data"]["forecast"])

    if args.generate:
        if args.filter:
            data = datagen.generate_dataset(args.filter)
        else:
            data = datagen.generate_dataset()

        # Export
        logging.info("Exporting data")
        filename = (
            f'Forecast Data_{data.datetime.min().strftime("%d %b %Y")} - '
            + f'{data.datetime.max().strftime("%d %b %Y")}.csv'
        )
        status, path = check_dir(filename)
        if status:
            data.to_csv(path, index=False)

    if args.analyze:
        data = datagen.read_forecast_data()
        name = (
            f'Forecast_{data.datetime.min().strftime("%d %b %Y")} - '
            + f'{data.datetime.max().strftime("%d %b %Y")}'
        )
        project_dir = get_project_dir(name)

        # for export purpose
        log = {"sentiment": [], "rmse": [], "mape": [], "model": []}

        log_arima = forecast(
            data, config["forecast"], config["data"]["forecast"]["groupby"], project_dir
        )
        for sentiment in log_arima:
            log["sentiment"].append(sentiment)
            log["rmse"].append(log_arima[sentiment]["rmse"])
            log["mape"].append(log_arima[sentiment]["mape"])
            log["model"].append("arima")

        if args.prophet:
            # Testing
            import platform

            assert (
                config["data"]["forecast"]["groupby"] == "day"
                or config["data"]["forecast"]["groupby"] == "week"
            ), "groupby harus 'day' atau 'week' untuk prophet"
            assert platform.system().lower() == "linux", "Prophet hanya support di linux"

            from Prophet import ProphetModel

            model = ProphetModel(data, config["forecast"])
            log_prophet = model.analyze(config["data"]["forecast"]["groupby"], project_dir)

            for sentiment in log_prophet:
                log["sentiment"].append(sentiment)
                log["rmse"].append(log_prophet[sentiment]["rmse"])
                log["mape"].append(log_prophet[sentiment]["mape"])
                log["model"].append("prophet")

        if args.export:
            logging.info("Exporting performace models to readable csv")
            pd.DataFrame(log).to_csv(os.path.join(project_dir, "performance.csv"), index=False)

    logging.info("Done !")
