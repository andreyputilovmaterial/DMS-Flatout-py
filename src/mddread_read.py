




if __name__ == '__main__':
    # run as a program
    import util_var_functions
elif '.' in __name__:
    # package
    from . import util_var_functions
else:
    # included with no parent package
    import util_var_functions





def _reassign(cb,obj):
    def fn(*args,**kwargs):
        # return method_fn(self,*args,**kwargs)
        return cb(obj,*args,**kwargs)
    return fn

class VariableRecordBase(dict):
    def __init__(self,q):
        def convert_list_to_dict(data_lst):
            result = {}
            for record in data_lst:
                if '(' in record['name']:
                    continue
                result[record['name'].lower()] = record['value']
            return result
        q = {
            **q,
            'properties': convert_list_to_dict(q['properties'] if 'properties' in q else []),
            'attributes':convert_list_to_dict(q['attributes'] if 'attributes' in q else []),
        }
        if 'extend_methods' in q:
            extend_methods_passed = q['extend_methods']
            extend_methods_unreferenced = {}
            for method_name, method_fn in extend_methods_passed.items():
                # def fn(*args,**kwargs):
                #     # return method_fn(self,*args,**kwargs)
                #     return extend_methods_passed[method_name](self,*args,**kwargs)
                # extend_methods_unreferenced[method_name] = fn
                # extend_methods_unreferenced[method_name] = lambda *args,**kwargs: extend_methods_passed[method_name](self,*args,**kwargs)
                extend_methods_unreferenced[method_name] = _reassign(method_fn,self)
            q['extend_methods'] = extend_methods_unreferenced
        return super().__init__(q)




class VariableRootRecord(VariableRecordBase):
    def __init__(self,q):
        return super().__init__(q)

class VariableRecord(VariableRecordBase):
    def __init__(self,q):
        return super().__init__(q)

class CategoryRecord(VariableRecordBase):
    def __init__(self,q):
        return super().__init__(q)




class VariableRecords(dict):
    def __init__(self,inp_mdd_scheme,extend_methods=None):
        mdd_data_records = ([sect for sect in inp_mdd_scheme['sections'] if sect['name']=='fields'])[0]['content']
        variable_records = {}
        for record in mdd_data_records:
            record_name = record['name']
            record_type = util_var_functions.detect_item_type(record_name)
            name_clean = util_var_functions.sanitize_item_name(record_name)
            record['type'] = record_type
            if extend_methods:
                if 'extend_methods' not in record:
                    record['extend_methods'] = {}
                record['extend_methods'] = {**record['extend_methods'],**extend_methods}
            if record_type=='variable':
                parent_path, field_name = util_var_functions.extract_field_name(record_name)
                record['parent'] = variable_records[util_var_functions.sanitize_item_name(parent_path)]
                if not 'fields' in record['parent']:
                    record['parent']['fields'] = []
                item = VariableRecord(record)
                record['parent']['fields'].append(item)
                variable_records[name_clean] = item
            elif record_type=='root':
                record['fields'] = []
                variable_records[''] = VariableRootRecord(record)
            elif record_type=='category':
                variable_name, category_name = util_var_functions.extract_category_name(record_name)
                record['variable'] = variable_records[util_var_functions.sanitize_item_name(variable_name)]
                record['category_name'] = category_name
                if not 'categories' in record['variable']:
                    record['variable']['categories'] = []
                item = CategoryRecord(record)
                record['variable']['categories'].append(item)
                variable_records[name_clean] = item
            else:
                raise Exception('reading variable_records from mdd_read: unrecognized item type: "{name}"'.format(name=record_name))
        return super().__init__(variable_records)






