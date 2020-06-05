def match_data(selected_table_local, df_no_nan_local, selectedData, col_name_logFC, i, index_list):
    """
    function for search same data in the datatable as data in the selectData
    :param selected_table_local: (dataframe) table with selected data by lasso/box select)
    :param df_no_nan_local: (dataframe) df with upload data
    :param selectedData: (dict of list) data which were selected by lasso/box select
    :param col_name_logFC: (list of string) name of column for logFC
    :param i: (number) iterator
    :param index_list: (ist of numbers) list of index
    :return: dataframe with selected data, list of index
    """
    match = df_no_nan_local.loc[df_no_nan_local[col_name_logFC] == selectedData['points'][i]['x']].loc[df_no_nan_local['logP'] == selectedData['points'][i]['y']]
    if match.shape[0] > 1:
        for j in range(len(selectedData['points'])):
            if selectedData['points'][j]['x'] == match[col_name_logFC].values[0]:
                index_list.append(j)
                list(set(index_list))

    match_dict = match.to_dict('records')
    selected_table_local = selected_table_local.append(match_dict, sort=False)
    return [selected_table_local, index_list]

