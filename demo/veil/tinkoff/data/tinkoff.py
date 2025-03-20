from veil.utils.logger import get_logger

from veil.tinkoff.services import TinkoffService
from veil.tinkoff.data import InstrumentDataModel



log = get_logger()

step = 180


class TinkoffDataModel(InstrumentDataModel):
    


    def __init__(self, instrument: dict, TService: 'TinkoffService', *args, **kwargs):
        super().__init__(instrument, TService, *args, **kwargs)

        self.name = 'tinkoffDataModel'



    @InstrumentDataModel.iterate_over_time_range(step=step)
    def get_data(
        self,
        from_date,
        to_date,

        candleIntervalType: str,
        indicatorIntervalType: str,

        additional_instruments: list = None,
    ):
        log.info(f"Получение данных с шагом {step} дней для инструмента {self.instrument.get('ticker')}")


        DATE_ARGS = dict(
            from_date=from_date,
            to_date=to_date,
        )

        log.info("- Получение свечей...")
        candles = self.get_candles(
            **DATE_ARGS,
            intervalType=candleIntervalType,
        )
        log.info(f'- | Получено ({len(candles)})')


        # SMA
        log.info('- Получение индикаторов SMA...')
        SMA_ARGS = dict(
            **DATE_ARGS,

            intervalType=indicatorIntervalType,

            indicatorType=self.marketDataService.IndicatorType.SMA,
            typeOfPrice=self.marketDataService.TypeOfPrice.CLOSE,
        )
        SMA_LENGTHS = [7, 14, 56]

        
        #*__| This is equivalent to the commented code below |__*#
        SMA_DATA = self.get_multiple_indicators(SMA_ARGS, SMA_LENGTHS, "SMA")
        #| SMA_7 = self.get_indicators(**SMA_ARGS, length=7)    |#
        #| SMA_14 = self.get_indicators(**SMA_ARGS, length=14)  |#
        #| SMA_56 = self.get_indicators(**SMA_ARGS, length=56)  |#
        #* |--------------------:D----------------------------| *#


        # RSI
        log.info('- Получение индикаторов RSI...')
        RSI_ARGS = dict(
            **DATE_ARGS,

            intervalType=indicatorIntervalType,

            indicatorType=self.marketDataService.IndicatorType.RSI,
            typeOfPrice=self.marketDataService.TypeOfPrice.CLOSE,
        )
        RSI_LENGTHS = [7, 14, 56]
        
        RSI_DATA = self.get_multiple_indicators(RSI_ARGS, RSI_LENGTHS, "RSI")


        # MACD
        log.info('- Получение индикаторов MACD...')
        MACD_ARGS = dict(
            **DATE_ARGS,
            
            intervalType=indicatorIntervalType,

            indicatorType=self.marketDataService.IndicatorType.MACD,
            typeOfPrice=self.marketDataService.TypeOfPrice.CLOSE,
            additional=dict(
                smoothing=dict(
                    fastLength=12,
                    slowLength=26,
                    signalSmoothing=9,
                )
            )
        )
        MACD_12_26_9 = self.get_indicators(**MACD_ARGS)
        log.info(f'- | Получено {len(MACD_12_26_9)}')


        additional_data = {}
        # Additional instruments
        if additional_instruments:
            additional_data = self.get_additional_candles(
                from_date=from_date,
                to_date=to_date,
                additional_instruments=additional_instruments,
                intervalType=candleIntervalType
            )


        return self.get_gluing_data(
            candles,
            {
                **RSI_DATA,
                **SMA_DATA,
                'MACD_12_26_9': MACD_12_26_9,
            },
            additional_data
        )



            