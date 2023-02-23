# TODO: PRIORITY
from datetime import datetime, timedelta
import requests
import json
import time
import re
import mysql.connector
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, MultiSearch, A, Q
from config import configElasticsearch, configProxies, config, configSQL
from helper import Helper
import argparse
import random


class Traveloka(object):

    def __init__(self):
        self.proxies = {
            #                "http": configProxies.HTTP_PROXY,
            #                "https": configProxies.HTTPS_PROXY
        }
        self.limit = 30
        self.offset = 0
        self.es = Elasticsearch([configElasticsearch.HOST], port=configElasticsearch.PORT,
                                http_auth=(configElasticsearch.USER, configElasticsearch.PASSWD))

    def init_db(self):
        db = mysql.connector.connect(
            host=configSQL.DB_HOST,
            user=configSQL.DB_USER,
            password=configSQL.DB_PWD,
            database=configSQL.DB_NAME,
            port=configSQL.DB_PORT,
            auth_plugin='mysql_native_password'
        )
        return db
    
    def get_list_hotels(self):      
        db = self.init_db()
        cursor = db.cursor()

        cursor.execute("SELECT hotel_name FROM maps ORDER BY updated,id")
        get_data = [data[0] for data in cursor.fetchall()]

        return get_data

    def search(self, query):
        url = "https://content-api.acd.traveloka.com/id-id/v1/hotel/autocomplete"

        payload = json.dumps({
            "clientInterface": "mobile-android",
            "context": {
                "nonce": "4abc2c21-f0ba-481d-a4db-b6396a24cfc6",
                "tvLifetime": "qgdHX7GvehrD9XH5a3S4PdE8AYpuF3hYPaT5bxhY7ZbyjluSjBv/yveVvBLbRH9u1grZSZTFzrL2g5lbKoxsuqllI7+LzcdsZpWyG73RZVRZCCmWF4migmdJ8qf6D+54RV1Pt1/FKrZZ3oKjTkXo9gD5P+t18E86aNb9B/9QGjvvlyHfFnPptZUxAgMVwRNSCMYWUJplNNMY2P4/83O9X+8GNrPf8Ng75ZieUaJama8=",
                "tvSession": "qgdHX7GvehrD9XH5a3S4PWL3Nd74xArIuT+JzcRMbKddQHovERAJ9HWRLrAaZ0jP35AXF20Sv8sft4hqlEDk95h09S9kgr0a3/vSlzwCT9HhC540TquHsAWKmTo7u9TPcXHqdWPXRCIXGuL5vWAWh3zcMCC/7LiIRrgpYS+b9iSA5sIZ1PwBByCpfoeHkvXDvfT4/X9OyP/e6MpXO5D1OcuQ4HHgKYVNY9zZgRx9S/KO33iqZidvOXNshIBiO/jq5f6DDVnoOFtX5o41P9LjbqgX0KNqa89lU7WiG5RvHfZdxtKUSft/vTg8/6cRG+Ukc/LE6nFt83LOxSP7hKDCkKl/ZKWKAkmzoR4WZA/ymdDYI3t4NQP9rXWYYdOn3xNuDh3799QF2ujsSkuSu5sqexqHyQs9OUxII3XlGF27BM/eNbt/p/znMrtcDXEustuffCkxj3UBgXMnqHzNr+9KueDjS5SgNP6oki/ShAY0HUA="
            },
            "data": {
                "contexts": {
                    "currency": "IDR"
                },
                "query": query
            },
            "fields": []
        })

        headers = {
            'origin': 'm.traveloka.com',
            'Content-Type': 'application/json',
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, proxies=self.proxies)

        result = response.json()
        hotels = []

        if result['status'] == 'SUCCESS':
            if 'hotelContent' in result['data']:
                if (len(result['data']['hotelContent']['rows']) == 0):
                    print('No Hotels found')
                    hotels = 'No hotels found'

                for i in result['data']['hotelContent']['rows']:
                    hotel = {
                        "created_date": datetime.now(),
                        "crawled": datetime.now(),
                        "name": i['name'],
                        "type": i['type'],
                        "accommodation_type": i['accommodationType'],
                        "location": {
                            "address": i['additionalInfo'],
                            "coordinate": {
                                "lat": str(i['geoLocation']['lat']).replace('"', ''),
                                "lon": str(i['geoLocation']['lon']).replace('"', '')
                            }
                        },
                        'source': 'traveloka'
                    }
                    hotels.append(hotel)

                    res = self.es.search(index='hotels', q='_id:' + i['id'])
                    if res['hits']['total'] == 0:
                        result = self.es.index(
                            index='hotels',
                            doc_type='hotel',
                            body=hotel,
                            id=i['id']
                        )
                        print(result)
                    else:
                        print("="*70)
                        print("{} have been added".format(hotel['type'].encode('utf-8').title()))

        return hotels

    def get_hotels(self, source, hotels):
        # hotels = ["Horison Arcadia Mangga Dua Jakarta", "Horison Ciledug", "Horison Ultima Ratu Serang", "Horison Aziza Solo", "@HOM Premiere Cilacap", "@HOM Hotel Kudus by Horison Group", "Horison Pekalongan", "Horison Ultima Riss Malioboro Yogyakarta", "Horison Lynn Yogyakarta", "Horison Grand Serpong", "Horison Altama", "Horison Inn Laksana Solo", "Horison Inn Alaska Simpang Lima Semarang", "@HOM Semarang Simpang Lima by Horison", "Horison Kota Lama Semarang", "Horison Nindya Semarang", "@Hom Premiere Timoho",
        #           "Horex (Horison Express) Hotel Sentani", "Horison Kotaraja", "Horison Abepura", "Horison Diana Timika", "Horison Jayapura", "Horison Hotel Ultima Timika", "Horison Ultima Entrop Papua", "@HOM Premier by Horison Abepura", "Horison Kendari", "Horison Plaza Inn Kendari", "Horison Ultima Makassar", "Horison Samarinda", "Horison Sagita Balikpapan", "Horison Arcadia Surabaya", "Horison Pasuruan", "Horison GKB Gresik", "Azza Hotel Palembang by Horison", "Horison Lampung", "Hotel Horison Pematang Siantar", "Horison SKY Kualanamu", "Horison Tasikmalaya", "Horison Palma Pangandaran", "Horison Ultima Bhuvana Ciawi", "Horison Hotel Sukabumi", "Metland Hotel Bekasi", "Horison Ultima Bekasi Hotel"]
        # if args.hotel != 'horison':
        #     hotels = ["*"]

        # hotels = open("hotel_lists.txt", "r").read().splitlines()
        if args.hotel != 'horison':
            hotels = ["*"]

        # Search
        search = Search(using=self.es, index='hotels') \
            .sort('-created_date') \
            .query(Q('bool', must=[Q('match', source=source)])) \
            .query(Q('bool', should=[Q('match_phrase', name=hotel) for hotel in hotels]))

        hotels = []

        # Execute
        for i in search.scan():
            post_meta = i.meta.to_dict()
            hotels.append(post_meta['id'])
        hotels = random.sample(hotels, len(hotels))
        return hotels

    def hotel_detail(self, hotel_id):
        url = "https://search-api.apr.traveloka.com/en-id/v2/hotel/search/detail"

        payload = json.dumps({
            "clientInterface": "mobile-android",
            "context": {
                "nonce": "72af5cc8-5dc6-4ef6-882a-e8ff55b11b27",
                "tvLifetime": "qgdHX7GvehrD9XH5a3S4PdE8AYpuF3hYPaT5bxhY7ZbH8lBrd9BMEnf4f09HQ8mPBY+4YQTwOT3TWgtF1+K17W5n/5QtgKZtw2VhkkmsexMdUjOakMBusMgpx9RJk5HBQiUN/2C3JnSUJJddYBnJfeX8LNIltVJX4fG/lI2cMvrvlyHfFnPptZUxAgMVwRNSCMYWUJplNNMY2P4/83O9X+8GNrPf8Ng75ZieUaJama8=",
                "tvSession": "qgdHX7GvehrD9XH5a3S4PWL3Nd74xArIuT+JzcRMbKddQHovERAJ9HWRLrAaZ0jPcn3B2beSZC3ft5Gfmw5jH9LyRB97tOflcSi5Br4kloFcUbdqIy8JdBJAq7jtuDvRH3tli30+iUzxyvi+Gk90RTCCN4CX1SDVcGsmBYE/Jc2r4NMhZmdX9keZ1Qs9WW7i+z2V+PHTpPCAB2iAc2jWFBlR5eYwnLI647R3C60TL4j/ZqwZLfitcxsbj+LSosKS/XRn35Ta/fvByrQwu8X+NBWGF2HvLQX7wuUHLkRs8FctDOONOQj37mhWEZCwORc4PsxMZ+SJ+V2CJtyuR9hDj060w8K7mx4sezR1G4xp41SdokrTj2DF44Nx2g2ZscIWSi5uzR+N+IMYg0G4c1uTS7bKBeYAqjVxFgWKW/KdNnWC1BeOY56JY0x6qfKJ2bBWZFerH5Igf1wdITBbygLDYG2PeYg1sQr2h/wIBjIyPQ0rIzgirWg4SdUxiAHYgEHl"
            },
            "data": {
                "currency": "IDR",
                "height": 960,
                "hotelId": hotel_id,
                "userSearchPreferences": [],
                "width": 540
            },
            "fields": []
        })
        headers = {
            'Origin': 'm.traveloka.com',
            'Content-Type': 'application/json',
            'Cookie': 'AWSALB=G6ZcnGMoRvChop1ANgN0546bABIXSg67ks3NFxew1/jT94MCBaVrRyfEOoR1UXmIrYpLz9/rixK+KW8mwVX3z8DYH0yjqZP3PsSnw/tuzJlFwqPFOrvxZWKvKiRz; AWSALBCORS=G6ZcnGMoRvChop1ANgN0546bABIXSg67ks3NFxew1/jT94MCBaVrRyfEOoR1UXmIrYpLz9/rixK+KW8mwVX3z8DYH0yjqZP3PsSnw/tuzJlFwqPFOrvxZWKvKiRz'
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, proxies=self.proxies)
        result = response.json()

        return result['data']

    def hotel_room_price(self, hotel_id, hotel_name, crawled):
        url = "https://search-api.apr.traveloka.com/id-id/v2/hotel/searchRooms"

        data = []
        checkin = datetime.strptime(crawled['start'], "%Y-%m-%d")
        checkout = datetime.strptime(crawled['end'], "%Y-%m-%d")

        print("Checkin: ", crawled['start'])
        print("Checkout: ", crawled['end'])
        payload = json.dumps({
            "clientInterface": "mobile-android",
            "context": {
                "nonce": "235c4f12-4de7-483f-839a-49af036534db",
                "tvLifetime": "qgdHX7GvehrD9XH5a3S4PdE8AYpuF3hYPaT5bxhY7ZbyjluSjBv/yveVvBLbRH9uocGa4kqOKNayuW6SLX6xWKQCKa3/BumUUDxIt2yKXy2uAy8RkE5Eax8opZ+b8NCdRV1Pt1/FKrZZ3oKjTkXo9gD5P+t18E86aNb9B/9QGjvvlyHfFnPptZUxAgMVwRNSCMYWUJplNNMY2P4/83O9X+8GNrPf8Ng75ZieUaJama8=",
                "tvSession": "qgdHX7GvehrD9XH5a3S4PXWKx93/3Xi103f/kPpnhg12aEXpPupDgOYnFyyKE6aXB1MqbaJHKjsxaB1gcGl9Fw2kgjSK1UQ0px3x9bCpu8ZiSl3ZqFktwpH8W7f+6nrlRjr7IpOmQLP3TEAjHLqFe7v1v7GGqdWTrLtvnWCVUekICMYM8pmg9JEI+5wUn9uCQWEND2sGdAmDipquWpx9DIgJxKATL73QZE5zICT+5lrTxV7z+zqmGSu7vANzJCfn9XHhfDgnd1x0GkMxPv9M+90iwzdkqrkuN3RiR09Bcg2YC8jl7gsKhmSjTjPoGWBJ68hNC9q2O/vHHkKH8e7tQ5+YQdJSEe1mbC5ZghXnU6KsnM6IBZ2soAnTil9t4lwziHPMbBGGO/6kRPzC9e1kdw=="
            },
            "data": {
                "backdate": False,
                "ccGuaranteeOptions": {
                    "ccGuaranteeRequirementOptions": [
                        "CC_GUARANTEE",
                        "NO_CC_GUARANTEE"
                    ],
                    "ccInfoPreferences": [
                        "CC_TOKEN",
                        "CC_FULL_INFO"
                    ]
                },
                "checkInDate": {
                    "day": checkin.day,  # dt.day,
                    "month": checkin.month,  # dt.month,
                    "year": checkin.year  # dt.year
                },
                "checkOutDate": {
                    "day": checkout.day,  # new_dt.day,
                    "month": checkout.month,  # new_dt.month,
                    "year": checkout.year  # new_dt.year
                },
                "contexts": {
                    "sourceHotelDetail": "AUTOCOMPLETE_SF",
                    "funnelId": "hotel",
                    "funnelSource": "iconHomepage"
                },
                "currency": "IDR",
                "expressCheckInEligibility": False,
                "hotelId": hotel_id,
                "includeWorryFree": True,
                "isExtraBedIncluded": True,
                "isReschedule": False,
                "labelContext": {},
                "lastMinute": False,
                "monitoringSpec": {},
                "numAdults": 1,
                "numChildren": 0,
                "numOfNights": 1,
                "numRooms": 1,
                "prevSearchId": "",
                "rateTypes": [
                    "PAY_NOW",
                    "PAY_AT_PROPERTY"
                ],
                "sid": "tcode-7797-696E-mf-01"
            },
            "fields": []
        })
        headers = {
            'Origin': 'm.traveloka.com',
            'Content-Type': 'application/json',
            'Cookie': 'AWSALB=+xeB/xT/MJU674S0W9cl+yo+80hIUylOtIFsb3zSLgyamg3F/GJnuoNbWC12sTyhlCk3DECZzOMqEwz+/kNY6078uQabnOQFindwliatQn6z2wvsdDFTTAhnbuEm; AWSALBCORS=+xeB/xT/MJU674S0W9cl+yo+80hIUylOtIFsb3zSLgyamg3F/GJnuoNbWC12sTyhlCk3DECZzOMqEwz+/kNY6078uQabnOQFindwliatQn6z2wvsdDFTTAhnbuEm'
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, proxies=self.proxies)
        result = response.json()

        for i in result['data']['recommendedEntries']:
            for j in i['roomList']:
                local_category = helper_instance.define_local_category(j['name'])
                
                room = {
                    'name': j['name'],
                    'price': j['rateDisplay'],
                    "bed_type": j['hotelBedType'][0] if j['hotelBedType'] is not None else '',
                    "room_type": j['name'],
                    "cancellation_policy": j['roomCancellationPolicy']['cancellationPolicyString'],
                    "crawled": datetime.now(),
                    "description": j['labelDisplayData']['longDescription'] if j['labelDisplayData'] is not None else '',
                    "facilities": [i['name'] for i in j['roomHighlightFacilityDisplay']],
                    "breakfast": j['breakfastIncluded'],
                    "max_occupancy": j['maxOccupancy'],
                    "images": {
                        'original': {
                            'url': j['roomImages'][0] if len(j['roomImages']) is not 0 else []
                        }
                    },
                    "price": {
                        "currency": j['propertyCurrencyRateDisplay']['totalFare']['currency'],
                        "original": j['propertyCurrencyRateDisplay']['baseFare']['amount'],
                        "after_discount": j['propertyCurrencyRateDisplay']['totalFare']['amount'],
                        "total": j['propertyCurrencyRateDisplay']['totalFare']['amount'],
                        "taxes": j['propertyCurrencyRateDisplay']['taxes']['amount'],
                        "fees": j['propertyCurrencyRateDisplay']['fees']['amount']
                    },
                    "room_size": j['hotelRoomSizeDisplay']['value'] + j['hotelRoomSizeDisplay']['unit'] if j['hotelRoomSizeDisplay'] else '',
                    "source": "traveloka",
                    "hotel": {
                        "hotel_id": hotel_id,
                        "name": hotel_name
                    },
                    "checkin": crawled['start'],
                    "checkout": crawled['end'],
                    "local_category": local_category
                }

                res = self.es.search(
                    index='rooms', q='_id:' + str(j['hotelRoomId']) + str(datetime.strptime(crawled['start'], "%Y-%m-%d").strftime("%Y%m%d")))
                if res['hits']['total'] == 0:
                    result = self.es.index(
                        index='rooms',
                        doc_type='room',
                        body=room,
                        id=str(j['hotelRoomId']) + str(datetime.strptime(crawled['start'], "%Y-%m-%d").strftime("%Y%m%d"))
                    )

                    print(result)
                else:
                    print("="*70)
                    print("room have been added")

                    result = self.es.update(
                        index='rooms',
                        doc_type='room',
                        id=str(j['hotelRoomId']) + str(datetime.strptime(crawled['start'], "%Y-%m-%d").strftime("%Y%m%d")),
                        body={'doc':{'crawled':datetime.now()}},
                    )
                    
                    print(result)
                room['room_id'] = j['hotelRoomId']
                data.append(room)
        return data

    def crawl_histories(self, hotel, rooms):
        crawled = datetime.now()
        for room in rooms:
            history = {
                'crawled': crawled,
                'source': 'traveloka',
                'hotel': {
                    'name': hotel['name'],
                    'rating': hotel['starRating'] if 'starRating' in hotel else None,
                    'class': hotel['starRating'] if 'starRating' in hotel else None,
                    'id': hotel['id'],
                    'description': hotel['attribute']['description'] if 'attribute' in hotel else None,
                    'photo': {
                        'images': [
                            {
                                'thumbnail': {
                                    'url': hotel['assets'][0]['thumbnailUrl'] if hotel['assets'] else ''
                                }
                            },
                            {
                                'original': {
                                    'url': hotel['assets'][0]['url'] if hotel['assets'] else ''
                                }
                            }
                        ]
                    }
                },
                'room': room
            }
            res = self.es.search(
                index='histories', q='_id:' + str(room['room_id']) + str(crawled.strftime("%Y%m%d%H")))
            if res['hits']['total'] == 0:
                result = self.es.index(
                    index='histories',
                    doc_type='crawling',
                    body=history,
                    id=str(room['room_id']) + str(crawled.strftime("%Y%m%d%H"))
                )

                print(result)
            else:
                print("="*70)
                print("history have been added")

                result = self.es.update(
                    index="histories", 
                    doc_type="crawling", 
                    id=str(room['room_id']) + str(crawled.strftime("%Y%m%d%H")), 
                    body={"doc": {'crawled': crawled}}
                )

                print(result)

    def hotel_review(self, hotel_id, limit, offset):
        url = "https://content-api.acd.traveloka.com/id-id/v2/hotel/getHotelReviews"

        payload = json.dumps({
            "clientInterface": "mobile-android",
            "context": {
                "nonce": "8b42e92c-4450-45f9-8ab1-9c1491e5a3f5",
                "tvLifetime": "qgdHX7GvehrD9XH5a3S4PdE8AYpuF3hYPaT5bxhY7ZbyjluSjBv/yveVvBLbRH9unvaM1sKT5SqseZh3zMUyExAteIcP01sefRBxV/9pJa/anlhLQSKSAemYvg656qjvRV1Pt1/FKrZZ3oKjTkXo9gD5P+t18E86aNb9B/9QGjvvlyHfFnPptZUxAgMVwRNSCMYWUJplNNMY2P4/83O9X+8GNrPf8Ng75ZieUaJama8=",
                "tvSession": "qgdHX7GvehrD9XH5a3S4PXWKx93/3Xi103f/kPpnhg12aEXpPupDgOYnFyyKE6aXB1MqbaJHKjsxaB1gcGl9Fw2kgjSK1UQ0px3x9bCpu8ZiSl3ZqFktwpH8W7f+6nrlRjr7IpOmQLP3TEAjHLqFe7v1v7GGqdWTrLtvnWCVUekICMYM8pmg9JEI+5wUn9uCQWEND2sGdAmDipquWpx9DIgJxKATL73QZE5zICT+5lrTxV7z+zqmGSu7vANzJCfn9XHhfDgnd1x0GkMxPv9M+90iwzdkqrkuN3RiR09Bcg2YC8jl7gsKhmSjTjPoGWBJ68hNC9q2O/vHHkKH8e7tQ6v9JfiGLB/x5CwPGCCGAurdZ+W0OfF6/xkIdNQhXV1j7Nsrl5HNnrFcbDO8oRH08Q=="
            },
            "data": {
                "ascending": True,
                "filterSortSpec": {
                    "sortType": "DEFAULT",
                    "tagIds": [
                        "ALL"
                    ]
                },
                "hotelId": hotel_id,
                "skip": offset,
                "top": limit,
                "userSearchPreferences": []
            },
            "fields": []
        })
        headers = {
            'Origin': 'm.traveloka.com',
            'Content-Type': 'application/json',
            'Cookie': 'AWSALB=C+pGarsg1XSKeIVBzf5TPuO5rFVFdMywJvs5v2jQZTxalwV0dE9GR6eNIcT4lvCGwyPqeOCMhP2cNOX9VxLAom7PkzmW7j7L6LuRnqP1MLBdkg5nqzYWUPjdukKW; AWSALBCORS=C+pGarsg1XSKeIVBzf5TPuO5rFVFdMywJvs5v2jQZTxalwV0dE9GR6eNIcT4lvCGwyPqeOCMhP2cNOX9VxLAom7PkzmW7j7L6LuRnqP1MLBdkg5nqzYWUPjdukKW'
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, proxies=self.proxies)
        result = response.json()

        return result

    def hotel_generate_review(self, hotel, room_price, review):
        remove_html = re.compile('<.*?>')
        info = {}
        info['hotel'] = {
            'name': hotel['name'],
            'rating': hotel['starRating'] if 'starRating' in hotel else None,
            'class': hotel['starRating'] if 'starRating' in hotel else None,
            'id': hotel['id'],
            'description': re.sub(remove_html, '', hotel['attribute']['description']) if 'attribute' in hotel else None,
            'photo': {
                'images': [
                    {
                        'thumbnail': {
                            'url': hotel['assets'][0]['thumbnailUrl'] if hotel['assets'] else ''
                        }
                    },
                    {
                        'original': {
                            'url': hotel['assets'][0]['url'] if hotel['assets'] else ''
                        }
                    }
                ]
            }
        }
        info['location'] = {
            'name': hotel['localAddressString'],
            'address': hotel['address'],
            'city': hotel['city'],
            "coordinate": {
                "lat": str(hotel['latitude']).replace('"', '') if 'latitude' in hotel else 0,
                "lon": str(hotel['longitude']).replace('"', '') if 'longitude' in hotel else 0
            }
        }

        # info['price'] = {}
        # info['price']['traveloka'] = room_price['data']['recommendedEntries'][0]['roomList'][0]['rateDisplay']['totalFare']['amount']

        for i in review['data']['reviewList']:
            info['review'] = {
                # 'url': review['url'],
                'title': i['travelThemeDisplayName'],
                'rating': i['overallScore'],
                # 'total_user_review': int(data['user']['contributions']['reviews']) if 'user' in data and data['user'] is not None and 'contributions' in data['user']  else 0,
                # 'type_reviewer': data['user']['reviewer_type'] if 'user' in data and data['user'] is not None and 'reviewer_type' in data['user'] else None,
                'date': datetime.fromtimestamp(int(i['timestamp'])/1000),
                'language': i['language'].capitalize(),
                # 'type': data['type'],
                # 'platform': data['published_platform'],
                'id': i['reviewId'],
                'message': ' '.join(i['reviewText'].replace('\n', " ").replace('\n', " ").replace('\n', " ").split()) if i['reviewText'] is not None else ''
            }

            if 'businessReply' in review:
                info['response'] = {
                    # 'connection': review['businessReply']['connection'],
                    # 'response_owner': True,
                    # 'id': data['owner_response']['id'],
                    # 'title': data['owner_response']['title'],
                    # 'name': data['owner_response']['responder'],
                    'message': ' '.join(i['businessReply']['replyText'].replace('\n', " ").replace('\n', " ").replace('\n', " ").split()),
                    # 'language': data['owner_response']['lang'],
                    'date': datetime.fromtimestamp(i['businessReply']['timestamp'])
                }

            info['user'] = {
                # 'type': data['user']['type'] if data['user'] is not None and 'type' in data['user'] else None,
                'id': i['profileId'],
                'name': i['reviewerName'],
                # 'username': data['user']['username'] if data['user'] is not None and 'username' in data['user'] else None,
                # 'user_location': data['user']['user_location']['name'] if data['user'] is not None and 'user_location' in data['user'] else None,
                # 'created': data['user']['created_time'] if data['user'] is not None and 'created_time' in data['user'] else datetime.now()
            }

            info['source'] = 'traveloka'
            info['last_access'] = datetime.now()

            res = self.es.search(index='hotel_reviews', q='_id:' +
                                 str(info['user']['id'])+str(info['review']['id']))
            if res['hits']['total'] == 0:
                result = self.es.index(
                    index='hotel_reviews',
                    doc_type='review',
                    body=info,
                    id=str(info['user']['id']) +
                    str(info['review']['id'])
                )

                print(result)
            else:
                print("="*70)
                print("review have been added")

    def save_to_json(self, filename, result):  # TODO: Not implemented yet
        with open(filename + '.json', 'a+') as outfile:
            json.dump(result, outfile, indent=4)


