
import random
from time import time
from typing import Union, List

import pyuseragents
import requests
import urllib3
from PySide6.QtCore import QObject, Signal

from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.http_request.request import HTMLSession
from gui.helpers.thread import ManageThreadPool

URL = ['http://ip-api.com/json/?fields=8217', 'http://azenv.net/', 'http://httpheader.net/azenv.php',
       'http://mojeip.net.pl/asdfa/azenv.php']
SITES = ['http://ip-api.com/json/?fields=8217', ]

CMD_CLEAR_TERM = "clear"
TIMEOUT = 2

HEADERS = {
    "User-Agent": pyuseragents.random(),
    "Accept": "*/*",
    "Accept-Language": "en-US,en-GB; q=0.5",
    "Accept-Encoding": "gzip, deflate",
    # "Content-Type": "application/x-www-form-urlencoded; application/json; charset=UTF-8",
    "Connection": "keep-alive"
}


class ProxyChecker(QObject):
    finishedCheckLiveProxySignal = Signal(str, object)

    def __init__(self, manage_thread_pool: ManageThreadPool):
        super().__init__()
        self.session = HTMLSession()
        self.manage_thread_pool = manage_thread_pool
        self.list_proxy_live = []
        self.list_proxy_die = []
        self.count_proxy = 0
        self.total_proxy = 0

        self.manage_thread_pool.resultChanged.connect(self._resultThread)

    def get_my_ip(self):
        ip = self._get_info(url=random.choice(SITES))
        return ip.text

    def _get_info(self, url=None, proxy=None):
        info = {}
        proxy_type = []
        if url != None:
            try:
                response = self.session.get(url, headers=HEADERS, timeout=TIMEOUT)
                return response
            except:
                pass
        elif proxy != None:

            for protocol in ['http', 'socks4', 'socks5']:
                proxy_dict = {
                    'https': f'{protocol}://{proxy}',
                    'http': f'{protocol}://{proxy}',
                }
                try:
                    start = time()
                    response = self.session.get(random.choice(URL), proxies=proxy_dict, headers=HEADERS,
                                                timeout=TIMEOUT)
                    finish = time() - start
                    if response.status_code == 200:
                        proxy_type.append(protocol)
                        info['type'] = proxy_type
                        info['time_response'] = ("%.3f" % finish)
                        info['status'] = True
                        ip_client = self.get_my_ip()  # ip gốc

                        if str(ip_client) in response.text:  # thông số này để kiêm tra đã fake Ip Thành Công Chưa
                            info['ip_faked'] = False
                        else:
                            info['ip_faked'] = True
                        if protocol == 'http':
                            return info
                except:
                    pass

            if 'status' not in info.keys():
                info['status'] = False
                return info
            else:
                return info

    def get_geo(self, ip):
        url = ['http://ipwhois.app/json/', 'http://ip-api.com/json/', 'https://api.techniknews.net/ipgeo/']
        resp = self._get_info(url=f'{random.choice(url)}{ip}')
        return resp

    def checkInfoProxy(self, proxy):
        ip = proxy.split(':')
        resp = self._get_info(proxy=proxy)

        if resp['status'] == True:
            result = {}
            geo = self.get_geo(ip[0])
            geo_info = geo.json()
            result['status'] = resp['status']
            result['type'] = resp['type']
            result['time_response'] = resp['time_response']
            result['ip_faked'] = resp['ip_faked']
            result['country'] = geo_info['country']
            result['city'] = geo_info['city']
            try:
                result['country_code'] = geo_info['country_code']
            except:
                result['country_code'] = geo_info['countryCode']

            return result

        else:
            return resp

    def checkLiveProxy(self, proxy):
        '''
            Check proxy đơn lẻ không chạy trong thread
        '''

        try:

            # session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            self.session.max_redirects = 300
            proxy_dict = {
                'https': f'https://{proxy}',
                'http': f'http://{proxy}',
            }

            self.session.get(random.choice(URL), proxies=proxy_dict, headers=HEADERS, timeout=TIMEOUT,
                             allow_redirects=True)
        except requests.exceptions.ConnectionError as e:
            return e
        except requests.exceptions.ConnectTimeout as e:
            return e
        except requests.exceptions.HTTPError as e:
            return e
        except requests.exceptions.Timeout as e:
            return e
        except urllib3.exceptions.ProxySchemeUnknown as e:
            return e
        except requests.exceptions.TooManyRedirects as e:
            return e

        except requests.exceptions.InvalidURL as e:
            return e

        except urllib3.exceptions.LocationParseError as e:
            return e

    def _resultThread(self, id_worker, id_thread, result):

        if hasattr(self, 'typeThread') is True:

            if id_thread == self.typeThread:

                if "status" in result.keys():
                    self.count_proxy = self.count_proxy + 1

                    if result["status"] is True:
                        self.list_proxy_live.append(result["proxy"])

                    else:
                        self.list_proxy_die.append(result["proxy"])

                if self.count_proxy == self.total_proxy:  # kết thúc tất cả thiết sẽ thực hiện code o đây tiếp

                    result['proxy_live'] = self.list_proxy_live
                    result['proxy_die'] = self.list_proxy_die
                    self.finishedCheckLiveProxySignal.emit(id_thread, result)
                    # print("self.count_proxy")

                    self.list_proxy_live = []
                    self.list_proxy_die = []
                    self.count_proxy = 0
                    self.total_proxy = 0

    def _funCheckLiveProxy(self, **kwargs):
        '''
            Function chạy trong thread trả về dữ liệu
        '''
        if "proxy" in kwargs.keys():
            proxy = kwargs["proxy"]

            thread_pool = kwargs["thread_pool"]
            id_worker = kwargs["id_worker"]
            typeThread = kwargs["typeThread"]
            try:

                self.session.max_redirects = 300
                proxy_dict = {
                    # 'https': f'https://{proxy}',
                    'http': f'http://{proxy}',
                }
                url = random.choice(SITES)
                # print(url)
                # print(self.session.proxies)
                if 'url' in kwargs.keys():
                    res =self.session.get(kwargs['url'], proxies=proxy_dict, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
                else:
                    res = self.session.get(url, proxies=proxy_dict, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)

                # print(res.json())
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": True, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": True, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.ConnectionError as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.ConnectTimeout as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.HTTPError as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.Timeout as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except urllib3.exceptions.ProxySchemeUnknown as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.TooManyRedirects as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread,{"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.InvalidURL as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread, {"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except urllib3.exceptions.LocationParseError as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread, {"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except urllib3.exceptions.MaxRetryError as e:
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except requests.exceptions.ProxyError as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread, {"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

            except OSError as e:
                # self.resultCheckLiveProxySignal.emit(id_worker, typeThread, {"status": False, "proxy": proxy})
                thread_pool.finishSingleThread(id_worker)

                return {"status": False, "proxy": proxy, 'kwargs': kwargs}

    @decorator_try_except_class
    def checkLiveProxyOnThread(self, thread: ManageThreadPool, proxy_urls: Union[str, List], typeThread, **kwargs):
        '''
          hàm kiểm tra danh sách proxy trong thread được chuyền từ hàm gọi
        '''
        proxies = list(
            filter(None, ([proxy_urls] if isinstance(proxy_urls, str) else list(proxy_urls))))  # lọc item rỗng

        if len(proxies) > 0:
            self.total_proxy = len(proxies)
            # thread.resultChanged.emit(typeThread,typeThread,{"total_proxy":len(proxies)})
            self.typeThread = typeThread

            for proxy in proxies:
                kwargs['proxy'] = proxy
                thread.start(self._funCheckLiveProxy, id_worker=proxy,
                             typeThread=typeThread,
                             **kwargs)
