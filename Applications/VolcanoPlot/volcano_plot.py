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
import base64
import mimetypes
import argparse
from dash_table.Format import Format
import plotly.graph_objects as go

import annotation
import upload_data
import select_data_table_match

parser = argparse.ArgumentParser(description='Set path for data.')
parser.add_argument('-f', '--file_input', type=str,
                   help='Set path for data, which will be use in application')


# initialization of app + import css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# definition of category table
category_significant = 'Significant'
category_significant_up = 'Up&Sign'
category_significant_down = 'Down&Sign'
category_notsignificant = 'Not sign'
category_table = pd.DataFrame([[0, 0, 0, 0]],
                              columns=[category_significant, category_significant_up, category_significant_down,
                                       category_notsignificant])

new_data = None
old_data = None
marks_slider = np.round(np.arange(0, 1, 0.05).tolist(), 2)

def prepare_data(filename):
    file_name = []
    encoded_data = []
    # file_name.append('volcano_data3_pokus.txt')
    # file_name.append(args.file_input)

    file_name.append(filename)

    if file_name and file_name[0] is not None:
        data = open(file_name[0], 'rb').read()
        prepend_info = 'data:%s;base64' % mimetypes.guess_type(file_name[0])[0]
        s_encoded = base64.b64encode(data)
        s_encoded_str = str(s_encoded)[2:-1]
        data_format_for_dccUpload = '%s,%s' % (prepend_info, s_encoded_str)
        encoded_data.append(data_format_for_dccUpload)

    else:
        encoded_data = []
        file_name = []
    return encoded_data, file_name

