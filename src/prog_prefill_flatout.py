from datetime import datetime, timezone
import argparse
from pathlib import Path
import json
import pandas as pd





if __name__ == '__main__':
    # run as a program
    import mddread_read
    import mddread_spss_methods
    import flatout_read
    import prefill_flatout
elif '.' in __name__:
    # package
    from . import mddread_read
    from . import mddread_spss_methods
    from . import flatout_read
    from . import prefill_flatout
else:
    # included with no parent package
    import mddread_read
    import mddread_spss_methods
    import flatout_read
    import prefill_flatout









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

    # config = {}

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

    print('Reading mdd data saved in "{file}"...'.format(file=inp_mddscheme_filename))
    inp_mdd_scheme = None
    with open(inp_mddscheme_filename) as f:
        try:
            inp_mdd_scheme = json.load(f)
        except json.JSONDecodeError as e:
            # just a more descriptive message to the end user
            # can happen if the tool is started two times in parallel and it is writing to the same json simultaneously
            raise TypeError('Patch: Can\'t read left file as JSON: {msg}'.format(msg=e))
    variable_records = mddread_read.VariableRecords(inp_mdd_scheme,extend_methods=mddread_spss_methods.variable_record_extend_methods)
    print('Filling variable type for every item...')
    for _, record in variable_records.items():
        record['extend_methods']['detect_var_type_by_attrs']()
    print('Updating levels...')
    variable_records['']['extend_methods']['update_levels']() # start from root, which is at ['']
    print('Reading SPSS properties...')
    for _, record in variable_records.items():
        record['extend_methods']['update_spss_properties']()

    print('Reading flatout map "{file}"...'.format(file=inp_map_filename))
    xls = pd.ExcelFile(inp_map_filename,engine='openpyxl')
    flatout_data = flatout_read.FlatoutMap(xls)
    
    print('And now we\'ll match those 2 together ')
    variables_df, categories_df = prefill_flatout.prefill(xls, flatout_data, variable_records)

    print('{script_name}: saving as "{fname}"'.format(fname=result_final_fname,script_name=script_name))
    with pd.ExcelWriter(result_final_fname) as writer:
        variables_df.to_excel(writer, sheet_name='variables')
        categories_df.to_excel(writer, sheet_name='cats by vars')

    time_finish = datetime.now()
    print('{script_name}: finished at {dt} (elapsed {duration})'.format(dt=time_finish,duration=time_finish-time_start,script_name=script_name))



if __name__ == '__main__':
    entry_point({'arglist_strict':True})
