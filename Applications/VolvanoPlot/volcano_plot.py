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
from dash.exceptions import PreventUpdate
import dash_table
import numpy as np
import csv

import annotation
import upload_data
import select_data_table_match

#initialization of app + import css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

#defition of category table
category_significant = 'Significant'
category_significant_up = 'Up&Sign'
category_significant_down = 'Down&Sign'
category_notsignificant = 'Not sign'
category_table = pd.DataFrame([[0,0,0,0]], columns=[category_significant, category_significant_up, category_significant_down, category_notsignificant])

#defition of layout (definition of all components and its id, properties in the app)
#https://dash.plot.ly/getting-started - dash documentation for layout
#https://dash.plot.ly/dash-core-components  - dash documentation for components
#https://dash.plot.ly/datatable/reference - dash documentation for interactivity table
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

    "choose separator",

    dcc.Dropdown(
        id='separator-dropdown',
         options=[
                {'label': "tabulator", 'value': "\t"},
                {'label': "semicolon", 'value': ";"},
                {'label': "comma", 'value': ","} #should I add semothing else?
         ],
        value=None
    ),

    html.Br(),

    'Select log fold change',

    dcc.Dropdown(
        id='logFC-dataset-dropdown'
    ),

    html.Br(),

    'Select p-value',

    dcc.Dropdown(
        id='P-value-dataset-dropdown'
    ),

    html.Br(),

    'Select annotation column(s)',

    dcc.Dropdown(
        id='annotations_input',
        multi=True,
    ),

    html.Br(),

    html.Button(id='submit-button', n_clicks=0, children='Submit'),

    html.Br(),
    html.Br(),
    html.Br(),

    'logFC',
    #range slider for log fold change
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
    #slider for p-value
    dcc.Slider(
        id='volcanoplot-input_p',
        value=-np.log10(0.05),
        max=8,
        min=0.01, #i cant give there 0, becouse the number must be positive
        step=0.05,
        marks={i: {'label': str(i)} for i in range(0, 8)}
    ),


    html.Br(),

    html.Div([
        dcc.Graph(
            id='my-dashbio-volcanoplot',
        )]      # html.Div(id='datatable-interactivity-container')]
    ),

    html.Br(),

    dash_table.DataTable(
        id='my-dashbio-table',
        columns=[{"name": i, "id": i} for i in category_table.columns],
        data=category_table.to_dict('records'),
        ),

    html.Br(),
    #table for data from lasso selection
    html.Div([
        dash_table.DataTable(
        id='selected-data-table',
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
            editable=False,
            # filter_action="native",
            sort_action="native",
            sort_mode="multi",
            export_format='csv',
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10

        ),

        html.Div(id='datatable-interactivity-container')
    ])
])


#Callbacks have output, input and state, which are difined by id of some layout component and spesific property, which we want to use in function.
#I use callbacks for update app after uploading data - outputs are always updated with change of Input or State
#https://dash.plot.ly/getting-started-part-2
#https://dash.plot.ly/state - dash documentation for callbacks


@app.callback(
    [
     dash.dependencies.Output('logFC-dataset-dropdown', 'options'),
     dash.dependencies.Output('P-value-dataset-dropdown', 'options'),
     dash.dependencies.Output('annotations_input', 'options')],
    [
     dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename'),
     dash.dependencies.Input('separator-dropdown', 'value')
    ]
 )

def update_dropdown(contents, filename, separ):
    """
    function for update dropdowns for logFC, p-value and annotations - "on hover"
    :param contents(string): get from upload data - data for reading csv - used in function read_csv.parse_contents
    :param filename(string): get from upload data - used in function read_csv.parse_contents
    :param separ(list of string): get from separator-dropdown - actual choose of separator, default is automatic
    :return: option for all 3 dropdown (names of columns in the updated table)
    """

    if contents:
        contents = contents[0]
        filename = filename[0]
        df_no_nan_local = upload_data.parse_contents(contents, filename, separ)

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
    dash.dependencies.Output('separator-dropdown', 'options'),
    [
     dash.dependencies.Input('upload-data', 'contents'),
     dash.dependencies.Input('upload-data', 'filename')
    ],
    [
     dash.dependencies.State('separator-dropdown', 'options')
    ]
)

