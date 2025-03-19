import json
import typing

import requests

from services import TinkoffService
from utils.time import now, now_str, prepare_date


class MarketDataService:

    class TypeOfPrice:
        UNSPECIFIED = "TYPE_OF_PRICE_UNSPECIFIED"
        CLOSE = "TYPE_OF_PRICE_CLOSE"
        OPEN = "TYPE_OF_PRICE_OPEN"
        HIGH = "TYPE_OF_PRICE_HIGH"
        LOW = "TYPE_OF_PRICE_LOW"
        AVG = "TYPE_OF_PRICE_AVG"

    class IndicatorType:
        UNSPECIFIED = "INDICATOR_TYPE_UNSPECIFIED"
        BB = "INDICATOR_TYPE_BB"
        EMA = "INDICATOR_TYPE_EMA"
        RSI = "INDICATOR_TYPE_RSI"
        MACD = "INDICATOR_TYPE_MACD"
        SMA = "INDICATOR_TYPE_SMA"

    class IndicatorIntervalType:
        UNSPECIFIED = "INDICATOR_INTERVAL_UNSPECIFIED"
        ONE_MINUTE = "INDICATOR_INTERVAL_ONE_MINUTE"
        FIVE_MINUTES = "INDICATOR_INTERVAL_FIVE_MINUTES"
        FIFTEEN_MINUTES = "INDICATOR_INTERVAL_FIFTEEN_MINUTES"
        ONE_HOUR = "INDICATOR_INTERVAL_ONE_HOUR"
        ONE_DAY = "INDICATOR_INTERVAL_ONE_DAY"
        TWO_MINUTES = "INDICATOR_INTERVAL_2_MIN"
        THREE_MINUTES = "INDICATOR_INTERVAL_3_MIN"
        TEN_MINUTES = "INDICATOR_INTERVAL_10_MIN"
        THIRTY_MINUTES = "INDICATOR_INTERVAL_30_MIN"
        TWO_HOURS = "INDICATOR_INTERVAL_2_HOUR"
        FOUR_HOURS = "INDICATOR_INTERVAL_4_HOUR"
        WEEK = "INDICATOR_INTERVAL_WEEK"
        MONTH = "INDICATOR_INTERVAL_MONTH"


    class CandleInterval:
        UNSPECIFIED = "CANDLE_INTERVAL_UNSPECIFIED"
        ONE_MINUTE = "CANDLE_INTERVAL_1_MIN"
        FIVE_MINUTES = "CANDLE_INTERVAL_5_MIN"
        FIFTEEN_MINUTES = "CANDLE_INTERVAL_15_MIN"
        ONE_HOUR = "CANDLE_INTERVAL_HOUR"
        ONE_DAY = "CANDLE_INTERVAL_DAY"
        TWO_MINUTES = "CANDLE_INTERVAL_2_MIN"
        THREE_MINUTES = "CANDLE_INTERVAL_3_MIN"
        TEN_MINUTES = "CANDLE_INTERVAL_10_MIN"
        THIRTY_MINUTES = "CANDLE_INTERVAL_30_MIN"
        TWO_HOURS = "CANDLE_INTERVAL_2_HOUR"
        FOUR_HOURS = "CANDLE_INTERVAL_4_HOUR"
        WEEK = "CANDLE_INTERVAL_WEEK"
        MONTH = "CANDLE_INTERVAL_MONTH"

    class CandleSource:
        UNSPECIFIED = "CANDLE_SOURCE_UNSPECIFIED"
        EXCHANGE = "CANDLE_SOURCE_EXCHANGE"
        INCLUDE_WEEKEND = "CANDLE_SOURCE_INCLUDE_WEEKEND"

    class TradeSource:
        UNSPECIFIED = "TRADE_SOURCE_UNSPECIFIED"
        EXCHANGE = "TRADE_SOURCE_EXCHANGE"
        DEALER = "TRADE_SOURCE_DEALER"
        ALL = "TRADE_SOURCE_ALL"



    def __init__(self, service: TinkoffService):
        service.name = 'MarketDataService'
        self.manager = service

        self.URL = self.manager.get_url()


    def get_last_trades(
        self,
        from_date: str = None,
        to_date: str = None,
        instrumentId: str = None,
        tradeSource = TradeSource.ALL,
    ):
        path = '/GetLastTrades'

        data = json.dumps(
            {
                "from": prepare_date(from_date),
                "to": prepare_date(to_date),
                "instrumentId": instrumentId,
                "tradeSource": tradeSource,
            }, default=str
        )

        response = self.manager.session.post(
            url=self.URL + path,
            data=data,
        )


        return response.json()


    def get_order_book(
        self,
        depth: int,
        instrumentId: str
    ) -> dict:
        path = '/GetOrderBook'

        data = json.dumps(
            {
                "depth": depth,
                "instrumentId": instrumentId,
            }, default=str
        )

        return self.manager.session.post(
            url=self.URL + path,
            data=data,
        ).json()


    def get_tech_analysis(
        self,
        instrumentUid: str,
        from_date: str,
        to_date: str,
        indicatorType: str = IndicatorType.UNSPECIFIED,
        interval: str = IndicatorIntervalType.UNSPECIFIED,
        typeOfPrice: str = TypeOfPrice.UNSPECIFIED,
        smoothing: dict = {
            "fastLength": 0,
            "slowLength": 0,
            "signalSmoothing": 0,
        },
        length=None,
        

    ) -> dict:
        path = '/GetTechAnalysis'

        raw_data = {
            "indicatorType": indicatorType,
            "instrumentUid": instrumentUid,
            "from": prepare_date(from_date),
            "to": prepare_date(to_date),
            "interval": interval,
            "typeOfPrice": typeOfPrice,
            "smoothing": smoothing,
        }


        if length:
            raw_data['length'] = length
        

        data = json.dumps(
            raw_data, default=str
        )
        

        return self.manager.session.post(
            url=self.URL + path,
            data=data,
        ).json()
    


    def get_candles(
        self,
        from_date,
        to_date=now(),
        interval=CandleInterval.ONE_DAY,
        instrumentId='',
        candleSourceType=CandleSource.UNSPECIFIED,
        limit=None,
    ) -> dict:
        """
        Запросить исторические свечи по инструменту
        https://developer.tbank.ru/invest/api/market-data-service-get-candles

        :param from_date:
        :param to_date:
        :param interval:
        :param instrumentId:
        :param candleSourceType:
        :param limit:
        :return:
        """
        path = '/GetCandles'


        data = json.dumps(
            {
                "from": prepare_date(from_date),
                "to": prepare_date(to_date),
                "interval": interval,
                "instrumentId": instrumentId,
                "candleSourceType": candleSourceType,
                "limit": limit,
            },
            default=str,
        )

        return self.manager.session.post(
            url=self.URL + path,
            data=data,
        ).json()
    


    @staticmethod
    def get_limit(intervalType: str) -> int:
        """
            1 минута    — От 1 минуты до 1 дня. Максимальное значение limit — 2400.\n
            2 минуты    — От 2 минут до 1 дня. Максимальное значение limit — 1200.\n
            3 минуты    — От 3 минут до 1 дня. Максимальное значение limit — 750.\n
            5 минут     — От 5 минут до недели. Максимальное значение limit — 2400.\n
            10 минут    — От 10 минут до недели. Максимальное значение limit — 1200.\n
            15 минут    — От 15 минут до 3 недель. Максимальное значение limit — 2400.\n
            30 минут    — От 30 минут до 3 недель. Максимальное значение limit — 1200.\n
            1 час       — От 1 часа до 3 месяцев. Максимальное значение limit — 2400.\n
            2 часа      — От 2 часов до 3 месяцев. Максимальное значение limit — 2400.\n
            4 часа      — От 4 часов до 3 месяцев. Максимальное значение limit — 700.\n
            1 день      — От 1 дня до 6 лет. Максимальное значение limit — 2400.\n
            1 неделя    — От 1 недели до 5 лет. Максимальное значение limit — 300.\n
            1 месяц     — От 1 месяца до 10 лет. Максимальное значение limit — 120.

        """
        return {
            "INDICATOR_INTERVAL_UNSPECIFIED": 2400,
            "INDICATOR_INTERVAL_ONE_MINUTE": 2400,
            "INDICATOR_INTERVAL_FIVE_MINUTES": 2400,
            "INDICATOR_INTERVAL_FIFTEEN_MINUTES": 2400,
            "INDICATOR_INTERVAL_ONE_HOUR": 2400,
            "INDICATOR_INTERVAL_ONE_DAY": 2400,
            "INDICATOR_INTERVAL_2_MIN": 1200,
            "INDICATOR_INTERVAL_3_MIN": 750,
            "INDICATOR_INTERVAL_10_MIN": 1200,
            "INDICATOR_INTERVAL_30_MIN": 1200,
            "INDICATOR_INTERVAL_2_HOUR": 2400,
            "INDICATOR_INTERVAL_4_HOUR": 700,
            "INDICATOR_INTERVAL_WEEK": 300,
            "INDICATOR_INTERVAL_MONTH": 120,

        }.get(intervalType, 2400)

