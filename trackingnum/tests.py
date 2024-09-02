from unittest import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from datetime import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor
import pytz
import requests
from dateutil.parser import isoparse
import re
# Create your tests here.

class TrackingNumberAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('tracking-number-view')
        self.query_params = {
            "origin_country_id": "MY",
            "destination_country_id": "ID",
            "weight": "1.238",
            "created_at": "2018-11-20T19:29:32+08:00",
            "customer_id": "fe619854-b59b-425e-9db4-943979e1bd49",
            "customer_name": "RedBox Logistics",
            "customer_slug": "redbox-logistics"
        }

    def test_valid_tracking_number_generation(self):
        response = self.client.get(self.url, self.query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tracking_number', response.data)
        self.assertIn('created_at', response.data)
        created_at = response.data['created_at']
        # Check if the timestamp is in RFC 3339 format by parsing it
        try:
            # Attempt to parse the created_at value
            isoparse(created_at)
        except ValueError:
            # If parsing fails, the test should fail, indicating an incorrect format
            self.fail(f"'created_at' timestamp is not in RFC 3339 format: {created_at}")

        # Optional: Add regex check to confirm the format explicitly
        rfc3339_regex = re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
        )
        self.assertRegex(created_at, rfc3339_regex, f"'created_at' does not match RFC 3339 format: {created_at}")
        self.assertRegex(response.data["tracking_number"], r"^[A-Z0-9]{1,16}$")

    def test_tracking_number_api_with_missing_params(self):
        # Send GET request with one of the required parameters missing
        invalid_params = self.query_params.copy()
        invalid_params.pop('origin_country_id')  # Remove a required field
        response = self.client.get(self.url, invalid_params)
        # Check if the response indicates a bad request which indicates an invalid input
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tracking_number_api_with_invalid_country_code(self):
        # Test with invalid country code
        invalid_params = self.query_params.copy()
        invalid_params['origin_country_id'] = 'XX'  # Non-existent ISO 3166-1 alpha-2 code
        response = self.client.get(self.url, invalid_params)
        # Check if the response indicates a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tracking_number_api_with_invalid_weight(self):
        # Test with invalid weight format
        invalid_params = self.query_params.copy()
        invalid_params['weight'] = 'abc'  # Invalid weight format
        response = self.client.get(self.url, invalid_params)
        # Check if the response indicates a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tracking_number_api_with_invalid_timestamp(self):
        # Test with invalid timestamp format
        invalid_params = self.query_params.copy()
        invalid_params['created_at'] = 'invalid-date-format'
        response = self.client.get(self.url, invalid_params)
        # Check if the response indicates a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TrackingNumberConcurrentTest(TestCase):

    def setUp(self):
        # Common parameters used for the requests
        self.url = 'https://scalpro.online/next-tracking-number/'
    def create_query_params(self):
        customer_id = str(uuid.uuid4())
        current_time = datetime.now(pytz.utc)
        timezone = pytz.timezone('Asia/Singapore')
        local_time = current_time.astimezone(timezone)
        formatted_time = local_time.strftime('%Y-%m-%dT%H:%M:%S%z')

        # Adjust the offset format to include a colon (e.g., +08:00 instead of +0800)
        formatted_time_with_colon = f"{formatted_time[:-2]}:{formatted_time[-2:]}"
        return {
            "origin_country_id": "MY",
            "destination_country_id": "ID",
            "weight": "1.234",
            "created_at": formatted_time_with_colon,
            "customer_id": customer_id,
            "customer_name": "RedBox Logistics",
            "customer_slug": "redbox-logistics",
        }

    def make_request(self):
        """Helper function to make a single request to the API."""
        response = requests.get(self.url, params=self.create_query_params())
        return response

    def test_concurrent_requests(self):
        # Define the number of concurrent requests
        num_requests = 50

        # Use ThreadPoolExecutor to simulate concurrent requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            # Send multiple requests concurrently
            futures = [executor.submit(self.make_request) for _ in range(num_requests)]

            # Collect the responses
            results = [future.result() for future in futures]
            #print(results)
            # To store all tracking numbers
            tracking_numbers = set()
            for response in results:
                self.assertEqual(response.status_code, 200)
                data = response.json()
                #print(data)
                self.assertIn("tracking_number", data)
                self.assertIn("created_at", data)
                # Ensure tracking number matches regex pattern
                self.assertRegex(data["tracking_number"], r"^[A-Z0-9]{1,16}$")
                tracking_number = data["tracking_number"]
                self.assertNotIn(tracking_number, tracking_numbers, f"Duplicate tracking number found: {tracking_number}")
                # Add the tracking number to the set
                tracking_numbers.add(tracking_number)
            # Assert that the number of tracking numbers matches the number of requests
            self.assertEqual(len(tracking_numbers), num_requests, "Tracking numbers are not unique.")

