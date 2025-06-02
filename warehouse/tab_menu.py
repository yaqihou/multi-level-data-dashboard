
import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH, Patch, callback
import dash_bootstrap_components as dbc
import uuid # For generating unique tab IDs

# --- App Initialization ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# --- Initial Tab Definitions ---
# Let's start with one default tab that cannot be closed.

class Tab:

    def __init__(self, id, label, closable=True):
        self.id = id
        self.label = label
        self.closable = closable

    @property
    def html(self):
        return dbc.Tab(
            label=self.label,
            id={'type': "tab", 'id': self.id},
            tab_id=self.id,
        )

    @property
    def content(self): 
        return html.Div([
            html.H4(f"Content for: {self.label}"),
            html.P("This is dynamically generated content for this tab."),
        ])

class MainTab(Tab):

    @property
    def content(self):
        return html.Div([
            html.H2("This is the main tab"),
            html.P("This is the main tab content."),
        ])
    

tabs = {
    'tab-1': MainTab(id="tab-1", label="Tab 1", closable=False),
    'tab-2': Tab(id="tab-2", label="Tab 2")
}  

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
def add_tab(n_clicks):

    idx = len(tabs) + 1

    tab = Tab(
        id=f"tab-{idx}",  # Generate a unique ID for the new tab
        label=f"Tab {idx}",
        closable=True
    )
    tabs[f"tab-{idx}"] = tab

    tab_children = Patch()
    tab_children.append(tab.html)
    
    return tab_children

@callback(
    Output('tab-content', 'children'),
    Input('tabs-container', 'active_tab'),
)
def update_tab_content(activate_tab_id):
    ret = tabs.get(activate_tab_id)
    if ret is None:
        return html.Div("Select a tab to see its content.")
    else:
        return ret.content

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)
