import json

from veil.tinkoff.services import TinkoffService


class InstrumentsService:


    class InstrumentType:
        UNSPECIFIED = "INSTRUMENT_TYPE_UNSPECIFIED"
        BOND = "INSTRUMENT_TYPE_BOND"
        SHARE = "INSTRUMENT_TYPE_SHARE"
        CURRENCY = "INSTRUMENT_TYPE_CURRENCY"
        ETF = "INSTRUMENT_TYPE_ETF"
        FUTURES = "INSTRUMENT_TYPE_FUTURES"
        SP = "INSTRUMENT_TYPE_SP"
        OPTION = "INSTRUMENT_TYPE_OPTION"
        CLEARING_CERTIFICATE = "INSTRUMENT_TYPE_CLEARING_CERTIFICATE"
        INDEX = "INSTRUMENT_TYPE_INDEX"
        COMMODITY = "INSTRUMENT_TYPE_COMMODITY"

    def __init__(self, service: TinkoffService):
        service.name = 'InstrumentsService'
        self.manager = service

        self.URL = self.manager.get_url()

    def bonds(self, data=None):
        path = '/Bonds'
        if data is None:
            data = ''

        return self.manager.session.post(
            url=self.URL + path,
            data=data
        ).json()


    def find_instrument(self, query: str, instrumentKind=InstrumentType.UNSPECIFIED, apiTradeAvailableFlag=True):
        path = '/FindInstrument'

        return self.manager.session.post(
            url=self.URL + path,
            data=json.dumps({
                'query': query,
                'instrumentKind': instrumentKind,
                'apiTradeAvailableFlag': apiTradeAvailableFlag,
            })
        ).json()
    

    def get_indicatives(
        self,
        query:str=None
    ):
        path = '/Indicatives'


        data = json.dumps({
            
        }, default=str)

        response = self.manager.session.post(
            url=self.URL + path,
            data=data
        ).json()

        if query:
            for instrument in response.get('instruments'):
                if query in instrument.get('name') or query in instrument.get('ticker') or query in instrument.get('uid') or query in instrument.get('figi'):
                    return {'instruments': [instrument]}

        return response


