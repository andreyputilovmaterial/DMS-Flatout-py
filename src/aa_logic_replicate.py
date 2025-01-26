

import re

# this file includes functions that replicate logic from AA


def check_val_txt_true(value_assess):
    # return re.match(r'^\s*?(?:true)\s*?$',value_assess,flags=re.I|re.DOTALL)
    return check_val_txt(value_assess,'true')

def check_val_txt(value_assess,value_compare):
    def trim(s):
        return re.sub(r'^\s*','',re.sub(r'\s*$','',s))
    def sanitize(s):
        s = '{s}'.format(s=s)
        s = trim(s)
        s = s.lower()
        return s
    return sanitize(value_assess)==sanitize(value_compare)


def should_process_short_name(record):
    # repeating the same logic that wenhad in AA:
    # If (question.IsSystem) Or (question.DataType = DataTypeConstants.mtNone) Or (question.HasCaseData = False) Or (question.Properties(S_CUSTOM_PROPERTY_REMOVE_VARIABLE) = True) Then
    if (
           ( 'is_system' in record['attributes'] and check_val_txt_true(record['attributes']['system']) )
        or ( 'data_type' in record['attributes'] and check_val_txt(record['attributes']['data_type'],'0') )
        or ( 'has_case_data' in record['attributes'] and check_val_txt(record['attributes']['has_case_data'],'false') )
        or ( 'SavRemove' in record['properties'] and check_val_txt_true(record['properties']['SavRemove']) )
    ):
        return False
    return True
