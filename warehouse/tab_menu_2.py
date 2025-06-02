import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import uuid # For generating unique tab IDs

# App initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    html.H1("Dynamic Closable Tabs Example"),
    html.P("Add tabs and close them using the '×' button on each tab."),
    html.Br(),

    dbc.Button("Add New Tab", id="add-tab-button", n_clicks=0, color="primary", className="mb-3"),

    # Store for holding the list of current tabs
    # Data structure: [{'id': 'unique-id-1', 'label': 'Tab 1 Label'}, {'id': 'unique-id-2', 'label': 'Tab 2 Label'}]
    dcc.Store(id='tabs-state-store', data=[]),

    # Store for holding the ID of the currently active tab
    dcc.Store(id='active-tab-id-store', data=None),

    # This Div will hold the dcc.Tabs component
    html.Div(id='tabs-container'),

    # This Div will hold the content of the active tab
    html.Div(id='tab-content-container', className="mt-3 p-3 border rounded bg-light")
], fluid=True, className="py-4")

# --- Callbacks ---

# 1. Callback to add a new tab
@app.callback(
    Output('tabs-state-store', 'data'),
    Output('active-tab-id-store', 'data', allow_duplicate=True), # Make the new tab active
    Input('add-tab-button', 'n_clicks'),
    State('tabs-state-store', 'data'),
    prevent_initial_call=True
)
def add_new_tab(n_clicks, existing_tabs_data):
    if n_clicks > 0:
        new_tab_id = str(uuid.uuid4())
        tab_number = len(existing_tabs_data) + 1
        new_tab_data = {'id': new_tab_id, 'label': f'Tab {tab_number}'}

        updated_tabs_data = existing_tabs_data + [new_tab_data]
        return updated_tabs_data, new_tab_id # Return updated tabs and set new tab as active
    return no_update, no_update


# 2. Callback to render the dcc.Tabs component based on tabs-state-store
@app.callback(
    Output('tabs-container', 'children'),
    Output('active-tab-id-store', 'data', allow_duplicate=True), # May need to update active tab if closed tab was active
    Input('tabs-state-store', 'data'),
    State('active-tab-id-store', 'data'), # Get current active tab to try and preserve it
    prevent_initial_call=True # Let initial empty state be handled by layout
)
def render_tabs_component(tabs_data, current_active_tab_id):
    if not tabs_data:
        return html.Div(), None # No tabs to show, clear active tab

    # Determine the active tab
    new_active_tab_id = current_active_tab_id
    current_tab_ids = {tab['id'] for tab in tabs_data}

    if current_active_tab_id not in current_tab_ids: # If active tab was closed or doesn't exist
        if tabs_data: # If there are tabs left
            new_active_tab_id = tabs_data[-1]['id'] # Default to the last tab
        else:
            new_active_tab_id = None

    tabs_children = []
    for tab_info in tabs_data:
        tab_label_with_close = html.Span([
            tab_info["label"] + " ",
            dbc.Button(
                "×", # A common symbol for close
                id={"type": "close-tab-button", "index": tab_info["id"]},
                n_clicks=0,
                size="sm",
                color="danger",
                outline=True,
                className="ml-2 p-0", # Bootstrap margin and padding utilities
                style={
                    "border": "none",
                    "background": "transparent",
                    "color": "gray", # Initial subtle color
                    "fontSize": "1.2em",
                    "lineHeight": "1",
                    "fontWeight": "bold",
                    "verticalAlign": "middle",
                    "paddingBottom": "2px" # Fine-tuning alignment
                }
            )
        ], style={"display": "inline-flex", "alignItems": "center", "justifyContent": "space-between", "width":"100%"})

        # Apply different style if the tab is active, primarily for the close button
        # This is tricky here directly; better to style close button on hover globally via CSS if needed.
        # For simplicity, the style is kept static in this MWE.

        tabs_children.append(
            dcc.Tab(
                children=tab_label_with_close,
                label=tab_info['label'],
                value=tab_info["id"],
                id=f"dynamic-tab-{tab_info['id']}", # Unique ID for each dcc.Tab component
                style={'padding': '8px 10px'}, # Adjust padding for dcc.Tab
                selected_style={'fontWeight': 'bold', 'borderTop': '2px solid #007bff'} # Example selected style
            )
        )

    # If new_active_tab_id is None and there are tabs, set it to the first tab
    if new_active_tab_id is None and tabs_data:
        new_active_tab_id = tabs_data[0]['id']

    return dcc.Tabs(id='dynamic-dcc-tabs', children=tabs_children, value=new_active_tab_id), new_active_tab_id


# 3. Callback to handle closing a tab
@app.callback(
    Output('tabs-state-store', 'data', allow_duplicate=True), # Update the source of truth for tabs
    Input({"type": "close-tab-button", "index": ALL}, "n_clicks"),
    State('tabs-state-store', 'data'),
    prevent_initial_call=True
)
def close_selected_tab(close_button_n_clicks, tabs_data):
    ctx = callback_context
    if not ctx.triggered_id or not any(n_clicks > 0 for n_clicks in close_button_n_clicks if n_clicks is not None):
        return no_update

    # The ID of the button has the tab_id in its 'index' key
    tab_id_to_close = ctx.triggered_id['index']

    # Filter out the tab to be closed
    updated_tabs_data = [tab for tab in tabs_data if tab['id'] != tab_id_to_close]
    return updated_tabs_data


# 4. Callback to update active tab ID in store when user clicks a tab in dcc.Tabs
@app.callback(
    Output('active-tab-id-store', 'data'),
    Input('dynamic-dcc-tabs', 'value'), # 'value' of dcc.Tabs is the 'value' of the selected dcc.Tab
    prevent_initial_call=True
)
def sync_active_tab_id(selected_tab_value):
    return selected_tab_value


# 5. Callback to render the content of the active tab
@app.callback(
    Output('tab-content-container', 'children'),
    Input('active-tab-id-store', 'data'), # Triggered by change in active tab ID
    State('tabs-state-store', 'data') # Get all tabs data to find the active one's details
)
def render_active_tab_content(active_tab_id, all_tabs_data):
    if not active_tab_id or not all_tabs_data:
        return dbc.Alert("No tab selected or no tabs available. Click 'Add New Tab' to get started!", color="info")

    active_tab_info = next((tab for tab in all_tabs_data if tab['id'] == active_tab_id), None)

    if active_tab_info:
        return html.Div([
            html.H4(f"Content for: {active_tab_info['label']}"),
            html.P(f"You are viewing the content for tab with ID: {active_tab_info['id']}."),
            html.P("Each tab could have completely different content, like graphs, forms, or text."),
            dcc.Input(placeholder=f"Type something for {active_tab_info['label']}...", className="mt-2 form-control"),
            # In a real app, you would generate more complex content here based on tab_info
            # e.g., dcc.Graph(figure=some_figure_function(active_tab_info['id']))
        ])
    return dbc.Alert("Content for the selected tab could not be found.", color="warning")


if __name__ == '__main__':
    app.run(debug=True, port=8051) # Changed port just in case 8050 is busy
