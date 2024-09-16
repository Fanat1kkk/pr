from typing import Dict, List
from time import sleep

from requests.sessions import Session

from .models import Task


class Provider:

    url: str
    key: str
    name: str
    key_name = 'key'
    time_limit = 0.1
    client = Session()

    status = {
        'In progress': Task.IN_WORCK,
        'Processing': Task.WAITSTART,
        'Completed': Task.COMPLITE,
        'Awaiting': Task.WAITSTART,
        'Pending': Task.WAITSTART,
        'Canceled': Task.CANC,
        'Partial': Task.PARTIAL,
        'Fail' : Task.FAIL,
        'Cancellation process' : Task.WAITCANCEL
    }

    def __init__(self) -> None:
        self.params: dict

    def _send_request(self):
        self.params.update({self.key_name: self.key})
        sleep(self.time_limit)
        with Provider.client.post(url=self.url, params=self.params) as resp:
            return resp.json()
        

    def resp_norm(self)-> dict:
        '''
        Приведение ответа к единому формату:

        '''

    def create_order(self) -> int:
        return self._send_request()

    def orders_status(self) -> dict:
        return self._send_request()

    def cancel_order(self) -> dict:
        return self._send_request()

    def balance(self) -> int:
        return self._send_request()


class LikeHub(Provider):
    url = 'https://api-resale.likehub.io/v1/just'
    key = 'fc911f95796f06eb347e4af887c7a48eac9aaafa25b4cba022266ed227c3dc0e'
    name = 'likehub'

    def balance(self) -> int:
        self.params = {'action': 'balance'}
        return super().balance()
    
    def orders_status(self, orders: list) -> dict:
        self.params = {'action': 'status', 'orders': ','.join(map(str, orders))}
        return super().orders_status()

    def create_order(self, order_id: int, service_provider_id: int, link: str, count: int) -> dict:
        self.params = {'action': 'add', 'operation_id': order_id, 'service': service_provider_id, 'link': link, 'quantity': count }
        result = super().create_order()

        if result.get('error', None):
            return result
        return {'order': result['order']}

    def cancel_order(self, provider_order_id: int) -> dict:
        self.params = {'action': 'cancel', 'order': provider_order_id}
        r = super().cancel_order()
        if 'error' in r:
            return r
        else:
            return {'success': True}

    def formating(self, pre_result: dict) -> dict:
        formatted_result = dict()
        for r_order in pre_result:
            start_count = pre_result[r_order]['start_count']
            formatted_result.update({r_order : {'start_count': start_count if start_count is not None else 0,
                                                'status': self.status[pre_result[r_order]['status']],
                                                'remains': int(pre_result[r_order]['remains'])}})
        return formatted_result
        

class Socgres(Provider):
    url = 'https://socgress.com/api/v2'
    key = '8fK2IoC65wwUvz0RoFVVXQn3sILAxqOgSfClpv1O4zs5SPhoaV'
    name = 'socgress'

    def balance(self) -> int:
        self.params = {'action': 'balance'}
        return super().balance()

    def orders_status(self, orders: list) -> dict:
        self.params = {'action': 'status', 'orders': ','.join(map(str, orders))}
        return super().orders_status()

    def create_order(self, service_provider_id: int, link: str, count: int, order_id=None) -> dict:
        self.params = {'action': 'add', 'service': service_provider_id, 'link': link, 'quantity': count }
        result = super().create_order()

        if result.get('error', None):
            return result
        return {'order': result['order']}

    def cancel_order(self, provider_order_id: int) -> dict:
        self.params = {'action': 'cancel', 'order': provider_order_id}
        r = super().cancel_order()

        if 'error' in r:
            return r
        else:
            return {'success': True}

    def formating(self, pre_result: dict) -> dict:
        '''
        {'order_id': {'start_count': int, 
                      'status': 'Canceled', 
                      'remains': int
                     }            
        }
        '''
        formatted_result = dict()
        for r_order in pre_result:
            start_count = pre_result[r_order]['start_count']
            formatted_result.update({r_order : {'start_count': start_count if start_count is not None else 0,
                                                'status': self.status[pre_result[r_order]['status']],
                                                'remains': int(pre_result[r_order]['remains'])}})
        return formatted_result


class ProviderManager:

    def __init__(self) -> None:
        self.provider = {
                'likehub': LikeHub(),
                'socgress': Socgres(),
            }

    def data_order_formating(self, provider_name: str, pre_result: dict) -> dict:
        return self.provider[provider_name].formating(pre_result)

    def provider_status(self, provider_name: str, status: str) -> str:
        return self.provider[provider_name].status[status]

    def balance(self, provider_name: str) -> int:
        result = self.provider[provider_name].balance()
        return result['balance']

    def orders_status(self, provider_name: str, orders_list: List[int]) -> dict:
        result = self.provider[provider_name].orders_status(orders = orders_list)
        return result

    def create_order(self, provider_name: str, order_id: int, service_provider_id: int, link: str, count: int) -> dict:
        result = self.provider[provider_name].create_order(order_id=order_id, service_provider_id=service_provider_id, link=link, count=count)
        return result

    def cancel_order(self, provider_name: str, provider_order_id: int):
        return self.provider[provider_name].cancel_order(provider_order_id=provider_order_id)

    def create_orders(self, tasks: List[Task]):
        for task in tasks:
            r = self.create_order(provider_name=task.service.provider.name, 
                                  order_id=task.order_id, 
                                  link=task.task_url, 
                                  count=task.count, 
                                  service_provider_id=task.service.provider_service_id)
            # Если провайдер вернул ошибку
            if r.get('error', None):
                task.provider_error(error_text=r.get('error'))
            # Если провайдер вернул результат
            else:
                task.provider_ok(order_id=r.get('order'))
            
    def update_orders_status(self, tasks: Dict[str, List[int]]) -> Dict[str, Dict[str, dict]]:
        '''
        # Получает на вход dict({'provider_name': [orders_id's]})
        # Возвращает dict({'provider_name': {'order_id': {'start_count': int, 
        #                                                 'status': 'Canceled', 
        #                                                 'remains': int
        #                                                }                
        #                                    }
        #                 })
        '''

        result = dict()
        for provider in tasks:
            pre_result = self.orders_status(provider_name=provider,
                                            orders_list=tasks[provider])
            # Приведение результата в нужный формат
            result.update({provider: self.data_order_formating(provider_name=provider, pre_result=pre_result)})
        return result
                

pm = ProviderManager()