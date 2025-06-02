import dash
from dash import html
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__,
                external_stylesheets=[
                    'https://codepen.io/chriddyp/pen/bWLwgP.css',
                    dbc.themes.BOOTSTRAP
                ],
                suppress_callback_exceptions=True,
                use_pages=True)
# Main app layout with basic routing structure
app.layout = html.Div([
    # dcc.Location(id='url', refresh=False),
    html.H1(
        html.A("Data Management Dashboard", href="/", className="text-decoration-none text-dark"),
        className="mb-4"),
    dash.page_container
])

# CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- AG Grid CSS -->
        <link rel="stylesheet" href="https://unpkg.com/ag-grid-community/styles/ag-grid.css">
        <link rel="stylesheet" href="https://unpkg.com/ag-grid-community/styles/ag-theme-alpine.css">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background-color: #f8f9fa;
            }
            .ag-theme-alpine {
                --ag-background-color: white;
                --ag-border-color: #dee2e6;
            }
            .ag-row-selected {
                --ag-selected-row-background-color: #e3f2fd !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