def update_separator(contents, filename, options):
    """
    function for changing separator, which should be used for read csv,
    In the function upload_data.parse_contents i use as default automatic choose of separator with Python engine - csv.Sniffer()
    Function recognize which separator was used. User can choose their separator.
    :param contents(string): get from upload data - data for decode upload data
    :param options(dict): get from separator-dropdown
    :return: options for dropdown with added info (text - auto), which type of separator was used.
    """
    if contents:
        contents = contents[0]
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)

        # csvfile = io.StringIO(decoded.decode('utf-8'))
        try:
            if 'csv' or 'txt' in filename:
                # Assume that the user uploaded a CSV file
                try:
                    csvfile = io.StringIO(decoded.decode('utf-8'))
                except:
                    PreventUpdate

            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                try:
                    csvfile = io.BytesIO(decoded)
                except:
                    PreventUpdate
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        dialect = csv.Sniffer().sniff(csvfile.readline())
        print(dialect.delimiter)
        csv_delimiter = dialect.delimiter

        options = [
                      {'label': "tabulator", 'value': "\t"},
                      {'label': "semicolon", 'value': ";"},
                      {'label': "comma", 'value': ","},
                  ]

        for option in options:
            if option["value"] == csv_delimiter:
                option["label"] = option["label"] + "(auto)"

    return options

@app.callback(
    [
     dash.dependencies.Output('datatable-interactivity', 'data'),
     dash.dependencies.Output('datatable-interactivity', 'columns'),
     dash.dependencies.Output('datatable-interactivity', 'filter_action'),

    ],
    [
     dash.dependencies.Input('submit-button', 'n_clicks')
    ],
    [
     dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value'),
     dash.dependencies.State('separator-dropdown', 'value')
    ]
 )

def update_interactivity_table(button, contents, filename, col_name_p_value, col_name_logFC, separ):
    """
    Function for updating interactivity table, which is used for filtering and selecting table.
    It's updated after clicking submit-button, it submit upload data, selected column for p-value and logFC, annotation
    from uploaded table and selected separator.

    Function switch on filtering of table (property filter_action), when is uploaded data & isn't empty

    :param button (number): for submit and upload changes from state properties
    :param contents (string):  get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function upload_data.parse_contents
    :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :return: interactive table with actual data from uploaded data, table columns from uploaded table for interactive table, type of filter action
    """

    if contents:
        df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC)
        filter_action = "native"
    else:
        df_no_nan_local = pd.DataFrame()
        filter_action = "none"

    table_columns = [{"name": i, "id": i, "deletable": True} for i in df_no_nan_local.columns]

    return [df_no_nan_local.to_dict('records'), table_columns, filter_action]


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
     dash.dependencies.State('logFC-dataset-dropdown', 'value'),
     dash.dependencies.State('separator-dropdown', 'value')
    ]
 )
def update_summary_table(button, threshold_logFC, threshold_P_log10, contents, filename, col_name_p_value, col_name_logFC, separ):
    """
    Function update summary table (table of number significant/nonsignificant/significant up/significant down proteins)
    Updated after clicking submit-button or updated after changing slider input for p value or logFC

    :param button (number): for submit and upload changes from state properties
    :param threshold_logFC (list of numbers): get from rangeslider volcanoplot-input - used for summation proteins in categories
    :param threshold_P_log10 (number): get from slider volcanoplot-input_p -  used for summation proteins in categories
    :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function upload_data.parse_contents
    :param col_name_p_value (list of string):get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :return: category table (dict)
    """
    # if isinstance(col_name_p_value, str):
    #     raise PreventUpdate
    # if isinstance(col_name_logFC):
    #     raise PreventUpdate

    category_table[category_significant] = 0
    category_table[category_significant_up] = 0
    category_table[category_significant_down] = 0
    category_table[category_notsignificant] = 0

    if contents:
        df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC)

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

@app.callback(
    [
     dash.dependencies.Output('selected-data-table', 'data'),
     dash.dependencies.Output('selected-data-table', 'columns')
    ],
    [
     dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('my-dashbio-volcanoplot','selectedData'),
    ],
    [
     dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value'),
     dash.dependencies.State('separator-dropdown', 'value')
    ]
 )

