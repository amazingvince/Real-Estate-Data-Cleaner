import unittest
from pandas import DataFrame
from RealEstateDataCleaning import add_upper_and_main
from RealEstateDataCleaning import extract_dummies

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

    def check_dummy_columns(self, frame, pk, dumy_cols):
        row = frame.loc[pk]

        # Check if the right value was placed in each column
        for col in frame.columns:
            if col in dumy_cols:
                self.assertEqual(1, row[col], "Wrong value for '{}' in row {}".format(col, pk))
            else:
                self.assertEqual(0, row[col], "Wrong value for '{}' in row {}".format(col, pk))

    
    def test_extract_dummies(self):
        features = {
            'StoveDesc' : ['Gas','Electric','Range'],
            'BasementDesc' : ['Crawl Space','Slab', 'Basement', 'Floating'],
            'Stories' : ['1 Story', '2 Story', 'More'] 
        }

        data = {
            'StoveDesc': ['Gas','Electric','Gas Range'],
            'BasementDesc': ['Crawl Space','Slab', 'Basement'],
            'Stories': ['More', '1 Story', '2 Story'],
            'OtherStuff' : [1, 1, 1]
        }
        
        frame = DataFrame(data, index=[0, 1, 2])
        extract_dummies(frame, features)

        # should only effect columns in feature leaving other columns untouched
        self.assertIsNotNone(frame.get('OtherStuff', None), "'OtherStuff' should exist")

        # should have removed columns named in features
        for col in features:
            self.assertIsNone(frame.get(col, None), "{} should not exist".format(col))

        # should have a column for each item in the features in 
        for col in features:    
            for feature in features[col]:
                self.assertIsNotNone(frame.get(feature, None), "{} should exist".format(feature))

        self.check_dummy_columns(frame, pk=0, dumy_cols=['Crawl Space', 'More', 'Gas', 'OtherStuff'])
        self.check_dummy_columns(frame, pk=1, dumy_cols=['Slab', '1 Story', 'Electric','OtherStuff'])
        self.check_dummy_columns(frame, pk=2, dumy_cols=['Basement', '2 Story', 'Gas', 'Range', 'OtherStuff'])

if __name__ == '__main__':
    unittest.main()