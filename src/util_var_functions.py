
import re







def extract_name_parts(name):
    template = {
            'parent_path': '',
            'field_name': '',
            'category_name': None,
            'parent_first': '',
            'parent_rest': '',
        }
    pattern_root_item = r'^\s*?$'
    pattern_category_part = r'^\s*(.*?)\s*?\.(?:categories|elements)\s*?\[\s*?\{?\s*(.*?)\s*\}?\s*\]\s*?$'
    def process_root_item():
        name_parts = {
            **template,
            'field_name': '',
        }
        return name_parts
    def process_category_item(matches):
        name_parts = extract_name_parts(matches[1])
        if name_parts['category_name']:
            name_parts = extract_name_parts(re.sub(r'^\s*(.*?)\s*?\[\s*?\{?\s*(.*?)\s*\}?\s*\]\s*?$',lambda m: m[1],matches[1],flags=re.I|re.DOTALL))
        _, name_parts['category_name'] = extract_field_name(matches[2])
        return name_parts
    def process_variable_item(name):
        name_parts = {
            **template
        }
        name = re.sub(r'^\s*?\.+','',re.sub(r'\.+\s*?$','',name,flags=re.I|re.DOTALL),flags=re.I|re.DOTALL)
        name = re.sub(r'\s','',name,flags=re.I|re.DOTALL)
        name = re.sub(r'\[\s*?\{?\s*?(?:\.{2}|(?:\s*?(?:(?:\w+\.)*?\w+)(?:\s*?,\s*?(?:\w+\.)*?\w+)*\s*?))\s*?\}?\s*?\]','',name,flags=re.I|re.DOTALL)
        name_part_list = name.split('.')
        name_parts['field_name'] = '.'.join(name_part_list[-1:])
        name_parts['parent_path'] = '.'.join(name_part_list[:-1])
        name_parts['parent_first'] = '.'.join(name_part_list[:1])
        name_parts['parent_rest'] = '.'.join(name_part_list[1:])
        return name_parts
    matches = re.match(pattern_root_item,name,flags=re.I|re.DOTALL)
    if matches:
        return process_root_item()
    matches = re.match(pattern_category_part,name,flags=re.I|re.DOTALL)
    if matches:
        return process_category_item(matches)
    return process_variable_item(name)


def sanitize_item_name(name):
    name_parts = extract_name_parts(name)
    if not name_parts['field_name']:
        return ''
    elif name_parts['category_name'] is not None:
        result = '{path}{sep}{field_name}.categories[{cat_name}]'.format(path=name_parts['parent_path'],sep='.' if name_parts['parent_path'] else '',field_name=name_parts['field_name'],cat_name=name_parts['category_name'])
        return result.lower()
    else:
        result = '{path}{sep}{field_name}'.format(path=name_parts['parent_path'],sep='.' if name_parts['parent_path'] else '',field_name=name_parts['field_name'])
        return result.lower()

def detect_item_type(name):
    name_parts = extract_name_parts(name)
    if not name_parts['field_name']:
        return 'root'
    elif name_parts['category_name'] is not None:
        return 'category'
    else:
        return 'variable'

def extract_field_name(name):
    name_parts = extract_name_parts(name)
    return '{path}'.format(path=name_parts['parent_path']), '{field_name}'.format(field_name=name_parts['field_name'])

def extract_parent_name(name):
    name_parts = extract_name_parts(name)
    return '{f}'.format(f=name_parts['parent_first']), '{f}'.format(f=name_parts['parent_rest'])

def extract_category_name(name):
    name_parts = extract_name_parts(name)
    return '{path}{sep}{field_name}'.format(path=name_parts['parent_path'],sep='.' if name_parts['parent_path'] else '',field_name=name_parts['field_name']), '{cat_name}'.format(cat_name=name_parts['category_name'])




