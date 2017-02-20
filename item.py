# -*- coding: utf-8 -*-
"""
Created on Sat Aug 13 17:34:10 2016

@author: Husayn
"""

from xml.etree import ElementTree as et
import sys
from utilities import get_value, get_values, get_attribute_value
import api

def create_request(product_id, page_number, item_completed):
    
    if item_completed==True:
        root = et.Element('findCompletedItemsRequest')
    else:
        root = et.Element('findItemsByProductRequest')
        
    root.attrib['xmlns'] = 'http://www.ebay.com/marketplace/search/v1/services'
    
    child = et.SubElement(root, 'sortOrder')
    child.text = 'EndTimeSoonest'
    
    child = et.SubElement(root, 'productId')
    child.text = str(product_id)
    child.attrib['type'] = 'ReferenceID'
    
    child = et.SubElement(root, 'paginationInput')
    child2 = et.SubElement(child, 'entriesPerPage')
    child2.text = '100'
    child3 = et.SubElement(child, 'pageNumber')
    child3.text = str(page_number)
    
    return root

# http://developer.ebay.com/devzone/xml/docs/reference/ebay/GetCategories.html
def get_api(product_id, page_number, item_completed):
    
    if item_completed == True:
        print('Starting FindItems completed api call.')
    else:
        print('Starting FindItems active api call.')
    print('  Building xml request arguments, with product id ' 
            + str(product_id) + ' and pg number ' + str(page_number) + '.')
    
    xml_request = create_request(product_id, page_number, item_completed)
    
    if item_completed == True:
        xml_response = api.get_response_finding_api('findCompletedItems', xml_request) 
    else:
        xml_response = api.get_response_finding_api('findItemsByProduct', xml_request) 
    
    print('  Checking for response errors.')
    
    # Check if error
    if xml_response.find('ack').text != 'Success':
        print('  API request returned error. Look in files for more detail.')
        return None
    
    api_timestamp = xml_response.find('timestamp').text
    xml_item_array = xml_response.find('searchResult').findall('item')

    print('  ' + str(len(xml_item_array)) + ' search results returned. Parsing data.')

    items = []    
    for xml_item in xml_item_array:
        try:
            items.append(Item(api_timestamp, xml_item))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
            
    print('Exiting FindItems api call sucessfully.')
    
    return items

def get_db(number_of_levels):
    pass