def create_layout(encoded_data, file_name):
    """
    Function, which define layout - all components and it's parameters.
    :param encoded_data: string of imported data encoded in base64, with prepended info in the start - like it use dash iba component dcc.Upload
    :param file_name: string - name or path to data, used only for showing it in the UI
    :return: layout of app
    """
    # defition of layout (definition of all components and its id, properties in the app)
    # https://dash.plot.ly/getting-started - dash documentation for layout
    # https://dash.plot.ly/dash-core-components  - dash documentation for components
    # https://dash.plot.ly/datatable/reference - dash documentation for interactivity table
    return html.Div(id='page-content', children=[

        html.Div(style={
                        'display': 'inline-block',
                        'width': '25%',
                        'height': '700px'
                        }, children=[
            html.Div(id='vp-control-tabs', className='control-tabs',
                     style={
                         'height': '100%',
                         'borderWidth': '1px',
                         'borderStyle': 'solid',
                         'borderColor': '#bbbbbb',
                         'margin-bottom': '2px',
                         'display': 'flex',
                         'flex-direction': 'column',
                         'flex-wrap': 'wrap',
                         'justify-content': 'space-between'


                     }, children=[
                html.Div(children=[dcc.Tabs(id='vp-tabs', value='Upload_data', children=[
                    dcc.Tab(
                        label='Upload data',
                        value="Upload_data",
                        style={
                            'z-index': '1',  # for more area to click
                        },
                        children=html.Div(className='control-tab', style={'margin': '10px'}, children=[
                            'Upload data *',
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files'),
                                    dcc.Markdown(id='upload-file-name', children=['''Uploaded file name: -'''])

                                ]),
                                contents=encoded_data,
                                filename=file_name,
                                style={
                                    'width': '100%',
                                    'borderWidth': '1px',
                                    'borderStyle': 'solid',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'color': '#555',
                                    'borderColor': '#bbbbbb',
                                    'z-index': '1',
                                    'padding-top': '10px',
                                    'padding-bottom': '10px'
                                },
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                            html.Br(),
                            "Choose separator *",
                            dcc.Dropdown(
                                id='separator-dropdown',
                                options=[
                                    {'label': "Tabulator", 'value': "\t"},
                                    {'label': "Semicolon", 'value': ";"},
                                    {'label': "Comma", 'value': ","}  # should I add semothing else?
                                ],
                                value=None,
                                style={'textAlign': 'left'}
                            )
                        ],
                        )
                    ),
                    dcc.Tab(
                        label='Column select',
                        style={'z-index': '1'}, # for more area to click
                        children=html.Div(className='control-tab', style={'margin': '10px'}, children=[
                                'Select log fold change column *',
                                dcc.Dropdown(
                                    id='logFC-dataset-dropdown'
                                ),

                                html.Br(),

                                'Select p-value column *',
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
                                dcc.Markdown(id='prevent-update-info', children=[''' '''])

                        ]
                        )
                    ),
                    dcc.Tab(
                        label='Zero value replace',
                        style={
                            'z-index': '1',  # for more area to click

                        },
                        value='view', children=html.Div(className='control-tab', style={'margin': '10px'}, children=[
                            "Specify value to replace zero p-value",
                            html.Br(),
                            html.Form(children=[dcc.Input(
                                id="input_zero_value_replace", type="number", placeholder="0.01",
                                min=1 * (10 ** (-6)),
                                max=1,
                                step=0.001,
                                style={'width': '100%'}
                            )],
                                # noValidate='novalidate',
                                action="javascript:void(0);"),
                            html.Br(),
                            dcc.Markdown(id='prevent-update-info2', children=[''' '''])

                        ]
                        )
                    )
                ]
                ),]),

                # html.Br(),
                html.Div(
                 style={
                    'display': 'flex',
                    'flex-direction': 'row',
                     'flex-wrap': 'wrap',
                     'justify-content': 'space-between'
                 },
                 children=[
                     dcc.Markdown(children = ['\* Required'],
                         style={
                            'margin': '10px',
                         }),
                    html.Button(id='submit-button', n_clicks=0, children='Submit', disabled=True, title='Set required values in Upload data and Column select.',
                                style={
                                    'margin': '10px',
                                    'border-color': '#b8b0b0',
                                    'color': '#ccb6b6'
                                    },
                                )
                         ]

                ),


                ],
                     )
        ]),
        html.Div(style={
                'margin': '10px',
                'float': 'right',
                'display': 'inline-block',
                'width': '70%',
                'height': '700px',
                'padding-bottom': '40px'

                }, children=[
      'Log fold-change threshold',
               # range slider for log fold change
               dcc.RangeSlider(
                   id='volcanoplot-input',
                   min=-6,
                   max=6,
                   step=0.001,
                   marks={
                       i: {'label': str(i)} for i in
                       range(-6, 6)
                   },
                   allowCross=False,
                   value=[-1, 1],
                   tooltip={
                       'always_visible': False,
                       'placement': 'topLeft'
                            },
               ),
                html.Div(
                        children=[
                            html.P(style={
                               'display':'inline-block',
                                'padding':'5px'
                           },
                                children=['Type a number to set the rangeslider values:  ']),
                            html.Form(
                                children=[dcc.Input(
                                    id="value_logFC_slider_inputer", type="number", placeholder="1",
                                    value=1,
                                    style={
                                        'margin': '3px'
                                    }
                                    )

                                ],
                                noValidate='novalidate',
                                action="javascript:void(0);",
                                style={
                                   'display':'inline-block',
                               },

                        )]),

               html.Br(),

               'P-value threshold',
                    html.Br(),
               html.Div(
                   children=[
                       html.Div(
                           children=[dcc.Slider(
                               id='volcanoplot-input_p',
                               value=0.05,
                               max=1,
                               min=0.001,
                               # i cant give there 0, becouse the number must be positive
                               step=0.001,
                               marks={i: {'label': str(i)} for i in marks_slider},
                               tooltip={
                                   'always_visible': False,
                                   'placement': 'topLeft'
                               },
                               included=True,
                           )]),
                       html.Div(
                        children=[
                            html.P(style={
                               'display':'inline-block',
                                'padding':'5px'
                           },
                                children=['Type a number to set the slider value:  ']),
                            html.Form(
                                children=[dcc.Input(
                                    id="value_p_slider_inputer", type="number", placeholder="0.05",
                                    min=0.000001,
                                    max=1,
                                    step=0.000001,
                                    value=0.05,
                                    )],
                                # noValidate='novalidate',
                                action="javascript:void(0);",
                                style={
                                   'display':'inline-block',
                               },

                        )]),

           ]),
            dcc.Loading(className='dashbio-loading', style={'height': '450px'}, children=[
               dcc.Graph(
                   id='my-dashbio-volcanoplot',
                   config={"toImageButtonOptions": {'format': 'svg',
                                                    'height': 800,
                                                    'width': 800,
                                                    'scale': 1
                                                    }},
               )
           ]

                        ),
        ]
        ),

        html.Br(),
        html.Div(
            children=[
                html.Div(
                    style={'margin-top': '30px'},
                    children=[
                    html.H6('Summary table'),
                    dash_table.DataTable(
                    id='my-dashbio-table',
                    columns=[{"name": i, "id": i} for i in category_table.columns],
                    data=category_table.to_dict('records'),
                    export_format='csv',
            ),
                ]
                ),


        html.Br(),
        # table for data from lasso selection

        html.Hr(
            style={
            'border': None,
            'border-top': '3px double #bbb',
            'overflow': 'visible',
            'text-align': 'center',
            'height': '5px',
            'border-color': '#bbb'
                    }
                ),
        html.H6('Table of selected proteins'),
        html.Div(
                 children=[
                     html.Form(children = [dcc.Input(id="input_rows_per_page_1", type="number", placeholder="10",
                        min=0,
                        max=250,
                        step=1,
                        value=10,
                        debounce=True,
                                                     ),
                        ],
                        action="javascript:void(0);",
                        title='Rows per page in the table'
        ),



                     dash_table.DataTable(
                        id='selected-data-table',
                        export_format='csv',
                        page_size=10,
                        page_action='native',
                        export_headers='names',
                        virtualization=True,
                        fixed_rows={'headers': True, 'data': 0},
                         style_table={
                             'overflowX': 'auto'
                         },
                         style_cell={
                             'height': 'auto',
                             # all three widths are needed
                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                             'whiteSpace': 'normal',
                             'word-break': 'break-all'
                         }
            ),
            html.Div(id='datatable-interactivity-container_1')]


        ),
        html.Br(),
        html.Hr(
            style={
            'border': None,
            'border-top': '3px double #bbb',
            'overflow': 'visible',
            'text-align': 'center',
            'height': '5px',
            'border-color': '#bbb'
                    }
                ),
        html.H6('Table for filtering proteins in the graph'),
        html.Div(
            children=[
                html.Div(children=[
                    html.Button(id='reset-filters-button', children='Reset filtering',  style={'display': 'inline-block',
                                                                                               'margin-right': '5px'
                                                                                               },
                                ),
                    html.Form(children=[dcc.Input(id="input_rows_per_page_2", type="number", placeholder="10",
                                            min=0,
                                            max=250,
                                            step=1,
                                            value=10,
                                            debounce=True,

                                            )
                                          ],
                         action="javascript:void(0);",
                         title='Rows per page in the table',
                         style={'display': 'inline-block',}
                              ),

                                    ],
                ),


            dash_table.DataTable(
                id='datatable-interactivity',
                editable=False,
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
                page_size=10,
                virtualization=True,
                fixed_rows={'headers': True, 'data': 0},
                style_table={
                    'overflowX': 'auto'
                            },
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'word-break' : 'break-all'
                }
            ),

            html.Div(id='datatable-interactivity-container')],

        ),
        html.Div(style={"display": "none"},
                 children=[ dcc.Slider(
            id='hide-slider',
            value=-np.log10(0.05),
            max=8,
            min=0.01,
            # i cant give there 0, becouse the number must be positive
            step=0.05,
            marks={i: {'label': str(i)} for i in
                   range(0, 8)}
        )]),
        html.Div(id='hidden-div', style={'display':'none'})
        ])

    ]
                          )

