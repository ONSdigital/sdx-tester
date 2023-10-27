import json
import unittest

from scripts.v1_to_v2.convert_v1_to_v2 import transform_v1_to_v2


class TestTransform(unittest.TestCase):

	def test_transform_v1_to_v2(self):
		# Load mock v1 data from a file
		with open('v1.example.json', 'r') as file:
			mock_v1 = json.load(file)

		# Load expected v2 data from a file
		with open('v2.expected.json', 'r') as file:
			expected_v2 = json.load(file)

		transformed_data = transform_v1_to_v2(mock_v1)

		print("\n")
		print(transformed_data)
		self.assertEqual(expected_v2, transformed_data)
