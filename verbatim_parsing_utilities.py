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
        in_tag = is_tag(p)
        in_header = is_header(p)
        in_cite = is_cite(p)
        if in_tag:
            tag_flag = True
            in_card = False
            card_list.append((card_text,card_emphs))
            if len(card_text.split()) != len(card_emphs):
                print('Length error thing reee')
            # resets the things 
            card_text = ''
            card_emphs = []
        if in_header:
            in_card = False
        if in_card and not in_cite:
            # text dump
            r_sections = p.findall('w:r',ns)
            for r in r_sections:
                # text dump
                sec_text = get_section_text(r)
                for snip in sec_text:
                    card_text = card_text + snip
                # classification symbol dump
                class_val = 0
                is_high = is_highlight(r)
                is_under = is_underline(r)
                is_bold = is_emph(r)
                if is_under:
                    class_val+=1
                if is_high:
                    class_val+=2
                if is_bold:
                    class_val+=2
                word_list = sec_text.split()
                for word in word_list:
                    card_emphs.append(class_val)

        if tag_flag:
            in_card = True
            tag_flag = False
    card_list.append((card_text,card_emphs))
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
def is_header(p):
    return is_block(p) or is_hat(p) or is_pocket(p)
def is_underline(r):
    return_val = False
    #heading_style_elem = r.find("w:val=\"StyleUnderline\"", ns)
    heading_style_elem = r.find(".//w:rStyle[@w:val='StyleUnderline']", ns)
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_highlight(r):
    return_val = False
    heading_style_elem = r.find(".//w:highlight", ns) #TODO fixed?
    if heading_style_elem is not None:
        return_val = True
    return return_val
def is_emph(r):
    return_val = False
    #heading_style_elem = r.find("w:val=\"Emphasis\"", ns)
    heading_style_elem = r.find(".//w:rStyle[@w:val='Emphasis']", ns)
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
stuff = parse_file('verb_ex_two.docx')

np.save('verb_ex_two',stuff)

stuff = np.load('verb_ex_two.npy',allow_pickle=True)
#print(len(stuff))
#print(stuff)

# TODO add thing later to delete first phantom entry 