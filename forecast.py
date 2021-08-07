import os, argparse
import json, logging
import numpy as np
import pandas as pd

from forecastdata import Data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script untuk melakukan forecasting")
    parser.add_argument(
        "-p",
        "--path",
        help="Path ke data atau direktori tempat penyimpanan data",
        type=str,
        required=True)
    parser.add_argument("-g",
                        "--generate",
                        help="Generate forecasting data",
                        action="store_true")
    parser.add_argument("-a",
                        "--analyze",
                        help="Melakukan forecasting terhadap data",
                        action="store_true")
    parser.add_argument("-e",
                        "--export",
                        help="Export hasil ke csv",
                        action="store_true")

    args = parser.parse_args()
    logging.basicConfig(format='[ %(levelname)s ] %(message)s',
                        level=logging.INFO)

    logging.info('Getting config from "./forecast-config.json"')
    with open("./forecast-config.json") as reader:
        config = json.load(reader)

    datagen = Data(args.path, config)

    if args.generate:
        data = datagen.generate_dataset()

    if args.analyze:
        data = datagen.read_forecast_data()

    logging.info('Done !')