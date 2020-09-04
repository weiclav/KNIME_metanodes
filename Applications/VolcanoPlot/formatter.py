import pandas as pd


def table_formatting(df_no_nan_local, num_columns_option):
    """
    Function define type of columns and specify format for numbers.

    :param df_no_nan_local: dataframe - data
    :param num_columns_option: string - name of columns specified by user in the form's dropdown
    :return: dictionary with specified type and format for all columns in data
    """
    dict_type_format = {}

    if num_columns_option:
        df_no_nan_local[num_columns_option] = df_no_nan_local[num_columns_option].apply(pd.to_numeric, errors='coerce')
    else:
        df_no_nan_local = df_no_nan_local.apply(pd.to_numeric, errors='ignore')

    numeric_columns = df_no_nan_local.select_dtypes(include='number')
    for i in numeric_columns.columns:
        dict_type_format[i] = {'type': 'numeric', 'format': {'specifier': '.4~g'}}

    datetime_columns = df_no_nan_local.select_dtypes(include='datetime')
    for i in datetime_columns.columns:
        dict_type_format[i] = {'type': 'datetime'}

    string_columns = df_no_nan_local.select_dtypes(include='object')
    for i in string_columns.columns:
        dict_type_format[i] = {'type': 'text'}

    bool_columns = df_no_nan_local.select_dtypes(include='bool')
    for i in bool_columns.columns:
        dict_type_format[i] = {'type': 'text'}

    list_columns_with_type = dict_type_format.keys()
    list_columns_all = df_no_nan_local.columns.tolist()
    missing_columns = set(list_columns_all) - set(list_columns_with_type)

    if missing_columns:
        for i in missing_columns:
            dict_type_format[i] = {'type': 'text'}

    return dict_type_format