class Item:
    
    def __init__(self, api_timestamp, xml):
        self.api_timestamp = api_timestamp
        
        self.item_id = get_value(int, xml, 'itemId', False)
        self.title = get_value(str, xml, 'title', False)
        self.subtitle = get_value(str, xml, 'subtitle', True)
        self.global_id = get_value(str, xml, 'globalId', False)       
        self.category_id = get_value(int, xml, 'primaryCategory/categoryId', False)
        self.category_name = get_value(str, xml, 'primaryCategory/categoryName', False)
        self.gallery_url = get_value(str, xml, 'galleryURL', True)
        self.view_item_url = get_value(str, xml, 'viewItemURL', True)
        self.product_id = get_value(int, xml, 'productId[@type="ReferenceID"]', False)
        
        # Payment Info
        self.pi_payment_method = get_values(xml, 'paymentMethod', True)        
        self.pi_auto_pay = get_value(bool, xml, 'autoPay', True)
        self.pi_postal_code = get_value(str, xml, 'postalCode', True)
        self.pi_location = get_value(str, xml, 'location', True)  
        self.pi_country = get_value(str, xml, 'country', True)
        
        # Shipping Info
        self.si_shipping_service_cost = get_value(float, xml, 'shippingInfo/shippingServiceCost', True)        
        self.si_shipping_service_cost_currency_id = get_attribute_value(str, xml, 'shippingInfo/shippingServiceCost','currencyId', True)        
        self.si_shipping_type = get_value(str, xml, 'shippingInfo/shippingType', True)        
        self.si_ship_to_locations = get_values(xml, 'shippingInfo/shipToLocations', True)        
        self.si_expedited_shipping = get_value(bool, xml, 'shippingInfo/expeditedShipping', True)
        self.si_one_day_shipping_available = get_value(bool, xml, 'shippingInfo/oneDayShippingAvailable', True)
        self.si_handling_time = get_value(int, xml, 'shippingInfo/handlingTime', True)
        
        # Selling Status
        self.ss_current_price = get_value(float, xml, 'sellingStatus/currentPrice', True)
        self.ss_current_price_currency_id = get_attribute_value(str, xml, 'sellingStatus/currentPrice', 'currencyId', True)
        self.ss_converted_current_price = get_value(float, xml, 'sellingStatus/convertedCurrentPrice', True)
        self.ss_converted_current_price_currency_id = get_attribute_value(str, xml, 'sellingStatus/convertedCurrentPrice', 'currencyId', True)
        self.ss_bid_count = get_value(int, xml, 'sellingStatus/bidCount', True)
        self.ss_selling_state = get_value(str, xml, 'sellingStatus/sellingState', True)
        self.ss_time_left = get_value(str, xml, 'sellingStatus/timeLeft', True)
        
        # Listing Info
        self.li_best_offer_enabled = get_value(bool, xml, 'listingInfo/bestOfferEnabled', True)
        self.li_buy_it_now_available = get_value(bool, xml, 'listingInfo/buyItNowAvailable', True)
        self.li_buy_it_now_price = get_value(float, xml, 'listingInfo/buyItNowPrice', True)
        self.li_buy_it_now_price_currency_id = get_attribute_value(str, xml, 'listingInfo/buyItNowPrice', 'currencyId', True)
        self.li_converted_buy_it_now_price = get_value(float, xml, 'listingInfo/convertedBuyItNowPrice', True)
        self.li_converted_buy_it_now_price_currency_id = get_attribute_value(str, xml, 'listingInfo/convertedBuyItNowPrice', 'currencyId', True)
        self.li_start_time = get_value(str, xml, 'listingInfo/startTime', True)
        self.li_end_time = get_value(str, xml, 'listingInfo/endTime', True)
        self.li_listing_type = get_value(str, xml, 'listingInfo/listingType', True)
        self.li_gift = get_value(str, xml, 'listingInfo/gift', True)
        
        # Other stuff
        self.returns_accepted = get_value(str, xml, 'returnsAccepted', True)
        self.condition_id = get_value(int, xml, 'condition/conditionId', True)
        self.condition_display_name = get_value(str, xml, 'condition/conditionDisplayName', True)
        self.is_multi_variation_listing = get_value(bool, xml, 'isMultiVariationListing', True)
        self.top_rated_listing = get_value(bool, xml, 'topRatedListing', True)
        
    def to_string(self):
        return "{0}\t{1}\t{2}\t{3}\t{4}".format(self.product_id, self.item_id, self.title, self.pi_country, self.ss_current_price)
        
    def to_sql_insert_script(self):
        return """INSERT INTO Items (api_timestamp, item_id, title, category_id, category_name, gallery_url, 
                                     view_item_url, product_id, pi_payment_method, pi_auto_pay, pi_postal_code, pi_location, 
                                     pi_country, si_shipping_service_cost, si_shipping_type, ss_current_price, ss_bid_count,
                                     ss_selling_state, li_best_offer_enabled, li_buy_it_now_available, li_buy_it_now_price, 
                                     li_start_time, li_end_time, li_listing_type, li_gift,condition_id, condition_display_name,
                                     is_multi_variation_listing, top_rated_listing) 
                                     VALUES('{0}',{1},'{2}',{3},'{4}','{5}','{6}',{7},'{8}','{9}','{10}','{11}','{12}',{13},'{14}',{15},{16},'{17}',
                                     '{18}','{19}',{20},'{21}','{22}','{23}','{24}',{25},'{26}','{27}','{28}')""".format(self.api_timestamp,
                                     self.item_id,
                                     self.title.replace("'","''"),
                                     self.category_id,
                                     self.category_name.replace("'","''"),
                                     'null' if self.gallery_url is None else self.gallery_url,
                                     self.view_item_url,
                                     self.product_id,
                                     'null' if self.pi_payment_method is None else self.pi_payment_method ,
                                     'null' if self.pi_auto_pay is None else self.pi_auto_pay,
                                     'null' if self.pi_postal_code is None else self.pi_postal_code ,
                                     'null' if self.pi_location.replace("'","''") is None else self.pi_location.replace("'","''") ,
                                     'null' if self.pi_country is None else self.pi_country,
                                     'null' if self.si_shipping_service_cost is None else self.si_shipping_service_cost,
                                     'null' if self.si_shipping_type is None else self.si_shipping_type,
                                     'null' if self.ss_current_price is None else self.ss_current_price,
                                     'null' if self.ss_bid_count is None else self.ss_bid_count,
                                     'null' if self.ss_selling_state is None else self.ss_selling_state,
                                     'null' if self.li_best_offer_enabled is None else self.li_best_offer_enabled, 
                                     'null' if self.li_buy_it_now_available is None else self.li_buy_it_now_available,
                                     'null' if self.li_buy_it_now_price is None else self.li_buy_it_now_price,
                                     'null' if self.li_start_time is None else self.li_start_time ,
                                     'null' if self.li_end_time is None else self.li_end_time,
                                     'null' if self.li_listing_type is None else self.li_listing_type,
                                     'null' if self.li_gift is None else self.li_gift,
                                     'null' if self.condition_id is None else self.condition_id,
                                     'null' if self.condition_display_name is None else self.condition_display_name,
                                     'null' if self.is_multi_variation_listing is None else self.is_multi_variation_listing,
                                     'null' if self.top_rated_listing is None else self.top_rated_listing)
                                     
                                     
                    
  