def define_callbacks():
    '''
    Function which coll alldefined callbacks
    '''

    @app.callback(
        [
            dash.dependencies.Output('datatable-interactivity', "derived_virtual_data"),
            dash.dependencies.Output('datatable-interactivity', "derived_virtual_indices"),
            dash.dependencies.Output('datatable-interactivity', "derived_virtual_selected_rows"),
            dash.dependencies.Output('datatable-interactivity', "derived_virtual_selected_row_ids"),  #
            dash.dependencies.Output('datatable-interactivity', "selected_rows"),
            dash.dependencies.Output('datatable-interactivity', "derived_filter_query_structure"),#
            dash.dependencies.Output('datatable-interactivity', "filter_query"),#
            dash.dependencies.Output('hide-slider', "value"),
        ],
        [
            dash.dependencies.Input('reset-filters-button', 'n_clicks'),
            dash.dependencies.Input('upload-data', 'contents'),
        ],
        [dash.dependencies.State('hide-slider', "value"),]
    )
    def reset_filtering(reset_button, upload_data, hide_slider):
        """
        Function which reset all parameters of components in case it's not output of some else function. The parameters
        are reset, when new data are upload or the form is changed or reset filtering with button.
        :param reset_button: number - number of clicks to button, used to for updating aplication, when it is clicked ane all filtering is removed
        :param upload_data: string - data encoded by base64, changed with new uploaded data
        :param hide_slider: value of invisible slider is used, for making something like buffer
        :return: list of parameters of components
        """

        selected_rows = []
        derived_virtual_data = []
        derived_virtual_indices = []
        derived_virtual_selected_rows = []
        derived_virtual_selected_row_ids = []
        derived_filter_query_structure = {}
        filter_query = ''
        return [derived_virtual_data, derived_virtual_indices, derived_virtual_selected_rows, derived_virtual_selected_row_ids, selected_rows, derived_filter_query_structure, filter_query, hide_slider]

    @app.callback(
        [
         dash.dependencies.Output('my-dashbio-volcanoplot', 'selectedData'),
         dash.dependencies.Output('reset-filters-button', 'n_clicks'),
         dash.dependencies.Output('logFC-dataset-dropdown', 'value'),
         dash.dependencies.Output('P-value-dataset-dropdown', 'value'),
         dash.dependencies.Output('annotations_input', 'value')
         ],
        [dash.dependencies.Input('upload-data', 'contents')],
        [
            dash.dependencies.State('my-dashbio-volcanoplot', 'selectedData'),
            dash.dependencies.State('reset-filters-button', 'n_clicks'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('annotations_input', 'value')
        ]

    )
    def update_new_data(contents, selectedData,  filter_button, value_log_fc, value_p, value_annot):
        """
        Function, which save in global vatiable new_data, that new data are uploaded and reset values of dropdowns in the form
        :param contents: string - data encoded by base64, changed with new uploaded data
        :param selectedData: dictionary of selected data in the graph
        :param filter_button: number - number of clicks to button, used to for updating aplication, when it is clicked ane all filtering is removed
        :param value_log_fc: string - value of dropdown for logFC
        :param value_p: string - value of dropdown for p-value
        :param value_annot: string - value of dropdown for annotations
        :return: list of reseted parameters
        """

        global new_data
        new_data = contents
        selectedData = {}
        value_log_fc = None
        value_p = None
        value_annot = []
        return [selectedData, filter_button, value_log_fc, value_p, value_annot]


    @app.callback(
        dash.dependencies.Output('hidden-div', 'children'),
        [dash.dependencies.Input('submit-button', 'n_clicks')],
        [dash.dependencies.State('hidden-div', 'children')]

    )
    def update_old_data(button, children):
        """
        Function which save uploaded data from new_data to old_data, when are all components are reset after upload of new data
        :param button: number - number of clicks to button, used to for updating application, when it is clicked setting
        of form is used in the application
        :param children: children of hidden_div, which in the output this function, so after call this function are called
        all function, which has this parameter in the input; it's changed after uploading new data and reseting all components
        :return: children of hidden_div
        """
        global old_data
        old_data = new_data
        return children

    @app.callback(
        [
            dash.dependencies.Output('upload-file-name', 'children')
        ],
        [
            dash.dependencies.Input('hide-slider', "value")
        ],
        [
            dash.dependencies.State('upload-file-name', 'children'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('separator-dropdown', 'value')

        ]
    )
    def update_file_name_markdown(hide_slider, file_name_text, filename, contents, separ):
        """
        Function update text in the form, which inform user about filename and size of uploaded data
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param file_name_text: list - info about filename
        :param filename: string - name of file
        :param contents: string - data encoded by base64, changed with new uploaded data
        :param separ: string - separator in the data
        :return: list of strings (filename and data size)
        """
        if filename:
            file_name_text = ['''Uploaded file name: ''' + filename[0]]
        else:
            file_name_text = ['''Uploaded file name: -''']

        if contents:
            contents = contents[0]
            filename = filename[0]
            df_no_nan_local = upload_data.parse_contents(contents, filename, separ)
            size = df_no_nan_local.shape
            file_info = [file_name_text[0] + '''
    Dataset size: ''' + str(size[0]) + '''x''' + str(size[1])]
        else:
            file_info = [file_name_text[0] + '''
    Dataset size: -''']
        return file_info

    @app.callback(
        [
            dash.dependencies.Output('separator-dropdown', 'options'),
            dash.dependencies.Output('separator-dropdown', 'value'),
         ],
        [
            dash.dependencies.Input('hide-slider', "value")
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('separator-dropdown', 'options'),
            dash.dependencies.State('separator-dropdown', 'value'),

        ]
    )
    def update_separator(hide_slider, contents, filename, options, value):
        """
        function for changing separator, which should be used for read csv,
        In the function upload_data.parse_contents i use as default automatic choose of separator with Python engine - csv.Sniffer()
        Function recognize which separator was used. User can choose their separator.
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param filename: string - name of file
        :param value: actual value of separator
        :param contents(string): get from upload data - data for decode upload data
        :param options(dict): get from separator-dropdown
        :return: options for dropdown with added info (text - auto), which type of separator was used.
        """

        if contents:
            contents = contents[0]
            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)

            try:
                if 'csv' or 'txt' in filename:
                    # Assume that the user uploaded a CSV file
                    try:
                        csvfile = io.StringIO(decoded.decode('utf-8'))
                    except:
                        raise PreventUpdate

                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    try:
                        csvfile = io.BytesIO(decoded)
                    except:
                        raise PreventUpdate
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])

            dialect = csv.Sniffer().sniff(csvfile.readline())
            csv_delimiter = dialect.delimiter

            options = [
                {'label': "tabulator", 'value': "\t"},
                {'label': "semicolon", 'value': ";"},
                {'label': "comma", 'value': ","},
            ]

            for option in options:
                if option["value"] == csv_delimiter:
                    option["label"] = option["label"] + "(auto)"
                    value = csv_delimiter

        return [options, value]



    @app.callback(
        [
            dash.dependencies.Output('logFC-dataset-dropdown', 'options'),
            dash.dependencies.Output('P-value-dataset-dropdown', 'options'),
            dash.dependencies.Output('annotations_input', 'options')
        ],
        [
            dash.dependencies.Input('hide-slider', "value"),
            dash.dependencies.Input('separator-dropdown', 'value')
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            #dash.dependencies.State('separator-dropdown', 'value')
        ]
    )
    def update_dropdown(hide_slider, separ, contents, filename):
        """
        Function for update dropdowns for logFC, p-value and annotations - "on hover"
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param contents(string): get from upload data - data for reading csv - used in function read_csv.parse_contents
        :param filename(string): get from upload data - used in function read_csv.parse_contents
        :param separ(list of string): get from separator-dropdown - actual choose of separator, default is automatic
        :return: option for all 3 dropdown (names of columns in the updated table)
        """
        if contents:
            contents = contents[0]
            filename = filename[0]
            df_no_nan_local = upload_data.parse_contents(contents, filename, separ)

            option = [
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

    def enable_submit_button():
        """
        Function, which change SCC style of submit button and disable it
        :return: list
        """
        disable_button = True
        title = 'Set required values in Upload data and Column select.'
        style = {
            'margin': '10px',
            'border-color': '#b8b0b0',
            'color': '#ccb6b6'
            }

        return [disable_button, title, style]


    @app.callback(
        [
            dash.dependencies.Output('prevent-update-info', 'children'),
            dash.dependencies.Output('prevent-update-info2', 'children'),
            dash.dependencies.Output('submit-button', 'disabled'),
            dash.dependencies.Output('submit-button', 'title'),
            dash.dependencies.Output('submit-button', 'style')
        ],
        [
            dash.dependencies.Input('hide-slider', "value"),
            dash.dependencies.Input('logFC-dataset-dropdown', 'value'),
            dash.dependencies.Input('P-value-dataset-dropdown', 'value'),
            dash.dependencies.Input('input_zero_value_replace', 'value'),

        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('prevent-update-info', 'children'),
            dash.dependencies.State('prevent-update-info2', 'children'),
            dash.dependencies.State('submit-button', 'disabled'),
            dash.dependencies.State('submit-button', 'title'),
            dash.dependencies.State('submit-button', 'style')
        ]
    )
    def update_prevent_update_info(hide_slider, col_name_logFC, col_name_p_value, input_value, contents, filename, separ, children, children2, disable_button, title, style):
        """
        Function, which shows error info with specification, what is mistake
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param col_name_logFC: (list of string) get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_p_value: (list of string) get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :param contents: (string)  get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename(string): get from upload data - used in function read_csv.parse_contents
        :param separ(list of string): get from separator-dropdown - actual choose of separator, default is automatic
        :param children: list of strings - error info
        :param children2: list of strings - error info
        :param disable_button: boolean - disabled / enabled  submit button
        :param title: string - info on hover under submit button
        :param style: dictionary - CSS of submit button
        :return: list of prevent update info and submit button setting
        """
        button = [disable_button, title, style]
        if contents:
            contents = contents[0]
            filename = filename[0]
            df = upload_data.parse_contents(contents, filename, separ)
            children = '''
    '''
            children2 = '''
    '''
            disable_button = False
            title = None
            style = {
                'margin':'10px',
                'border-color': '#bbb',
                'color': '#555'
            }
            button = [disable_button, title, style]
            if separ is None:
                button = enable_submit_button()
            if col_name_p_value is not None or col_name_logFC is not None:

                if col_name_p_value is None:
                    button = enable_submit_button()
                    children += '''
    Column for p-value is missing
    '''
                    if isinstance(df[col_name_logFC][0], str) or np.isnan(df[col_name_logFC][0]):
                        df[col_name_logFC] = pd.to_numeric(df[col_name_logFC], errors='coerce')
                        df_no_nan = df.dropna(subset=[col_name_logFC])
                        df_no_nan = df_no_nan.reset_index(drop=True)
                        if df_no_nan.empty:
                            button = enable_submit_button()
                            children += '''
    Selected column for log fold change should contain numbers
    '''
                elif col_name_logFC is None:
                    button = enable_submit_button()
                    children += '''
    Column for log fold change is missing
    '''
                    if isinstance(df[col_name_p_value][0], str) or np.isnan(df[col_name_p_value][0]):
                        df[col_name_p_value] = pd.to_numeric(df[col_name_p_value], errors='coerce')
                        df_no_nan = df.dropna(subset=[col_name_p_value])
                        df_no_nan = df_no_nan.reset_index(drop=True)
                        if df_no_nan.empty:
                            button = enable_submit_button()
                            children += '''
    Selected column for p-value should contain numbers
    '''
                        elif not (df_no_nan[col_name_p_value] >= 0).all(axis=None):
                            button = enable_submit_button()
                            children += '''
    Selected column for p-value should contain numbers greater than 0 and less than 1
    '''
                        elif not (df_no_nan[col_name_p_value] <= 1).all(axis=None):
                            button = enable_submit_button()
                            children += '''
    Selected column for p-value should contain numbers greater than 0 less than 1                        
    '''
                else:
                    if col_name_logFC == col_name_p_value:
                        button = enable_submit_button()
                        children += '''
    Log fold change and p-value columns shouldn't be same                    
    '''
                    if(isinstance(df[col_name_logFC][0], str) or isinstance(df[col_name_p_value][0], str) or np.isnan(df[col_name_p_value][0]) or np.isnan(df[col_name_logFC][0])):
                        if isinstance(df[col_name_logFC][0], str) or np.isnan(df[col_name_logFC][0]): #or vsechno nan?
                            df[col_name_logFC] = pd.to_numeric(df[col_name_logFC], errors='coerce')
                            df_no_nan = df.dropna(subset=[col_name_logFC])
                            df_no_nan = df_no_nan.reset_index(drop=True)
                            if df_no_nan.empty:
                                button = enable_submit_button()
                                children += '''
    Selected column for log fold change should contain numbers                            
    '''
                        if isinstance(df[col_name_p_value][0], str) or  np.isnan(df[col_name_p_value][0]): #or nan?
                            df[col_name_p_value] = pd.to_numeric(df[col_name_p_value], errors='coerce')
                            df_no_nan = df.dropna(subset=[col_name_p_value])
                            df_no_nan = df_no_nan.reset_index(drop=True)
                            if df_no_nan.empty:
                                button = enable_submit_button()
                                children += '''
    Selected column for p-value should contain numbers                            
    '''
                            elif not (df_no_nan[col_name_p_value] >= 0).all(axis=None):
                                button = enable_submit_button()
                                children += '''
    Selected column for p-value should contain numbers greater than 0 and less than 1    
    '''
                            elif not (df_no_nan[col_name_p_value] <= 1).all(axis=None):
                                button = enable_submit_button()
                                children += '''
    Selected column for p-value should contain numbers greater than 0 less than 1    
    '''

                    else:
                        df_no_nan = df.dropna(subset=[col_name_p_value, col_name_logFC])
                        df_no_nan = df_no_nan.reset_index(drop=True)
                        if df_no_nan.empty:
                            button = enable_submit_button()
                            children += '''
    Dataframe is empty after filtering    
    '''
                        elif not (df_no_nan[col_name_p_value] >= 0).all(axis=None):
                            button = enable_submit_button()
                            children += '''
    Selected column for p-value should contain numbers greater than 0 and less than 1                        
    '''

                        elif not (df_no_nan[col_name_p_value] <= 1).all(axis=None):
                            button = enable_submit_button()
                            children += '''
    Selected column for p-value should contain numbers greater than 0 less than 1                        
    '''

            else:
                button = enable_submit_button()
                children += '''
    Columns for p-value and log fold change are missing            
    '''
            if col_name_p_value is not None and col_name_logFC is not None:
                if input_value is None:
                    children2 += '''
                Zero p-values are replaced by minimum dataset p-value
                '''
                else:
                    children2 += '''
                Zero p-values are replaced by input value
                '''


        return [children, children2, *button]

    @app.callback(
       [
           dash.dependencies.Output('volcanoplot-input_p', 'value'),
           dash.dependencies.Output('volcanoplot-input_p', 'min'),
           dash.dependencies.Output('volcanoplot-input_p', 'step'),

        ],
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('hide-slider', "value"),
            dash.dependencies.Input('value_p_slider_inputer', 'value')
        ],
        [

        dash.dependencies.State('upload-data', 'contents'),
        dash.dependencies.State('upload-data', 'filename'),
        dash.dependencies.State('P-value-dataset-dropdown', 'value'),
        dash.dependencies.State('logFC-dataset-dropdown', 'value'),
        dash.dependencies.State('separator-dropdown', 'value'),
        dash.dependencies.State('input_zero_value_replace', 'value'),
        dash.dependencies.State('volcanoplot-input_p', 'min'),
        dash.dependencies.State('volcanoplot-input_p', 'value'),
        dash.dependencies.State('volcanoplot-input_p', 'step')
         ]
    )
    def update_slider_p_value(hiden_div, hide_slider, p_input_value, contents, filename, col_name_p_value,
                             col_name_logFC, separ, input_value, p_slider_min, p_value_slider, step):
        """

        :param hiden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param p_input_value: number - p-value inputed by dcc.Input, it is changing setting of p-value's slider
        :param contents: (string)  get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename(string): get from upload data - used in function read_csv.parse_contents
        :param col_name_p_value:  (list of string) get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC: (list of string) get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param separ(list of string): get from separator-dropdown - actual choose of separator, default is automatic
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :param p_slider_min: number - minimum of p-value slider, it could change by smallest p-value of dataset
        :param p_value_slider:  get from slider volcanoplot-input_p -  used for specification of volcanoplot property - tresholds
        :param step: number - minimum step of slider for p-value
        :return: list -setting of p-value slider
        """

        global old_data
        global new_data
        if old_data == None and new_data != None or old_data == new_data:
            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC,
                                                       input_value)
                if df_no_nan_local[col_name_p_value].min() > 0.000001:
                    p_slider_min = df_no_nan_local[col_name_p_value].min()
                else:
                    p_slider_min = 0.000001

                if p_input_value is None:
                    raise PreventUpdate
                elif p_input_value == 0:
                    log_p_slider_min = np.floor(np.log10(p_slider_min))
                    step = 1 * 10 ** (log_p_slider_min)
                    p_slider_min = step
                else:
                    p_value_slider = p_input_value

                if(p_input_value < p_slider_min and (p_input_value != 0)):
                    p_slider_min = p_input_value

                log_p_slider_min = np.floor(np.log10(p_slider_min))
                step = 1 * 10 ** (log_p_slider_min)
                p_slider_min = step
        else:
            p_slider_min = 0.01

        return [p_value_slider, p_slider_min, step]




    @app.callback(
        [
            dash.dependencies.Output('volcanoplot-input', 'min'),
            dash.dependencies.Output('volcanoplot-input', 'max'),
            dash.dependencies.Output('volcanoplot-input', 'marks'),
            dash.dependencies.Output('volcanoplot-input', 'value'),
        ],
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('hide-slider', "value"),
            dash.dependencies.Input('value_logFC_slider_inputer', 'value')
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('input_zero_value_replace', 'value'),
            dash.dependencies.State('volcanoplot-input', 'min'),
            dash.dependencies.State('volcanoplot-input', 'max'),
            dash.dependencies.State('volcanoplot-input', 'marks'),
            dash.dependencies.State('volcanoplot-input', 'value')
        ]
    )
    def update_logfc_slider_range(hiden_div, hide_slider, logFC_input_value, contents, filename, col_name_p_value,
                             col_name_logFC, separ, input_value, logFC_slider_min, logFC_slider_max, marks, logFC_value_slider):
        """

        :param hiden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param logFC_input_value: number - logFC inputed by dcc.Input, it is changing setting of logFC's slider
        :param contents: (string)  get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename(string): get from upload data - used in function read_csv.parse_contents
        :param col_name_p_value:  (list of string) get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC: (list of string) get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param separ(list of string): get from separator-dropdown - actual choose of separator, default is automatic
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :param logFC_slider_min: number - minimum of logFC slider, it could be changed by smallest logFC value of dataset
        :param logFC_slider_max: number - max of logFC slider, it could be changed by largest logFC value of dataset
        :param marks: dict - sets labels for steps in logFC slider
        :param logFC_value_slider: (list of number) get from rangeslider volcanoplot-input - used for specification of volcanoplot property
        :return: list for setting logFC slider
        """

        global old_data
        global new_data
        if old_data==None and new_data != None or old_data == new_data:
            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC, input_value)

                min_logFC_data = int(np.floor(df_no_nan_local[col_name_logFC].min()))
                max_logFC_data = int(np.ceil(df_no_nan_local[col_name_logFC].max()))
                range_abs = max(abs(min_logFC_data), abs(max_logFC_data))
                logFC_input_min = np.negative(range_abs)
                logFC_slider_min = np.negative(range_abs)
                logFC_input_max = range_abs
                logFC_slider_max = range_abs

                if logFC_input_value is None:
                    raise PreventUpdate

                if (logFC_input_value > logFC_input_max) or (logFC_input_value < logFC_input_min):
                    range_abs = int(np.ceil(abs(logFC_input_value)))
                    logFC_slider_min = np.negative(range_abs)
                    logFC_slider_max = range_abs
                marks = {}
                step = int(np.ceil(logFC_slider_max*2/35)) #I use 68 as divider because in the aplication is max 68 marks, which rendered without overlay
                marks = {i: {'label': str(i)} for i in range(logFC_slider_min, logFC_slider_max, step)}
        else:
            logFC_slider_min = -6
            logFC_slider_max = 6
            marks = {}
            marks = {i: {'label': str(i)} for i in range(-6, 6)}



        logFC_input = abs(logFC_input_value)
        logFC_value_slider[0] = np.negative(logFC_input)
        logFC_value_slider[1] = logFC_input

        return [logFC_slider_min, logFC_slider_max, marks, logFC_value_slider]

    @app.callback(
        [
            dash.dependencies.Output('datatable-interactivity', 'page_size'),
            dash.dependencies.Output('selected-data-table', 'page_size'),
        ],
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('hide-slider', "value"),
            dash.dependencies.Input('input_rows_per_page_1', 'value'),
            dash.dependencies.Input('input_rows_per_page_2', 'value'),

        ],
        [
            dash.dependencies.State('datatable-interactivity', 'page_size'),
            dash.dependencies.State('selected-data-table', 'page_size'),
        ]
    )
    def update_number_tables_rows(hidden_div, hide_slider, input_page_size_selected, input_page_size_interactivity, page_size_interactivity, page_size_selected):
        """

        :param hidden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param input_page_size_selected: number - inputed by user to set number of rows per side in the table of selected proteins
        :param input_page_size_interactivity: number - inputed by user to set number of rows per side in the interactivity table
        :param page_size_interactivity: number - set by input_page_size_interactivity
        :param page_size_selected: number - set by input_page_size_selected
        :return: list of setting of rows by page in the tables
        """
        global old_data
        global new_data
        if old_data == None and new_data != None or old_data == new_data:
            if input_page_size_interactivity is None:
                raise PreventUpdate
            elif input_page_size_selected is None:
                raise PreventUpdate
            else:
                page_size_interactivity = input_page_size_interactivity
                page_size_selected = input_page_size_selected


        return [page_size_interactivity, page_size_selected]


    @app.callback(
        [
            dash.dependencies.Output('datatable-interactivity', 'data'),
            dash.dependencies.Output('datatable-interactivity', 'columns'),
            dash.dependencies.Output('datatable-interactivity', 'filter_action'),
        ],
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('hide-slider', "value"),
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('input_zero_value_replace', 'value')
        ]
    )
    def update_interactivity_table(hidden_div, hide_slider, contents, filename, col_name_p_value, col_name_logFC, separ, input_value):
        """
        Function for updating interactivity table, which is used for filtering and selecting table.
        It's updated after clicking submit-button, it submit upload data, selected column for p-value and logFC, annotation
        from uploaded table and selected separator.

        Function switch on filtering of table (property filter_action), when is uploaded data & isn't empty

        :param hidden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param contents: (string)  get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename (string): get from upload data - used in function upload_data.parse_contents
        :param col_name_p_value: (list of string) get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :return: interactive table with actual data from uploaded data, table columns from uploaded table for interactive table, type of filter action
        """
        global old_data
        global new_data
        if old_data == None and new_data != None or old_data == new_data:
            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC, input_value)
                filter_action = "native"
            else:
                df_no_nan_local = pd.DataFrame()
                filter_action = "none"
                filter_query = ''
        else:
            df_no_nan_local = pd.DataFrame()
            filter_action = "none"


        # table_columns = [{"name": i, "id": i, "hideable": 'first', 'type': 'numeric', 'format' : Format(precision = 4)} for i in df_no_nan_local.columns]
        table_columns = [{"name": i, "id": i, "hideable": 'first', 'type': 'text'} for i in df_no_nan_local.columns]


        return [df_no_nan_local.to_dict('records'), table_columns, filter_action]


    @app.callback(
        dash.dependencies.Output('my-dashbio-table', 'data'),
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('volcanoplot-input', 'value'),
            dash.dependencies.Input('volcanoplot-input_p', 'value'),
            dash.dependencies.Input('hide-slider', "value"),
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('input_zero_value_replace', 'value')
        ]
    )
    def update_summary_table(hidden_div, threshold_logFC, threshold_P, hide_slider, contents, filename, col_name_p_value,
                             col_name_logFC, separ, input_value):
        """
        Function update summary table (table of number significant/nonsignificant/significant up/significant down proteins)
        Updated after clicking submit-button or updated after changing slider input for p value or logFC

        :param hidden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param threshold_logFC: (list of numbers) get from rangeslider volcanoplot-input - used for summation proteins in categories
        :param threshold_P_log10 (number): get from slider volcanoplot-input_p -  used for summation proteins in categories
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename (string): get from upload data - used in function upload_data.parse_contents
        :param col_name_p_value (list of string):get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :return: category table (dict)
        """

        threshold_P_log10 = -np.log10(threshold_P)
        category_table[category_significant] = 0
        category_table[category_significant_up] = 0
        category_table[category_significant_down] = 0
        category_table[category_notsignificant] = 0
        global old_data
        global new_data
        if old_data==None and new_data != None or old_data == new_data:
            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC, input_value)

                for index, row in df_no_nan_local.iterrows():

                    if row[col_name_logFC] < threshold_logFC[1] and row[col_name_logFC] > threshold_logFC[0] and -np.log10(
                            row[col_name_p_value]) > threshold_P_log10:
                        category_table[category_significant] = category_table[category_significant] + 1

                    elif row[col_name_logFC] > threshold_logFC[1] and -np.log10(row[col_name_p_value]) > threshold_P_log10:
                        category_table[category_significant_up] = category_table[category_significant_up] + 1

                    elif row[col_name_logFC] < threshold_logFC[0] and -np.log10(row[col_name_p_value]) > threshold_P_log10:
                        category_table[category_significant_down] = category_table[category_significant_down] + 1

                    else:
                        category_table[category_notsignificant] = category_table[category_notsignificant] + 1

                return category_table.to_dict('records')
            else:
                return category_table.to_dict('records')
        else:
            return category_table.to_dict('records')


    @app.callback(
        [
            dash.dependencies.Output('selected-data-table', 'data'),
            dash.dependencies.Output('selected-data-table', 'columns')
        ],
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('my-dashbio-volcanoplot', 'selectedData'),
            dash.dependencies.Input('hide-slider', "value"),
        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('input_zero_value_replace', 'value')
        ]
    )
    def update_select_data_table(hidden_div, selectedData, hide_slider, contents, filename, col_name_p_value, col_name_logFC, separ,
                                 input_value):
        """
        Function for updating selected data table where written the data from lasso or box select in the graph
        It's updated after clicking submit-button (it submit upload data,selected separator and selected column for p-value and logFC, annotation
        from uploaded table) or after lasso or box select in the graph

        I use logP and logFC for search in the table. logP and logFC are coordinates (x,y) of proteins in the graph - function select_data_table_match.match_data.
        :param hidden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param selectedData (dict of lists): get from selected-data-table (property selectedData) - info from lasso/box select
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename (string): get from upload data - used in function upload_data.parse_contents
        :param col_name_p_value (list of string): get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :return: (list of string) datable containing rows of proteins which was selected by lasso/box selection
        """
        global old_data
        global new_data
        if old_data == None and new_data != None or old_data == new_data:
            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC, input_value)

                index_list = []
                selected_table = pd.DataFrame(columns=[i for i in df_no_nan_local.columns])
                selected_table_local = selected_table

                if selectedData:
                    for i in range(len(selectedData['points'])):
                        if index_list:
                            for index in index_list:
                                if selectedData['points'][i]['x'] == selectedData['points'][index][
                                    'x']:  # control of proteins in the same coordinates
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

                table_columns = [{"name": i, "id": i, 'hideable': 'first'} for i in df_no_nan_local.columns]

                return [selected_table_local.to_dict('records'), table_columns]

            else:
                df_no_nan_local = pd.DataFrame()
                table_columns = [{"name": i, "id": i, 'hideable': 'first'} for i in df_no_nan_local.columns]
                return [df_no_nan_local.to_dict('records'), table_columns]
        else:
            df_no_nan_local = pd.DataFrame()
            table_columns = [{"name": i, "id": i, 'hideable': 'first'} for i in df_no_nan_local.columns]
            return [df_no_nan_local.to_dict('records'), table_columns]




    @app.callback(

        dash.dependencies.Output('my-dashbio-volcanoplot', "figure"),
        [
            dash.dependencies.Input('hidden-div', 'children'),
            dash.dependencies.Input('datatable-interactivity', "derived_virtual_data"),
            dash.dependencies.Input('datatable-interactivity', "derived_virtual_indices"),
            dash.dependencies.Input('datatable-interactivity', "derived_virtual_selected_rows"),
            dash.dependencies.Input('volcanoplot-input_p', 'value'),
            dash.dependencies.Input('volcanoplot-input', 'value'),
            dash.dependencies.Input('hide-slider', "value"),

        ],
        [
            dash.dependencies.State('upload-data', 'contents'),
            dash.dependencies.State('upload-data', 'filename'),
            dash.dependencies.State('logFC-dataset-dropdown', 'value'),
            dash.dependencies.State('P-value-dataset-dropdown', 'value'),
            dash.dependencies.State('annotations_input', 'value'),
            dash.dependencies.State('separator-dropdown', 'value'),
            dash.dependencies.State('input_zero_value_replace', 'value')
        ]

    )
    def update_graph(hidden_div, rows, indices, derived_virtual_selected_rows, effects_p, effects, hide_slider, contents, filename,
                     col_name_logFC, col_name_p_value, annotations, separ, input_value):
        """
        Function for update graph.
        It's updated with change of inputs.
         -> It's updated after clicking submit-button (it submit upload data,selected separator and selected column for p-value and logFC, annotation
            from uploaded table)
         -> It's updated with selecting rows in the interactivity table or with derived_virtual_data (I have to control how it works)
         ->It's updated after changing slider input for p value or logFC

         Function cooperate with interactivity table due to derived_virtual_data and derived_virtual_selected_rows.

        :param hidden_div: children of hidden_div; it's changed after uploading new data and reseting all components
        :param rows (list of dict): property derived-virtual-data - this property represents the visible state of data across all pages after the front-end sorting and filtering as been applied.
        :param indices: derived_virtual_indices indicates the order in which the original rows appear after being filtered and sorted
        :param derived_virtual_selected_rows (list of numbers): derived_virtual_selected_rows represents the indices of the selected_rows from the perspective of the derived_virtual_indices
            (derived_virtual_indices indicates the order in which the original rows appear after being filtered and sorted)
        :param effects_p (number): get from slider volcanoplot-input_p -  used for specification of volcanoplot property
        :param effects: (list of number) get from rangeslider volcanoplot-input - used for specification od volcanoplot property
        :param hide_slider: value of invisible slider is used, for making something like buffer, its changed when are uploaded new data
        :param contents (string): get from upload data - data for reading csv - used in function upload_data.parse_contents
        :param filename (string): get from upload data - used in function read_csv.parse_contents
        :param col_name_p_value: (list of string) get from P-value-dataset-dropdown - used in function upload_data.parse_contents
        :param col_name_logFC (list of string): get from logFC-dataset-dropdown - used in function upload_data.parse_contents
        :param annotations (string): get from multi choose dropdown annotations-input, it's used for text 'on  hover' - there are function annotation.call_update_annotation
        :param separ (list of string): get from separator-dropdown - actual choose of separator, default is automatic - used in function upload_data.parse_contents
        :param input_value: number - inputed number in the form for replacing zeros p-values in the dataset
        :return: (figure) it returns volcano plot
        """
        effects_p = -np.log10(effects_p)
        global old_data
        global new_data
        if old_data == None and new_data != None or old_data == new_data:
            if derived_virtual_selected_rows is None:
                derived_virtual_selected_rows = []

            if contents:
                df_no_nan_local = upload_data.get_data(contents, filename, separ, col_name_p_value, col_name_logFC, input_value)

                if rows is None:
                    dff = df_no_nan_local
                else:
                    dff = pd.DataFrame(rows, index=indices)
                if dff.empty:
                    dff = df_no_nan_local

                # color part
                #############
                category_color = []
                significant_color = 'rgba(255,221,0)'
                sign_up_color = 'rgba(255,0,0)'
                sign_down_color = 'rgba(0,255,0)'
                not_sign_color = 'rgba(0,170,255)'

                for index, row in dff.iterrows():

                    if row[col_name_logFC] <= effects[1] and row[col_name_logFC] >= effects[0] and -np.log10(
                            row[col_name_p_value]) > effects_p:
                        category_color.append(significant_color)

                    elif row[col_name_logFC] > effects[1] and -np.log10(row[col_name_p_value]) > effects_p:
                        category_color.append(sign_up_color)

                    elif row[col_name_logFC] < effects[0] and -np.log10(row[col_name_p_value]) > effects_p:
                        category_color.append(sign_down_color)

                    else:
                        category_color.append(not_sign_color)

                colors = ['rgba(0,0,0)' if i in derived_virtual_selected_rows else category_color[i]
                          for i in range(len(dff))]

                point_sizes = [10 if i in derived_virtual_selected_rows else 6
                               for i in range(len(dff))]
                arrow_x = []
                arrow_y = []

                for i in range(len(dff)):
                    if i in derived_virtual_selected_rows:
                        arrow_y.append(dff.loc[i]['logP'])
                        arrow_x.append(dff.loc[i][col_name_logFC])

                #############

                y_label_t = "-log10(" + col_name_p_value + ")"
                [annotations_str, dff] = annotation.call_update_annotation(annotations, dff)

                fig = dashbio.VolcanoPlot(
                    p=col_name_p_value,
                    effect_size=col_name_logFC,
                    xlabel=col_name_logFC,
                    ylabel=y_label_t,
                    dataframe=dff,
                    point_size=point_sizes,
                    col=colors,
                    genomewideline_value=effects_p,
                    effect_size_line=effects,
                    highlight_color=None,
                    highlight=None,
                    annotation=annotations_str,
                    snp=None,
                    gene=None)

                for i in range(len(arrow_x)):
                    fig.add_annotation(
                        x=arrow_x[i],
                        y=arrow_y[i],
                    )

                fig.update_annotations(dict(
                    xref="x",
                    yref="y",
                    arrowsize=1,
                    arrowwidth=2,
                    showarrow=True,
                    arrowhead=2, #shape of arrowhead
                    startarrowsize=5,
                    ax=20,
                    ay=-30,
                    opacity=0.8
                ))

                return fig

            else:
                return {'data': [], 'layout': {}, 'frames': []}
        else:
            return {'data': [], 'layout': {}, 'frames': []}


if __name__ == '__main__':
    args = parser.parse_args()
    encoded_data, file_name = prepare_data(args.file_input)
    app.layout = create_layout(encoded_data, file_name)
    define_callbacks()
    app.run_server(debug=False)
