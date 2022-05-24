import zipfile
import xml.etree.ElementTree as ET
import numpy as np
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def parse_file(filename):
    doc = zipfile.ZipFile(filename).read('word/document.xml')
    root = ET.fromstring(doc)
    #print(ET.tostring(root))
    card_list = [] # each entry contains tuple with list of text and list of classification values as follows:
    # 0 - normal ununderlined text
    # 1 - underlined text
    # 2 - emphasis text
    # 3 - highlighted and underlined text
    # 4 - bolded and highlighted and underlined text
    # those two lists should be the same length! for obvious reasons 
    body = root.find('w:body', ns)  # find the XML "body" tag
    p_sections = body.findall('w:p', ns)  # under the body tag, 
    in_card = False
    tag_flag = False
    card_text = ''
    card_emphs = []
    for p in p_sections:
        if is_tag(p):
            tag_flag = True
            in_card = False
            card_list.append((card_text,0))
            card_text = ''
        if in_card and not is_cite(p):
            r_sections = p.findall('w:r',ns)
            for r in r_sections:
                for snip in get_section_text(r):
                    card_text = card_text + snip
        if tag_flag:
            in_card = True
            tag_flag = False
    card_list.append((card_text,0))
    return card_list
def is_tag(p):
    """Returns True if the given paragraph section has been styled as a Tag"""
    return_val = False
    heading_style_elem = p.find(".//w:pStyle[@w:val='Heading4']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_pocket(p):
    return_val = False
    heading_style_elem = p.find(".//w:pStyle[@w:val='Heading1']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_hat(p):
    return_val = False
    heading_style_elem = p.find(".//w:pStyle[@w:val='Heading2']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_block(p):
    return_val = False
    heading_style_elem = p.find(".//w:pStyle[@w:val='Heading3']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_cite(p):
    return_val = False
    heading_style_elem = p.find(".//w:rStyle[@w:val='Style13ptBold']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_underline(r):
    return_val = False
    heading_style_elem = r.find("w:val=\"StyleUnderline\"", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
 
def get_section_text(p):
    """Returns the joined text of the text elements under the given paragraph tag"""
    return_val = ''
    text_elems = p.findall('.//w:t', ns)
    if text_elems is not None:
        return_val = ''.join([t.text for t in text_elems])
    return return_val
#stuff = parse_file('verb_ex.docx')
#stuff = np.array(parse_file('Q_Impact_Turn_Master_File.docx'))
#np.save('impact_text',stuff)
#print('done')
max_length = 0
index = 0
stuff = np.load('impact_text.npy')
for i,card in enumerate(stuff):
    length = len(card[0])
    if length > max_length:
        index = i
        max_length = length
print(max_length)
print(stuff[index])