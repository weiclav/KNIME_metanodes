import numpy as np
def update_annotations(row, columns):
    """
    Function make new column (in the row), where are fused info from selected columns from the row.
    :param row: row from the dataframe
    :param columns: (list of strings), column names
    :return: row of dataframe with added column, where is fused info from selected columns
    """
    row['onhover'] = '<br>'.join([f"{str(column)}: {str(row[column])}" if row[column] is not None and row[column] is not np.nan else f"{str(column)}: {str('')}" for column in columns])
    return row


def call_update_annotation(annotations, df_no_nan_local):

    """
    Function control if annotation is empty or not. Use annotation for selecting rows for fusing in the new column onhover
    :param indices:
    :param annotations: (list), choosed columns in the dropdown
    :param df_no_nan_local: (dataframe), copy of global df_no_nan
    :param dff: new dataframe with added column "onhover"
    :return: (string) - name of column, where are annotations, (dataframe) - new dataframe with added column "onhover" 
    """
    if not annotations:
        annotations_str = None
    else:
        df_no_nan_local = df_no_nan_local.apply(update_annotations, axis=1, columns=annotations)
        annotations_str = 'onhover'
    return [annotations_str, df_no_nan_local]