def update_select_data_table(button, selectedData, contents, filename, col_name_p_value, col_name_logFC, separ):
    """
    Function for updating selected data table where written the data from lasso or box select in the graph
    It's updated after clicking submit-button (it submit upload data,selected separator and selected column for p-value and logFC, annotation
    from uploaded table) or after lasso or box select in the graph

    I use logP and logFC for search in the table. logP and logFC are coordinates (x,y) of proteins in the graph - function select_data_table_match.match_data.

    :param button (number): for submit and upload changes from state properties
    :param selectedData (dict of lists): get from selected-data-table (property selectedData) - info from lasso/box select
    :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function upload_data.parse_contents
    :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :return: (list of string) datable containing rows of proteins which was selected by lasso/box selection
    """
    if contents:
        df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC)

        index_list = []
        selected_table = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])
        selected_table_local = selected_table

        if selectedData:
            for i in range(len(selectedData['points'])):
                if index_list:
                    for index in index_list:
                        if selectedData['points'][i]['x'] == selectedData['points'][index]['x']: #control of proteins in the same coordinates
                            break
                        else:
                            [selected_table_local, index_list] = select_data_table_match.match_data(
                                selected_table_local, df_no_nan_local, selectedData, col_name_logFC, i, index_list)
                            break
                else:
                    [selected_table_local, index_list] = select_data_table_match.match_data(
                        selected_table_local, df_no_nan_local, selectedData, col_name_logFC, i, index_list)
        else:
            selected_table_local = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])

        table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]

        return [selected_table_local.to_dict('records'), table_columns]

    else:
        df_no_nan_local = pd.DataFrame()
        table_columns = [{"name": i, "id": i} for i in df_no_nan_local.columns]
        return [df_no_nan_local.to_dict('records'), table_columns]

@app.callback(
    dash.dependencies.Output('datatable-interactivity', 'style_data_conditional'),
    [dash.dependencies.Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(

    dash.dependencies.Output('my-dashbio-volcanoplot', "figure"),
    [
     dash.dependencies.Input('submit-button', 'n_clicks'),
     dash.dependencies.Input('datatable-interactivity', "derived_virtual_data"),
     dash.dependencies.Input('datatable-interactivity', "derived_virtual_indices"),
     dash.dependencies.Input('datatable-interactivity', "derived_virtual_selected_rows"),
     dash.dependencies.Input('volcanoplot-input_p', 'value'),
     dash.dependencies.Input('volcanoplot-input', 'value'),

     ],
    [
     dash.dependencies.State('upload-data', 'contents'),
     dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('logFC-dataset-dropdown', 'value'),
     dash.dependencies.State('P-value-dataset-dropdown', 'value'),
     dash.dependencies.State('annotations_input', 'value'),
     dash.dependencies.State('separator-dropdown', 'value')
     ]

)
def update_graph(button, rows, indices, derived_virtual_selected_rows, effects_p, effects, contents, filename, col_name_logFC, col_name_p_value, annotations, separ):
    """
    Function for update graph.
    It's updated with change of inputs.
     -> It's updated after clicking submit-button (it submit upload data,selected separator and selected column for p-value and logFC, annotation
        from uploaded table)
     -> It's updated with selecting rows in the interactivity table or with derived_virtual_data (I have to control how it works)
     ->It's updated after changing slider input for p value or logFC

     Function cooperate with interactivity table due to derived_virtual_data and derived_virtual_selected_rows.


    :param button (number): for submit and upload changes from state properties
    :param rows (list of dict): property derived-virtual-data - this property represents the visible state of data across all pages after the front-end sorting and filtering as been applied.
    :param derived_virtual_selected_rows (list of numbers): derived_virtual_selected_rows represents the indices of the selected_rows from the perspective of the derived_virtual_indices
        (derived_virtual_indices indicates the order in which the original rows appear after being filtered and sorted)
    :param effects_p (number): get from slider volcanoplot-input_p -  used for specification od volcanoplot property
    :param effects (list of number): get from rangeslider volcanoplot-input - used for specification od volcanoplot property
    :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
    :param filename (string): get from upload data - used in function read_csv.parse_contents
    :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
    :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
    :param annotations (string): get from multi choose dropdown annotations-input, it's used for text 'on  hover' - there are function annotation.call_update_annotation
    :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
    :return: (figure) it returns volcano plot
    """

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    if contents:
        df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC)

        if rows is None:
            dff = df_no_nan_local
        else:
            dff = pd.DataFrame(rows, index=indices)
        # print(dff)
        if dff.empty:
           dff = df_no_nan_local

        colors = ['#ff0000' if i in derived_virtual_selected_rows else '#000000'
                  for i in range(len(dff))]
        point_sizes = [15 if i in derived_virtual_selected_rows else 6
                  for i in range(len(dff))]


        [annotations_str, dff] = annotation.call_update_annotation(annotations, dff)


        return dashbio.VolcanoPlot(
                        p=col_name_p_value,
                        effect_size=col_name_logFC,
                        xlabel='logFC',
                        dataframe=dff,
                        point_size=point_sizes,
                        col=colors,
                        genomewideline_value=effects_p,
                        effect_size_line=effects,
                        highlight_color=None,
                        highlight=None,  #if it's none, there are only 1 highlighted point defined in color, if you selec one. , you should highligh proteins, which are under tresholds
                        annotation=annotations_str,
                        snp=None,
                        gene=None)
    else:
        return {'data': [], 'layout': {}, 'frames': []}

if __name__ == '__main__':
    app.run_server(debug=True)





