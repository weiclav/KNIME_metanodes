import numpy as np
def update_annotations(row, columns):
    """
    Function make new column (in the row), where are fused info from selected columns from the row.
    :param row: row from the dataframe
    :param columns: (list of strings), column names
    :return: row of dataframe with added column, where is fused info from selected columns
    """

    # for splitting too long annotations
    row_local = row
    for column in columns:
        output_string = ''
        string_row = row_local[column]
        if isinstance(row_local[column], str):
            if string_row is not None or string_row is not np.nan:
                num_char = len(string_row)
                if num_char > 50:
                    div_num_char = int(num_char / 50)
                    mod_num_char = num_char % 50
                    for i in range(div_num_char):
                        add_string = string_row[(i * 50): ((i + 1) * 50)]
                        output_string = output_string + add_string + '<br>'

                    output_string = output_string + string_row[div_num_char * 50:div_num_char * 50 + mod_num_char]
                else:
                    output_string = string_row
            else:
                output_string = ''
        else:
            output_string = row_local[column]

        row_local[column] = output_string

    row['onhover'] = '<br>'.join([f"{str(column)}: {str(row_local[column])} <br>" if row_local[column] is not None and row_local[column] is not np.nan else f"{str(column)}: {str('')} <br>" for column in columns])

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