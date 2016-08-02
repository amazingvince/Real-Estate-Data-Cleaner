"""This script takes in real estate data and cleans it up for regression analysis

Todo:
    *Build a column with the S&P/Case-Shiller National Home Price Index value
    *Build a column with inflation adjustment for ClosingPrice
"""

import pandas as pd
import numpy as np
import argparse

features = {'Exterior' : ['Porch','Patio','Deck','Fenced','Out-Building'],
            'BasementDesc' : ['Crawl Space','Slab', 'Basement'],
            'ParkingDesc' : ['Driveway','Carport', '1 Car Garage', '2 Car Garage', '3 Car Garage'],
            'Stories' : ['1 Story', '2 Story', 'More'] }

address_pieces = ['StreetNumber', 'StreetName', 'City', 'CountyOrParish',
                    'StateOrProvince', 'PostalCode']

def make_YearBuilt_bins(data_frame, size):
    """Divides YearBuilt into bins and creates new column named YearBuiltBins

    Args:
        data_frame (pandas DataFrame): The DataFrame to make bins on
        size (int): The size of each bin

    Returns:
        pandas DataFrame: with an additional column named YearBuiltBins
    """
    oldest_house = data_frame['YearBuilt'].min()
    newest_house = data_frame['YearBuilt'].max()
    # I meant to do this the first time list comp SO much cleaner
    bins = [year for year in range(oldest_house, newest_house+size, size)] 
    data_frame['YearBuiltBins'] = pd.cut(data_frame['YearBuilt'], bins)


def concatenate_address(data_frame, address_pieces):
    """Takes all pieces of address and concatenates them into a unique key column named Address

    Args:
        data_frame (pandas DataFrame): The DataFrame to concatenate address on

    Returns:
        pandas DataFrame: with an additional column named Address
    """

    data_frame['Address'] = data_frame[address_pieces].apply(lambda x: ' '.join(x.map(str)), axis=1)
    data_frame.drop(address_pieces, axis=1, inplace=True)

def Basement_cleanup(x):
    # Recodes BasementDesc into three categories mapped onto a DataFrame

    x = str(x)
    if 'Crawl Space' in x:
        return 'Crawl Space'
    elif 'Slab' in x:
        return 'Slab'
    else:
        return 'Basement'

def Stories_cleanup(x):
    # Recodes Stories into three categories mapped onto a DataFrame

    x = str(x)
    if '+' in x:
        return 'More'
    elif '1 Story' in x:
        return '1 Story'
    else:
        return '2 Story'

def extract_dummies(data_frame,features):
    """
    Takes a dictionary of columns to features and maps over those columns and makes a column for each phrase in that list
    it places a 1 in that column if that phrase is present in the description else it places a 0

    Args:
        data_frame (pandas DataFrame): The DataFrame containing the descriptions
        features (dic): Key = Column name value = list of phrases that are being looked for in descriptions

    Returns:
        None
    """

    def extract_col(col):
        for feature in features[col]:
            data_frame[feature] = np.where((data_frame[col].str.contains(feature)),1,0)
        data_frame.drop([col], axis=1, inplace=True)
    
    map(extract_col,features)

def add_upper_and_main(data_frame, desired):
    """
    Look for the "Upper" and "Main" values for the desired column.  Sum these together and
    create a new column named desired.  Finally, remove the "Upper" and "Main" columns

    e.g. "Bedrooms" is the sum of the "UpperBedrooms" and "MainBedrooms" values

    :param data_frame: callback frame object to manipulate
    :param desired: string denoting the desired domain
    :return: None
    """
    upper = "Upper{}".format(desired)
    main = "Main{}".format(desired)

    data_frame[desired] = data_frame[upper] + data_frame[main]

    data_frame.drop([upper, main], axis=1, inplace=True)

def main(data_frame):

    data_frame.drop(data_frame[data_frame.SqFtTotal == 0].index, inplace=True)
    data_frame['CloseDate'] = pd.to_datetime(data_frame['CloseDate'])
    concatenate_address(data_frame, address_pieces)
    
    data_frame['BasementDesc'] = data_frame['BasementDesc'].apply(Basement_cleanup)
    data_frame['Stories'] = data_frame['Stories'].apply(Stories_cleanup)
    extract_dummies(data_frame,features)

    # some whitespace will help in this method :)
    make_YearBuilt_bins(data_frame, size=10)
    data_frame['Year'] = pd.DatetimeIndex(data_frame['CloseDate']).year
    data_frame['Age'] = data_frame['Year'] - data_frame['YearBuilt']
    data_frame['AssociationFee'] = np.where((data_frame['AssociationFee']> 0),1,0)
    data_frame['PoolonProperty'] = np.where((data_frame['PoolonProperty'] !=  'None'),1,0)


    for domain in ['Bedrooms', 'FullBaths', 'HalfBaths']:
        add_upper_and_main(data_frame, domain)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="the path to the csv file to clean",
                    type=str)
    args = parser.parse_args()
    input_file = args.input_file  #'Candler Park.csv'
    output_file = 'Cleaned_'+input_file
    data_frame = pd.read_csv(input_file)
    main(data_frame)
    data_frame.to_csv(output_file)

