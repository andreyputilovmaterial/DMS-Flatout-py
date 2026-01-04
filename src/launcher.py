
import argparse
# from pathlib import Path
import traceback






if __name__ == '__main__':
    # run as a program
    from lib.mdmreadpy import read_mdd as prog_read_mdd
    from lib.mdmreadpy.lib.mdmreportpy import report_create as prog_report_create
    import prog_prefill_flatout
elif '.' in __name__:
    # package
    from .lib.mdmreadpy import read_mdd as prog_read_mdd
    from .lib.mdmreadpy.lib.mdmreportpy import report_create as prog_report_create
    from . import prog_prefill_flatout
else:
    # included with no parent package
    from lib.mdmreadpy import read_mdd as prog_read_mdd
    from lib.mdmreadpy.lib.mdmreportpy import report_create as prog_report_create
    import prog_prefill_flatout






def call_read_mdd_program():
    return prog_read_mdd.entry_point({'arglist_strict':False})

def call_report_program():
    return prog_report_create.entry_point({'arglist_strict':False})

def call_prog_prefill_flatout_program():
    return prog_prefill_flatout.entry_point({'arglist_strict':False})






run_programs = {
    'read_mdd': call_read_mdd_program,
    'report': call_report_program,
    'fill-map': call_prog_prefill_flatout_program,
}



def main():
    try:
        parser = argparse.ArgumentParser(
            description="Universal caller of mdmfillmapap-py utilities"
        )
        parser.add_argument(
            #'-1',
            '--program',
            choices=dict.keys(run_programs),
            type=str,
            required=True
        )
        args, args_rest = parser.parse_known_args()
        if args.program:
            program = '{arg}'.format(arg=args.program)
            if program in run_programs:
                run_programs[program]()
            else:
                raise AttributeError('program to run not recognized: {program}'.format(program=args.program))
        else:
            print('program to run not specified')
            raise AttributeError('program to run not specified')
    except Exception as e:
        # the program is designed to be user-friendly
        # that's why we reformat error messages a little bit
        # stack trace is still printed (I even made it longer to 20 steps!)
        # but the error message itself is separated and printed as the last message again

        # for example, I don't write "print('File Not Found!');exit(1);", I just write "raise FileNotFoundErro()"
        print('')
        print('Stack trace:')
        print('')
        traceback.print_exception(e,limit=20)
        print('')
        print('')
        print('')
        print('Error:')
        print('')
        print('{e}'.format(e=e))
        print('')
        exit(1)


if __name__ == '__main__':
    main()


