

import re


# this file includes functions that replicate logic from AA





if __name__ == '__main__':
    # run as a program
    import util_var_functions
elif '.' in __name__:
    # package
    from . import util_var_functions
else:
    # included with no parent package
    import util_var_functions



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
















# repeating the same logic that wenhad in AA:
def should_process_short_name(record):
    # If (question.IsSystem) Or (question.DataType = DataTypeConstants.mtNone) Or (question.HasCaseData = False) Or (question.Properties(S_CUSTOM_PROPERTY_REMOVE_VARIABLE) = True) Then
    if (
           ( 'is_system' in record['attributes'] and check_val_txt_true(record['attributes']['is_system']) )
        or ( 'data_type' in record['attributes'] and check_val_txt(record['attributes']['data_type'],'0') )
        or ( 'has_case_data' in record['attributes'] and check_val_txt(record['attributes']['has_case_data'],'false') )
        or ( 'SavRemove' in record['properties'] and check_val_txt_true(record['properties']['SavRemove']) )
    ):
        return False
    return True



# 'Returns true if Object is a Numeric Grid
# 'Returns false otherwise
# 'MK Modified Definition to Exclude Dummy Var, and Allow for Single Field Numeric or Text Grids (without Iterations)
def check_is_numeric_grid(record):
#     Dim oField
#     CheckIsNumericGrid = False
#     On Error GoTo ErrorHandler
#     With question
#         If (.ObjectTypeValue = 1 And .Fields.Count > 0) Then
#             CheckIsNumericGrid = True
#             For Each oField In .Fields
#                 If oField.ObjectTypeValue = 1 Then
#                     'Handling for Grids?
#                     CheckIsNumericGrid = False
#                 Else
#                     If (oField.DataType <> &H6 And oField.DataType <> &H1 And LCase(oField.Name) <> "dummy") Then CheckIsNumericGrid = False
#                 End If
#             Next
#         Else
#         End If
#     End With
#     On Error GoTo 0
#     Exit Function
# ErrorHandler:
#     CheckIsNumericGrid = False
#     On Error GoTo 0
    result = False
    if check_val_txt(record['attributes']['object_type_value'],'1') and len(record['fields'])>0:
        result = True
        for child_record in record['fields']:
            if check_val_txt(child_record['attributes']['object_type_value'],'1'):
                result = False # this is not entirely clear to me but I am trying to replicate older logic; why are we only checking for nested loops but not other types?
            _, field_name = util_var_functions.extract_field_name(child_record['name'])
            if util_var_functions.sanitize_item_name(field_name)=='dummy':
                continue # this is also not entirely clear; if we have a loop with the only "dummy" field it will be classified as numeric grid? really?
            if check_val_txt(child_record['attributes']['object_type_value'],'0'):
                if check_val_txt(child_record['attributes']['data_type'],'1') or check_val_txt(child_record['attributes']['data_type'],'6'):
                    # '1' is 'long' and '6' is 'double' - checking for these 2 types; '2' is 'text'
                    pass
                else:
                    result = False
    return result



# 'MK Added based on Excel Author Implementation
# 'Returns true if Object is a Text Grid
# 'Returns false otherwise
def check_is_text_grid(record):
# Function CheckIsTextGrid(question)
#     Dim oField
#     CheckIsTextGrid = False
#     On Error GoTo ErrorHandler
#     With question
#         If (.ObjectTypeValue = 1 And .Fields.Count > 0) Then
#             CheckIsTextGrid = True
#             For Each oField In .Fields
#                 If oField.ObjectTypeValue = 1 Then
#                     'Handling for Grids?
#                     CheckIsTextGrid = False
#                 Else
#                     'Text = &H2
#                     If (oField.DataType <> &H2 And LCase(oField.Name) <> "dummy") Then CheckIsTextGrid = False
#                 End If
#             Next
#         Else
#         End If
#     End With
#     On Error GoTo 0
#     Exit Function
# ErrorHandler:
#     CheckIsTextGrid = False
#     On Error GoTo 0
# End Function
    result = False
    if check_val_txt(record['attributes']['object_type_value'],'1') and len(record['fields'])>0:
        result = True
        for child_record in record['fields']:
            if check_val_txt(child_record['attributes']['object_type_value'],'1'):
                result = False # still not clear, see comment in check_is_numeric_grid
            else:
                _, field_name = util_var_functions.extract_field_name(child_record['name'])
                if util_var_functions.sanitize_item_name(field_name)=='dummy':
                    continue # this is also not entirely clear; if we have a loop with the only "dummy" field it will be classified as numeric grid? really?
                if check_val_txt(child_record['attributes']['object_type_value'],'0'):
                    if check_val_txt(child_record['attributes']['data_type'],'2'):
                        # '2' is 'text'; '1' is 'long' and '6' is 'double'
                        pass
                    else:
                        result = False
    return result



