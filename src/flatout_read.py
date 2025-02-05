

import re















class FlatoutMap:
    def __init__(self,df):
        pass

































# if __name__ == '__main__':
#     # run as a program
#     import helper_utility_performancemonitor
#     import aa_logic_replicate
# elif '.' in __name__:
#     # package
#     from . import helper_utility_performancemonitor
#     from . import aa_logic_replicate
# else:
#     # included with no parent package
#     import helper_utility_performancemonitor
#     import aa_logic_replicate




CONFIG_ANALYSISVALUE_CHECK_IF_WHOLE_ERROR = 0.0001








CONFIG_MAP_DATA_VARIABLE_FIELDS = [
	'Variable',
	'Row Type',
	'Level',
	'Type',
	'Label',
	'Label Length',
	'Categories',
	'Category Labels',
	'# Categories',
	'Attributes',
	'Properties',
	'Shared Lists',
	'Depth',
	'Response Type',
	'History Full',
	'History First',
	'History Last',
	'Explode Grid',
	'Question Type',
	'Question Role',
	'Question L2',
	'Category Names L2',
	'Category Labels L2',
	'Question L1',
	'Category Names L1',
	'Category Labels L1',
	'Question L0',
	'Category Names L0',
	'Category Labels L0',
]

CONFIG_MAP_DATA_CATEGORY_FIELDS = [
	'Variable',
	'Category',
	'Offset',
	'Type',
	'Label',
	'Label Length',
	'Attributes',
	'Properties',
]






# the idea of this function
# is to resolve some naming mismatches
# there are different ways to address items
# sometimes the "Name" is "Familiarity[..].GV"
# which is in fact more common, it seems
# maybe I should update my tools to match
# bacuse I am just using "Familiarity.GV"
# because "[..]" part is really unnecessary
# and in mdm you access objects via mdm.Fields["Familiarity"].Fields["GV"]
# so this function is just removing any "[...]" and keeps just item names separated with a dot between levels
def sanitize_map_name_to_mdd_scheme_name(s):
    return re.sub(r'(\w+)\s*?\[\s*?\{?[^\]]*?\s*?\}?\s*?\]',lambda m: '{s}'.format(s=m[1]),s,flags=re.I|re.DOTALL)

# a helper fn that makes it easier to produce combined name from parent name and field name
# I can just append parent name and field name with a dot and trim if some of the names is blank and we have a dot at the beginning or at the end
# this looks like maybe dirty, adding something unnecessary and then trimming with regex
# Grant is just leaving a dot at the end
# I don't think it's a beautiful solution either
# so I have this fn trim_dots to have names standartized - even if there is a dot at the end or not
def trim_dots(s):
    return re.sub(r'^\s*?\.','',re.sub(r'\.\s*?$','',s,flags=re.I),flags=re.I)

# make name lowercase so that we can check against dict entries case-insensitively
# this fn also trims whitespaces at the beginning and at the end, in case someone copied name from some word doc and pasted it to excel with specs, and the are some non-breakable non-visible spaces, or something like this, which is common, when people us MS Office
def sanitize_item_name(item_name):
    return re.sub(r'\s*$','',re.sub(r'^\s*','',re.sub(r'\s*([\[\{\]\}\.])\s*',lambda m:'{m}'.format(m=m[1]),item_name,flags=re.I))).lower()

# helper fn
# to make spss variable name a name
# trim whitespaces (as described above - they can be coming if specs are copied from MS Word)
# and also
# if SHortName is just a number which is supposed to be for numeric of text grids,
# in AA scheme it is also appeneded to 3 decimal places
# that's what we are doing right here, if ShortName is a number
def sanitize_shortname(s):
    def trim(s):
        if s==0:
            return trim('0')
        if not s:
            return ''
        return re.sub(r'^\s*','',re.sub(r'\s*$','',s))
    def append_zeros(s):
        if len(s)<3:
            s = '000'[0:3-len(s)] + s
        return s
    s = trim(s)
    if not s:
        return s
    s = re.sub(r'^\s*?(\d+)(?:\.0*?)?\s*?$',lambda m: append_zeros(m[1]),s,flags=re.I|re.DOTALL)
    return trim(s)

# helper fn
# similar to my other tools
# splits the name with dots and extracts the last part
def extract_field_name(item_name):
    m = re.match(r'^\s*((?:\w.*?\.)*)(\w+)\s*$',item_name,flags=re.I)
    if m:
        return re.sub(r'\s*\.\s*$','',m[1]),m[2]
    else:
        raise ValueError('Can\'t extract field name from "{s}"'.format(s=item_name))

