import os, logging
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import *

try:
    from prophet import Prophet
except:
    raise EnvironmentError("Prophet belum terinstall. Ikuti cara penginstalan di README.md")


class ProphetModel:
    def __init__(self, data, config):
        self.data = data
        self.config = config

    @staticmethod
    def get_performance(y_true, y_pred):
        logging.info("Performance")
        rmse = round(
            mean_squared_error(y_true, y_pred) ** 0.5,
            2,
        )
        mape = round(
            mean_absolute_percentage_error(y_true, y_pred) * 100,
            2,
        )
        print(f"   *  Test RMSE : {rmse}")
        print(f"   *  Test MAPE : {mape}%")
        print()

        return rmse, mape

    def analyze(self, project_dir):
        logging.info("Using Prophet")
        log_score = {}
        for sentiment in ["negative", "neutral", "positive"]:
            logging.info(f"Forecasting {sentiment} (Prophet)")
            temp_data = self.data[["datetime", sentiment]].copy()
            temp_data.rename(columns={"datetime": "ds", sentiment: "y"}, inplace=True)

            model = Prophet(**self.config["prophet"]).fit(temp_data[: -self.config["n-test"]])

            future = model.make_future_dataframe(periods=self.config["n-test"])
            forecast = model.predict(future)

            rmse, mape = self.get_performance(
                temp_data["y"][-self.config["n-test"] :], forecast["yhat"][-self.config["n-test"] :]
            )
            log_score[sentiment] = {"rmse": rmse, "mape": mape}

            self.model = Prophet().fit(temp_data)
            future = self.model.make_future_dataframe(periods=30)
            forecast = self.model.predict(future)
            print()

            plt.figure(figsize=(10, 5))
            plt.plot(temp_data["ds"].values, temp_data["y"].values, alpha=0.75)
            plt.plot(
                forecast["ds"].values[-self.config["n-predict"] :],
                forecast["yhat"].values[-self.config["n-predict"] :],
                alpha=0.75,
            )
            plt.fill_between(
                forecast["ds"].values[-self.config["n-predict"] :],
                forecast["yhat_lower"].values[-self.config["n-predict"] :],
                forecast["yhat_upper"].values[-self.config["n-predict"] :],
                alpha=0.1,
                color="g",
            )
            plt.title(f"{sentiment.title()} forecasts", fontsize=20)
            plt.xticks(rotation=90)
            plt.xlabel("Date")
            plt.savefig(os.path.join(project_dir, f"Prophet-{sentiment}.png"), bbox_inches="tight")

        return log_score
