# useful references:
# https://dadoverflow.com/2022/01/30/parsing-word-documents-with-python/
# https://docs.microsoft.com/en-us/office/open-xml/structure-of-a-wordprocessingml-document
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from bloom_filter2 import BloomFilter
import glob
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def parse_file(read_file,print_stats=True):
    doc = zipfile.ZipFile(read_file).read('word/document.xml')
    root = ET.fromstring(doc)
    #print(ET.tostring(root))
    card_list = [] # each entry contains tuple with list of text and list of classification values as follows:
    length_error_count = 0
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
    print_bad_card = False
    card_text = ''
    card_emphs = []
    
    for p in p_sections:
        in_tag = is_tag(p)
        in_header = is_header(p)
        in_cite = is_cite(p)
        if in_tag: # saves current card to list, resets list
            tag_flag = True
            in_card = False
            # adds the card or doesn't 
            card_list.append((card_text,card_emphs))
            if len(card_text.split()) != len(card_emphs):
                length_error_count+=1
                if print_bad_card:
                    #print(card_list[-1])
                    print_bad_card = False
                #print (abs(len(card_text.split()) - len(card_emphs)))
            # resets the things 
            card_text = ''
            card_emphs = []
        if in_header: # sets in_card to false, skips
            in_card = False
        if in_card and not in_cite: # adds paragraph's runs to the running talley
            prev_last_space = True
            next_first_space = False
            r_sections = p.findall('w:r',ns)
            for r in r_sections:
                sec_text = get_section_text(r)
                # stuff for across run word managment 
                if len(sec_text) !=0:
                    next_first_space = sec_text[0]==' '
                else:
                    next_first_space = True
                # text dump
                sec_text = get_section_text(r)
                for snip in sec_text:
                    card_text = card_text + snip # I think sec_text is just a string but wtv 
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
                if (not prev_last_space) and (not next_first_space):
                    if len(card_emphs) != 0:
                        if class_val < card_emphs[-1]:
                            class_val = card_emphs[-1]
                        card_emphs.pop()
                for word in word_list:
                    card_emphs.append(class_val)
                # more stuff for across run word managment 
                if len(sec_text) !=0:
                    prev_last_space = sec_text[-1]==' '
                else:
                    prev_last_space = True
            card_text = card_text + ' ' # simulates paragraph break with a space, needed for parsing stuff or everything breaks
        if in_cite and tag_flag:
            in_card = True
            tag_flag = False
    card_list.append((card_text,card_emphs)) # appends last card at end of file
    if len(card_text.split()) != len(card_emphs):
                length_error_count+=1
                if print_bad_card:
                    #print(card_list[-1])
                    print_bad_card = False
    card_list.pop(0) # gets rid of weird phantom card that gets added 
    if(print_stats):
        print('Number of length errors: ' + str(length_error_count))
        print('Total card count: ' + str(len(card_list)))
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
    heading_style_elem_one = p.find(".//w:rStyle[@w:val='Style13ptBold']", ns)
    heading_style_elem_two = p.find(".//w:rStyle[@w:val='Style12ptBold']", ns)
    heading_style_elem_three = p.find(".//w:rStyle[@w:val='Style11ptBold']", ns)
    if heading_style_elem_one is not None:
        return_val = True
    if heading_style_elem_two is not None:
        return_val = True
    if heading_style_elem_three is not None:
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
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    # thanks to Greenstick on StackOverflow for the method 
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
def parse_card_dump(print_file_names = False):
    # set up stuff 
    length_error_count = 0
    valid_card_count = 0
    repeated_card_count = 0
    card_list = []
    bloom = BloomFilter(max_elements=10000, error_rate=0.001)
    #bloom.add("test-key")
    #assert "test-key" in bloom
    word_doc_list = glob.glob('*.docx')
    total_docs = len(word_doc_list)
    current_doc = 0
    for card_file in word_doc_list:
        current_doc+=1
        printProgressBar(current_doc,total_docs)
        if(print_file_names):
            print(card_file)
        try:
            temp_card_list = parse_file(card_file,print_stats=False)
        finally:
            for card_tuple in temp_card_list:
                if len(card_tuple[0].split()) != len(card_tuple[1]):
                    length_error_count+=1
                else:
                    if not card_tuple[0] in bloom:
                        card_list.append(card_tuple)
                        valid_card_count+=1
                        bloom.add(card_tuple[0])
                    else:
                        repeated_card_count+=1
    np.save('training_data',card_list)
    print('Total Valid Cards: ' + str(valid_card_count))
    print('Total Invalid Cards: ' + str(length_error_count))
    print('Total Repeated Cards: ' + str(repeated_card_count))
    #stuff = np.load(test_doc + '.npy',allow_pickle=True)


parse_card_dump()