import xml.dom.minidom
import io
    
def format_xml(xml_str):
    xml_dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_str = xml_dom.toprettyxml()
    return pretty_xml_str
    
def save_xml_to_file(path, xml_str):
    xml_file = io.open(path, 'w', encoding='utf-8')
    xml_str_formatted = format_xml(xml_str)
    xml_file.write(xml_str_formatted)
    xml_file.close()
    return xml_str_formatted
 
def get_value(convert, xml_element, name, ignore_null):
    
    if xml_element.find(name) is not None:
        return convert(xml_element.find(name).text)
    
    if ignore_null == True:     
        return None
    else:
        raise ValueError(name + ' not found.')
        
def get_values(xml_element, name, ignore_null):
    
    values = xml_element.findall(name)
    
    if values == []:
        if ignore_null == True:
            return None
        else:
            raise ValueError(name + ' not found.')
    else:
        return ";".join([value.text for value in values])

def get_attribute_value(convert, xml_element, name, attribute_name, ignore_null):
    
    if xml_element.find(name) is not None:
        if attribute_name in xml_element.find(name).attrib:
            return convert(xml_element.find(name).attrib[attribute_name])

    if ignore_null == True:
        return None
    else:
        raise ValueError(name + ' not found.')

        
        
        

