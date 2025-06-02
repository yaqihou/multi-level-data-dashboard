
import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH, Patch, callback
import dash_bootstrap_components as dbc
import uuid # For generating unique tab IDs

# --- App Initialization ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# --- Initial Tab Definitions ---
# Let's start with one default tab that cannot be closed.


class Plots:

    @property
    def layout(self):

        return dcc.Graph(

        )

class Plot:

    @property
    def layout(self):

        return dcc.Graph(
            figure=None
        )


# --- App Layout ---
app.layout = html.Div([
    html.H3("Dynamic Tab Demo"),
    html.Div([
        dcc.Input(id="new-tab-label-input", placeholder="Enter new tab label", value=""),
        html.Button("Add Tab", id="add-tab-button", n_clicks=0, style={'marginLeft': '10px'}),
    ], style={'marginBottom': '20px'}),

    dbc.Tabs(id="tabs-container", children=[x.html for x in tabs.values()], active_tab='tab-1'),

    html.Div(id="tab-content"),
    
])

# --- Callbacks ---

# Callback 1: Add a new tab definition to the store
@callback(
    Output('tabs-container', 'children'),
    Input('add-tab-button', 'n_clicks'),
    prevent_initial_call=True,
)


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)