# 'Returns true if object is a MixedGrid
# 'For now, allowing NumericGrids to ALSO be considered here
# 'In logic above, simply check for MixedGrids AFTER checking for numeric grids
# 'Include in function that the 2+ fields are Not _Factor and Not _Info
def check_is_mixed_grid(record):
# Function CheckIsMixedGrid(question)
#     Dim oField, validCounter
#     validCounter = 0
#     CheckIsMixedGrid = False
#     On Error GoTo ErrorHandler
#     With question
#         If (.ObjectTypeValue = 1 And .Fields.Count > 1) Then
#             For Each oField In .Fields
#                 If oField.ObjectTypeValue = 1 Then
#                     'Handling for Grids?
#                 Else
#                     If (oField.DataType <> &H0 And oField.Properties("IsFactorVariable") <> True) Then
#                         validCounter = validCounter + 1
#                     End If
#                 End If
#             Next
#             If validCounter > 1 Then CheckIsMixedGrid = True
#         Else
#         End If
#     End With
#     On Error GoTo 0
#     Exit Function
# ErrorHandler:
#     CheckIsMixedGrid = False
#     On Error GoTo 0
# End Function
    # this does not make sense
    return False



# Function CheckIsClassOrBlock(oField)
def check_is_class_or_block(record):
#     On Error GoTo ErrHandler
#     If oField.ObjectTypeValue = 3 Then
#         CheckIsClassOrBlock = True
#     End If
#     Exit Function
# ErrHandler:
#     CheckIsClassOrBlock = False
# End Function
    return check_val_txt(record['attributes']['object_type_value'],'3')



# Function CheckIsCategoricalGrid(oField)
def check_is_categorical_grid(record):
#     Dim oSubField
#     CheckIsCategoricalGrid = True
#     On Error GoTo ErrHandler
#     'NOTE: MK Modified to only work for one categorical inner field, otherwise, it should be treated like a regular Array
#     If oField.Fields.Count = 1 Then
#         For Each oSubField In oField.Fields
#             If oSubField.DataType <> DataTypeConstants.mtCategorical Then
#                 CheckIsCategoricalGrid = False
#                 Exit Function
#             End If
#         Next
#     Else
#         CheckIsCategoricalGrid = False
#     End If
#     Exit Function
# ErrHandler:
#     CheckIsCategoricalGrid = False
# End Function
    def should_skip(field_record):
        if 'data_type' in field_record['attributes'] and check_val_txt(field_record['attributes']['data_type'],'0'):
            return True
        _, field_name = util_var_functions.extract_field_name(field_record['name'])
        if util_var_functions.sanitize_item_name(field_name)=='dummy':
            return True
        return False
    result = False
    if (check_val_txt(record['attributes']['object_type_value'],'1')) or (check_val_txt(record['attributes']['object_type_value'],'2')):
        fields = [ f for f in record['fields'] if not should_skip(f) ]
        if len(fields)==1:
            if check_val_txt(fields[0]['attributes']['object_type_value'],'0') and check_val_txt(fields[0]['attributes']['data_type'],'3'):
                result = True
    return result



# Function CheckIsNumericOrTextGrid(question)
#     CheckIsNumericOrTextGrid = CheckIsNumericGrid(question) Or CheckIsTextGrid(question)
# End Function
def check_is_numeric_or_text_grid(q):
    return check_is_numeric_grid(q) or check_is_text_grid(q)



