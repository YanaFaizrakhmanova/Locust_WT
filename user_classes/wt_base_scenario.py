from locust import task, SequentialTaskSet, FastHttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, generationFlightsDate
import random
from urllib.parse import unquote_plus


class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)

    test_users_csv_file = './test_data/user_data_test.csv'
    test_typeSeat_csv_file = './test_data/typeSeat.csv'
    test_users_data = open_csv_field(test_users_csv_file)
    test_type_seat = open_csv_field(test_typeSeat_csv_file)

    def on_start(self) -> None:
        @task
        def uc01_01_getHomePage(self) -> None:

            self.client.get(
                '/WebTours/',
                name='REQ01_01_1_/WebTours/',
                headers={
                    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding':'gzip, deflate, br, zstd'
                },
                 #debug_stream=sys.stderr
            )
            self.client.get(
                '/cgi-bin/welcome.pl?signOff=true',
                name='REQ01_01_2_/cgi-bin/welcome.pl?signOff=true',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False, # если есть редирект
                #debug_stream=sys.stderr
            )
            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name='REQ01_01_3_/cgi-bin/nav.pl?in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,  # если есть редирект
                catch_response=True,
                #debug_stream=sys.stderr
            ) as req_01_3_response:
               check_http_response(req_01_3_response,"name=\"userSession\"")

               self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req_01_3_response.text).group(1)

        @task
        def uc01_02_getLogin(self) -> None:

            self.user_data_row = random.choice(self.test_users_data)

            self.userName = self.user_data_row['username']

            self.password = self.user_data_row['password']

            req_body_02_1 = f'userSession={self.userSession}&username={self.userName}&password={self.password}&login.x=0&login.y=0&JSFormSubmit=off'
            with self.client.post(
                '/cgi-bin/login.pl',
                name='REQ01_02_1_/cgi-bin/login.pl',
                headers={
                    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding':'gzip, deflate, br, zstd',
                    'content-type':'application/x-www-form-urlencoded'
                },
                data=req_body_02_1,
                catch_response=True,
                #debug_stream=sys.stderr
            ) as req_02_1_response:
                check_http_response(req_02_1_response,"User password was correct")

            self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='REQ01_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                #debug_stream=sys.stderr,
            )

            with self.client.get(
                '/cgi-bin/login.pl?intro=true',
                name='REQ01_02_3_/cgi-bin/login.pl?intro=true',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,  # если есть редирект
                catch_response=True,
                #debug_stream=sys.stderr
            ) as req_02_3_response:
                check_http_response(req_02_3_response, f'Welcome, <b>{self.userName}</b>')

        uc01_01_getHomePage(self)
        uc01_02_getLogin(self)

    @task
    def uc01_03_openFlight(self):
        self.client.get(
            '/cgi-bin/welcome.pl?page=search',
            name='REQ01_03_1_/cgi-bin/welcome.pl?page=search',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                'accept-encoding': 'gzip, deflate, br, zstd'
            },
             #debug_stream=sys.stderr
        )
        self.client.get(
            '/cgi-bin/nav.pl?page=menu&in=flights',
            name='REQ01_03_2_/cgi-bin/nav.pl?page=menu&in=flights',
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                'accept-encoding': 'gzip, deflate, br, zstd'
            },
            allow_redirects=False,  # если есть редирект
            #debug_stream=sys.stderr
        )
        with self.client.get(
            '/cgi-bin/reservations.pl?page=welcome',
            name='REQ01_03_3_/cgi-bin/reservations.pl?page=welcome',
            headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,  # если есть редирект
                catch_response=True,
                #debug_stream=sys.stderr
        ) as req_03_3_response:
            check_http_response(req_03_3_response, "Flight Selections")

    @task
    def uc01_04_findFlight(self):
        self.seat_data_row = random.choice(self.test_type_seat)

        self.seatType = self.seat_data_row['seatType']

        self.seatPref = self.seat_data_row['seatPref']

        self.depart = self.user_data_row['depart']

        self.arrive = self.user_data_row['arrive']

        data_list = generationFlightsDate()

        req_body_04_1 = f'advanceDiscount=0&depart={self.depart}&departDate={data_list["depert_date"]}&arrive={self.arrive}&returnDate={data_list["arrive_date"]}&numPassengers=1&seatPref={self.seatPref}&seatType={self.seatType}&findFlights.x=36&findFlights.y=15&.cgifields=roundtrip&.cgifields=seatType&.cgifields=seatPref'
        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_04_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_04_1,
                catch_response=True,
                #debug_stream=sys.stderr

        ) as req_04_1_response:
            check_http_response(req_04_1_response, "name=\"outboundFlight\"")
        self.outboundFlight = re.search(r'name=\"outboundFlight\" value="(.*)\">', req_04_1_response.text).group(1)
        #print(self.outboundFlight)

    @task
    def uc01_05_choiceFlight(self):

        req_body_05_1 = f'outboundFlight={unquote_plus(self.outboundFlight)}&numPassengers=1&advanceDiscount=0&seatType={self.seatType}&seatPref={self.seatPref}&reserveFlights.x=62&reserveFlights.y=13'
        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_05_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_05_1,
                catch_response=True,
                #debug_stream=sys.stderr
        ) as req_05_1_response:
            check_http_response(req_05_1_response, "Flight Reservation")

    @task
    def uc01_06_paymentFlight(self):

        self.expDate = self.seat_data_row['expDate']

        self.creditCard = self.seat_data_row['creditCard']

        self.address1 = self.user_data_row['address1']

        self.address2 = self.user_data_row['address2']

        self.pass1 = self.user_data_row['pass1']


        req_body_06_1 = f'firstName={self.userName}&lastName={self.password}&address1={self.address1}&address2={self.address2}&pass1={self.pass1}&creditCard={self.creditCard}&expDate={self.expDate}&saveCC=on&oldCCOption=on&numPassengers=1&seatType={self.seatType}&seatPref={self.seatPref}&outboundFlight={unquote_plus(self.outboundFlight)}&advanceDiscount=0&returnFlight=&JSFormSubmit=off&buyFlights.x=57&buyFlights.y=9&.cgifields=saveCC'
        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_06_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_06_1,
                catch_response=True,
                 # debug_stream=sys.stderr

        ) as req_06_1_response:
            check_http_response(req_06_1_response, f"from {self.depart} to {self.arrive}.</u></b>")



class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.webtours_base.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host:{host}')

    tasks = [PurchaseFlightTicket]