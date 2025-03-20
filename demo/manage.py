from datetime import datetime, timedelta, timezone
from veil.neuro.model import NeuroModel
from veil.neuro.model.lstm import LstmModel

from veil.tinkoff.services import InstrumentsService, MarketDataService, TinkoffService
from veil.tinkoff.data import InstrumentDataModel, TinkoffDataModel

from veil.utils.config import SANDBOX_TOKEN
from veil.utils.logger import setup_logger
from veil.utils.time import now


log = setup_logger()


class Manager:
    params = [
        "close",
        # "open",
        # "high",
        # "low",
        # "volume",
    ]

    additive_params = [
        "IMOEXF",
        "USD000UTSTOM",
    ]

    indicators = [
        "RSI_7",
        "RSI_14",
        "RSI_56",
        "SMA_7",
        "SMA_14",
        "SMA_56",
        "MACD_12_26_9",
    ]

    # Variables
    features = []

    # Data models
    tinkoffDataModel: "TinkoffDataModel" = None

    # Neuro models
    model: "NeuroModel" = None



    def init_features(self) -> None:
        self.features = self.params + self.additive_params + self.indicators
        self.features_length = len(self.features)

        log.info(f"- Features ({self.features_length}): {self.features}")


    def init_services(self) -> None:
        self.TService = TinkoffService(token=SANDBOX_TOKEN, is_sandbox=True)

        self.instrumentsService = InstrumentsService(self.TService)
        self.marketDataService = MarketDataService(self.TService)

        log.info("- Init services")


    def init_models(self) -> None:
        self.model = NeuroModel(
            prototype=LstmModel,
        )
        self.model.set_features(self.features)

        log.info(f"- Init model {self.model.prototype.name}")


    def __init__(self) -> None:
        log.info("Запуск программы")

        self.init_features()
        self.init_services()
        self.init_models()


    def set_data_model(self, data_model: "InstrumentDataModel") -> None:
        log.info(f"Установка модели инструмента: {data_model.name}")
        setattr(self, data_model.name, data_model)





if __name__ == "__main__":
    manager = Manager()

    # *______________________________________________________________________________
    # *| Setup data and settings                                                     |
    # Main: TBANK
    response = manager.instrumentsService.find_instrument("RU000A107UL4")
    tbank = response.get("instruments")[0]
    log.info(f"Инструмент найден: {tbank['ticker']}")

    # - Dop: MOEX
    response = manager.instrumentsService.find_instrument("IMOEXF Индекс МосБиржи")
    moex = response.get("instruments")[0]
    log.info(f"Инструмент найден: {moex['ticker']}")

    # - Dop: Доллар
    response = manager.instrumentsService.find_instrument("BBG0013HGFT4")
    dollar = response.get("instruments")[0]
    log.info(f"Инструмент найден: {dollar['ticker']}")

    manager.set_data_model(
        data_model=TinkoffDataModel(
            instrument=tbank,
            TService=manager.TService,
        )
    )

    # *|____________________________________________________________________________|



    # *______________________________________________________________________________
    # *| Fetch data and save                                                        |
    GET_DATA_ARGS = dict(
        candleIntervalType=manager.marketDataService.CandleInterval.ONE_HOUR,
        indicatorIntervalType=manager.marketDataService.IndicatorIntervalType.ONE_HOUR,

        additional_instruments=[
            dollar,
            moex
        ]
    )
    # tinkoff_data = manager.tinkoffDataModel.get_data(
    #     from_date=now() - timedelta(days=3000),
    #     to_date=now(),
    #     **GET_DATA_ARGS
    # )
    # log.debug(f'Итого данных: {len(tinkoff_data)} ({tbank.get("ticker")})')
    # InstrumentDataModel.save_to_json(tinkoff_data, filename="tbank/full.json", indent=4)
    # *|____________________________________________________________________________



    # *______________________________________________________________________________
    # *| Load data                                                                  |
    tinkoff_data = InstrumentDataModel.load_from_json(filename="tbank/full.json")
    
    # Update data
    tinkoff_data = manager.tinkoffDataModel.update_data(
        initial_data=tinkoff_data,
        **GET_DATA_ARGS
    )



    log.debug(f"Итого данных: {len(tinkoff_data)} ({tbank.get('ticker')})")
    exit()
    # *|____________________________________________________________________________|



    # *______________________________________________________________________________
    # *| Train model                                                                 |
    # manager.model.set_batch_size(64)
    # manager.model.set_epochs(50)
    # manager.model.set_look_back(96)
    # manager.model.set_model_version(4)

    manager.model.train(
        train_data=tinkoff_data,
        features=manager.features
    )

    # *|____________________________________________________________________________

    # exit()

    # *______________________________________________________________________________
    # *| Test models                                                                |
    # Параметры для перебора
    # look_back_list = [48, 60, 96, 120]
    # batch_size_list = [32, 64, 128,]
    # epochs_list = [20, 40, 60]
    # model_list = [3, 4]

    # # Цикл по всем комбинациям параметров
    # for look_back in look_back_list:
    #     for batch_size in batch_size_list:
    #         for epochs in epochs_list:
    #             for model_version in model_list:

    #                 manager.model.reset()

    #                 log.info("Запуск тренировки с параметрами:")
    #                 manager.model.set_batch_size(batch_size)
    #                 manager.model.set_epochs(epochs)
    #                 manager.model.set_look_back(look_back)
    #                 manager.model.set_model_version(model_version)

    #                 manager.model.train(
    #                     train_data=tinkoff_data,
    #                     features=manager.features
    #                 )

    #                 manager.model.save(
    #                     name=f'tbank_lb_{look_back}_bs_{batch_size}_eps_{epochs}_v_{model_version}',
    #                     test=True
    #                 )

    # *|___________________________________________________________________________|
