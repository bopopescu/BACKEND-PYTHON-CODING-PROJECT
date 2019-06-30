from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from servicearea.models import Provider, ServiceArea
from servicearea.provider_api import ProviderSerializer
import json
from random import randint
from django.contrib.gis.geos import Polygon

# Create your tests here.

class ProviderTests(APITestCase):
    """
        Provider API tests class
    """
    
    
    def setUp(self):
        """
            set up some providers for testing purpose
        """
        Provider.objects.create(
            name = 'Paul',
            email = 'paul@mymozio.com',
            phone = '+237 697769641',
            language = 'fr',
            currency = 'USD'
        )
        Provider.objects.create(
            name = 'Batoum',
            email = 'batoum@mymozio.com',
            phone = '+237 681375649',
            language = 'ga',
            currency = 'XAF'
        )
        self.client = Client()

    def test_provider_currency(self):
        """
            Make sure created provider in the setup has valid currency
        """
        paul = Provider.objects.get(email='paul@mymozio.com')
        batoum = Provider.objects.get(email='batoum@mymozio.com')
        self.assertEqual(paul.currency, 'USD')
        self.assertEqual(batoum.currency, 'XAF')

    def test_get_all_providers(self):
        """
           MAke sure we can retrieve all providers
           GET /api/providers/
        """
        url = '/api/providers/'
        response = self.client.get(url)
        providers = Provider.objects.all()
        self.assertEqual(len(response.json()), len(providers))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_valid_single_provider(self):
        """
            Make sure we can retrieve an existing provider
        """
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        url = '/api/providers/%s/'%providers[0].id
        response = self.client.get(url)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json()['name'], providers[0].name)
        self.assertEqual(response.json()['email'], providers[0].email)

    def test_get_invalid_single_provider(self):
        """
            Make sure we cant retrieve an non existing provider
        """
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        ids = [x.id for x in providers]
        rn = -1
        while rn == -1:
            n = randint(0, 1000000)
            if n not in ids:
                rn = n
        url = '/api/providers/%s/'%rn
        response = self.client.get(url)
        self.assertIn('detail', response.json().keys())
        self.assertEqual(response.json()['detail'], 'Not found.')
        
    def test_create_valid_provider(self):
        """
            Make sure we can create a valid provider
        """
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        url = '/api/providers/'
        valid_provider = {
            'name' : "toto",
            'email' : 'toto@mymozio.com',
            'phone' : '00237560874',
            'language' : 'en',
            'currency' : 'USD'
        }
        response = self.client.post(
            url,
            data=valid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 3)
        provider = Provider.objects.get(email='toto@mymozio.com')
        self.assertIsNotNone(provider)
        self.assertEqual(provider.language, 'en')

    def test_create_invalid_provider(self):
        """
            Make sure we cant create provider without 
            - Valid email
            - Valid currency
            - Valid language
            - no name
        """
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        url = '/api/providers/'
        #invalid email
        invalid_provider = {
            'name' : "toto",
            'email' : 'toto@mymoziocom',
            'phone' : '00237560874',
            'language' : 'en',
            'currency' : 'USD'
        }
        response = self.client.post(
            url,
            data=invalid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json().keys())
        self.assertEqual(response.json()['email'], ['Enter a valid email address.'])
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        #existing email
        invalid_provider = {
            'name' : "toto",
            'email' : 'paul@mymozio.com',
            'phone' : '00237560874',
            'language' : 'en',
            'currency' : 'USD'
        }
        response = self.client.post(
            url,
            data=invalid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.json().keys())
        self.assertEqual(response.json()['email'], ['provider with this email already exists.'])
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        #invalid currency
        invalid_provider = {
            'name' : "toto",
            'email' : 'paul@mymozio.com',
            'phone' : '00237560874',
            'language' : 'en',
            'currency' : '$'
        }
        response = self.client.post(
            url,
            data=invalid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('currency', response.json().keys())
        self.assertIn('is not a valid choice.', response.json()['currency'][0])
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        #invalid language
        invalid_provider = {
            'name' : "toto",
            'email' : 'paul@mymozio.com',
            'phone' : '00237560874',
            'language' : 'frte',
            'currency' : '$'
        }
        response = self.client.post(
            url,
            data=invalid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', response.json().keys())
        self.assertIn('is not a valid choice.', response.json()['language'][0])
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        #blank name
        invalid_provider = {
            'name' : "",
            'email' : 'blank@mymozio.com',
            'phone' : '00237560874',
            'language' : 'en',
            'currency' : 'USD'
        }
        response = self.client.post(
            url,
            data=invalid_provider
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.json().keys())
        self.assertEqual(response.json()['name'], ['This field may not be blank.'])
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        
    def test_valid_update_provider(self):
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        url = "/api/providers/%s/"%providers[0].id
        valid_provider = {
            'name' : 'Paulo',
            'email' : 'paul@mymozio.com',
            'phone' : '+237 697769641',
            'language' : 'fr',
            'currency' : 'USD'
        }
        response = self.client.put(
            url,
            data=valid_provider,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)        

    def test_invalid_update_provider(self):
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        rn = -1
        ids = [x.id for x in providers]
        while rn == -1:
            n = randint(0, 1000000)
            if n not in ids:
                rn = n
        url = '/api/providers/%s/'%rn
        invalid_provider = {
            'name' : 'Paulo',
            'email' : 'paul@mymozio.com',
            'phone' : '+237 697769641',
            'language' : 'fr',
            'currency' : 'USD'
        }
        response = self.client.put(
            url, kwargs={'id': rn},
            data=invalid_provider,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        paul = Provider.objects.get(email='paul@mymozio.com')
        self.assertEqual(paul.name, 'Paul')

    def test_valid_delete_provider(self):
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        url = "/api/providers/%s/"%providers[0].id
        response = self.client.delete(
            url,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 1)

    def test_invalid_delete_provider(self):
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)
        rn = -1
        ids = [x.id for x in providers]
        while rn == -1:
            n = randint(0, 1000000)
            if n not in ids:
                rn = n
        url = '/api/providers/%s/'%rn
        response = self.client.delete(
            url,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        providers =  Provider.objects.all()
        self.assertEqual(len(providers), 2)


class ServiceAreaTests(APITestCase):
    """
        ServiceArea API tests class
    """
    def setUp(self):
        """
            set up some ServiceArea for testing purpose
        """
        Provider.objects.create(
            name = 'Paul',
            email = 'paul@mymozio.com',
            phone = '+237 697769641',
            language = 'fr',
            currency = 'USD'
        )
        Provider.objects.create(
            name = 'Batoum',
            email = 'batoum@mymozio.com',
            phone = '+237 681375649',
            language = 'ga',
            currency = 'XAF'
        )
        self.client = Client()
        ServiceArea.objects.create(
            provider = Provider.objects.get(email='paul@mymozio.com'),
            price = 5000000.0,
            area_name = 'Bermuda Triangle',
            area = Polygon(
                        ((-64.73, 32.31),
                        (-80.19, 25.76),
                        (-66.09, 18.43),
                        (-64.73, 32.31))
            )
        )
        ServiceArea.objects.create(
            provider = Provider.objects.get(email='batoum@mymozio.com'),
            price = 5000000.0,
            area_name = "Flemish Diamond",
            area = Polygon(
                    (
                        (3.55, 51.08),
                        (4.36, 50.73),
                        (4.84, 50.85),
                        (4.45, 51.30),
                        (3.55, 51.08)
                    )
                )
        )
        
    def test_aervicearea_name(self):
        """
            Make sure setup created areas
        """
        bermuda = ServiceArea.objects.get(area_name = "Flemish Diamond")
        self.assertEqual(bermuda.price, 5000000.0)
        self.assertEqual(bermuda.provider.name, 'Batoum')
        
    def test_get_all_serviceareas(self):
        """
            MAke sure we can retrieve all serviceareas
            GET /api/serviceareas/
        """
        url = '/api/serviceareas/'
        response = self.client.get(url)
        serviceareas = ServiceArea.objects.all()
        self.assertEqual(len(response.json()), len(serviceareas))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_servicearea(self):
        """
            Make sure we can retrieve an existing servicearea
        """
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 2)
        url = '/api/serviceareas/%s/'%serviceareas[0].id
        response = self.client.get(url)
        self.assertIsNotNone(response.json())
        self.assertEqual(response.json()['price'], serviceareas[0].price)
        self.assertEqual(response.json()['area_name'], serviceareas[0].area_name)
    
    def test_get_invalid_single_servicearea(self):
        """
            Make sure we cant retrieve an non existing servicearea
        """
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 2)
        ids = [x.id for x in serviceareas]
        rn = -1
        while rn == -1:
            n = randint(0, 1000000)
            if n not in ids:
                rn = n
        url = '/api/serviceareas/%s/'%rn
        response = self.client.get(url)
        self.assertIn('detail', response.json().keys())
        self.assertEqual(response.json()['detail'], 'Not found.')

    def test_create_valid_servicearea(self):
        """
            Make sure we can create a valid servicearea
        """
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 2)
        url = '/api/serviceareas/'
        paul = Provider.objects.get(email='paul@mymozio.com')
        paul_url = '/api/providers/%s/'%paul.id
        valid_servicearea = {
            'provider' : paul_url,
            'price' : '150000000.0',
            'area_name' : 'Research Triangle',
            'area' : json.dumps({
                "type": "Polygon",
                "coordinates": [
                    [
                        [-78.93, 36.00],
                        [-78.67, 35.78],
                        [-79.04, 35.90],
                        [-78.93, 36.00]
                    ]
                ]
            })
        }
        response = self.client.post(
            url,
            data=json.dumps(valid_servicearea),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 3)
        servicearea = ServiceArea.objects.get(area_name='Research Triangle')
        self.assertIsNotNone(servicearea)
        self.assertEqual(servicearea.price, 150000000.0)
        
    def test_create_invalid_servicearea(self):
        """
            Make sure we can create a valid servicearea
        """
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 2)
        url = '/api/serviceareas/'
        paul = Provider.objects.get(email='paul@mymozio.com')
        paul_url = '/api/providers/%s/'%paul.id
        invalid_servicearea = {
            'price' : '150000000.0',
            'area_name' : 'Research Triangle',
            'area' : json.dumps({
                "type": "Polygon",
                "coordinates": [
                    [
                        [-78.93, 36.00],
                        [-78.67, 35.78],
                        [-79.04, 35.90],
                        [-78.93, 36.00]
                    ]
                ]
            })
        }
        response = self.client.post(
            url,
            data=json.dumps(invalid_servicearea),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        serviceareas =  ServiceArea.objects.all()
        self.assertEqual(len(serviceareas), 2)
        self.assertIn('provider', response.json().keys())
        self.assertEqual(response.json()['provider'], ['This field is required.'])

    def test_point_in_areas(self):
        """
            Make sure we can retrieve all areas where point is
        """
        url = "/api/serviceareas/25.450234/-70.253727/get/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.json())
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['area_name'], 'Bermuda Triangle')
        ServiceArea.objects.create(
            provider = Provider.objects.get(email='paul@mymozio.com'),
            price = 5000000.0,
            area_name = 'Bermuda Triangle 2',
            area = Polygon(
                        ((-64.73, 32.31),
                        (-80.19, 25.76),
                        (-66.09, 18.43),
                        (-64.73, 32.31))
            )
        )
        serviceareas = ServiceArea.objects.all()
        self.assertEqual(3, len(serviceareas))
        url2 = "/api/serviceareas/29.344022/-67.651616/get/"
        response2 = self.client.get(url2)
        print(response2.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response2.json())
        self.assertEqual(len(response2.json()), 2)


if __name__ == '__main__':
    unittest.main()
