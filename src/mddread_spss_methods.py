
import re




if __name__ == '__main__':
    # run as a program
    import util_var_functions
    import aa_logic_replicate
elif '.' in __name__:
    # package
    from . import util_var_functions
    from . import aa_logic_replicate
else:
    # included with no parent package
    import util_var_functions
    import aa_logic_replicate





def detect_var_type_by_attrs(self):
    if self['type']=='variable':
        variable_attributes = self['attributes']
        result = None
        variable_is_plain = False
        variable_is_categorical = False
        variable_is_loop = False
        variable_is_grid = False
        variable_is_block = False
        variable_maxvalue = None
        for attr_name, attr_value in variable_attributes.items():
            if attr_name=='type':
                variable_is_plain = variable_is_plain or not not re.match(r'^\s*?plain\b',attr_value)
                variable_is_categorical = variable_is_categorical or not not re.match(r'^\s*?plain/(?:categorical|multipunch|singlepunch)',attr_value)
                variable_is_loop = variable_is_loop or not not re.match(r'^\s*?(?:array|grid|loop)\b',attr_value)
                variable_is_block = variable_is_block or not not re.match(r'^\s*?(?:block)\b',attr_value)
            elif attr_name=='is_grid':
                variable_is_grid = variable_is_grid or not not re.match(r'^\s*?true\b',attr_value)
            elif attr_name=='object_type_value':
                variable_is_loop = variable_is_loop or not not re.match(r'^\s*?(?:1|2)\b',attr_value)
            elif attr_name=='data_type':
                variable_is_categorical = variable_is_categorical or not not re.match(r'^\s*?(?:3)\b',attr_value)
            elif attr_name=='maxvalue':
                if re.match(r'^\s*?(?:none)?\s*?$',attr_value,flags=re.I|re.DOTALL):
                    pass
                else:
                    try:
                        variable_maxvalue = int(attr_value)
                    except:
                        pass
        if variable_is_plain or variable_is_categorical:
            if variable_is_categorical:
                if variable_maxvalue==1:
                    result='singlepunch'
                else:
                    result='multipunch'
            else:
                result = 'plain'
        elif variable_is_loop:
            if variable_is_grid:
                result = 'grid'
            else:
                result = 'loop'
        elif variable_is_block:
            result = 'block'
        self['variable_type'] = result


def update_levels(self):
    has_iterative_level = not(self['type']=='root') and ((self['variable_type']=='loop') or (self['variable_type']=='grid'))
    has_iterative_data = not(self['type']=='root') and ((self['variable_type']=='multipunch'))
    assert not has_iterative_level or not has_iterative_data, 'error updating levels: variable can\'t be both iterative and have iterative data ({n})'.format(n=self['name'])
    self['has_iterative_level'] = has_iterative_level
    self['has_iterative_data'] = has_iterative_data
    max_children_level_reached = 0
    if 'fields' in self:
        for child in self['fields']:
            child['extend_methods']['update_levels']()
            if child['max_level_reached'] > max_children_level_reached:
                max_children_level_reached = child['max_level_reached']
    if has_iterative_level:
        self['level'] = max_children_level_reached + 1 # if it's zero, we start with 1, if 1 was used, we assign 2, and so on
    elif has_iterative_data:
        self['level'] = 0
    # TODO: a good question here: what happens if current item has HelperFields (and noe of the fields has levels - is a loop)? Most probably, meaningless question, because I have never seen it in my practice
    if has_iterative_level:
        self['max_level_reached'] = self['level']
    else:
        self['max_level_reached'] = max_children_level_reached



def should_exclude_field_heuristic(variable_record):
    field_exclude = False
    if (variable_record['attributes']['data_type'] if variable_record['attributes']['object_type_value']=='0' else '4') == '0': # info item, skip, 4 = "object"
        field_exclude = True
    if util_var_functions.sanitize_item_name(variable_record['name'])==util_var_functions.sanitize_item_name('NavButtonSelect'):
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
    if 'parent' in record and record['parent']:
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

def get_recursive_prop_shortname(variable_record):
    field_prop_shortname = None
    if variable_record['name']:
        if 'shortname' in variable_record['properties']:
            field_prop_shortname = variable_record['properties']['shortname']
        if not field_prop_shortname:
            parent_path, _ = util_var_functions.extract_field_name(variable_record['name'])
            if parent_path:
                return get_recursive_prop_shortname(variable_record['parent'])
    return field_prop_shortname

def find_final_complex_name(field_prop_shortname,variable_record):
    parent_path, field_name = util_var_functions.extract_field_name(variable_record['name'])
    if parent_path:
        return find_final_complex_name(field_name if not check_if_improper_name(field_name) and not field_prop_shortname else '',variable_record['parent'],) + ( '_'+field_prop_shortname if field_prop_shortname else '' )
    else:
        return variable_record['name'] + '_' + field_prop_shortname

def find_final_short_name_fallback(variable_record):
    if variable_record['name']=='':
        return None
    field_prop_shortname = variable_record['properties']['shortname'] if 'shortname' in variable_record['properties'] else ''
    
    parent_path, field_name = util_var_functions.extract_field_name(variable_record['name'])
    siblings = []
    siblings_including_this_field = []
    if 'parent' in variable_record:
        for  var_record in variable_record['parent']['fields']:
            if not (var_record['name']==variable_record['name']):
                siblings.append(var_record)
            siblings_including_this_field.append(var_record)
    
    parent_variable_record = variable_record['parent'] if 'parent' in variable_record else None

    is_bad_name = False
    is_bad_name = is_bad_name or not field_prop_shortname
    is_bad_name = is_bad_name or check_if_improper_name(field_prop_shortname)
    already_used = field_prop_shortname in [ (f['properties']['shortname'] if 'shortname' in f['properties'] else '') for _,f in siblings ]
    is_bad_name = is_bad_name or already_used

    if is_bad_name:
        if not parent_path:
            return field_name
        elif len(siblings)==0:
            return find_final_short_name_fallback(parent_variable_record)
        elif not check_if_improper_name(field_name) and variable_record['name']==siblings_including_this_field[0]['name']:
            return find_final_short_name_fallback(parent_variable_record)
        else:
            return find_final_short_name_fallback(parent_variable_record) + '_' + ( field_prop_shortname if field_prop_shortname else field_name )
    else:
        return field_prop_shortname






