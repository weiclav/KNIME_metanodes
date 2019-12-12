#!/usr/bin/env python
# coding: utf-8

# In[9]:
import base64
import io

import pandas as pd

import dash
import dash_bio as dashbio
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import numpy as np

import edit_df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)


# df_1 = pd.read_csv('volcano_data3_pokus.txt', sep="\t")
# df_no_nan = edit_df.dataframe_edit(df_1, 'P', 'EFFECTSIZE')

# df_no_nan = df_1.dropna(subset = ['P','EFFECTSIZE'])
# df_no_nan = df_no_nan.reset_index(drop=True)
# df_no_nan['GENE'] = [x for x in range(0, len(df_no_nan))]
# df_no_nan['logP'] = df_no_nan['P'].apply(lambda x: -np.log10(x))

category_significant = 'Significant'
category_significant_up = 'Up&Sign'
category_significant_down = 'Down&Sign'
category_notsignificant = 'Not sign'

category_table = pd.DataFrame([[0,0,0,0]], columns=[category_significant, category_significant_up, category_significant_down, category_notsignificant])
print(category_table)

# selected_table = pd.DataFrame(columns=[i for i in df_no_nan.columns])
# filtering_table = pd.DataFrame(columns=[i for i in df_no_nan.columns])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    html.Div(id='output-data-upload'),
    html.Br(),
    'Select log fold change',
    dcc.Dropdown(
        id='logFC-dataset-dropdown',
        # options=[
        #     {
        #         'label': dset,
        #         'value': dset
        #     }
        #     for dset in df_no_nan.columns
        # ]
        # value='logFC'
    ),
    html.Br(),
    'Select p-value',
    dcc.Dropdown(
        id='P-value-dataset-dropdown',
        # options=[
        #     {
        #         'label': dset1,
        #         'value': dset1
        #     }
        #     for dset1 in df_no_nan.columns
        # ]
        # value='p_val'

    ),
    html.Br(),
    'Select annotation column(s)',
    dcc.Dropdown(
        id='annotations_input',
        multi=True,
        # options=[
        #     # {'label': 'Majority protein IDs', 'value': 'Majority protein IDs'},
        #     # {'label': 'Protein IDs', 'value': 'Protein IDs'},
        #     # {'label': 'Protein names', 'value': 'Protein names'},
        #     # {'label': 'Gene', 'value': 'GENE'},
        #     {
        #         'label': dset2,
        #         'value': dset2
        #     }
        #     for dset2 in df_no_nan.columns
        # ],
        # value=[]  # mit primarne vse zaklikle / resit s implementaci do knimu
    ),
    html.Br(),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Br(),
    html.Br(),
    html.Br(),

    'logFC',

    dcc.RangeSlider(
        id='volcanoplot-input',
        min=-6,
        max=7,
        step=0.05,
        marks={
            i: {'label': str(i)} for i in range(-6, 7)
        },
        value=[-1, 1]
    ),
    html.Br(),
    'p-value',

    dcc.Slider(
        id='volcanoplot-input_p',
        value=-np.log10(0.05),
        max=8,
        min=0.01, #i cant give there 0, becouse the number must be positive
        step=0.05,
        marks={i: {'label': str(i)} for i in range(0, 8)}
    ),


    html.Br(),
    html.Div(
        dcc.Graph(
            id='my-dashbio-volcanoplot',
            # figure=dashbio.VolcanoPlot(
            #     dataframe=df_no_nan,
            #     # p="p_val",
            #     # effect_size="logFC",
            #     xlabel='logFC',
            #     annotation='Protein IDs',
            #     gene=None,
            #     snp=None,
            #     point_size=5,
            #     genomewideline_value=-np.log10(0.05),
            #     effect_size_line=[-1, 1],
            #     highlight_color='#119DFF',
            #     col='#2A3F5F'
            #
            #
            # )
        )
    ),
    html.Br(),
        dash_table.DataTable(
        id='my-dashbio-table',
        # columns=[{"name": i, "id": i} for i in category_table.columns],
        # data=category_table.to_dict('records'),
    ),
    html.Br(),
    html.Div([
        dash_table.DataTable(
        id='selected-data-table',
        # columns=[{"name": i, "id": i} for i in selected_table.columns],
        # data=selected_table.to_dict('records'),
        export_format='csv',
        export_headers='names'
    ),
        html.Div(id='datatable-interactivity-container_1')
    ]),
    html.Br(),

    html.Div(id='display'),
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            # columns=[
            #     # {"name": i, "id": i, "deletable": True} for i in filtering_table.columns
            #     {"name": i, "id": i, "deletable": True} for i in df_no_nan.columns
            # ],
            # data=df_no_nan.to_dict('records'),
            editable=False,
            # filter_action="native", #je tam neco pokazenyho, hledej kde...
            sort_action="native",
            sort_mode="multi",
            export_format='csv',
            row_selectable="multi",
            row_deletable=True, #chceme mazatelny radky?
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10

        ),

        # dcc.Graph(
        #     id='my-dashbio-volcanoplot',
        #     figure=dashbio.VolcanoPlot(
        #         dataframe=df_no_nan,
        #         xlabel='logFC',
        #         annotation='Protein IDs',
        #         gene=None,
        #         snp=None,
        #         point_size=5,
        #         genomewideline_value=-np.log10(0.05),
        #         effect_size_line=[-1, 1],
        #         highlight_color='#119DFF',
        #         col='#2A3F5F'
        #
        #
        #     )
        # ),
        html.Div(id='datatable-interactivity-container')
    ])


])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' or 'txt' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep="\t")
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


