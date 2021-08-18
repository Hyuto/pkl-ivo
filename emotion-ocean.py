import os, argparse
import json, logging

from analyzer import Analyzer
from data import Data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script untuk melakukan analisis & OCEAN")
    parser.add_argument(
        "-p",
        "--path",
        help="Path ke data atau direktori tempat penyimpanan data",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-a", "--analysis", help="Tipe analisis yang digunakan 'emotion' atau 'ocean'", type=str
    )
    parser.add_argument("-e", "--export", help="Export hasil ke csv", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO)

    logging.info('Getting config from "./config.json"')
    with open("./config.json") as reader:
        config = json.load(reader)["data"]["emotion-ocean"]

    datagen = Data(args.path, config)
    data = datagen.read_ocean_emotion_data()

    if args.analysis:
        logging.info(f"Running {args.analysis} analisis".title())
        analyzer = Analyzer(data, args.analysis)
        analyzer.analyse(args.export, config)

    logging.info("Done !")
