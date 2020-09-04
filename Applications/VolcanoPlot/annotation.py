import numpy as np
import pandas as pd
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
    :param annotations: (list), choosed columns in the dropdown
    :param df_no_nan_local: (dataframe), copy of global df_no_nan
    :return: (string) - name of column, where are annotations, (dataframe) - new dataframe with added column "onhover"
    """
    if not annotations:
        annotations_str = None
    else:
        df_no_nan_local = df_no_nan_local.apply(update_annotations, axis=1, columns=annotations)
        annotations_str = 'onhover'
    return [annotations_str, df_no_nan_local]

def find_topN(annotations, df, threshold_topN, criterion_topN, input_num_topN, col_name_logFC, col_name_p_value, threshold_logFC):
    """
    Function find out topN proteins and return list of lists with their x and y axis and annotations.
    :param annotations: string - name of column, which values are used to annotate topN proteins
    :param df: dataframe
    :param threshold_topN: string - value used to specify type of threshold to find out topN proteins
    :param criterion_topN: string - value used to specify type of distance metric to find out topN proteins
    :param input_num_topN: number - number of topN proteins
    :param col_name_logFC: string - name of column with values for logFC, graph's x axis
    :param col_name_p_value: string - name of column with values for p-value, graph's y axis
    :param threshold_logFC: list - two numbers, threshold for logFC
    :return: list of lists - x and y axis of topN proteins and it's annotations
    """
    list_axis_x_topN = []
    list_axis_y_topN = []
    list_annot_text = []
    df_filtered = pd.DataFrame()
    if input_num_topN > 0 and annotations:
        if threshold_topN == 'decreased':
            df_filtered = df[df[col_name_logFC] < threshold_logFC[0]]
        elif threshold_topN == 'changed':
            df_filtered = df[df[col_name_logFC] < threshold_logFC[0]]
            df_filtered = df_filtered.append(df[df[col_name_logFC]>threshold_logFC[1]])
        elif threshold_topN == 'increased':
            df_filtered = df[df[col_name_logFC]>threshold_logFC[1]]
        else:
            df_filtered = df

        if criterion_topN and not df_filtered.empty:
            if criterion_topN == 'manhattan':
                df_filtered = df_filtered.apply(manhattan, axis=1, columns=[col_name_logFC, col_name_p_value])
                column = 'manhattan'
            elif criterion_topN == 'euclid':
                df_filtered = df_filtered.apply(euclidian, axis=1, columns=[col_name_logFC, col_name_p_value])
                column = 'euclid'
            elif criterion_topN == 'fc':
                column = [col_name_logFC, col_name_p_value]
            else:
                column = [col_name_p_value, col_name_logFC]

            df_sorted = df_filtered.sort_values(by=column, ascending=False).reset_index(drop=True)
            list_axis_x_topN = df_sorted.loc[0:input_num_topN, col_name_logFC].tolist()
            list_axis_y_topN = df_sorted.loc[0:input_num_topN, col_name_p_value].tolist()
            list_annot_text = df_sorted.loc[0:input_num_topN, annotations].tolist()


    return [list_axis_x_topN, list_axis_y_topN, list_annot_text]

def manhattan(row, columns):
    """
    Function finds out manhattan distance for proteins from x=0 and y=0
    :param row: series - row of protein
    :param columns: list of strings - name of columns for x and y axis in the graph
    :return: row - series with added column with distance
    """
    row['manhattan'] = abs(0 - row[columns[0]]) + abs(0 - row[columns[1]])
    return row

def euclidian(row, columns):
    """
    Function finds ou euclidian distance for proteins from x=0 and y=0
    :param row: series - row of protein
    :param columns:  list of strings - name of columns for x and y axis in the graph
    :return: row - series with added one column with distance
    """
    row['euclid'] = np.sqrt((0 - row[columns[0]])**2 + (0 - row[columns[1]])**2)
    return row