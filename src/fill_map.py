from datetime import datetime, timezone
import argparse
from pathlib import Path
import json, re
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




def sanitize_map_name_to_mdd_scheme_name(s):
    return re.sub(r'(\w+)\s*?\[\s*?\{?[^\]]*?\s*?\}?\s*?\]',lambda m: '{s}'.format(s=m[1]),s,flags=re.I|re.DOTALL)


def fill(map_df,mdd_scheme):
    print("\nFilling the map...")
    
    rows = map_df.index
    row = None
    print('   starting working on variables sheet...')
    print('   iterating over rows...')
    for row in rows:
        variable_name = map_df.loc[row,'Variable']
        variable_mdd_scheme_name = sanitize_map_name_to_mdd_scheme_name(variable_name)
        processing_last_item = variable_name
        try:
            pass
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