# helper fn
# similar to my other tools
# splits the name with dots and extracts the leading part
def extract_parent_name(item_name):
    if item_name=='':
        return '', ''
    m = re.match(r'^\s*(\w+)((?:\.\w*?)+)\s*$',item_name,flags=re.I)
    if m:
        return trim_dots(m[1]), trim_dots(m[2])
    else:
        # raise ValueError('Can\'t extract field name from "{s}"'.format(s=item_name))
        return '', item_name

# helper fn
# similar to my other tools
# in items populated from mdd_read, the syntax for addressing items is
# "Variable.Categories[CategoryName]"
# so this fn helps us extract category name
def extract_category_name(item_name):
    m = re.match(r'^\s*(\w+.*?\w)\.(?:categories|elements)\s*?\[\s*?\{?\s*?(\w+)\s*?\}?\s*?\]\s*$',item_name,flags=re.I)
    if m:
        return trim_dots(m[1]), trim_dots(m[2])
    else:
        raise ValueError('Can\'t extract category name from "{s}"'.format(s=item_name))

# helper fn
# similar to my other tools
# in items populated from mdd_read, the syntax for addressing items is
# "Variable.Categories[CategoryName]"
# so this fn helps us detect if an item is a category or a variable or a root item (name='')
def detect_item_type_from_mdddata_fields_report(item_name):
    item_name_clean = sanitize_item_name(item_name)
    if re.match(r'^\s*?$',item_name_clean,flags=re.I):
        return 'blank'
    elif re.match(r'^\s*?(\w(?:[\w\[\{\]\}\.]*?\w)?)\.(?:categories|elements)\s*?\[\s*?\{?\s*?(\w+)\s*?\}?\]\s*?$',item_name_clean,flags=re.I):
        return 'category'
    elif re.match(r'^\s*?(\w(?:[\w\[\{\]\}\.]*?\w)?)\s*?$',item_name_clean,flags=re.I):
        return 'variable'
    else:
        raise ValueError('Item name is not recognized, is it a variable or a category: "{s}"'.format(s=item_name))




# the main goal - strip html tags
# I know, in python, we have better ways than just using raw regex
# but I am using the same what is used in dms scripts
# my goal is just to replicate the same logic
def sanitize_label(t):
    if t==0:
        return '0'
    if not t:
        return ''
    t = '{t}'.format(t=t)
    t = t.replace('&amp;','&')
    t = re.sub(r'<(.|\n)+?>','',t,flags=re.I|re.DOTALL)
    t = re.sub(r'^\s*','',re.sub(r'\s*$','',t,flags=re.I|re.DOTALL),flags=re.I|re.DOTALL)
    return t

def sanitize_variable_label(t):
    return sanitize_label(t)

def sanitize_category_label(t):
    return sanitize_label(t)
    # t = sanitize_label(t)
    # if ',' in t:
    #     t = '\'{t}\''.format(t=t)
    # return t








# helper fn to prep propgram inputs
def get_mdd_data_records_from_input_data(inp_mdd_scheme):
    def convert_list_to_dict(data_lst):
        result = {}
        for record in data_lst:
            result[record['name']] = record['value']
        return result
    mdd_data_records = ([sect for sect in inp_mdd_scheme['sections'] if sect['name']=='fields'])[0]['content']
    mdd_data_records = [ {**q,'properties':convert_list_to_dict(q['properties'] if 'properties' in q else []),'attributes':convert_list_to_dict(q['attributes'] if 'attributes' in q else [])} for q in mdd_data_records ]
    return mdd_data_records

# helper fn to prep propgram inputs
def prepare_variable_records(mdd_data_records,mdd_data_categories,mdd_data_root):
    variable_records = {}
    # for rec in variable_specs['variables_metadata']:
    for rec in mdd_data_records:
        question_id_clean = sanitize_item_name(rec['name'])
        variable_records[question_id_clean] = rec
    for rec in mdd_data_records:
        path, _ = extract_field_name(rec['name'])
        rec['parent'] = None
        if path and not (path==''):
            variable_parent = variable_records[sanitize_item_name(path)]
            if not 'fields' in variable_parent:
                variable_parent['fields'] = []
            variable_parent['fields'].append(rec) # that's a reference, and child item should also be updated, when it receives its own fields
            rec['parent'] = variable_parent
    for cat_mdd in mdd_data_categories:
        question_name, category_name = extract_category_name(cat_mdd['name'])
        question_id_clean = sanitize_item_name(question_name)
        variable = variable_records[question_id_clean]
        if not 'categories' in variable:
            variable['categories'] = []
        variable['categories'].append({**cat_mdd,'name':category_name}) # that's not a reference, that's a copy; and name is a category name

    variable_records[''] = mdd_data_root

    mdd_data_root['fields'] = []
    for _, rec in variable_records.items():
        if not (rec['name']==''):
            parent_path, _ = extract_parent_name(rec['name'])
            if parent_path=='' or not parent_path:
                mdd_data_root['fields'].append(rec)

    return variable_records

