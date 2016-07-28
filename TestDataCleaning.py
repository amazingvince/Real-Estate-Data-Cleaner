import unittest
from pandas import DataFrame
from RealEstateDataCleaning import add_upper_and_main

class TestDataCleaning(unittest.TestCase):

    def check_room_count(self, frame, pk, expected):
        row = frame.loc[pk]

        # check that the two are added correctly
        self.assertEqual(expected, row['Hallways'], "Wrong value for 'Hallways' in row {}".format(pk))

        # also ensure that kitchens were unaffected
        self.assertEqual(1, row['MainKitchens'], "Wrong value for 'MainKitchens' in row {}".format(pk))

    def test_add_upper_and_main(self):
        data = {
            'MainHallways': [0, 1, 1],
            'UpperHallways': [0, 0, 1],
            'MainKitchens': [1, 1, 1]
        }

        frame = DataFrame(data, index=[0, 1, 2])
        add_upper_and_main(frame, 'Hallways')

        # should have 'Hallways', but no 'Main' or 'UpperHallways'
        self.assertIsNotNone(frame.get('Hallways', None), "'Hallways' should exist")
        self.assertIsNone(frame.get('MainHallways', None), "'MainHallways' should not exist")
        self.assertIsNone(frame.get('UpperHallways', None), "'UpperHallways' should not exist")

        self.check_room_count(frame, pk=0, expected=0)
        self.check_room_count(frame, pk=1, expected=1)
        self.check_room_count(frame, pk=2, expected=2)