if __name__ == "__main__":
    traveloka = Traveloka()
    parser = argparse.ArgumentParser(description='OTA Crawling - Traveloka')
    parser.add_argument('-s', '--search', dest='search',
                        type=str, required=False, help="Search for Hotel")
    parser.add_argument('-ro', '--room', dest='room', required=False,
                        help="Search for Hotel Rooms", action="store_true")
    parser.add_argument('-re', '--review', dest='review', required=False,
                        help="Get Hotel Review", action="store_true", default=True)
    parser.add_argument('-hr', '--histories', dest='histories', required=False,
                        help="Get Histories Information", action="store_true")
    parser.add_argument('-db', '--database', dest='database', required=False,
                        help="Get list hotel from db", action="store_true")    
    # escape argument for horison
    parser.add_argument('-hotel', dest='hotel', type=str, required=False,
                        help="Horison Hotel Review", default="horison")
    args, unknown = parser.parse_known_args()

    # 1. Search
    if args.search:
        print('Traveloka - Search Hotel')
        try:
            if args.database:
                hotels = traveloka.get_list_hotels()
            else:
                hotels = open("hotel_lists.txt", "r").read().splitlines()
            for hotel in hotels:
                # print('Get Hotel', args.search)
                # result = traveloka.search(args.search)
                print('Get Hotel', hotel)
                result = traveloka.search(hotel)
        except OSError:
            print("Please create file named 'hotel_lists.txt' first")

        # result = traveloka.search('Horison Ultima Bhuvana Ciawi')
        # result = traveloka.search('Horison')

    # 2. Rooms
    elif args.room:
        print('Traveloka - Get Hotel Room')
        if args.database:
            hotels_name = traveloka.get_list_hotels()
        else:
            hotels_name = open("hotel_lists.txt", "r").read().splitlines()
        hotels = traveloka.get_hotels('traveloka',hotels_name)
        for hotel_id in hotels:
            hotel = traveloka.hotel_detail(hotel_id)
            print(hotel['name'])
            rooms = traveloka.hotel_room_price(hotel_id, hotel['name'])

    # 3. Histories
    elif args.histories:
        print('Traveloka - Histories Hotel')
        if args.database:
            hotels_name = traveloka.get_list_hotels()
        else:
            hotels_name = open("hotel_lists.txt", "r").read().splitlines()
        hotels = traveloka.get_hotels('traveloka',hotels_name)
        for hotel_id in hotels:
            hotel = traveloka.hotel_detail(hotel_id)
            print(hotel['name'])
            helper_instance = Helper()
            helper_booking_dates = helper_instance.checkin_checkout_dates(days=config.CRAWLING_DAYS)  # return list of dates
            for hbd in helper_booking_dates:
                rooms = traveloka.hotel_room_price(hotel_id, hotel['name'], hbd)
                traveloka.crawl_histories(hotel, rooms)

    # 4. Reviews
    elif args.review:
        print('Traveloka - Review Hotel')
        traveloka.limit = 300
        if args.database:
            hotels_name = traveloka.get_list_hotels()
        else:
            hotels_name = open("hotel_lists.txt", "r").read().splitlines()
        hotels = traveloka.get_hotels('traveloka',hotels_name)
        for hotel_id in hotels:
            hotel = traveloka.hotel_detail(hotel_id)
            print(hotel['name'])

            helper_instance = Helper()
            helper_booking_dates = helper_instance.checkin_checkout_dates(days=config.CRAWLING_DAYS)  # return list of dates
            for hbd in helper_booking_dates:
                rooms = traveloka.hotel_room_price(hotel_id, hotel['name'], hbd)
                offset = 0
                limit = 10
                review = traveloka.hotel_review(hotel_id, limit, offset)
                result = traveloka.hotel_generate_review(hotel, rooms, review)
                loop = True
                while loop:
                    offset = offset+len(review['data']['reviewList'])
                    review = traveloka.hotel_review(hotel_id, limit, offset)
                    result = traveloka.hotel_generate_review(
                        hotel, rooms, review)
                    time.sleep(5)
                    if len(review['data']['reviewList']) < 10:
                        loop = False