# Function IsBipolarCategory(question)
#     On Error GoTo ErrHandler
#     IsBipolarCategory = (LCase(question.Parent.Properties("QType")) = "bipolar")
#     Exit Function
# ErrHandler:
#     IsBipolarCategory = False
# End Function





class AAFailedFindShortnameException(Exception):
    """AAFailedFindShortnameException"""
def replicate_read_shortnames_logic(record):
    def trim(s):
        if s==0:
            return trim('0')
        if not s:
            return ''
        return re.sub(r'^\s*','',re.sub(r'\s*$','',s))
    def sanitize_numeric_short_name_with_z3(s):
        def append_zeros(s):
            if len(s)<3:
                s = '000'[0:3-len(s)] + s
            return s
        s = re.sub(r'^\s*?(\d+)(?:\.0*?)?\s*?$',lambda m: append_zeros(m[1]),s,flags=re.I|re.DOTALL)
        return s
    try:
        assert record['attributes']['object_type_value']=='0'
        has_parent = not not record['parent']
        if not has_parent:
            result = trim(record['properties']['shortname']) if 'shortname' in record['properties'] else None
            if not result:
                raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
            return result
        else:
            if 'parent' in record and record['parent'] and not(record['parent']['name']=='') and check_is_numeric_or_text_grid(record['parent']):
                if 'shortname' not in record['properties'] or not re.match(r'^\s*?(\d+)(?:\.0*?)?\s*?$',record['properties']['shortname']):
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                result_part1 = trim(record['parent']['properties']['shortname']) if 'parent' in record and 'properties' in record['parent'] and 'shortname' in record['parent']['properties'] and not not trim(record['parent']['properties']['shortname']) else trim(record['parent']['name'])
                result_part2 = trim(sanitize_numeric_short_name_with_z3(trim(record['properties']['shortname'])))
                if not result_part1:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                if not result_part2:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                return '{p1}{add}{p2}'.format(p1=result_part1,p2=result_part2,add='<@>_')
            elif 'parent' in record and record['parent'] and not(record['parent']['name']=='') and check_is_categorical_grid(record['parent']):
                result = None
                try:
                    result = trim(record['parent']['properties']['shortname'])
                except KeyError:
                    pass
                if not result:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                return result
            else:
                result = trim(record['properties']['shortname']) if 'shortname' in record['properties'] else None
                if not not result and re.match(r'^\s*?\d+\s*?$',result):
                    result_part1 = trim(record['parent']['properties']['shortname']) if 'parent' in record and 'properties' in record['parent'] and 'shortname' in record['parent']['properties'] and not not trim(record['parent']['properties']['shortname']) else trim(record['parent']['name'])
                    result_part2 = trim(sanitize_numeric_short_name_with_z3(trim(record['properties']['shortname'])))
                    if not result_part1:
                        raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                    if not result_part2:
                        raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                    result = '{p1}{add}{p2}'.format(p1=result_part1,p2=result_part2,add='<@>_')
                if not result:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                return result
    except AAFailedFindShortnameException as e:
        is_helper_field = False
        if 'is_helper_field' in record['attributes'] and check_val_txt(record['attributes']['is_helper_field'],'true'):
            is_helper_field = True
        if has_parent and is_helper_field:
            parent_shortname = replicate_read_shortnames_logic(record['parent'])
            _, field_name = util_var_functions.extract_field_name(record['name'])
            if False:
            # if '<@>' in parent_shortname:
                # matches = re.match(r'^(.*?)(<@>)(.*?$',parent_shortname,flags=re.I|re.DOTALL)
                # result_part1 = trim(matches[1])
                # result_part2 = trim(matches[3])
                # result_partiter = trim(field_name)
                # if not result_part1:
                #     raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                # if not result_part2:
                #     raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                # return '{p1}{future_iters_add}{iter_add}{p2}'.format(p1=result_part1,p2=result_part2,add='<@>_')
                pass
            else:
                result_part1 = trim(parent_shortname)
                result_part2 = trim(field_name)
                if not result_part1:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                if not result_part2:
                    raise AAFailedFindShortnameException('Failed to find shortname: {s}'.format(s=record['name']))
                return '{p1}{add}{p2}'.format(p1=result_part1,p2=result_part2,add='_')
        else:
            raise e