def should_exclude_field_heuristic(variable_record):
    field_exclude = False
    if (variable_record['attributes']['data_type'] if variable_record['attributes']['object_type_value']=='0' else '4') == '0': # info item, skip, 4 = "object"
        field_exclude = True
    if sanitize_item_name(variable_record['name'])==sanitize_item_name('NavButtonSelect'):
        field_exclude = True # that stupid field from mf-polar
    return field_exclude

def should_exclude_field_removed_properties(record):
    def trim(s):
        return re.sub(r'^\s*','',re.sub(r'\s*$','',s))
    def check_val_sanitize_value(s):
        s = '{s}'.format(s=s)
        s = trim(s)
        s = s.lower()
        return s
    def check_flag_removal(record):
        properties_check = [
            'SavRemove',
            'D_Remove',
            'D_RemoveSav',
        ]
        flag_exclusion = False
        for prop_name, prop_value in record['properties'].items():
            is_prop_of_interest = False
            for prop_of_interest in properties_check:
                if check_val_sanitize_value(prop_name)==check_val_sanitize_value(prop_of_interest):
                    is_prop_of_interest = True
            if is_prop_of_interest:
                flag_exclusion = flag_exclusion or (check_val_sanitize_value(prop_value)==check_val_sanitize_value('true'))
        return flag_exclusion
    if record['parent']:
        return check_flag_removal(record) or should_exclude_field_removed_properties(record['parent'])
    else:
        return check_flag_removal(record)

def check_if_improper_name(name):
    is_improper_name = False
    # and there are less common cases but still happening in disney bes
    is_improper_name = is_improper_name or not not re.match(r'^\s*?(\d+)\s*?$',name,flags=re.I)
    is_improper_name = is_improper_name or not not re.match(r'^\s*?((?:Top|T|Bottom|B))(\d*)((?:B|Box))\s*?$',name,flags=re.I)
    is_improper_name = is_improper_name or not not re.match(r'^\s*?(?:GV|Rank|Num)\s*?$',name,flags=re.I)
    return is_improper_name





def detect_field_type(variable_record):
    if variable_record['name']=='':
        return 'root'
    object_type_value = variable_record['attributes']['object_type_value']
    data_type = variable_record['attributes']['data_type'] if object_type_value=='0' else None
    # ObjectTypeValue constants:
    # 0 = Question
    # 1 = Array
    # 2 = Grid
    # 3 = Class
    # 4 = Element
    # 10 = VariableInstance
    # 16 = Variables
    if object_type_value=='1' or object_type_value=='2':
        return 'loop'
    elif object_type_value=='3':
        return 'block'
    elif object_type_value=='16':
        return 'plain'
    elif object_type_value=='0':
        if data_type=='3':
            if 'maxvalue' in variable_record['attributes'] and variable_record['attributes']['maxvalue']=='1':
                return 'single-punch'
            else:
                return 'multi-punch'
        else:
            return 'plain'
    else:
        raise ValueError('unrecognized object_type_value: {o}'.format(o=object_type_value))


def get_recursive_prop_shortname(variable_record,variable_records):
    field_prop_shortname = None
    if variable_record['name']:
        if 'ShortName' in variable_record['properties']:
            field_prop_shortname = variable_record['properties']['ShortName']
        if not field_prop_shortname:
            parent_path, _ = extract_field_name(variable_record['name'])
            if parent_path:
                return get_recursive_prop_shortname(variable_records[sanitize_item_name(parent_path)],variable_records)
    return field_prop_shortname

def find_final_complex_name(field_prop_shortname,variable_record,variable_records):
    parent_path, field_name = extract_field_name(variable_record['name'])
    if parent_path:
        return find_final_complex_name(field_name if not check_if_improper_name(field_name) and not field_prop_shortname else '',variable_records[sanitize_item_name(parent_path)],variable_records) + ( '_'+field_prop_shortname if field_prop_shortname else '' )
    else:
        return variable_record['name'] + '_' + field_prop_shortname



def get_collection_of_levels(variable_record,variable_records,is_last=True):
    this_levels = [variable_record['level']] if 'level' in variable_record and variable_record['level'] is not None else []
    if not is_last and 'level' in variable_record and variable_record['level']==0:
        this_levels = []
    parent_path, _ = extract_field_name(variable_record['name'])
    parent_levels = get_collection_of_levels(variable_records[sanitize_item_name(parent_path)],variable_records,is_last=False) if parent_path else []
    return this_levels + parent_levels





