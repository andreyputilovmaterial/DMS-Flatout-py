

import sys # for error reporting



if __name__ == '__main__':
    # run as a program
    import util_var_functions
    import prefill_flatout_template
elif '.' in __name__:
    # package
    from . import util_var_functions
    from . import prefill_flatout_template
else:
    # included with no parent package
    import util_var_functions
    import prefill_flatout_template


def detect_columns_upd_variables_df(map_df):
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
        return {
            'comment':  columns_last_7[0],
            'include':  columns_last_7[1],
            'exclude':  columns_last_7[2],
            'shortname':     columns_last_7[3],
            'label':    columns_last_7[4],
            'format':   columns_last_7[5],
            'markup':   columns_last_7[6],
        }
    except:
        raise Exception('Last 7 columns on \'variables\' sheet should include words ">>>", "include", "exclude", "name"... This test was not passed. Exiting.')

def detect_columns_upd_categories_df(map_df):
    columns_last_6 = ['{m}'.format(m=m) for m in map_df.columns[-6:]]
    try:
        assert len(columns_last_6)==6
        assert '>>>' in columns_last_6[0]
        assert '- include' in columns_last_6[1]
        assert '- exclude' in columns_last_6[2]
        assert '- punch' in columns_last_6[3]
        assert '- label' in columns_last_6[4]
        assert '- markup' in columns_last_6[5]
        return {
            'comment':  columns_last_6[0],
            'include':  columns_last_6[1],
            'exclude':  columns_last_6[2],
            'value':     columns_last_6[3],
            'label':    columns_last_6[4],
            'markup':   columns_last_6[5],
        }
    except:
        raise Exception('Last 6 columns on \'variables\' sheet should include words ">>>", "include", "excelude", "name"... This test was not passed. Exiting.')




def validate_spss_prefill_variables(flatout_record,variable_spss_prefilled_properties):
    return True

def validate_spss_prefill_categories(flatout_record,variable_spss_prefilled_properties):
    return True

def lookup_variable_in_variable_records(name_in_flatout_map,variable_records,flatout_data):
    variable_spss_prefilled_properties = {}
    try:
        name_lookup = util_var_functions.sanitize_item_name(name_in_flatout_map)
        if name_lookup not in variable_records:
            raise Exception('matching mdd variable not found: "{name}"'.format(name=name_in_flatout_map))
        variable_record = variable_records[name_lookup]
        # if name_lookup not in flatout_data:
        #     raise Exception('flatout row not found: "{name}"'.format(name=name_in_flatout_map))
        variable_spss_prefilled_properties = variable_record['spss_properties']
        # flatout_record = flatout_data[name_lookup]
        # try:
        #     validate_spss_prefill_variables(flatout_record,variable_spss_prefilled_properties)
        # except Exception as e:
        #     variable_spss_prefilled_properties['comment'] = ( ' ; '+variable_spss_prefilled_properties['comment'] if 'comment' in variable_spss_prefilled_properties and variable_spss_prefilled_properties['comment'] else '' ) + 'validation failed: {e}'.format(e=e)
    except Exception as e:
        variable_spss_prefilled_properties['comment'] = ( ' ; '+variable_spss_prefilled_properties['comment'] if 'comment' in variable_spss_prefilled_properties and variable_spss_prefilled_properties['comment'] else '' ) + 'validation failed: {e}'.format(e=e)
    return variable_spss_prefilled_properties

def lookup_category_in_variable_records(name_variable_in_flatout_map,name_category_in_flatout_map,variable_records,flatout_data):
    category_spss_prefilled_properties = {}
    try:
        name_lookup = util_var_functions.sanitize_item_name('{name_var}.categories[{name_cat}]'.format(name_var=name_variable_in_flatout_map,name_cat=name_category_in_flatout_map))
        if name_lookup not in variable_records:
            raise Exception('matching mdd variable and category not found: variable: "{name_var}", category: "{name_cat}"'.format(name_var=name_variable_in_flatout_map,name_cat=name_category_in_flatout_map))
        category_record = variable_records[name_lookup]
        # if name_lookup not in flatout_data:
        #     raise Exception('flatout row not found: variable: "{name_var}", category: "{name_cat}"'.format(name_var=name_variable_in_flatout_map,name_cat=name_category_in_flatout_map))
        category_spss_prefilled_properties = category_record['spss_properties']
        # flatout_record = flatout_data[name_lookup]
        # try:
        #     validate_spss_prefill_categories(flatout_record,category_spss_prefilled_properties)
        # except Exception as e:
        #     category_spss_prefilled_properties['comment'] = ( ' ; '+category_spss_prefilled_properties['comment'] if 'comment' in category_spss_prefilled_properties and category_spss_prefilled_properties['comment'] else '' ) + 'validation failed: {e}'.format(e=e)
    except Exception as e:
        category_spss_prefilled_properties['comment'] = ( ' ; '+category_spss_prefilled_properties['comment'] if 'comment' in category_spss_prefilled_properties and category_spss_prefilled_properties['comment'] else '' ) + 'validation failed: {e}'.format(e=e)
    return category_spss_prefilled_properties



