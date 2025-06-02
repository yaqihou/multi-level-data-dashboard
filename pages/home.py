import dash
from dash import dcc, html, Input, Output, State, callback
import dash_ag_grid as dag

import pandas as pd
from datetime import datetime
import json

import data_loader as dl


dash.register_page(__name__, path='/')

df = dl.df

# Define the layout for the data table page
def create_data_table_layout():
    
    # Column definitions for AG Grid
    # columnDefs = [
        # {'field': 'id', 'headerName': 'ID', 'width': 80, 'pinned': 'left'},
        # {'field': 'name', 'headerName': 'Product Name', 'width': 150},
        # {'field': 'category', 'headerName': 'Category', 'width': 120},
        # {'field': 'price', 'headerName': 'Price ($)', 'width': 100, 'type': 'numericColumn'},
        # {'field': 'stock', 'headerName': 'Stock', 'width': 100, 'type': 'numericColumn'},
        # {'field': 'last_updated', 'headerName': 'Last Updated', 'width': 130}
    # ]
    columnDefs = []
    for col_name, col_type in zip(df.columns, df.dtypes):
        col_def = {
            'field': col_name,
            'id': col_name.lower().replace(' ', '_'),
            'headerName': col_name,
            'width': 150
        }
        if pd.api.types.is_numeric_dtype(col_type):
            col_def['type'] = 'numericColumn'
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            col_def['type'] = 'dateColumn'
        else:
            col_def['type'] = 'textColumn'

        columnDefs.append(col_def)
    
    
    return html.Div([
        # Control panel
        html.Div([
            html.Div([
                html.Button(
                    "Show Details", 
                    id="show-details-btn",
                    className="btn btn-secondary",
                    disabled=True,
                    style={'marginRight': '10px'}
                ),
                html.Button(
                    "Refresh Data", 
                    id="refresh-btn",
                    className="btn btn-primary"
                ),
            ], className="mb-3"),
            
            # Selected row info
            html.Div([
                html.Div([
                    html.Strong("Selected Item: "),
                    html.Span("None", id="selected-row-info-text")
                ], className="alert alert-info")
            ], id="selected-row-info", className="mb-3"),
        ]),
        
        # AG Grid table
        dag.AgGrid(
            id="data-table",
            rowData=df.to_dict('records'),
            columnDefs=columnDefs,
            defaultColDef={
                'resizable': True,
                'sortable': True,
                'filter': True,
            },
            dashGridOptions={
                'rowSelection': 'single',
                'suppressRowClickSelection': False,
                'animateRows': True,
                'pagination': True,
                'paginationPageSize': 15,
            },
            style={'height': '500px', 'width': '100%'},
            className="ag-theme-alpine"
        ),
        
        # Store selected row data
        dcc.Store(id='selected-row-store'),
        
        # URL component for navigation (will be used later for multi-page)
        dcc.Location(id='url', refresh=False),
    ])

# Main app layout with basic routing structure
def layout():

    return  html.Div([
    # dcc.Location(id='url', refresh=False),
    html.Div(
        create_data_table_layout(),
        id='page-content'
    )
])

# # Callback for page routing
# @app.callback(Output('page-content', 'children'),
#               Input('url', 'pathname'))
# def display_page(pathname):
#     if pathname == '/details':
#         # Placeholder for details page - implement later
#         return html.Div([
#             html.H2("Details Page"),
#             html.P("Details page will be implemented here"),
#             dcc.Link("Back to Data Table", href="/")
#         ])
#     else:
#         # Default to data table page
#         return create_data_table_layout()

# Callback for handling row selection and button state
@callback(
    [Output('show-details-btn', 'disabled'),
     Output('show-details-btn', 'className'),
     Output('selected-row-info-text', 'children'),
     Output('selected-row-store', 'data')],
    [Input('data-table', 'selectedRows'),
     # Add This input so that double clicked will update the stroed row selection
     Input('data-table', 'cellDoubleClicked')],
    prevent_initial_call=True
)
def handle_row_selection(selected_rows, double_clicked):
    """Handle row selection and double-click events"""
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return True, "btn btn-secondary", "", None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle both single selection and double-click
    if trigger_id == 'data-table':
        if selected_rows and len(selected_rows) > 0:
            selected_row = selected_rows[0]
            
            # Enable button and change to blue
            button_disabled = False
            button_class = "btn btn-primary"
            
            # Display selected row info
            info_display = f"{selected_row['Position ID']} at {selected_row['Business Date']}"

            return button_disabled, button_class, info_display, selected_row
    
    # No selection
    return True, "btn btn-secondary", "", None

# Callback for refresh button
@callback(
    Output('data-table', 'rowData'),
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """Refresh the data in the table"""
    if n_clicks:
        return df.to_dict('records')
    return dash.no_update

# Callback for show details button (placeholder for navigation)
dash.clientside_callback(
    """
    function(n_clicks, cell_double_clicked, selected_row_data) {
        console.log(dash_clientside.callback_context);

        if (n_clicks && selected_row_data) {
            const positionId = selected_row_data["Position ID"];
            const businessDate = selected_row_data["Business Date"];
            if (positionId && businessDate) {
                 const url = encodeURIComponent(`/details/position/${positionId}/${businessDate}`);
                 window.open(url, '_blank');
            } 
        }

        return dash_clientside.no_update;
    }
    """,
    Output('show-details-btn', 'value'),
    [Input('show-details-btn', 'n_clicks'),
     Input('data-table', 'cellDoubleClicked')],
    [State('selected-row-store', 'data')],
    prevent_initial_call=True
)