def find_final_short_name_fallback(variable_record,variable_records):
    if variable_record['name']=='':
        return None
    field_prop_shortname = variable_record['properties']['ShortName'] if 'ShortName' in variable_record['properties'] else ''
    
    parent_path, field_name = extract_field_name(variable_record['name'])
    siblings = []
    siblings_including_this_field = []
    for  _, var_record in variable_records.items():
        child_parent_path, child_item_name = extract_field_name(var_record['name'])
        if child_parent_path==parent_path or var_record['name']==parent_path and not detect_field_type(var_record) in ['loop','block']:
            if not (var_record['name']==variable_record['name']):
                siblings.append(var_record)
            siblings_including_this_field.append(var_record)
    
    parent_variable_record = variable_records[sanitize_item_name(parent_path)] if parent_path else None

    is_bad_name = False
    is_bad_name = is_bad_name or not field_prop_shortname
    is_bad_name = is_bad_name or check_if_improper_name(field_prop_shortname)
    already_used = field_prop_shortname in [ (f['properties']['ShortName'] if 'ShortName' in f['properties'] else '') for _,f in variable_records.items() if not (variable_record['name']==f['name']) ]
    is_bad_name = is_bad_name or already_used

    if is_bad_name:
        if not parent_path:
            return field_name
        elif len(siblings)==0:
            return find_final_short_name_fallback(parent_variable_record,variable_records)
        elif not check_if_improper_name(field_name) and variable_record['name']==siblings_including_this_field[0]['name']:
            return find_final_short_name_fallback(parent_variable_record,variable_records)
        else:
            return find_final_short_name_fallback(parent_variable_record,variable_records) + '_' + ( field_prop_shortname if field_prop_shortname else field_name )
    else:
        return field_prop_shortname




# TODO: this is not a clean fn, it modifies its passed arguments
# but I don't care for now, it's easier, and saves more memory and processor time, if we don't create unnecessary copies
# because its intended use is
# variable_records = populate_levels_variable_records(variable_records)
def populate_levels_variable_records(variable_records):
    def update(node):
        if not 'fields' in node:
            return
        level_max = None
        for child in node['fields']:
            update(child)
            if 'level' in child and child['level'] is not None:
                if level_max is None or child['level']>level_max:
                    level_max = child['level']
            elif 'level_reached' in child:
                if level_max is None or child['level_reached']>level_max:
                    level_max = child['level_reached']
        if 'level' in node:
            level_add = node['level']
            if node['level'] is not None:
                node['level'] = (level_max if level_max is not None else 0) + level_add
            node['level_reached'] = (level_max if level_max is not None else 0) + (level_add if level_add is not None else 0)
        else:
            node['level_reached'] = level_max
    
    mdd_data_root = variable_records['']
    for _, variable_record in variable_records.items():
        type = detect_field_type(variable_record)
        level = None
        if type=='loop':
            level = 1
        elif type=='block' or type=='root' or type=='plain' or type=='single-punch':
            level = None
        elif type=='multi-punch':
            level = 0
        else:
            raise ValueError('unrecognized variable type: {o}'.format(o=type))
        variable_record['level'] = level
        # parent_path, field_name = extract_field_name(variable_record['name'])
        # parent = None
        # if parent_path:
        #     parent = variable_records[sanitize_item_name(parent_path)]
        # else:
        #     parent = mdd_data_root
        # # omg I'm stupid this was already appended above in prepare_variable_records()
        # if not 'fields' in parent:
        #     parent['fields'] = []
        # parent['fields'].append(variable_record)
        
    update(mdd_data_root)
    return variable_records




# TODO: this is not a clean fn, it modifies its passed arguments
# but I don't care for now, it's easier, and saves more memory and processor time, if we don't create unnecessary copies
# because its intended use is
# variable_records = normalize_properties_variable_records(variable_records)
def normalize_properties_variable_records(variable_records):
    for _, variable_record in variable_records.items():
        field_prop_shortname = None
        field_prop_savremove = None # SavRemove
        for prop_name, prop_value in variable_record['properties'].items():
            if sanitize_item_name(prop_name)==sanitize_item_name('shortname'):
                field_prop_shortname = prop_value
            if sanitize_item_name(prop_name)==sanitize_item_name('savremove'):
                field_prop_savremove = prop_value
        # if field_prop_shortname:
        if field_prop_shortname:
            field_prop_shortname = sanitize_shortname(field_prop_shortname)
        if True:
            variable_record['properties']['ShortName'] = field_prop_shortname
        if field_prop_savremove:
            variable_record['properties']['SavRemove'] = field_prop_savremove
    return variable_records


