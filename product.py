# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 17:34:10 2016

@author: Husayn
"""

from xml.etree import ElementTree as et
import api, utilities
import sys
import pypyodbc


def create_request(category_id, page_number):
    
    root = et.Element('FindProductsRequest')
    root.attrib['xmlns'] = 'urn:ebay:apis:eBLBaseComponents'
    
    child = et.SubElement(root, 'AvailableItemsOnly')
    child.text = 'true'
    
    child = et.SubElement(root, 'MaxEntries')
    child.text = '20'
    
    child = et.SubElement(root, 'PageNumber')
    child.text = str(page_number)
    
    child = et.SubElement(root, 'CategoryID')
    child.text = str(category_id)
    
    return root
    
# http://developer.ebay.com/devzone/xml/docs/reference/ebay/GetCategories.html
def get_api(category_id, page_number):
    
    print('Starting FindProducts api call.')    
    print('  Building xml request arguments, with category id ' 
            + str(category_id) + ' and pg number ' + str(page_number) + '.')
            
    xml_request = create_request(category_id, page_number)

    xml_response = api.get_response_shopping_api('FindProducts', xml_request) 
    
    print('  Checking for response errors.')
    
    # Check if error
    if xml_response.find('Ack').text != 'Success':
        print('  API request returned error. Look in files for more detail.')
        return None
    
    api_timestamp = xml_response.find('Timestamp').text
    xml_product_array = xml_response.findall('Product')

    print('  ' + str(len(xml_product_array)) + ' search results returned. Parsing data.')
    
    products = []
    for xml_product in xml_product_array:
        try:
            products.append(Product(api_timestamp, xml_product))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
            
    print('Exiting FindProducts api call sucessfully.')
    
    return products

def get_from_db():
    connection = pypyodbc.connect('DRIVER={SQL Server};''SERVER=DESKTOP-O6RSVA3\SQLEXPRESS;''DATABASE=ebay;')
    cursor = connection.cursor()
    sql_command = "select product_id from Products"
    cursor.execute(sql_command)
    product_ids = cursor.fetchall()
    
    connection.close()
    
    print('selected product IDs from product table')
    
    return product_ids
    

class Product:
    
    def __init__(self, api_timestamp, xml):
        self.api_timestamp = api_timestamp
        
        self.product_id = utilities.get_value(int, xml, 'ProductID[@type="Reference"]', False)
        
        self.title = utilities.get_value(str, xml, 'Title', False)
        self.review_count = utilities.get_value(int, xml, 'ReviewCount', True)
        self.domain_name = utilities.get_value(str, xml, 'DomainName', True)
        self.details_url = utilities.get_value(str, xml, 'DetailsURL', True)
        self.stock_photo_url = utilities.get_value(str, xml, 'StockPhotoURL', True)
        
    def to_string(self):
        return "{0}\t{1}\t{2}\t{3}".format(self.product_id, self.domain_name, self.review_count, self.title)
        
    
    
    
    def to_sql_insert_script(self):
        return """INSERT INTO Products (api_timestamp, product_id, title,
                                                   review_count, domain_name , details_url, stock_photo_url)
                  VALUES('{0}',{1},'{2}',{3},'{4}','{5}','{6}')""".format(self.api_timestamp
                  , self.product_id
                  , self.title.replace("'","''")
                  , self.review_count
                  , self.domain_name.replace("'","''") 
                  , self.details_url
                  , self.stock_photo_url)
        
    
    