# extracting-eBay-categories-products-items-using-eBay-API-in-Python
# The code is used to extract first the categories from eBay, then products of those categories and finally the items completed for the products
# Microsoft sql server is used to store the data

import category, product, item
from xml.etree import ElementTree as et
import io
import pypyodbc

# Run once to get categories
def main_categories():
         
        #categorie and sub-category       
        category_levels = 2   
        # Get all categories
        categories = category.get_api(category_levels)
        # Find out which ones are category enabled
        i = 0
        for cat in categories:
            i = i + 1
            if cat.category_level == 2: #We only interested in sub categories
                print(i)
                products = product.get_api(cat.category_id, page_number=1)
                if products is not None:
                    cat.category_enabled = True
        
        
            connection = pypyodbc.connect('DRIVER={SQL Server};''SERVER=DESKTOP-O6RSVA3\SQLEXPRESS;''DATABASE=ebay;')
            cursor = connection.cursor()
            for categoryy in categories:
                       cursor.execute(categoryy.to_sql_insert_script())
            connection.commit()
            connection.close()
        
            return categories
 # Run once

def main_products():
    
    
    category_ids = category.get_from_db()
    
    for category_id in category_ids:
        category_id = category_id[0]
        for page_number in range(1,11):
            products = product.get_api(category_id, page_number)
            
            if products is None:
                break
            
            
            #Save to db
            connection = pypyodbc.connect('DRIVER={SQL Server};''SERVER=DESKTOP-O6RSVA3\SQLEXPRESS;''DATABASE=ebay;')
            cursor = connection.cursor()
            for productt in products:
                cursor.execute(productt.to_sql_insert_script())
            connection.commit()
            connection.close()
            
            if len(products) < 20:
                break      
        
def main_items():        
      
    product_ids = product.get_from_db()
    
    for product_id in product_ids:
        product_id = product_id[0]
        for page_number in range(1,21):
            items = item.get_api(product_id, page_number, item_completed = True)
            
            if items is None:
                break
            
            
            #Save to db
            connection = pypyodbc.connect('DRIVER={SQL Server};''SERVER=DESKTOP-O6RSVA3\SQLEXPRESS;''DATABASE=ebay;')
            cursor = connection.cursor()
            for itemm in items:
                cursor.execute(itemm.to_sql_insert_script())
            connection.commit()
            connection.close()
            
            if len(items) < 100:
                break      