# TODO: this is not a clean fn, it modifies its passed arguments
# but I don't care for now, it's easier, and saves more memory and processor time, if we don't create unnecessary copies
# because its intended use is
# variable_records = normalize_properties_category_records(variable_records)
def normalize_properties_category_records(category_records):
    for _, category_record in category_records.items():
        field_prop_shortname = None
        field_prop_savremove = None # SavRemove
        field_prop_value = None
        for prop_name, prop_value in category_record['properties'].items():
            if sanitize_item_name(prop_name)==sanitize_item_name('shortname'):
                field_prop_shortname = prop_value
            if sanitize_item_name(prop_name)==sanitize_item_name('savremove'):
                field_prop_savremove = prop_value
            if sanitize_item_name(prop_name)==sanitize_item_name('value'):
                field_prop_value = prop_value
        if field_prop_value is not None:
            try:
                field_prop_value = float(field_prop_value)
                if abs(field_prop_value-round(field_prop_value))<CONFIG_ANALYSISVALUE_CHECK_IF_WHOLE_ERROR:
                    # if it's close enough to rounded whole
                    field_prop_value = int(round(field_prop_value))
                    field_prop_value = '{s}'.format(s=field_prop_value)
            except:
                pass
        # if field_prop_shortname:
        if True:
            category_record['properties']['ShortName'] = field_prop_shortname
        if field_prop_savremove:
            category_record['properties']['SavRemove'] = field_prop_savremove
        if True:
            category_record['properties']['Value'] = field_prop_value
    return category_records





def process_row_variable(map_data,variable_record,variable_records):
    result_field_include = None
    result_field_exclude = None
    result_field_name = None
    result_field_label = None
    result_field_format = None
    result_field_markup = None
    result_field_comment = None

    skip = False
    if should_exclude_field_removed_properties(variable_record):
        skip = True
        result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'skip - SavRemove=true'

    if not skip:

        # detect variable type
        field_type = detect_field_type(variable_record)

        if field_type=='loop' or field_type=='block':
            skip = True
            result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'skip - loop of block - definitions should be only applied to its fields'
        
        if not aa_logic_replicate.should_process_short_name(variable_record):
            skip = True
            result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'skip - we replicated AA logic and it indicated False - maybe a system variable or has no case data...'
        else:
            result_field_include = ''

        
        if not skip:

            # indicates if it's iterative
            field_levels = get_collection_of_levels(variable_record,variable_records)

            # find if it has shortname
            item_has_shortname = not not get_recursive_prop_shortname(variable_record,variable_records)

            should_include = False
            if item_has_shortname:
                should_include = True
            else:
                result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'skip - ShortName property not found'
            
            if should_include:

                # assert not should_exclude_field_heuristic(variable_record) # BannerCopyRight has a short name but it can't be represented in SPSS - this check fails but we need to continue
                
                result_field_include = 'x' if should_include else None

                levels_count = 0

                result_field_name = None
                try:
                    result_field_name = aa_logic_replicate.replicate_read_shortnames_logic(variable_record)
                except aa_logic_replicate.AAFailedFindShortnameException:
                    result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'Err: failed to read ShortName in the style of AA'
                    result_field_name = find_final_short_name_fallback(variable_record,variable_records)
                
                if not re.match(r'^\s*?[a-zA-Z\$].*?',result_field_name):
                    raise Exception('Suggested ShortName is invalid: {s}'.format(s=result_field_name))

                for d in field_levels:
                    # explanation
                    # "<@>" is an insert marker
                    # I designed it to indicate where the iterative part should be added
                    # so I am using "result = result.replace('<@>",iterative_part..." instead of result = result + iterative_part
                    # cause sometimes we have S3_001_Codes
                    # so the iterative part ("_001") is not added at the end but in the middle
                    # this is not super beautiful design but it is also quite simple and efficient and is working well
                    # so I don't feel sorry for this)))
                    # note I added similar marker to "aa_logic-replicate", so it's now program-wide
                    if not '<@>' in result_field_name:
                        result_field_name = result_field_name + '<@>'
                    result_field_name = result_field_name.replace('<@>','<@>_[L{d}z3]'.format(d=d))
                    levels_count = levels_count + 1
                    if d<=2:
                        if not(map_data['Question L{d}'.format(d=d)]):
                            # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                            result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])
                result_field_name = result_field_name.replace('<@>','')
                
                levels_count = 0
                result_field_label = variable_record['label']
                if 0 in field_levels:
                    d = 0
                    result_field_label = result_field_label + ' - {{L{d}}}'.format(d=d)
                    levels_count = levels_count + 1
                    if d<=2:
                        if not(map_data['Question L{d}'.format(d=0)]):
                            # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                            result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])
                for d in [m for m in field_levels if m!=0]:
                    # TODO:
                    # AA logic is the following:
                    # if category is inserted before question name (it's not L0, it's of any higher level)
                    # and it has a comma (",") in its label,
                    # then this part is enclosed with single quotes
                    # it does not apply to ALL categories - categories as normal stubs or categories coming as L0 (that become parts of a multi-punch variable) should not have these single quotes added
                    # but categories of loops should!
                    # I know, I'll update process_row_category()
                    result_field_label = '{{L{d}}}{sep}{rest}'.format(d=d,rest=result_field_label,sep=(' : ' if d==[m for m in field_levels if m!=0][0] else ', '))
                    levels_count = levels_count + 1
                    if d<=2:
                        if not(map_data['Question L{d}'.format(d=d)]):
                            # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                            result_field_comment = ( result_field_comment + '; ' if result_field_comment else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])

    assert (not not result_field_name)==(not not result_field_include)
    if result_field_name and not result_field_label:
        # flatout is generating the word "nan" if label is blank
        # that's funny, we can't leave an empty string
        # ok, I will use variable name as a label
        result_field_label = result_field_name
    return {
        'comment': result_field_comment,
        'include': result_field_include,
        'exclude': result_field_exclude,
        'name': result_field_name,
        'label': sanitize_variable_label(result_field_label),
        'format': result_field_format,
        'markup': result_field_markup,
    }