# def list_loop_through_variables_logic(record, is_numeric_or_text_grid, numeric_or_text_grid_text, short_name_dict, global_found_errors, application, xldoc, xlworksheet, xlcurrentrow):
#     if check_val_txt(record['attributes']['object_type_value'],'0'):
#         # 'Consider adding Conditional Logging here if it returns false (for now handilng within the function)
#         # 'If the question is the ONLY Field of a Grid, then pass the Question.Parent.Parent to the function.
#         # If question.LevelDepth > 1 Then
#         if record['parent']:
#             if check_is_numeric_or_text_grid(record['parent']):
#                 pass
#             # 'NOTE: MK Modified to deal with GV Categoricals vs. Categorical Arrays with Multiple Fields
#             # If CheckIsCategoricalGrid(question.Parent.Parent) Then
#             if check_is_categorical_grid(record['parent']):
#                 # 'If Categorical Grid, then Don't list Array, otherwise adds duplicate
#                 # 'xlCurrentRow = ListAlias(Question.Parent.Parent, IsNumericOrTextGrid, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#                 return list_alias(record['parent'], is_numeric_or_text_grid, numeric_or_text_grid_text, short_name_dict, application, xldoc, xlworksheet, xlcurrentrow )
#             else:
#                 # xlCurrentRow = ListAlias(question, IsNumericOrTextGrid, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#                 return list_alias(record, is_numeric_or_text_grid, numeric_or_text_grid_text, short_name_dict, application, xldoc, xlworksheet, xlcurrentrow )
#         else:
#             # xlCurrentRow = ListAlias(question, IsNumericOrTextGrid, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#             return list_alias(record, is_numeric_or_text_grid, numeric_or_text_grid_text, short_name_dict, application, xldoc, xlworksheet, xlcurrentrow )
                
#     elif check_val_txt(record['attributes']['object_type_value'],'1'):
#         # 'Adding handling for NumericGrids and TextGrids
#         # If question.Fields.Count > 0 Then
#         #     FoundNumericOrTextGrid = CheckIsNumericOrTextGrid(question)
#         #     If (FoundNumericOrTextGrid) Then
#         #         'Send top-level As well
#         #         xlCurrentRow = ListAlias(question, False, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         #         For Each oField In question.Fields
#         #             xlCurrentRow = ListAlias(oField, True, oField.Properties("shortname"), shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         #         Next
#         #     Else
#         #         'Send top-level As well
#         #         xlCurrentRow = ListAlias(question, IsNumericOrTextGrid, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         #         xlCurrentRow = ListLoopThruVariables(question.Fields, FoundNumericOrTextGrid, "", shortNameDict, globalFoundErrors, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         #     End If
#         # Else
#         #     xlCurrentRow = ListLoopThruVariables(question.Fields, False, "", shortNameDict, globalFoundErrors, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         # End If
#         pass

#     #  'Grids are No Longer Supported
#     elif check_val_txt(record['attributes']['object_type_value'],'2'):
#         #  Case 2 'Grid
#         #  '   MsgBox S_ERROR_GRIDS_NOT_SUPPORTED, vbOKOnly, "Invalid Metadata Structure Found"
#         #  '  xlCurrentRow = ListLoopThruVariables(Question.Fields, False, "", shortNameDict, globalFoundErrors, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         pass

#     elif check_val_txt(record['attributes']['object_type_value'],'3'):
#         #  Case 3 ' Class (Block)
#         # xlCurrentRow = ListLoopThruVariables(question.Fields, False, "", shortNameDict, globalFoundErrors, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         # return list_loop_through_variables_logic(question.Fields, False, "", shortNameDict, globalFoundErrors, Application, xlDoc, xlWorksheet, xlCurrentRow)
#         pass