def prefill(xls, flatout_data, variable_records):
    # header=2 means how many rows to skip above the banner line
    # , index_col='Index' is a possible param but we probably don't need it
    # and ",keep_default_na=False" is needed to address pandas bug (or maybe openpyxl bug, idk) that converts "None" (text) to nothing
    # maybe I'll report it but first I should find the root where it happens and also check if it was already reported, it's really hard to search for word "None" within thousands of submitted issues
    variables_df = xls.parse(sheet_name='variables', header=2, keep_default_na=False).fillna('')
    columns_upd = detect_columns_upd_variables_df(variables_df)
    for row in variables_df.index:
        try:
            name_in_flatout_map = variables_df.loc[row,'Variable']
            try:
                if name_in_flatout_map in prefill_flatout_template.CONFIG_KNOWN_SYSTEM_FIELDS:
                    variable_spss_prefilled_properties = prefill_flatout_template.CONFIG_KNOWN_SYSTEM_FIELDS[name_in_flatout_map]
                else:
                    variable_spss_prefilled_properties = lookup_variable_in_variable_records(name_in_flatout_map,variable_records,flatout_data)
                if 'include' in variable_spss_prefilled_properties:
                    variables_df.loc[row,columns_upd['include']] = variable_spss_prefilled_properties['include']
                else:
                    # keep default value from original flatout map
                    pass
                # if 'exclude' in variable_spss_prefilled_properties:
                #     variables_df.loc[row,columns_upd['exclude']] = variable_spss_prefilled_properties['exclude']
                # else:
                #     # keep default value from original flatout map
                #     pass
                if 'shortname' in variable_spss_prefilled_properties:
                    variables_df.loc[row,columns_upd['shortname']] = variable_spss_prefilled_properties['shortname']
                else:
                    # keep default value from original flatout map
                    pass
                if 'label' in variable_spss_prefilled_properties:
                    variables_df.loc[row,columns_upd['label']] = variable_spss_prefilled_properties['label']
                else:
                    # keep default value from original flatout map
                    pass
                if 'format' in variable_spss_prefilled_properties:
                    variables_df.loc[row,columns_upd['format']] = variable_spss_prefilled_properties['format']
                else:
                    # keep default value from original flatout map
                    pass
                if 'markup' in variable_spss_prefilled_properties:
                    variables_df.loc[row,columns_upd['markup']] = variable_spss_prefilled_properties['markup']
                else:
                    # keep default value from original flatout map
                    pass
                if 'comment' in variable_spss_prefilled_properties and variable_spss_prefilled_properties['comment']:
                    variables_df.loc[row,columns_upd['comment']] = '>>>>>>>>' + ' ' + variable_spss_prefilled_properties['comment']
                else:
                    # keep default value from original flatout map
                    pass
            except Exception as e:
                print('Failed when processing variable {s}'.format(s=name_in_flatout_map),file=sys.stderr)
                raise e
        except Exception as e:
            print('Failed when processing row {s}'.format(s=row),file=sys.stderr)
            raise e
        
    categories_df = xls.parse(sheet_name='cats by vars', header=2, keep_default_na=False).fillna('')
    columns_upd = detect_columns_upd_categories_df(categories_df)
    for row in categories_df.index:
        try:
            name_variable_in_flatout_map = categories_df.loc[row,'Variable']
            name_category_in_flatout_map = categories_df.loc[row,'Category']
            try:
                category_spss_prefilled_properties = lookup_category_in_variable_records(name_variable_in_flatout_map,name_category_in_flatout_map,variable_records,flatout_data)
                if 'include' in category_spss_prefilled_properties:
                    categories_df.loc[row,columns_upd['include']] = category_spss_prefilled_properties['include']
                else:
                    # keep default value from original flatout map
                    pass
                if 'exclude' in category_spss_prefilled_properties:
                    categories_df.loc[row,columns_upd['exclude']] = category_spss_prefilled_properties['exclude']
                else:
                    # keep default value from original flatout map
                    pass
                if 'value' in category_spss_prefilled_properties:
                    categories_df.loc[row,columns_upd['value']] = category_spss_prefilled_properties['value']
                else:
                    # keep default value from original flatout map
                    pass
                if 'label' in category_spss_prefilled_properties:
                    categories_df.loc[row,columns_upd['label']] = category_spss_prefilled_properties['label']
                else:
                    # keep default value from original flatout map
                    pass
                if 'markup' in category_spss_prefilled_properties:
                    categories_df.loc[row,columns_upd['markup']] = category_spss_prefilled_properties['markup']
                else:
                    # keep default value from original flatout map
                    pass
                if 'comment' in category_spss_prefilled_properties and category_spss_prefilled_properties['comment']:
                    categories_df.loc[row,columns_upd['comment']] = '>>>>>>>>' + ' ' + category_spss_prefilled_properties['comment']
                else:
                    # keep default value from original flatout map
                    pass
            except Exception as e:
                print('Failed when processing category {s1}.{s2}'.format(s1=name_variable_in_flatout_map,s2=name_category_in_flatout_map),file=sys.stderr)
                raise e
        except Exception as e:
            print('Failed when processing row {s}'.format(s=row),file=sys.stderr)
            raise e
    
    return variables_df, categories_df