def process_row_category(map_data,category_record,variable_records):
    category_analysis_value = category_record['properties']['Value']
    try:
        category_analysis_value = float(category_analysis_value)
        if abs(round(category_analysis_value)-category_analysis_value)<CONFIG_ANALYSISVALUE_CHECK_IF_WHOLE_ERROR:
            # if it's close enough to rounded whole
            category_analysis_value = int(round(category_analysis_value))
    except:
        pass
    category_level = None
    if 'variable' in category_record and category_record['variable']:
        if 'level' in category_record['variable'] and category_record['variable']['level']:
            category_level = category_record['variable']['level']
    category_label = sanitize_category_label(category_record['label'])
    if category_level and category_level>0:
        if ',' in category_label:
            category_label = '{open}{t}{close}'.format(open='\'',close='\'',t=category_label)
    result = {
        'value': category_analysis_value,
    }
    if not(category_label==map_data['Label']):
        result['label'] = category_label
    return result



def fill_variables(map_df,mdd_scheme):
    print("Working on the map: variables...")
    
    mdd_data_records = get_mdd_data_records_from_input_data(mdd_scheme)
    mdd_data_root = [ field for field in mdd_data_records if field['name']=='' ][0]
    mdd_data_questions = [ field for field in mdd_data_records if detect_item_type_from_mdddata_fields_report(field['name'])=='variable' ]
    mdd_data_categories = [ cat for cat in mdd_data_records if detect_item_type_from_mdddata_fields_report(cat['name'])=='category' ]
    variable_records = prepare_variable_records(mdd_data_questions,mdd_data_categories,mdd_data_root)

    print("Normalizing property format from MDD read...")
    variable_records = normalize_properties_variable_records(variable_records)

    print("Detecting levels for every variable...")
    variable_records = populate_levels_variable_records(variable_records)
 
    rows = map_df.index
    print('variables sheet, filling the map...')
    known_system_fields_with_name_clean = {}
    for record_name, record_contents in CONFIG_KNOWN_SYSTEM_FIELDS.items():
        record_name_clean = sanitize_item_name(trim_dots(record_name))
        known_system_fields_with_name_clean[record_name_clean] = record_contents
    
    print('iterating over rows...')
    performance_counter = iter(helper_utility_performancemonitor.PerformanceMonitor(config={
        'total_records': len(rows),
        'report_frequency_records_count': 25,
        'report_frequency_timeinterval': 9,
        'report_text_pipein': 'filling up variables map',
    }))
    for row in rows:
        variable_name = map_df.loc[row,'Variable']
        processing_last_item = variable_name
        print('processing {s}...'.format(s=processing_last_item))
        next(performance_counter)
        try:
            map_result = {}
            try:
                variable_mdd_scheme_name = sanitize_map_name_to_mdd_scheme_name(trim_dots(variable_name))
                variable_mdd_scheme_name_clean = sanitize_item_name(variable_mdd_scheme_name)

                if variable_mdd_scheme_name_clean in known_system_fields_with_name_clean:
                    map_result['comment'] = (map_result['comment']+'; ' if 'comment' in map_result else '') + 'found a pre-defined item in hardcoded map with system variables'
                    map_result = known_system_fields_with_name_clean[variable_mdd_scheme_name_clean]
                else:
                    map_data = {}
                    for attr in CONFIG_MAP_DATA_VARIABLE_FIELDS:
                        map_data[attr] = map_df.loc[row,attr]
                    need_skip = False
                    if 'info' in sanitize_item_name(map_data['Type']):
                        need_skip = True
                        map_result['comment'] = (map_result['comment']+'; ' if 'comment' in map_result else '') + 'skipping - not a variable (info node)'
                    if 'historic' in sanitize_item_name(map_data['Row Type']):
                        need_skip = True
                        map_result['comment'] = (map_result['comment']+'; ' if 'comment' in map_result else '') + 'skipping - non-existen variable (it\'s historic record in the map)'

                    if not need_skip:
                        variable_record = variable_records[variable_mdd_scheme_name_clean]
                        map_result = process_row_variable(map_data,variable_record,variable_records)
                    else:
                        map_result['comment'] = (map_result['comment']+' -> ' if 'comment' in map_result else '') + 'skipping!'

            except Exception as e:
                map_result = {
                    'comment': 'Error: {e}'.format(e=e)
                }
                print('Error: failed when processing {item}: {e}'.format(item=processing_last_item,e=e))

            # apply result
            if map_result:
                columns_last_7 = ['{m}'.format(m=m) for m in map_df.columns[-7:]]
                try:
                    assert len(columns_last_7)==7
                    assert '>>>' in columns_last_7[0]
                    assert '- include' in columns_last_7[1]
                    assert '- exclude' in columns_last_7[2]
                    assert '- name' in columns_last_7[3]
                    assert '- label' in columns_last_7[4]
                    assert '- format' in columns_last_7[5]
                    assert '- markup' in columns_last_7[6]
                except:
                    raise Exception('Last 7 columns on \'variables\' sheet should include words ">>>", "include", "excelude", "name"... This test was not passed. Exiting.')
                if 'include' in map_result:
                    map_df.loc[row,columns_last_7[1]] = map_result['include']
                else:
                    # keep default value from original flatout map
                    pass
                if 'exclude' in map_result:
                    map_df.loc[row,columns_last_7[2]] = map_result['exclude']
                else:
                    # keep default value from original flatout map
                    pass
                if 'name' in map_result:
                    map_df.loc[row,columns_last_7[3]] = map_result['name']
                else:
                    # keep default value from original flatout map
                    pass
                if 'label' in map_result:
                    map_df.loc[row,columns_last_7[4]] = map_result['label']
                else:
                    # keep default value from original flatout map
                    pass
                if 'format' in map_result:
                    map_df.loc[row,columns_last_7[5]] = map_result['format']
                else:
                    # keep default value from original flatout map
                    pass
                if 'markup' in map_result:
                    map_df.loc[row,columns_last_7[6]] = map_result['markup']
                else:
                    # keep default value from original flatout map
                    pass
                if 'comment' in map_result and map_result['comment']:
                    map_df.loc[row,columns_last_7[0]] = '>>>>>>>>' + ' ' + map_result['comment']
                else:
                    # keep default value from original flatout map
                    pass

        except Exception as e:
            # something failed? alert which was the last row, and throw the exception back
            print('Error at {s}'.format(s=processing_last_item))
            raise e


    print("Finished!")
    return map_df


