# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 17:34:10 2016

@author: Husayn
"""

from xml.etree import ElementTree as et
import api
import utilities
import settings
import sys
import pypyodbc

def create_request(number_of_levels):
    
    root = et.Element('GetCategoriesRequest')
    root.attrib['xmlns'] = 'urn:ebay:apis:eBLBaseComponents'
    
    
    child = et.SubElement(root, 'RequesterCredentials')
    child2 = et.SubElement(child, 'eBayAuthToken')
    child2.text = settings.TOKEN
    
    child = et.SubElement(root, 'DetailLevel')
    child.text = 'ReturnAll'
    
    child = et.SubElement(root, 'LevelLimit')
    child.text = str(number_of_levels)
    
    return root
    
# http://developer.ebay.com/devzone/xml/docs/reference/ebay/GetCategories.html
def get_api(number_of_levels):
    
    print('Starting GetCategories api call.')    
    print('  Building xml request arguments, with number of levels ' 
            + str(number_of_levels) + '.')
            
    xml_request = create_request(number_of_levels)

    xml_response = api.get_response_trading_api('GetCategories', xml_request) 

    print('  Checking for response errors.')
    
    # Check if error
    if xml_response.find('Ack').text != 'Success':
        print('  API request returned error. Look in files for more detail.')
        return None
    
    api_timestamp = xml_response.find('Timestamp').text
    xml_category_array = xml_response.find('CategoryArray').findall('Category')
    
    print('  ' + str(len(xml_category_array)) + ' search results returned. Parsing data.')
    
    categories = []
    for xml_category in xml_category_array:
        try:
            categories.append(Category(api_timestamp, xml_category))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
            
    print('Exiting GetCategories api call sucessfully.')
    
    return categories

    
def get_from_db():
    connection = pypyodbc.connect('DRIVER={SQL Server};''SERVER=DESKTOP-O6RSVA3\SQLEXPRESS;''DATABASE=ebay;')
    cursor = connection.cursor()
    sql_command = "select category_id from Categories where category_enabled = 'True' "
    cursor.execute(sql_command)
    category_ids = cursor.fetchall()
    
    connection.close()
    
    print('Categories containing products found')
    
    return category_ids
    

class Category:
    
    def __init__(self, api_timestamp, xml):
        self.api_timestamp = api_timestamp
        self.best_offer_enabled = utilities.get_value(bool, xml, 'BestOfferEnabled', True)
        self.auto_pay_enabled = utilities.get_value(bool, xml, 'AutoPayEnabled', True)
        self.category_id = utilities.get_value(int, xml, 'CategoryID', False)
        self.category_level = utilities.get_value(int, xml, 'CategoryLevel', False)
        self.category_name = utilities.get_value(str, xml, 'CategoryName', False)
        self.category_parent_id = utilities.get_value(int, xml, 'CategoryParentID', False)
        self.category_enabled = False
        
    def to_string(self):
        return "{0}\t{1}\t{2}\t{3}".format(self.category_id, self.category_level, self.category_name, self.category_parent_id)
        
    def to_sql_insert_script(self):
        return """INSERT INTO Categories (api_timestamp, best_offer_enabled, auto_pay_enabled,
                                                   category_id, category_level, category_name, category_parent_id, category_enabled)
                  VALUES('{0}',{1},{2},{3},{4},'{5}',{6},'{7}')""".format(self.api_timestamp
                  , 1 if self.best_offer_enabled == True else 0
                  , 1 if self.auto_pay_enabled == True else 0
                  , self.category_id
                  , self.category_level
                  , self.category_name.replace("'","''") 
                  , self.category_parent_id
                  , self.category_enabled)
    

    