from locust import task, SequentialTaskSet, FastHttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, processCancelRequestBody
import random
from urllib.parse import unquote_plus


class PurchaseFlightTicket2(SequentialTaskSet): # класс с задачами (содержит основной сценарий)

    test_users_csv_file = './test_data/user_data_test.csv'

    test_users_data = open_csv_field(test_users_csv_file)

    def on_start(self) -> None:
        @task
        def uc02_01_getHomePage(self) -> None:
            self.client.get(
                '/WebTours/',
                name='REQ02_01_1_/WebTours/',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                # debug_stream=sys.stderr
            )
            self.client.get(
                '/cgi-bin/welcome.pl?signOff=true',
                name='REQ02_01_2_/cgi-bin/welcome.pl?signOff=true',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,  # если есть редирект
                # debug_stream=sys.stderr
            )
            with self.client.get(
                    '/cgi-bin/nav.pl?in=home',
                    name='REQ02_01_3_/cgi-bin/nav.pl?in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,  # если есть редирект
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req_01_3_response:
                check_http_response(req_01_3_response, "name=\"userSession\"")

                self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req_01_3_response.text).group(1)

        @task
        def uc02_02_getLogin(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)

            self.userName = self.user_data_row['username']

            self.password = self.user_data_row['password']

            req_body_02_1 = f'userSession={self.userSession}&username={self.userName}&password={self.password}&login.x=0&login.y=0&JSFormSubmit=off'
            with self.client.post(
                    '/cgi-bin/login.pl',
                    name='REQ02_02_1_/cgi-bin/login.pl',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    data=req_body_02_1,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req_02_1_response:
                check_http_response(req_02_1_response, "User password was correct")

            self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='REQ02_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                # debug_stream=sys.stderr,
            )

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ02_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,  # если есть редирект
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req_02_3_response:
                check_http_response(req_02_3_response, f'Welcome, <b>{self.userName}</b>')

        uc02_01_getHomePage(self)
        uc02_02_getLogin(self)

    @task
    def us02_03_openItinerary(self):
        with self.client.get(
            '/cgi-bin/welcome.pl?page=itinerary',
            name='REQ02_03_1_/cgi-bin/welcome.pl?page=itinerary',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                'accept-encoding': 'gzip, deflate, br, zstd'
            },
            allow_redirects=False,
            #debug_stream=sys.stderr
        ) as req02_03_1_response:
            check_http_response(req02_03_1_response, "User wants the intineraries")

        with self.client.get(
            '/cgi-bin/nav.pl?page=menu&in=itinerary',
            name='REQ02_03_2_/cgi-bin/nav.pl?page=menu&in=itinerary',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                'accept-encoding': 'gzip, deflate, br, zstd'
            },
            allow_redirects=False,
           #debug_stream=sys.stderr
        ) as req02_03_2_response:
            check_http_response(req02_03_2_response, "Web Tours Navigation Bar")

        with self.client.get(

                '/cgi-bin/itinerary.pl',
                name='REQ02_03_3_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as req02_03_3_response:
            check_http_response(req02_03_3_response, "Flights List")
        self.flightID = re.findall(r'name=\"flightID\" value=\"(.*)\"  /', req02_03_3_response.text)
        self.cgifields = re.findall(r'name=\".cgifields\" value=\"([0-9]{1,4})\"  />', req02_03_3_response.text)


        logger.info(f'WebToursBaseClass started. Host:{self.flightID}')
        logger.info(f'WebToursBaseClass started. Host:{self.cgifields}')


    @task
    def uc02_04_deleteTicket(self) -> None:

        req_body02_04_1 = processCancelRequestBody(self.flightID, self.cgifields)
        logger.info(f'Body_Cancel Host:{req_body02_04_1}')
        with self.client.post(
                '/cgi-bin/itinerary.pl',
                name='REQ02_04_1_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body02_04_1,
                catch_response=True,
                #debug_stream=sys.stderr
        ) as req02_04_1_response:
            check_http_response(req02_04_1_response, "Flights List")
            #check_http_response(req02_04_1_response, f"A total of {len(self.flightID)-1} scheduled flights." or "No flights have been reserved")



class WebToursCancelUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.webtours_cancel.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host:{host}')

    tasks = [PurchaseFlightTicket2]