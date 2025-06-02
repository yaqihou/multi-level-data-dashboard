# dash_multi_tab_dashboard/components/synchronized_table.py
from dash import html, dash_table
import pandas as pd

def create_synchronized_tables(df_dict, table_id_prefix):
    """
    Creates a layout with multiple tables that are meant to be synchronized vertically.
    df_dict: A dictionary where keys are panel names and values are pandas DataFrames.
             The first DataFrame in the dictionary should contain the common index.
    table_id_prefix: A unique prefix for the table IDs.
    """
    if not df_dict:
        return html.Div("No data provided for synchronized tables.")

    panels = []
    table_ids = []

    # Ensure 'id' column exists if not using index directly in DashTable
    # Or ensure index is named if using it. For simplicity, let's assume an 'id' column.

    first_panel = True
    for i, (panel_name, df) in enumerate(df_dict.items()):
        current_table_id = f"{table_id_prefix}-{i}"
        table_ids.append(current_table_id)

        columns_to_display = [{"name": col, "id": col} for col in df.columns]

        panel_style = {
            'overflowX': 'auto',
            'flex': '1', # Distribute space
            'minWidth': '200px', # Ensure panels don't get too small
            'marginRight': '5px' if not i == len(df_dict) -1 else '0px'
        }
        # The first panel will be the one others synchronize to vertically.
        # It might also contain the main index column.
        table_component = dash_table.DataTable(
            id=current_table_id,
            columns=columns_to_display,
            data=df.to_dict('records'),
            style_table={'height': '300px', 'overflowY': 'auto' if not first_panel else 'scroll'}, # Main scroll on first
            style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '100px', 'textAlign': 'left'},
            fixed_rows={'headers': True}, # Keep headers visible
            # For the first table, assign a class to identify it for JS
            className='sync-table-master' if first_panel else 'sync-table-slave'
        )
        panels.append(html.Div(table_component, style=panel_style))
        first_panel = False


    return html.Div(
        panels,
        id=f'{table_id_prefix}-container',
        style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'},
        # Custom data attribute to pass table IDs to JavaScript
        **{'data-table-ids': ','.join(table_ids)}
    )

# Example Usage (for testing this component standalone)
if __name__ == '__main__':
    from dash import Dash, html
    app = Dash(__name__, external_scripts=['/assets/synchronized_scroll.js']) # Ensure JS is loaded

    # Sample data
    data_main = {'ID': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
                 'Metric1': [i*10 for i in range(10)],
                 'Metric2': [i*10+5 for i in range(10)]}
    df_main = pd.DataFrame(data_main)

    data_group2 = {'FeatureA': [i*100 for i in range(10)],
                   'FeatureB': [f'Cat{i}' for i in range(10)]}
    df_group2 = pd.DataFrame(data_group2)

    data_group3 = {'DataX': [i*0.5 for i in range(10)],
                   'DataY': [i*0.1 for i in range(10)],
                   'DataZ': [i*2 for i in range(10)]}
    df_group3 = pd.DataFrame(data_group3)

    # Important: For synchronization, ensure all DataFrames have the same number of rows.
    # Typically, the 'ID' or index would be common and you'd select columns for each panel.
    # Here, we'll combine them and then split for demonstration:
    combined_df = pd.concat([df_main.set_index('ID'), df_group2, df_group3], axis=1).reset_index()

    tables_data = {
        "Main": combined_df[['ID', 'Metric1', 'Metric2']],
        "Group2": combined_df[['FeatureA', 'FeatureB']],
        "Group3": combined_df[['DataX', 'DataY', 'DataZ']]
    }

    app.layout = html.Div([
        html.H3("Synchronized Tables Demo"),
        create_synchronized_tables(tables_data, "demo-sync-table")
    ])
    app.run_server(debug=True)
