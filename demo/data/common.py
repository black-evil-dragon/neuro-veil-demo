from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
import typing

import numpy as np
import pandas as pd

from utils.logger import get_logger
from utils.numbers import parse_quotation

from services import InstrumentsService, TinkoffService
from services import MarketDataService

import json

from utils.time import prepare_date



log = get_logger()


class InstrumentDataModel:

    name = None

    def __init__(
        self,
        instrument: dict,
        TService: 'TinkoffService',
    ):

        self.instrument = instrument
        self.TService = TService
    
        self.instrumentsService = InstrumentsService(TService)
        self.marketDataService = MarketDataService(TService)

    
    # +-----------------------------------------------------------------------------------------------#
    # Методы установки параметров получения данных
    # +---------------------------------------------------------------------------------------------#
    # @classmethod
    # def set_iteration_step(cls, step: int):
    #     cls.step = step

    


    # +----------------------------------------------------------------------------------------------#
    # Методы получения данных 
    # +---------------------------------------------------------------------------------------------#
    def get_data(self):
        """Метод должен быть реализован в дочерних классах."""
        pass

    def get_name(self):
        """Метод должен быть реализован в дочерних классах."""
        pass



    def get_additional_candles(
        self,
        from_date,
        to_date,

        additional_instruments: list,
        intervalType,
    ):
        result = {}

        for instrument in additional_instruments:
            args = dict(
                from_date=from_date,
                to_date=to_date,
                instrumentId=instrument.get("uid"),
                interval=intervalType,
                limit=self.marketDataService.get_limit(intervalType),
            )
            
            prepared_additional_candles = self.prepare_candles(
                self.marketDataService.get_candles(**args)
            )


            result = result | {
                instrument.get("ticker"): prepared_additional_candles
            }

        return result






    def get_gluing_data(
        self,
        candles = None,
        indicators = None,
        additional = None,
    ):
        
        if candles is None:
            candles = {}
        if indicators is None:
            indicators = {}
        if additional is None:
            additional = {}


        result = {}


        for date, candle_data in candles.items():
            result[date] = candle_data


        for indicator_name, indicator_data in indicators.items():
            for date, indicator in indicator_data.items():
                if date in result:
                    result[date][indicator_name] = indicator.get('value')

        for additional_key, additional_data in additional.items():
            for date, instrument in additional_data.items():
                if date in result:
                    result[date][additional_key] = instrument.get('close')

        
        return result



    def get_candles(
        self,
        from_date,
        to_date,
        intervalType: str

    ) -> dict:
        args = dict(
            from_date=from_date,
            to_date=to_date,
            instrumentId=self.instrument.get("uid"),
            interval=intervalType,
            limit=self.marketDataService.get_limit(intervalType),
        )

        log.info(f'[InstrumentData] Получаем котировки ({args["limit"]}) по инструменту: {self.instrument.get("ticker", "")}')
        log.info(f'[InstrumentData] - Даты: {args["from_date"]} - {args["to_date"]}')

        candles = self.marketDataService.get_candles(**args)

        prepared_candles = self.prepare_candles(candles)

        return prepared_candles
    

    def get_indicators(
        self,
        from_date,
        to_date,
        intervalType: str,
        indicatorType: str,
        typeOfPrice: str,

        length: int = None,
        additional = None,
    ) -> dict:
        args = dict(  
            from_date=from_date,
            to_date=to_date,

            instrumentUid=self.instrument.get("uid"),

            interval=intervalType,
            indicatorType=indicatorType,

            typeOfPrice=typeOfPrice,
        )

        if additional:
            args = args | additional
        else:
            args['length'] = length


        indicators = self.marketDataService.get_tech_analysis(**args)

        prepare_indicators = self.prepare_indicators(indicators)


        return prepare_indicators
    


    def get_multiple_indicators(self, base_args, lengths, indicator_name):
        result = {}
        for length in lengths:
            key = f"{indicator_name}_{length}"
            indicators = self.get_indicators(**base_args, length=length)
            result[key] = indicators

            log.info(f'- | Получено ({len(indicators)}) длины ({length})')
        return result


    @staticmethod
    def prepare_indicators(indicators):
        processed_data = {}

        for indicator in indicators['technicalIndicators']:
            processed_data[
                indicator['timestamp']
            ] = {
                # 'time': indicator['timestamp'],
                'value': parse_quotation(indicator['signal']),      
            }
            
        return processed_data
    

    @staticmethod
    def prepare_candles(candles):
        processed_data = {}
        for candle in candles['candles']:
            processed_data[
                candle['time']
            ] = {
                # 'time': candle['time'],
                'is_complete': candle['isComplete'],
                'open': parse_quotation(candle['open']),
                'high': parse_quotation(candle['high']),
                'low': parse_quotation(candle['low']),
                'close': parse_quotation(candle['close']),

                'volume': int(candle['volume']),

                
                # 'candleSourceType': candle['candleSourceType'],
                
            }

        return processed_data
    

    @classmethod
    def save_to_json(cls, data, filename: str, indent = None) -> None:
        """
        Сохраняет данные в JSON файл. Создает каталоги, если они не существуют.

        :param data: Данные для сохранения.
        :param filename: Имя файла (включая путь).
        :param indent: Отступ для форматирования JSON (если None, форматирование отключено).
        """

        default_path = './output/data/'
        filename = default_path + filename
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=indent)

            log.debug(f"Data saved to {filename}")

        except (IOError, OSError) as e:
            log.error(f"Failed to save data to {filename}: {e}")
            raise
        except TypeError as e:
            log.error(f"Failed to serialize data: {e}")
            raise


    @classmethod
    def load_from_json(cls, filename: str):
        """
        Загружает данные из JSON файла.

        :param filename: Имя файла (включая путь).
        :return: Загруженные данные.
        """

        default_path = './output/data/'
        filename = default_path + filename
    
        try:
            with open(filename, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            log.debug(f"Data loaded from {filename}")
            return data

        except (IOError, OSError) as e:
            log.error(f"Failed to load data from {filename}: {e}")
            raise
        except json.JSONDecodeError as e:
            log.error(f"Failed to decode JSON from {filename}: {e}")
            raise
    

    @classmethod
    def dict_to_dataframe(cls, data: typing.Dict[str, typing.Dict[str, typing.Any]]) -> pd.DataFrame:
        """
        Преобразует словарь данных в упорядоченную таблицу (DataFrame).

        :param data: Словарь, где ключи — даты, а значения — данные.
        :return: DataFrame с упорядоченными данными.
        """

        df = pd.DataFrame.from_dict(data, orient="index")


        df.sort_index(inplace=True)

        initial_missing = df.isnull().sum().sum()
        df.ffill(inplace=True)
        df.bfill(inplace=True)
        log.info(f"Заполнено пропущенных значений: {initial_missing}")


        return df
    
    
    @staticmethod
    def differentiate_data(df: pd.DataFrame, column: str, order: int = 1) -> pd.DataFrame:
        """
        Применяет дифференцирование к указанному столбцу.

        :param df: DataFrame с данными.
        :param column: Название столбца для дифференцирования.
        :param order: Порядок дифференцирования (1 или 2).
        :return: DataFrame с дифференцированным столбцом.
        """
        diff_column = f"{column}_diff_{order}"
        df[diff_column] = df[column].diff(order)
        df.dropna(inplace=True)  # Удаляем NaN, которые появляются после дифференцирования
        return df
    

    @staticmethod
    def log_transform_data(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Применяет логарифмическое преобразование к указанному столбцу.

        :param df: DataFrame с данными.
        :param column: Название столбца для логарифмирования.
        :return: DataFrame с логарифмированным столбцом.
        """
        log_column = f"{column}_log"
        df[log_column] = np.log(df[column])
        return df
    


    # +--------------------------------------------
    # |  Декораторы
    # +--------------------------------------------
    @classmethod
    def iterate_over_time_range(cls, step: int):
        """Декоратор для итерации по временному диапазону."""

        def decorator(func):
            @wraps(func)
            def wrapper(self, from_date, to_date, *args, **kwargs):

                first_candle_date = self.instrument.get("first1dayCandleDate", None)
                first_candle_date = datetime.strptime(first_candle_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


                log.debug(f'Начальная дата свечи: {from_date}')
                log.debug(f'Первая дата свечи: {first_candle_date}')

                
                if first_candle_date and from_date < first_candle_date:
                    from_date = first_candle_date
                    log.debug(f"Обновление from_date до first_candle_date: {from_date}")
                    
                total_days = (to_date - from_date).days
                is_hours = total_days < 1

                if is_hours:
                    total = int((to_date - from_date).total_seconds() // 3600)
                else:
                    total = total_days

                result = {}

                for start in range(0, total, step):
                    if is_hours:
                        current_from_date = from_date + timedelta(hours=start)
                        current_to_date = min(from_date + timedelta(hours=start + step), to_date)
                    else:
                        current_from_date = from_date + timedelta(days=start)
                        current_to_date = min(from_date + timedelta(days=start + step), to_date)

                    log.debug(f"Обработка диапазона: {current_from_date} - {current_to_date}")
                    result.update(
                        func(self, current_from_date, current_to_date, *args, **kwargs)
                    )

                return result
            return wrapper
        return decorator