def update_annotations(row, columns):
    row['onhover'] = '<br>'.join([f"{str(column)}: {str(row[column])}" for column in columns])
    return row

# @app.callback(
#     dash.dependencies.Output('my-dashbio-volcanoplot', 'figure'),
#     [dash.dependencies.Input('volcanoplot-input', 'value'),
#      dash.dependencies.Input('volcanoplot-input_p', 'value'),
#      dash.dependencies.Input('annotations_input', 'value'),
#      # dash.dependencies.Input('gene_name_input', 'value')
#
#      ]
# )
#
# def update_volcanoplot(effects, effects_p, annotations):
#     print(annotations)
#
#     if not annotations:
#         annotations_str = None
#     else:
#         annotations.sort()#do budoucna neradit dle abecedy, ale dle poradi sloupecku vzbranzch uzivatelem
#         df_no_nan['onhover'] = df_no_nan[annotations].apply(lambda x: '<br>'.join(x.map(str)), axis=1)
#         annotations_str = 'onhover'
#
#     # if not gene:
#     #     gene_str = None
#     # else:
#     #     gene_str = ''.join(gene)
#
#
#     return dashbio.VolcanoPlot(
#         xlabel='logFC',
#         dataframe=df_no_nan,
#         genomewideline_value=effects_p,
#         effect_size_line=effects,
#         annotation=annotations_str,
#         snp=None,
#         gene='GENE'
#
#     )


@app.callback(
    [dash.dependencies.Output('logFC-dataset-dropdown', 'options'),
    dash.dependencies.Output('P-value-dataset-dropdown', 'options'),
    dash.dependencies.Output('annotations_input', 'options')],
    [dash.dependencies.Input('upload-data', 'contents'),
    dash.dependencies.Input('upload-data', 'filename')

    ]
    # [dash.dependencies.State('P-value-dataset-dropdown', 'value'),
    # dash.dependencies.State('logFC-dataset-dropdown', 'value')]
 )

# def update_dropdown(contents, filename, col_name_p_value, col_name_logFC):
def update_dropdown(contents, filename):

    if contents:
        contents = contents[0]
        filename = filename[0]
        df_no_nan_local = parse_contents(contents, filename)
        # df_no_nan_local = dataframe_edit(df, col_name_p_value, col_name_logFC)

        option=[
            {
            'label': dset,
            'value': dset
            }
            for dset in df_no_nan_local.columns
            ]
    else:
        df_no_nan_local = pd.DataFrame()
        option = [
                       {
                           'label': dset,
                           'value': dset
                       }
                       for dset in df_no_nan_local.columns
                   ]
    return [option, option, option]

