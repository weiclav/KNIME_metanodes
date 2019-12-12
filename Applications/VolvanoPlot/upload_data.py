import numpy as np
import pandas as pd
from dash.exceptions import PreventUpdate
import base64
import io
import dash_html_components as html

def get_data(contents, filename, separ, col_name_p_value, col_name_logFC):
    """
 Function which define dataframe from upload data and make a edit of dataframe
    :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function upload_data.parse_contents
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :return: dataframe - chnaged
    """
    contents = contents[0]
    filename = filename[0]
    df = parse_contents(contents, filename, separ)
    df_no_nan_local = dataframe_edit(df, col_name_p_value, col_name_logFC)
    return df_no_nan_local


def dataframe_edit(df, col_name_p_value, col_name_logFC):
    """
 Function which edit dataframe from uploaded data for better vizualization, (drop NANs, reset index, defined new column logP)
    :param df: dataframe, where are drop NANs, reset index, defined new column logP
    :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :return: edit dataframe
    """
    # if col_name_p_value is not None or col_name_logFC is not None:
    #     df_no_nan = df.dropna(subset=[col_name_p_value, col_name_logFC])
    #     df_no_nan = df_no_nan.reset_index(drop=True)
    #
    #     if isinstance(df[col_name_logFC][0], str) or col_name_logFC is None:
    #         raise PreventUpdate
    #
    #     if isinstance(df[col_name_p_value][0], str) or not (df[col_name_p_value] >= 0).all(axis=None) or col_name_p_value is None:
    #         raise PreventUpdate
    #
    #     if col_name_logFC == col_name_p_value:
    #         raise PreventUpdate
    #
    #     df_no_nan['logP'] = df_no_nan[col_name_p_value].apply(lambda x: -np.log10(x))
    # else:
    #     raise PreventUpdate
    if col_name_p_value is not None or col_name_logFC is not None:
        df_no_nan = df.dropna(subset=[col_name_p_value, col_name_logFC])
        df_no_nan = df_no_nan.reset_index(drop=True)

        # # df = df[df['id'].apply(lambda x: type(x) in [int, np.int64, float, np.float64])]
        # new= df_no_nan[col_name_p_value].apply(lambda x: type(x))
        # new2 = df_no_nan[col_name_logFC].apply(lambda x: type(x))

        # df_no_nan = df_no_nan.reset_index(drop=True)

        if isinstance(df_no_nan[col_name_logFC][0], str):
            raise PreventUpdate
        elif col_name_logFC is None:
            raise PreventUpdate

        if isinstance(df_no_nan[col_name_p_value][0], str):
            raise PreventUpdate
        elif not (df_no_nan[col_name_p_value] >= 0).all(axis=None):
            raise PreventUpdate
        elif col_name_p_value is None:
            raise PreventUpdate

        if col_name_logFC == col_name_p_value:
            raise PreventUpdate

        df_no_nan['logP'] = df_no_nan[col_name_p_value].apply(lambda x: -np.log10(x))
    else:
        raise PreventUpdate

    return df_no_nan


def parse_contents(contents, filename, separ):
    """
Function read dataframe from uploaded data, use right separator
    :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function upload_data.parse_contents
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :return: dataframe
    """

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    try:
        if 'csv' or 'txt' in filename:
            # Assume that the user uploaded a CSV file
            if separ is None:
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')), sep=separ, engine="python")
            else:
                try:
                    df = pd.read_csv(
                        io.StringIO(decoded.decode('utf-8')), sep=separ)
                except:
                    df = pd.DataFrame()
                    # raise PreventUpdate

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            try:
                df = pd.read_excel(io.BytesIO(decoded))
            except:
                df= pd.DataFrame()
                # raise PreventUpdate
    except Exception as e:
        print(e)
        df = pd.DataFrame()
        return df

    return df