def fill_categories(map_df,mdd_scheme):
    print("Working on the map: categories...")
    
    print("Normalizing property format from MDD read...")
    mdd_data_records = get_mdd_data_records_from_input_data(mdd_scheme)
    mdd_data_root = [ field for field in mdd_data_records if field['name']=='' ][0]
    mdd_data_questions = [ field for field in mdd_data_records if detect_item_type_from_mdddata_fields_report(field['name'])=='variable' ]
    mdd_data_categories = [ cat for cat in mdd_data_records if detect_item_type_from_mdddata_fields_report(cat['name'])=='category' ]
    variable_records = prepare_variable_records(mdd_data_questions,mdd_data_categories,mdd_data_root)
    category_records = {}
    for cat in mdd_data_categories:
        q_name, cat_name = extract_category_name(cat['name'])
        q = variable_records[sanitize_item_name(q_name)]
        cat['name_category'] = cat_name
        cat['name_variable'] = q_name
        cat['variable'] = q
        category_records[sanitize_item_name(cat['name'])] = cat

    # we'll normalize shortname property name
    category_records = normalize_properties_category_records(category_records)
 
    rows = map_df.index
    print('categories sheet, filling the map...')
    print('iterating over rows...')
    performance_counter = iter(helper_utility_performancemonitor.PerformanceMonitor(config={
        'total_records': len(rows),
        'report_frequency_records_count': 35,
        'report_frequency_timeinterval': 9,
        'report_text_pipein': 'filling up categories map',
    }))
    last_processing_item = None
    for row in rows:
        variable_name = map_df.loc[row,'Variable']
        category_name = map_df.loc[row,'Category']
        item_name = '{variable_name}.Categories[{cat_name}]'.format(variable_name=variable_name,cat_name=category_name)
        processing_last_item = item_name
        if not(variable_name==last_processing_item):
            print('processing categories of {s}...'.format(s=variable_name))
        last_processing_item = variable_name
        next(performance_counter)
        try:
            map_result = {}
            try:
                _, category_last_name = extract_field_name(category_name)
                item_name = '{variable_name}.Categories[{cat_name}]'.format(variable_name=sanitize_map_name_to_mdd_scheme_name(trim_dots(variable_name)),cat_name=category_last_name)
                variable_mdd_scheme_name_clean = sanitize_item_name(item_name)

                map_data = {}
                for attr in CONFIG_MAP_DATA_CATEGORY_FIELDS:
                    map_data[attr] = map_df.loc[row,attr]
                need_skip = False
                # if 'info' in sanitize_item_name(map_data['Type']):
                #     need_skip = True
                #     map_result['comment'] = (map_result['comment']+'; ' if 'comment' in map_result else '') + 'skipping - not a category (info node)'
                # if 'historic' in sanitize_item_name(map_data['Row Type']):
                #     need_skip = True
                #     map_result['comment'] = (map_result['comment']+'; ' if 'comment' in map_result else '') + 'skipping - non-existen category (it\'s historic record in the map)'

                if not need_skip:
                    # variable_record = variable_records[variable_mdd_scheme_name_clean]
                    category_record = category_records[variable_mdd_scheme_name_clean] if variable_mdd_scheme_name_clean in category_records else None
                    if category_record:
                        map_result = process_row_category(map_data,category_record,variable_records)
                    else:
                        map_result['comment'] ='Error: category not found in mdd scheme!'
                else:
                    map_result['comment'] = (map_result['comment']+' -> ' if 'comment' in map_result else '') + 'skipping!'

            except Exception as e:
                map_result = {
                    'comment': 'Error: {e}'.format(e=e)
                }
                print('Error: failed when processing {item}: {e}'.format(item=processing_last_item,e=e))

            # apply result
            if map_result:
                columns_last_6 = ['{m}'.format(m=m) for m in map_df.columns[-6:]]
                try:
                    assert len(columns_last_6)==6
                    assert '>>>' in columns_last_6[0]
                    assert '- include' in columns_last_6[1]
                    assert '- exclude' in columns_last_6[2]
                    assert '- punch' in columns_last_6[3]
                    assert '- label' in columns_last_6[4]
                    assert '- markup' in columns_last_6[5]
                except:
                    raise Exception('Last 6 columns on \'variables\' sheet should include words ">>>", "include", "excelude", "name"... This test was not passed. Exiting.')
                if 'include' in map_result:
                    map_df.loc[row,columns_last_6[1]] = map_result['include']
                else:
                    # keep default value from original flatout map
                    pass
                if 'exclude' in map_result:
                    map_df.loc[row,columns_last_6[2]] = map_result['exclude']
                else:
                    # keep default value from original flatout map
                    pass
                if 'value' in map_result:
                    map_df.loc[row,columns_last_6[3]] = map_result['value']
                else:
                    # reset
                    map_df.loc[row,columns_last_6[3]] = ''
                if 'label' in map_result:
                    map_df.loc[row,columns_last_6[4]] = map_result['label']
                else:
                    # keep default value from original flatout map
                    pass
                if 'markup' in map_result:
                    map_df.loc[row,columns_last_6[5]] = map_result['markup']
                else:
                    # keep default value from original flatout map
                    pass
                if 'comment' in map_result and map_result['comment']:
                    map_df.loc[row,columns_last_6[0]] = '>>>>>>>>' + ' ' + map_result['comment']
                else:
                    # keep default value from original flatout map
                    pass

        except Exception as e:
            # something failed? alert which was the last row, and throw the exception back
            print('Error at {s}'.format(s=processing_last_item))
            raise e


    print("Finished!")
    return map_df



