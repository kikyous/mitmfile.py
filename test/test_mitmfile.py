import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import mitmfile
from mitmproxy.test import taddons
from collections.abc import Sequence



def test_options_count():
    mf = mitmfile.MitmFile()
    with taddons.context(mf) as tctx:
        tctx.options.add_option("test_option", str, '', 'help msg')
        assert len(tctx.options._options) == 27


def test_option_parse():
    content = '''
    array_str_option foo
    array_str_option bar

    # a comment
    not_exist_option bar

    array_int_option 3
    array_int_option 5
    #array_int_option 6

    array_float_option 2
    array_float_option 3.3

    bool_option n
    bool_option2 1
    '''
    mf = mitmfile.MitmFile()
    with taddons.context(mf) as tctx:
        tctx.options.add_option(
            "array_str_option", Sequence[str], [], 'help msg')
        tctx.options.add_option(
            "array_int_option", Sequence[int], [], 'help msg')
        tctx.options.add_option("array_float_option",
                                Sequence[float], [], 'help msg')
        tctx.options.add_option("bool_option", bool, True, 'help msg')
        tctx.options.add_option("bool_option2", bool, False, 'help msg')
        parsed_options = mf.parse(content)
        assert len(parsed_options) == 5
        assert parsed_options['array_str_option'] == ['foo', 'bar']
        assert parsed_options['array_int_option'] == [3, 5]
        assert parsed_options['array_float_option'] == [2.0, 3.3]
        assert parsed_options['bool_option'] == False
        assert parsed_options['bool_option2'] == True


def test_option_apply():
    mf = mitmfile.MitmFile()
    with taddons.context(mf) as tctx:
        tctx.options.add_option("str_option", str, 'default', 'help msg')
        mf.apply({"str_option": 'foo'})
        assert tctx.options.str_option == 'foo'


def test_option_apply_sequence_with_default_value():
    mf = mitmfile.MitmFile()
    with taddons.context(mf) as tctx:
        tctx.options.add_option("array_str_option", Sequence[str], [
                                'default'], 'help msg')
        mf.apply({"array_str_option": ['foo', 'bar']})
        assert tctx.options.array_str_option == ['foo', 'bar', 'default']