# # Function ListAlias(question, IsNumericOrTextGrid, NumericOrTextGridText, shortNameDict, Application, xlDoc, xlWorksheet, xlCurrentRow)
# def list_alias(question, is_numeric_or_text_grid, numeric_or_text_grid_text, short_name_dict, application, xldoc, xlworksheet, xlcurrentrow):
# #     Dim mVariable, MyAlias, MySubAliases
# #     Dim varCat, catValue
# #     Dim shortname, Iteration, IterationArray, IterationCount, IterationText
# #     Dim Parent, tempVariable, intCount
# #     Dim textValue, textAliasValue
# #     Dim tempAliasValue, tempNumGridAliasValue
# #     Dim validateStatus
# #     validateStatus = True
# #     '-----------------------------------------------------------------------------------------------------------------------------------
# #     'Question-Level Handling
# #     'If the Question Should be processed, and has a Short Name, verify that it is unique
# #     'If it is Unique and Non-Blank, add to dictionary, with Dimensions Name as the Value
# #     If ShouldProcessShortName(question) Then
# #         'If it's an array, need to check ShortNames at the VariableInstance level (with special handling)
# #         'Numeric Grid handling
# #         If (IsNumericOrTextGrid) Then
# #             shortname = NumericOrTextGridText
# #             If Len(NumericOrTextGridText) > 0 Then
# #                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
# #             Else
# #                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, "", "Missing shortname Property for Numeric Grid " & question.Name, IsNumericOrTextGrid)
# #             End If
# #         Else
# #             'Others
# #             If (question.Properties("shortname")) > 1 Then
# #                 shortname = question.Properties("shortname")
# #             Else
# #                 shortname = question.Properties("shortname", "Question")
# #             End If
# #             If question.IsSystem = False Then
# #                 If Len(shortname) > 0 Then
# #                     If shortNameDict.Exists(shortname) Then
# #                         If shortNameDict(shortname) <> question.Name Then
# #                             'If it's an Array, check the Parent Parent Name
# #                             'Using Question.Name = "" as a surrogate (any other ideas?)
# #                             If question.Name = "" Then
# #                                 If shortNameDict.item(shortname) <> question.Parent.Parent.Name Then
# #                                     'MsgBox ("Found duplicate Short Name (" & shortname & ") " & Question.Name & " (" & shortNameDict.Item(shortname) & ")")
# #                                     validateStatus = False
# #                                     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Found duplicate Short Name (" & shortname & ") " & question.Name & " (" & shortNameDict.item(shortname) & ")", IsNumericOrTextGrid)
# #                                 Else
# #                                     shortNameDict.Add shortname, question.Parent.Parent.Name
# #                                     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
# #                                 End If
# #                             Else
# #                                 'MsgBox ("Found duplicate Short Name (" & shortname & ") " & Question.Name & ", (" & shortNameDict.Item(shortname) & ")")
# #                                 validateStatus = False
# #                                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Found duplicate Short Name (" & shortname & ") " & question.Name & ", (" & shortNameDict.item(shortname) & ")", IsNumericOrTextGrid)
# #                             End If
# #                         Else
# #                         End If
# #                     Else
# #                         shortNameDict.Add shortname, question.Name
# #                         xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
# #                     End If
# #                 Else
# #                     'Handling the Missing Names at the variable level to get more specificity
# #                     'Msgbox("Missing Short Name at " & Question.Name)
# #                     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Missing Short Name at " & question.Name, IsNumericOrTextGrid)
# #                 End If
# #             End If
# #         End If
# #     Else
# #     End If
# # ListAlias = xlCurrentRow
# # End Function
#     m_variable = None
#     my_alias = None
#     my_sub_alias = None
#     var_cat = None
#     cat_value = None
#     shortname = None
#     iteration = None
#     iteration_array = None
#     iteration_count = None
#     iteration_text = None
#     parent = None
#     temp_variable = None
#     int_count = None
#     text_value = None
#     text_alias_value = None
#     temp_alias_value = None
#     temp_num_grid_alias_value = None
#     validate_status = True
#     # '-----------------------------------------------------------------------------------------------------------------------------------
#     # 'Question-Level Handling
#     # 'If the Question Should be processed, and has a Short Name, verify that it is unique
#     # 'If it is Unique and Non-Blank, add to dictionary, with Dimensions Name as the Value
#     # If ShouldProcessShortName(question) Then
#     if should_process_short_name(question):
#         # 'If it's an array, need to check ShortNames at the VariableInstance level (with special handling)
#         # 'Numeric Grid handling
#         # If (IsNumericOrTextGrid) Then
#         if is_numeric_or_text_grid:
#             # shortname = NumericOrTextGridText
#             shortname = numeric_or_text_grid_text
#             if len(numeric_or_text_grid_text)>0:
#                 pass
#             else:
#                 pass
#             # If Len(NumericOrTextGridText) > 0 Then
#             #     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
#             # Else
#             #     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, "", "Missing shortname Property for Numeric Grid " & question.Name, IsNumericOrTextGrid)
#             # End If
#         else:
#     #     Else
#     #         'Others
#     #         If (question.Properties("shortname")) > 1 Then
#     #             shortname = question.Properties("shortname")
#     #         Else
#     #             shortname = question.Properties("shortname", "Question")
#     #         End If
#     #         If question.IsSystem = False Then
#     #             If Len(shortname) > 0 Then
#     #                 If shortNameDict.Exists(shortname) Then
#     #                     If shortNameDict(shortname) <> question.Name Then
#     #                         'If it's an Array, check the Parent Parent Name
#     #                         'Using Question.Name = "" as a surrogate (any other ideas?)
#     #                         If question.Name = "" Then
#     #                             If shortNameDict.item(shortname) <> question.Parent.Parent.Name Then
#     #                                 'MsgBox ("Found duplicate Short Name (" & shortname & ") " & Question.Name & " (" & shortNameDict.Item(shortname) & ")")
#     #                                 validateStatus = False
#     #                                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Found duplicate Short Name (" & shortname & ") " & question.Name & " (" & shortNameDict.item(shortname) & ")", IsNumericOrTextGrid)
#     #                             Else
#     #                                 shortNameDict.Add shortname, question.Parent.Parent.Name
#     #                                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
#     #                             End If
#     #                         Else
#     #                             'MsgBox ("Found duplicate Short Name (" & shortname & ") " & Question.Name & ", (" & shortNameDict.Item(shortname) & ")")
#     #                             validateStatus = False
#     #                             xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Found duplicate Short Name (" & shortname & ") " & question.Name & ", (" & shortNameDict.item(shortname) & ")", IsNumericOrTextGrid)
#     #                         End If
#     #                     Else
#     #                     End If
#     #                 Else
#     #                     shortNameDict.Add shortname, question.Name
#     #                     xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "NONE", IsNumericOrTextGrid)
#     #                 End If
#     #             Else
#     #                 'Handling the Missing Names at the variable level to get more specificity
#     #                 'Msgbox("Missing Short Name at " & Question.Name)
#     #                 xlCurrentRow = LogExcelShortNames(Application, xlDoc, xlWorksheet, xlCurrentRow, question, question.FullName, shortname, "Missing Short Name at " & question.Name, IsNumericOrTextGrid)
#     #             End If
#     #         End If
#     #     End If
#     # End If
#     return xlcurrentrow



# 'List shortname information in the Excel
# 'Will add code here that takes the starting point and iterates and lists the necessary information in the Excel
# 'It will return the new Row to be used as a pass back

# 'Starting with handling of ShortNames
# 'Include conditioanl adding of Final_ShortName column (one more to the right) if the shortname is there
# Function LogExcelShortNames(Application, xlDoc, xlWorksheet, xlStartRow, question, QuestionName, shortname, Description, IsNumericOrTextGrid)
#     Dim xlCurrentRow
#     xlCurrentRow = xlStartRow
    
#     With xlWorksheet
#         .Cells(xlStartRow, 1).Value = WriteType(question, IsNumericOrTextGrid)
#         .Cells(xlStartRow, 2).Value = Description
#         .Cells(xlStartRow, 3).Value = QuestionName
#         .Cells(xlStartRow, 4).Value = shortname
#         If shortname = "" Then
#             .Cells(xlStartRow, 5).Interior.Color = vbYellow
#         Else
#         End If
#         .Cells(xlStartRow, 5).Value = shortname
#     End With
    
#     xlCurrentRow = xlCurrentRow + 1
    
#     LogExcelShortNames = xlCurrentRow

# End Function