def read_variable_spss_properties(variable_record):
    if not(variable_record['type']=='variable'):
        return
    result = {
        'comment': None,
        'include': '',
    }
    should_skip = False
    if not should_skip:
        should_skip = should_skip or should_exclude_field_heuristic(variable_record)
        if should_skip:
            result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'skip - not a data variable'
    if not should_skip:
        should_skip = should_skip or should_exclude_field_removed_properties(variable_record)
        if should_skip:
            result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'skip - SavRemove=true'
    if not should_skip:
        should_skip = should_skip or (variable_record['variable_type']=='loop' or variable_record['variable_type']=='grid' or variable_record['variable_type']=='block')
        if should_skip:
            result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'skip - loop of block - definitions should be only applied to its fields'
    if not should_skip:
        should_skip = should_skip or not aa_logic_replicate.should_process_short_name(variable_record)
        if should_skip:
            result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'skip - we replicated AA logic and it indicated False - maybe a system variable or has no case data...'
    if not should_skip:
        field_levels = []
        q = variable_record
        if 'level' in q:
            field_levels.append(q['level'])
        while 'parent' in q:
            q = q['parent']
            if 'level' in q and q['level']>0:
                field_levels.insert(0,q['level'])
        item_has_shortname = not not get_recursive_prop_shortname(variable_record)
        should_skip = should_skip or not item_has_shortname
        if should_skip:
            result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'skip - shortname not found'
        if not should_skip:
            result['include'] = 'x'
            result['shortname'] = None
            try:
                result['shortname'] = aa_logic_replicate.replicate_read_shortnames_logic(variable_record)
            except aa_logic_replicate.AAFailedFindShortnameException:
                result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'Err: failed to read shortname in the style of AA'
                result['shortname'] = find_final_short_name_fallback(variable_record)
            
            if not re.match(r'^\s*?[a-zA-Z\$].*?',result['shortname']):
                raise Exception('Suggested shortname is invalid: {s}'.format(s=result['shortname']))

            levels_count = 0
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
                if not '<@>' in result['shortname']:
                    result['shortname'] = result['shortname'] + '<@>'
                result['shortname'] = result['shortname'].replace('<@>','<@>_[L{d}z3]'.format(d=d))
                levels_count = levels_count + 1
                # if d<=2:
                #     if not(map_data['Question L{d}'.format(d=d)]):
                #         # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                #         result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])
            result['shortname'] = result['shortname'].replace('<@>','')
            
            levels_count = 0
            result['label'] = variable_record['label']
            if 0 in field_levels:
                d = 0
                result['label'] = result['label'] + ' - {{L{d}}}'.format(d=d)
                levels_count = levels_count + 1
                # if d<=2:
                #     if not(map_data['Question L{d}'.format(d=0)]):
                #         # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                #         result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])
            for d in [m for m in field_levels if m!=0]:
                # TODO:
                # AA logic is the following:
                # if category is inserted before question name (it's not L0, it's of any higher level)
                # and it has a comma (",") in its label,
                # then this part is enclosed with single quotes
                # it does not apply to ALL categories - categories as normal stubs or categories coming as L0 (that become parts of a multi-punch variable) should not have these single quotes added
                # but categories of loops should!
                # I know, I'll update process_row_category()
                result['label'] = '{{L{d}}}{sep}{rest}'.format(d=d,rest=result['label'],sep=(' : ' if d==[m for m in field_levels if m!=0][0] else ', '))
                levels_count = levels_count + 1
                # if d<=2:
                #     if not(map_data['Question L{d}'.format(d=d)]):
                #         # raise Exception('levels check was not passes, detected {a} when iterating in mdd but int the map it\'s {b}'.format(a=levels_count,b=map_data['Level']))
                #         result['comment'] = ( result['comment'] + '; ' if result['comment'] else '' ) + 'WARNING: levels check mismatch, adding level L{d} but the column Question L{d} is blank ({q})'.format(d=d,q=map_data['Question L{d}'.format(d=d)])
    return result



def read_category_spss_properties(variable_record):
    analysisvalue = variable_record['properties']['value'] if 'value' in variable_record['properties'] else ''
    if not re.match(r'^\s*?$',analysisvalue):
        try:
            analysisvalue = float(analysisvalue)
            analysisvalue_closest_whole = int(round(analysisvalue))
            if abs(analysisvalue-analysisvalue_closest_whole)<0.001:
                analysisvalue = analysisvalue_closest_whole
        except Exception:
            pass
    return {
        'value': analysisvalue,
    }




def update_spss_properties(self):
    result = {
        'comment': 'item not processed, unrecognized type',
    }
    if self['type'] == 'variable':
        result = read_variable_spss_properties(self)
    elif self['type'] == 'category':
        result = read_category_spss_properties(self)
    self['spss_properties'] = result



variable_record_extend_methods = {
    'update_levels': update_levels,
    'detect_var_type_by_attrs': detect_var_type_by_attrs,
    'update_spss_properties': update_spss_properties,
}