@app.callback(
    [dash.dependencies.Output('datatable-interactivity', 'data'),
     dash.dependencies.Output('datatable-interactivity', 'columns')],
    [dash.dependencies.Input('submit-button', 'n_clicks')


    ],
    [dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value')]
 )

def update_interactivity_table(button, contents, filename, col_name_p_value, col_name_logFC):
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_contents(contents, filename)
        df_no_nan1 = edit_df.dataframe_edit(df, col_name_p_value, col_name_logFC)
    else:
        df_no_nan1 = pd.DataFrame()

    table_columns = [{"name": i, "id": i, "deletable": True} for i in df_no_nan1.columns]

    return [df_no_nan1.to_dict('records'), table_columns]


# @app.callback(
#     dash.dependencies.Output('annotations_input', 'options'),
#     [dash.dependencies.Input('upload-data', 'contents'),
#      dash.dependencies.Input('upload-data', 'filename')
#     ]
#  )
#
# def update_checklist(contents, filename):
#     if contents:
#         contents = contents[0]
#         filename = filename[0]
#         df = parse_contents(contents, filename)
#         df_no_nan = dataframe_edit(df)
#         option = [
#             {
#                 'label': dset,
#                 'value': dset
#             }
#             for dset in df_no_nan.columns
#         ]
#     else:
#         df_no_nan = pd.DataFrame()
#         option = [
#             {
#                 'label': dset,
#                 'value': dset
#             }
#             for dset in df_no_nan.columns
#         ]
#
#
#     return [option

@app.callback(
    dash.dependencies.Output('my-dashbio-table', 'data'),
    [
     dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('volcanoplot-input', 'value'),
     dash.dependencies.Input('volcanoplot-input_p', 'value'),
    ],
    [
     dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value')
    ]
 )

def update_summary_table(button, threshold_logFC, threshold_P_log10, contents, filename, col_name_p_value, col_name_logFC):

    category_table[category_significant] = 0
    category_table[category_significant_up] = 0
    category_table[category_significant_down] = 0
    category_table[category_notsignificant] = 0

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_contents(contents, filename)
        df_no_nan_local = edit_df.dataframe_edit(df, col_name_p_value, col_name_logFC)

        for index, row in df_no_nan_local.iterrows():

            if row[col_name_logFC] <= threshold_logFC[1] and row[col_name_logFC] >= threshold_logFC[0] and -np.log10(row[col_name_p_value]) > threshold_P_log10:
                category_table[category_significant] = category_table[category_significant]+1

            elif row[col_name_logFC] > threshold_logFC[1] and -np.log10(row[col_name_p_value]) > threshold_P_log10:
                category_table[category_significant_up] = category_table[category_significant_up]+1

            elif row[col_name_logFC] < threshold_logFC[0] and -np.log10(row[col_name_p_value]) > threshold_P_log10:
                category_table[category_significant_down] = category_table[category_significant_down]+1

            else:
                category_table[category_notsignificant] = category_table[category_notsignificant]+1

        return category_table.to_dict('records')
    else:
        return category_table.to_dict('records')

# @app.callback(
#     [dash.dependencies.Output('selected-data-table', 'data'),
#      dash.dependencies.Output('selected-data-table', 'columns')],
#     [dash.dependencies.Input('submit-button', 'n_clicks'),
#
#      dash.dependencies.Input('my-dashbio-volcanoplot','selectedData'),
#
#      ],
#     [dash.dependencies.State('upload-data', 'contents'),
#      dash.dependencies.State('upload-data', 'filename'),
#      dash.dependencies.State('P-value-dataset-dropdown', 'value'),
#      dash.dependencies.State('logFC-dataset-dropdown', 'value')]
#  )
#
# def update_select_data_table(button, selectedData, contents, filename, col_name_p_value, col_name_logFC):
#     if contents:
#         contents = contents[0]
#         filename = filename[0]
#         df = parse_contents(contents, filename)
#         df_no_nan_local = edit_df.dataframe_edit(df, col_name_p_value, col_name_logFC)
#
#         index_list = []
#         selected_table = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])
#         selected_table_local = selected_table
#
#         if selectedData:
#             for i in range(len(selectedData['points'])):
#                 if index_list:
#                     for index in index_list:
#                         if selectedData['points'][i]['x'] == selectedData['points'][index]['x']:
#                             break
#                         else:
#                             match = df_no_nan_local.loc[df_no_nan_local[col_name_logFC] == selectedData['points'][i]['x']].loc[
#                             df_no_nan_local['logP'] == selectedData['points'][i]['y']]
#                             if match.shape[0] > 1:
#                                 for j in range(len(selectedData['points'])):
#                                     if selectedData['points'][j]['x'] == match[col_name_logFC].values[0]:
#                                         index_list.append(j)
#                                         index_set = {*index_list}
#                                         index_list = list(index_set)
#
#                             match_dict = match.to_dict('records')
#                             selected_table_local = selected_table_local.append(match_dict, sort=False)
#                             break
#                 else:
#                     match = df_no_nan_local.loc[df_no_nan_local[col_name_logFC] == selectedData['points'][i]['x']].loc[
#                         df_no_nan_local['logP'] == selectedData['points'][i]['y']]
#                     if match.shape[0] > 1:
#                         for j in range(len(selectedData['points'])):
#                             if selectedData['points'][j]['x'] == match[col_name_logFC].values[0]:
#                                 index_list.append(j)
#                                 list(set(index_list))
#
#                     match_dict = match.to_dict('records')
#
#                     selected_table_local = selected_table_local.append(match_dict, sort=False)
#
#         else:
#
#             selected_table_local = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])
#
#         table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]
#
#         return [selected_table_local.to_dict('records'), table_columns]
#
#     else:
#         df_no_nan_local = pd.DataFrame()
#         table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]
#         return [df_no_nan_local.to_dict('records'), table_columns]


@app.callback(

    # [dash.dependencies.Output('datatable-interactivity-container', "children")
    #     ],
    dash.dependencies.Output('my-dashbio-volcanoplot', "figure"),
    [
     dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('my-dashbio-volcanoplot','selectedData'),
     dash.dependencies.Input('datatable-interactivity', "derived_virtual_data"),
     dash.dependencies.Input('datatable-interactivity', "derived_virtual_selected_rows"),
     dash.dependencies.Input('volcanoplot-input_p', 'value'),
     dash.dependencies.Input('volcanoplot-input', 'value'),

     ],
    [
     dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('annotations_input', 'value')
     ]

)


# def update_graphs(contents, filename, rows, derived_virtual_selected_rows, effects_p,effects, annotations, col_name_logFC, col_name_p_value):
def update_graphs(button, selectedData, rows, derived_virtual_selected_rows, effects_p, effects, contents, filename, col_name_logFC, col_name_p_value, annotations):


    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_contents(contents, filename)
        df_no_nan_local = edit_df.dataframe_edit(df, col_name_p_value, col_name_logFC)

        dff = df_no_nan_local if rows is None else pd.DataFrame(rows)

        if dff.empty:
            dff = df_no_nan_local
        dff = dff.reset_index(drop=True)

        index_list = []
        selected_table = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])
        selected_table_local = selected_table

        if selectedData:
            for i in range(len(selectedData['points'])):
                if index_list:
                    for index in index_list:
                        if selectedData['points'][i]['x'] == selectedData['points'][index]['x']:
                            break
                        else:
                            match = \
                            df_no_nan_local.loc[df_no_nan_local[col_name_logFC] == selectedData['points'][i]['x']].loc[
                                df_no_nan_local['logP'] == selectedData['points'][i]['y']]
                            if match.shape[0] > 1:
                                for j in range(len(selectedData['points'])):
                                    if selectedData['points'][j]['x'] == match[col_name_logFC].values[0]:
                                        index_list.append(j)
                                        index_set = {*index_list}
                                        index_list = list(index_set)

                            match_dict = match.to_dict('records')
                            selected_table_local = selected_table_local.append(match_dict, sort=False)
                            break
                else:
                    match = df_no_nan_local.loc[df_no_nan_local[col_name_logFC] == selectedData['points'][i]['x']].loc[
                        df_no_nan_local['logP'] == selectedData['points'][i]['y']]
                    if match.shape[0] > 1:
                        for j in range(len(selectedData['points'])):
                            if selectedData['points'][j]['x'] == match[col_name_logFC].values[0]:
                                index_list.append(j)
                                list(set(index_list))

                    match_dict = match.to_dict('records')

                    selected_table_local = selected_table_local.append(match_dict, sort=False)

        else:

            selected_table_local = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])

        rows = selected_table_local.to_dict("records")

        # table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]

        # return [selected_table_local.to_dict('records'), table_columns]

    # else:
    #     df_no_nan_local = pd.DataFrame()
    #     table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]
    #     # return [df_no_nan_local.to_dict('records'), table_columns]




        colors = ['#ff0000' if i in derived_virtual_selected_rows else '#596878'
                  for i in range(len(dff))]
        point_sizes = [10 if i in derived_virtual_selected_rows else 5
                  for i in range(len(dff))]

        # print(colors)
        # print(point_sizes)

        if not annotations:
            annotations_str = None
        else:
            # annotations.sort()  # do budoucna neradit dle abecedy, ale dle poradi sloupecku vybranzch uzivatelem
            # dff['onhover'] = df_no_nan[annotations].apply(lambda x: '<br>'.join(x.map(str)), axis=1, columns=annotations)
            dff = df_no_nan_local.apply(update_annotations, axis=1, columns=annotations)
            annotations_str = 'onhover'

        # print(P, logFC)

        return [
            dcc.Graph(
                id='my-dashbio-volcanoplot',
                figure=dashbio.VolcanoPlot(
                        p=col_name_p_value,
                        effect_size=col_name_logFC,
                        xlabel='logFC',
                        dataframe=dff,
                        point_size=point_sizes,
                        col=colors,
                        genomewideline_value=effects_p,
                        effect_size_line=effects,
                        highlight_color=None,
                        annotation=annotations_str,
                        snp=None,
                        gene=None

                    )


            ),
            dash_table.DataTable(
                id='datatable-interactivity',
                # columns=[
                #     # {"name": i, "id": i, "deletable": True} for i in filtering_table.columns
                #     {"name": i, "id": i, "deletable": True} for i in df_no_nan.columns
                # ],
                # data=df_no_nan.to_dict('records'),

                editable=False,
                derived_virtual_data = rows,
                # filter_action="native", #je tam neco pokazenyho, hledej kde...
                sort_action="native",
                sort_mode="multi",
                export_format='csv',
                row_selectable="multi",
                row_deletable=True,  # chceme mazatelny radky?
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10

            ),

        ]
if __name__ == '__main__':
    app.run_server(debug=True)





