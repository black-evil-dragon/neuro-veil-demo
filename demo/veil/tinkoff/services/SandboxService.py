

import json

from veil.tinkoff.services import TinkoffService


class SandboxService:

    class AccountStatus:
        UNSPECIFIED = "ACCOUNT_STATUS_UNSPECIFIED"
        NEW = "ACCOUNT_STATUS_NEW"
        OPEN = "ACCOUNT_STATUS_OPEN"
        CLOSED = "ACCOUNT_STATUS_CLOSED"
        ALL = "ACCOUNT_STATUS_ALL"


    def __init__(self, service: TinkoffService):
        service.name = 'SandboxService'
        self.manager = service

        self.URL = self.manager.get_url()


    
    def sandbox_pay_in(
        self,
        accountId: str,
        amount: dict,
    ) -> dict:
        path = '/SandboxPayIn'

        data = json.dumps(
            {
                "accountId": accountId,
                "amount": amount,
            }, default=str
        )

        return self.manager.session.post(
            url=self.URL + path,
            data=data,
        ).json()
        
    