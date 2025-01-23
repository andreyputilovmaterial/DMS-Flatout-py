from datetime import datetime, timezone
import argparse
from pathlib import Path
import json, re
from unittest import result
import pandas as pd




# if __name__ == '__main__':
#     # run as a program
#     import util_smth
# elif '.' in __name__:
#     # package
#     from . import util_smth
# else:
#     # included with no parent package
#     import util_smth



CONFIG_MAP_DATA_FIELDS = [
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
]



CONFIG_KNOWN_SYSTEM_FIELDS = {
    'Respondent.': { '_': 'Respondent.', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'Respondent.Serial': { '_': 'Respondent.Serial', 'include': 'x', 'exclude': '', 'name': 'Respondent_Serial', 'label': '', 'format': '', 'markup': '', },
    'Respondent.ID': { '_': 'Respondent.ID', 'include': 'x', 'exclude': '', 'name': 'Respondent_ID', 'label': '', 'format': '', 'markup': 'id', },
    'DataCollection.': { '_': 'DataCollection.', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'DataCollection.Status': { '_': 'DataCollection.Status', 'include': 'x', 'exclude': '', 'name': 'DataCollection_Status[L0]', 'label': 'Status - {L0}', 'format': '', 'markup': '', },
    'DataCollection.StartTime': { '_': 'DataCollection.StartTime', 'include': 'x', 'exclude': '', 'name': 'DataCollection_StartTime', 'label': 'Interview start time', 'format': '', 'markup': '', },
    'DataCollection.FinishTime': { '_': 'DataCollection.FinishTime', 'include': 'x', 'exclude': '', 'name': 'DataCollection_FinishTime', 'label': 'Interview finish time', 'format': '', 'markup': '', },
    'DataCollection.Removed': { '_': 'DataCollection.Removed', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'DataCollection.InterviewMode': { '_': 'DataCollection.InterviewMode', 'include': 'x', 'exclude': '', 'name': 'DataCollection_InterviewMode', 'label': 'Interview Mode', 'format': '', 'markup': '', },
    'QuotaDaily': { '_': 'QuotaDaily', 'include': 'x', 'exclude': '', 'name': '', 'label': 'QuotaDaily', 'format': '', 'markup': '', },
    'QuotaMonthly': { '_': 'QuotaMonthly', 'include': 'x', 'exclude': '', 'name': '', 'label': 'QuotaMonthly', 'format': '', 'markup': '', },
    'QuotaYearly': { '_': 'QuotaYearly', 'include': 'x', 'exclude': '', 'name': '', 'label': 'QuotaYearly', 'format': '', 'markup': '', },
    'CensusRegion': { '_': 'CensusRegion', 'include': 'x', 'exclude': '', 'name': '', 'label': 'CensusRegion', 'format': '', 'markup': '', },
    'PrelimBanner': { '_': 'PrelimBanner', 'include': 'x', 'exclude': '', 'name': '', 'label': 'PrelimBanner', 'format': '', 'markup': '', },
    'COMP': { '_': 'COMP', 'include': 'x', 'exclude': '', 'name': '', 'label': 'COMP', 'format': '', 'markup': '', },
    'DelayTermReasons': { '_': 'DelayTermReasons', 'include': 'x', 'exclude': '', 'name': 'DelayTermReasons_[L0z3]', 'label': 'DelayTermReasons - {L0}', 'format': '', 'markup': '', },
    'CompletedScreener': { '_': 'CompletedScreener', 'include': 'x', 'exclude': '', 'name': '', 'label': 'CompletedScreener', 'format': '', 'markup': '', },
    'WeightingStatus': { '_': 'WeightingStatus', 'include': 'x', 'exclude': '', 'name': 'WeightingStatus_[L0z3]', 'label': 'WeightingStatus - {L0}', 'format': '', 'markup': '', },
    'QCData.': { '_': 'QCData.', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'QCData.ErrorMsg': { '_': 'QCData.ErrorMsg', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'QCData.Flags': { '_': 'QCData.Flags', 'include': 'x', 'exclude': '', 'name': 'QCFlags_[L0z3]', 'label': 'QCData.Flags - {L0}', 'format': '', 'markup': '', },
    'QCData.Number': { '_': 'QCData.Number', 'include': 'x', 'exclude': '', 'name': 'QCFlagCount', 'label': 'QCData.Number', 'format': '', 'markup': '', },
    'USLocationData.': { '_': 'USLocationData.', 'include': '', 'exclude': '', 'name': '', 'label': '', 'format': '', 'markup': '', },
    'USLocationData.Zip': { '_': 'USLocationData.Zip', 'include': 'x', 'exclude': '', 'name': 'USLoc_Zip', 'label': 'USLocationData.Zip', 'format': '', 'markup': '', },
    'USLocationData.State': { '_': 'USLocationData.State', 'include': 'x', 'exclude': '', 'name': 'USLoc_State', 'label': 'USLocationData.State', 'format': '', 'markup': '', },
    'USLocationData.CensusRegion': { '_': 'USLocationData.CensusRegion', 'include': 'x', 'exclude': '', 'name': 'USLoc_Region', 'label': 'USLocationData.CensusRegion', 'format': '', 'markup': '', },
    'USLocationData.NielsenDMAText': { '_': 'USLocationData.NielsenDMAText', 'include': 'x', 'exclude': '', 'name': 'USLoc_NielsenDMA', 'label': 'USLocationData.NielsenDMAText', 'format': '', 'markup': '', },
    'USLocationData.NielsenCountySize': { '_': 'USLocationData.NielsenCountySize', 'include': 'x', 'exclude': '', 'name': 'USLoc_NielsenCountySize', 'label': 'USLocationData.NielsenCountySize', 'format': '', 'markup': '', },
}



def sanitize_map_name_to_mdd_scheme_name(s):
    return re.sub(r'(\w+)\s*?\[\s*?\{?[^\]]*?\s*?\}?\s*?\]',lambda m: '{s}'.format(s=m[1]),s,flags=re.I|re.DOTALL)

def trim_dots(s):
    return re.sub(r'^\s*?\.','',re.sub(r'\.\s*?$','',s,flags=re.I),flags=re.I)

def sanitize_item_name(item_name):
    return re.sub(r'\s*$','',re.sub(r'^\s*','',re.sub(r'\s*([\[\{\]\}\.])\s*',lambda m:'{m}'.format(m=m[1]),item_name,flags=re.I))).lower()

def extract_field_name(item_name):
    m = re.match(r'^\s*((?:\w.*?\.)*)(\w+)\s*$',item_name,flags=re.I)
    if m:
        return re.sub(r'\s*\.\s*$','',m[1]),m[2]
    else:
        raise ValueError('Can\'t extract field name from "{s}"'.format(s=item_name))

def extract_parent_name(item_name):
    if item_name=='':
        return '', ''
    m = re.match(r'^\s*(\w+)((?:\.\w*?)*)\s*$',item_name,flags=re.I)
    if m:
        return trim_dots(m[1]), trim_dots(m[2])
    else:
        raise ValueError('Can\'t extract field name from "{s}"'.format(s=item_name))

def extract_category_name(item_name):
    m = re.match(r'^\s*(\w+.*?\w)\.(?:categories|elements)\s*?\[\s*?\{?\s*?(\w+)\s*?\}?\s*?\]\s*$',item_name,flags=re.I)
    if m:
        return trim_dots(m[1]), trim_dots(m[2])
    else:
        raise ValueError('Can\'t extract category name from "{s}"'.format(s=item_name))







def get_mdd_data_records_from_input_data(inp_mdd_scheme):
    def convert_list_to_dict(data_lst):
        result = {}
        for record in data_lst:
            result[record['name']] = record['value']
        return result
    mdd_data_records = ([sect for sect in inp_mdd_scheme['sections'] if sect['name']=='fields'])[0]['content']
    mdd_data_records = [ {**q,'properties':convert_list_to_dict(q['properties'] if 'properties' in q else []),'attributes':convert_list_to_dict(q['attributes'] if 'attributes' in q else [])} for q in mdd_data_records ]
    return mdd_data_records


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

def prepare_variable_records(mdd_data_records,mdd_data_categories):
    variable_records = {}
    # for rec in variable_specs['variables_metadata']:
    for rec in mdd_data_records:
        question_id_clean = sanitize_item_name(rec['name'])
        variable_records[question_id_clean] = rec
    for rec in mdd_data_records:
        path, _ = extract_field_name(rec['name'])
        if path and not (path==''):
            variable_parent = variable_records[sanitize_item_name(path)]
            if not 'subfields' in variable_parent:
                variable_parent['subfields'] = []
            variable_parent['subfields'].append(rec) # that's a reference, and child item should also be updated, when it receives its own subfields
    for cat_mdd in mdd_data_categories:
        question_name, category_name = extract_category_name(cat_mdd['name'])
        question_id_clean = sanitize_item_name(question_name)
        variable = variable_records[question_id_clean]
        if not 'categories' in variable:
            variable['categories'] = []
        variable['categories'].append({**cat_mdd,'name':category_name}) # that's not a reference, that's a copy; and name is a category name

    return variable_records

def detect_var_type_by_record(variable_record):
    variable_attributes_captured_with_mdd_read = {}
    if not 'attributes' in variable_record:
        raise ValueError('Input data does not include "attributes" data, please adjust settings that you use to run mdd_read')
    else:
        assert isinstance(variable_record,dict)
    variable_attributes_captured_with_mdd_read = {**variable_record['attributes']}
    if not 'type' in variable_attributes_captured_with_mdd_read:
        raise ValueError('Input data must follow certain format and must include "type" within its list of attributes generated with mdd_read')

    # detect variable type - we are doing it from grabbing data from attributes that were written by mdd_read
    variable_type = None
    # variable_is_plain = re.match(r'^\s*?plain\b',variable_attributes_captured_with_mdd_read['type'])
    variable_is_categorical = re.match(r'^\s*?plain/(?:categorical|multipunch|singlepunch)',variable_attributes_captured_with_mdd_read['type'])
    variable_is_loop = re.match(r'^\s*?(?:array|grid|loop)\b',variable_attributes_captured_with_mdd_read['type'])
    # variable_is_block = re.match(r'^\s*?(?:block)\b',variable_attributes_captured_with_mdd_read['type'])
    if variable_is_loop:
        variable_type = 'loop'
    elif variable_is_categorical:
        variable_type = 'categorical'
    else:
        raise ValueError('Can\'t handle this type of variable: {s}'.format(s=variable_attributes_captured_with_mdd_read['type']))
    return variable_type

def should_exclude_field(variable_record):
    field_exclude = False
    if (variable_record['attributes']['data_type'] if variable_record['attributes']['object_type_value']=='0' else '4') == '0': # info item, skip, 4 = "object"
        field_exclude = True
    if sanitize_item_name(variable_record['name'])==sanitize_item_name('NavButtonSelect'):
        field_exclude = True # that stupid field from mf-polar
    return field_exclude

def check_if_improper_name(name):
    is_improper_name = False
    # and there are less common cases but still happening in disney bes
    is_improper_name = is_improper_name or not not re.match(r'^\s*?(\d+)\s*?$',name,flags=re.I)
    is_improper_name = is_improper_name or not not re.match(r'^\s*?((?:Top|T|Bottom|B))(\d*)((?:B|Box))\s*?$',name,flags=re.I)
    is_improper_name = is_improper_name or not not re.match(r'^\s*?(?:GV|Rank|Num)\s*?$',name,flags=re.I)
    return is_improper_name





def detect_field_type(variable_record):
    a = variable_record['attributes']
    if a['object_type_value']=='1' or a['object_type_value']=='2':
        return 'loop'
    elif a['object_type_value']=='3':
        return 'block'
    elif a['object_type_value']=='16':
        return 'plain'
    elif a['object_type_value']=='0':
        if a['data_type']=='3':
            if a['maxvalue']=='1':
                return 'single-punch'
            else:
                return 'multi-punch'
        else:
            return 'plain'
    else:
        raise ValueError('unrecognized object_type_value: {o}'.format(o=a['object_type_value']))


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



def get_number_of_iter_levels_recursive(variable_record,variable_records):
    def recursive(variable_record,variable_records):
        result_this_field = None
        field_type = detect_field_type(variable_record)
        if field_type=='plain' or field_type=='single-punch':
            result_this_field = 0
        elif field_type=='multi-punch':
            result_this_field = 0
        elif field_type=='block':
            result_this_field = 0
        elif field_type=='loop':
            result_this_field = 1
        else:
            raise ValueError('unrecognized field type: {t}'.format(t=field_type))
        result_parent = None
        parent_path, _ = extract_field_name(variable_record['name'])
        if parent_path:
            result_parent = recursive(variable_records[sanitize_item_name(parent_path)],variable_records)
        if not result_parent:
            result_parent = 0
        result = result_parent + result_this_field
        assert( isinstance(result,int) )
        return result
    result_this_field = None
    field_type = detect_field_type(variable_record)
    if field_type=='plain' or field_type=='single-punch':
        result_this_field = []
    elif field_type=='multi-punch':
        result_this_field = [0]
    elif field_type=='block':
        result_this_field = []
    elif field_type=='loop':
        # result_this_field = 1
        raise Exception('reached unreachable, please check')
    else:
        raise ValueError('unrecognized field type: {t}'.format(t=field_type))
    result_parent = None
    parent_path, _ = extract_field_name(variable_record['name'])
    if parent_path:
        result_parent = recursive(variable_records[sanitize_item_name(parent_path)],variable_records)
    if not result_parent:
        result_parent = 0
    assert( isinstance(result_parent,int) )
    result = result_this_field + [m for m in range(result_parent,1-1,-1)]
    return result





def find_final_short_name(variable_record,variable_records):
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
    is_bad_name = is_bad_name or field_prop_shortname in [ (f['properties']['ShortName'] if 'ShortName' in f['properties'] else '') for _,f in variable_records.items() if not (variable_record['name']==f['name']) ]

    if is_bad_name:
        if not parent_path:
            return field_name
        elif len(siblings)==0:
            return find_final_short_name(parent_variable_record,variable_records)
        elif not check_if_improper_name(field_name) and variable_record['name']==siblings_including_this_field[0]['name']:
            return find_final_short_name(parent_variable_record,variable_records)
        else:
            return find_final_short_name(parent_variable_record,variable_records) + '_' + ( field_prop_shortname if field_prop_shortname else field_name )
    else:
        return field_prop_shortname


def process_row(map_data,variable_record,variable_records):
    result_field_include = None
    result_field_exclude = None
    result_field_name = None
    result_field_label = None
    result_field_format = None
    result_field_markup = None

    if not ( ('SavRemove' in variable_record['properties']) and ('true' in sanitize_item_name(variable_record['properties']['SavRemove'])) ):

        # detect variable type
        field_type = detect_field_type(variable_record)

        if not(field_type=='loop' or field_type=='block'):

            # indicates if it's iterative
            field_number_of_iter_levels = get_number_of_iter_levels_recursive(variable_record,variable_records)

            # find if it has shortname
            item_has_shortname = not not get_recursive_prop_shortname(variable_record,variable_records)

            if item_has_shortname:
                result_field_include = 'x'
            
            if result_field_include:
                # assert not should_exclude_field(variable_record) # BannerCopyRight has a short name but it can't be represented in SPSS - this check fails but we need to continue

                result_field_name = find_final_short_name(variable_record,variable_records)
                for i in field_number_of_iter_levels:
                    result_field_name = result_field_name + '_[L{d}z3]'.format(d=i)

                result_field_label = variable_record['label']
                if 0 in field_number_of_iter_levels:
                    result_field_label = result_field_label + ' - {{L{d}}}'.format(d=0)
                for i in [m for m in field_number_of_iter_levels if m!=0]:
                    result_field_label = '{{L{d}}}: '.format(d=i) + result_field_label

    if result_field_name:
        print('including')
    else:
        print('excluding')
    assert (not not result_field_name)==(not not result_field_include)
    return {
        'include': result_field_include,
        'exclude': result_field_exclude,
        'name': result_field_name,
        'label': result_field_label,
        'format': result_field_format,
        'markup': result_field_markup,
    }




def fill(map_df,mdd_scheme):
    print("Filling the map...")
    
    mdd_data_records = get_mdd_data_records_from_input_data(mdd_scheme)
    # mdd_data_root = [ field for field in mdd_data_records if field['name']=='' ][0]
    mdd_data_questions = [ field for field in mdd_data_records if detect_item_type_from_mdddata_fields_report(field['name'])=='variable' ]
    mdd_data_categories = [ cat for cat in mdd_data_records if detect_item_type_from_mdddata_fields_report(cat['name'])=='category' ]
    variable_records = prepare_variable_records(mdd_data_questions,mdd_data_categories)

    # we'll normalize shortname property name
    for _, variable_record in variable_records.items():
        field_prop_shortname = None
        field_prop_savremove = None # SavRemove
        for prop_name, prop_value in variable_record['properties'].items():
            if sanitize_item_name(prop_name)==sanitize_item_name('shortname'):
                field_prop_shortname = prop_value
            if sanitize_item_name(prop_name)==sanitize_item_name('savremove'):
                field_prop_savremove = prop_value
        if field_prop_shortname:
            variable_record['properties']['ShortName'] = field_prop_shortname
        if field_prop_savremove:
            variable_record['properties']['SavRemove'] = field_prop_savremove

    known_system_fields_with_name_clean = {}
    for record_name, record_contents in CONFIG_KNOWN_SYSTEM_FIELDS.items():
        record_name_clean = sanitize_item_name(trim_dots(record_name))
        known_system_fields_with_name_clean[record_name_clean] = record_contents
    
    rows = map_df.index
    print('   starting working on variables sheet...')
    print('   iterating over rows...')
    for row in rows:
        variable_name = map_df.loc[row,'Variable']
        processing_last_item = variable_name
        print('processing {s}...'.format(s=processing_last_item))
        try:
            variable_mdd_scheme_name = sanitize_map_name_to_mdd_scheme_name(trim_dots(variable_name))
            variable_mdd_scheme_name_clean = sanitize_item_name(variable_mdd_scheme_name)

            map_result = None
            if variable_mdd_scheme_name_clean in known_system_fields_with_name_clean:
                print('found as a default variable')
                map_result = known_system_fields_with_name_clean[variable_mdd_scheme_name_clean]
            else:
                map_data = {}
                for attr in CONFIG_MAP_DATA_FIELDS:
                    map_data[attr] = map_df.loc[row,attr]
                need_skip = False
                need_skip = need_skip or 'info' in sanitize_item_name(map_data['Type'])
                need_skip = need_skip or 'historic' in sanitize_item_name(map_data['Row Type'])

                if not need_skip:
                    variable_record = variable_records[variable_mdd_scheme_name_clean]
                    map_result = process_row(map_data,variable_record,variable_records)
                else:
                    print('skip')

            # apply result
            if map_result:
                columns_last_6 = ['{m}'.format(m=m) for m in map_df.columns[-6:]]
                assert len(columns_last_6)==6
                assert '- include' in columns_last_6[0]
                assert '- exclude' in columns_last_6[1]
                assert '- name' in columns_last_6[2]
                assert '- label' in columns_last_6[3]
                assert '- format' in columns_last_6[4]
                assert '- markup' in columns_last_6[5]
                map_df.loc[row,columns_last_6[0]] = map_result['include']
                map_df.loc[row,columns_last_6[1]] = map_result['exclude']
                map_df.loc[row,columns_last_6[2]] = map_result['name']
                map_df.loc[row,columns_last_6[3]] = map_result['label']
                map_df.loc[row,columns_last_6[4]] = map_result['format']
                map_df.loc[row,columns_last_6[5]] = map_result['markup']

        except Exception as e:
            # something failed? alert which was the last row, and throw the exception back
            print('Error at {s}'.format(s=processing_last_item))
            raise e


    print("\nFilling finished")
    return map_df




def entry_point(runscript_config={}):

    time_start = datetime.now()
    script_name = 'mdttolsap-fill-pailess-map script'

    parser = argparse.ArgumentParser(
        description="Pre-fills flatout map",
        prog='mdd-patch'
    )
    parser.add_argument(
        '-1',
        '--inp-mdd-scheme',
        type=str,
        help='JSON with fields data from MDD Input File',
        required=True
    )
    parser.add_argument(
        '-2',
        '--map',
        type=str,
        help='The Flatout Map',
        required=True
    )
    parser.add_argument(
        '--output-filename',
        help='Set preferred output file name, with path',
        type=str,
        required=False
    )
    args = None
    args_rest = None
    if( ('arglist_strict' in runscript_config) and (not runscript_config['arglist_strict']) ):
        args, args_rest = parser.parse_known_args()
    else:
        args = parser.parse_args()
    
    inp_mddscheme_filename = ''
    if args.inp_mdd_scheme:
        inp_mddscheme_filename = Path(args.inp_mdd_scheme)
        inp_mddscheme_filename = '{inp_mddscheme_filename}'.format(inp_mddscheme_filename=inp_mddscheme_filename.resolve())
    else:
        raise FileNotFoundError('Inp source: file not provided; please use --inp-mdd-scheme option')

    inp_map_filename = ''
    if args.map:
        inp_map_filename = Path(args.map)
        inp_map_filename = '{inp_map_filename}'.format(inp_map_filename=inp_map_filename.resolve())
    else:
        raise FileNotFoundError('Inp source: file not provided; please use --map option')

    config = {}

    # report_part_filename = re.sub( r'\.json\s*?$', '', Path(inp_mddscheme_filename).name )
    result_final_fname = None
    if args.output_filename:
        result_final_fname = Path(args.output_filename)
    else:
        raise FileNotFoundError('Inp source: file not provided; please use --output-filename')
    

    if not(Path(inp_mddscheme_filename).is_file()):
        raise FileNotFoundError('file not found: {fname}'.format(fname=inp_mddscheme_filename))
    if not(Path(inp_map_filename).is_file()):
        raise FileNotFoundError('file not found: {fname}'.format(fname=inp_map_filename))

    print('{script_name}: script started at {dt}'.format(dt=time_start,script_name=script_name))

    inp_mdd_scheme = None
    with open(inp_mddscheme_filename) as f_l:
        try:
            inp_mdd_scheme = json.load(f_l)
        except json.JSONDecodeError as e:
            # just a more descriptive message to the end user
            # can happen if the tool is started two times in parallel and it is writing to the same json simultaneously
            raise TypeError('Patch: Can\'t read left file as JSON: {msg}'.format(msg=e))
    
    inp_map_df = None
    with open(inp_map_filename) as f_l:
        inp_map_df = None
        print("\n"+'Reading Excel "{file}"...'.format(file=inp_map_filename))
        # header=7 means how many rows to skip above the banner line
        inp_map_df = pd.read_excel(inp_map_filename, sheet_name='variables', index_col='Index',header=2,engine='openpyxl').fillna("")
        print("\n"+'Reading Excel successful')
    
    result_df = fill(inp_map_df,inp_mdd_scheme)

    print('{script_name}: saving as "{fname}"'.format(fname=result_final_fname,script_name=script_name))
    result_df.to_excel(result_final_fname, sheet_name='variables')

    time_finish = datetime.now()
    print('{script_name}: finished at {dt} (elapsed {duration})'.format(dt=time_finish,duration=time_finish-time_start,script_name=script_name))



if __name__ == '__main__':
    entry_point({'arglist_strict':True})
