import dash
from dash import dcc, html, Input, Output, State, callback
from dash import dash_table
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc

import urllib.parse 
import pandas as pd
from datetime import datetime
import json

import data_loader as dl

dash.register_page(__name__,
                   path_template="/details/position/<position_id>/<business_date>",
                   title="Detail View")

def layout(position_id, business_date):
    _position_id = urllib.parse.unquote(position_id)
    _business_date = urllib.parse.unquote(business_date)

    df_position = (
        dl.df
        .query("`Position ID` == @_position_id and `Business Date` == @_business_date")
        .reset_index(drop=True)
        .copy()
    )
    df_position_trend = dl.df.query("`Position ID` == @position_id").copy()

    return html.Div([
        # Details Card
        html.H2("Position Details", className="mb-4"),
        make_detail_card(df_position),

        # Trend Table Part
        html.H2("Position Trend", className="mb-4"),
        make_trend_table(df_position_trend),

        # Trend Plot Part
        make_trend_plot(df_position_trend),

    ])


def make_detail_card(df_position):

    cols1 = (
        ['Position ID', 'Business Date', 'Asset Type', 'CleanPnL']
        + [x for x in df_position.columns if x.startswith('Meta')]
    )
    cols2 = [x for x in df_position.columns if x.startswith('Pnl')]
    cols3 = [x for x in df_position.columns if x.startswith('RTPL')]
    cols4 = [x for x in df_position.columns if x.startswith('Settings')]

    _data = {
        'Basic': cols1,
        'Clean PnL': cols2,
        'RTPL': cols3,
        'Settings': cols4
    }

    return html.Div([
        dbc.Card([
            dbc.CardHeader(key),
            dbc.CardBody(make_detail_card_table(df_position[cols]))
        ])
        for key, cols in _data.items()
    ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px'})


def make_detail_card_table(df):
    assert len(df) == 1, "DataFrame should contain exactly one row for detail view."
    return [
        dash_table.DataTable(
            data=df.T.reset_index().rename(columns={'index': 'Field', 0: 'Value'}).to_dict('records'),
            columns=[
                {"name": "Field", "id": "Field", "type": "text"},
                {"name": "Value", "id": "Value", "type": "text"}
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '8px 12px',
                'fontFamily': 'inherit',
                'fontSize': '14px',
                'border': 'none',
            },
            style_header={
                'backgroundColor': 'transparent',
                'fontWeight': 'bold',
                'border': 'none',
                'borderBottom': '2px solid #dee2e6',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgba(0,0,0,0.02)'
                }
            ],
            style_table={'overflowX': 'auto'},
            css=[
                {
                    'selector': '.dash-table-container',
                    'rule': 'border: none !important;'
                }
            ]
        )
    ]


def make_trend_table(df):

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
        html.H3("Position Historical Trend", className="mb-5"),
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
    ])


def make_trend_plot(df):
    # Placeholder for future plot implementation
    
    _df = pd.melt(df, id_vars=['Business Date'], 
                  value_vars=['CleanPnL', 'RTPL'], 
                  var_name='PnL Type', value_name='PnL')
    fig_pnl_trend = px.line(_df, 
                            x='Business Date', 
                            y='PnL', 
                            color='PnL Type',
                            title='Position PnL Trend',
                            labels={'Business Date': 'Business Date', 'PnL': 'PnL Value'},
                            markers=True)

    _df = df[['Business Date', 'CleanPnL', 'RTPL']].copy()
    _df['Diff'] = _df['RTPL'] - _df['CleanPnL'] 
    fig_diff_dist = px.histogram(_df, 
                                 x='Diff', 
                                 nbins=30, 
                                 title='Difference Distribution (RTPL - CleanPnL)',
                                 labels={'Diff': 'Difference'})

    _df['DiffAbs'] = _df['Diff'].abs()
    _df_top_diff = _df.sort_values(by='DiffAbs', ascending=False).head(10)
    _df_top_diff = _df_top_diff[['Business Date', 'CleanPnL', 'RTPL', 'Diff']]
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader("Position PnL Trend"),
            dbc.CardBody(dcc.Graph(figure=fig_pnl_trend))
        ], id="cleanpnl-trend-card"),
        
        # Difference Distribution Card
        html.Div([
            dbc.Card([
                dbc.CardHeader("Difference Distribution"),
                dbc.CardBody(dcc.Graph(figure=fig_diff_dist))
            ], id="diff-dist-card", style={'minWidth': '70%'}),
            dbc.Card([
                dbc.CardHeader("Large Difference Info"),
                dbc.CardBody(
                    dash_table.DataTable(
                        data=_df_top_diff.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in _df_top_diff.columns],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '8px 12px',
                            'fontFamily': 'inherit',
                            'fontSize': '14px',
                            'border': 'none'
                        },
                        style_header={
                            'backgroundColor': 'transparent',
                            'fontWeight': 'bold',
                            'border': 'none',
                            'borderBottom': '2px solid #dee2e6'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgba(0,0,0,0.02)'
                            }
                        ],
                        style_table={'overflowX': 'auto'},
                        css=[
                            {
                                'selector': '.dash-table-container',
                                'rule': 'border: none !important;'
                            }
                        ]
                    )
                )
            ], id="additional-info-card", style={'minWidth': '30%'})
        ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px'})
    ])
