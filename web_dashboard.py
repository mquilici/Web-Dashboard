import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from animal_shelter import AnimalShelter # required module for MongoDB operations


# Data Manipulation / Model ############################################################################################

# Username and password for needed to access animal shelter database
username = "aacuser"
password = "password"
shelter = AnimalShelter(username, password)

# Create dataframe from MongoDB database
df = pd.DataFrame.from_records(shelter.read({}))

# Get animal properties for dropdown menu options
genders = list(sorted(df['sex_upon_outcome'].unique()))
types = list(sorted(df['animal_type'].unique()))
breeds = list(sorted(df['breed'].unique()))
gender_options = [{'label': str(o), 'value': str(o)} for o in genders]
type_options = [{'label': str(o), 'value': str(o)} for o in types]
breed_options = [{'label': str(o), 'value': str(o)} for o in breeds]

# Define age range slider limits
age_range_max = int(df['age_upon_outcome_in_weeks'].max())

# Appearance settings
pie_chart_text_color = 'white'
table_background_color = '#333'
table_title_color = '#444'
table_outline_color = '#000'


# Dashboard ############################################################################################################

# Start Dash application
app = dash.Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.DARKLY])

# Define dashboard layout
app.layout = html.Div([

    # Title
    html.Center(html.P(html.H2('Animal Shelter Dashboard'))),

    # Controls
    html.Div([

        # Reset button to clear menu selections
        html.Div([
            html.Button('Reset', id='reset-button', n_clicks=0),
        ], style={'width': '50px',
                  'margin-top': '24px',
                  'margin-left': '10px',
                  'margin-right': '10px',
                  'verticalAlign': 'top',
                  'display': 'inline-block'}
        ),

        # Animal type dropdown
        html.Label([
            "Animal Type:",
            dcc.Dropdown(
                id="types-dropdown",
                options=type_options,
                placeholder="Select a type",
                searchable=False,
            )
        ], style={'width': '15vw',
                  'margin-left': '10px',
                  'verticalAlign': 'top',
                  'display': 'inline-block'}
        ),

        # Animal breed dropdown
        html.Label([
            "Animal Breed:",
            dcc.Dropdown(
                id="breeds-dropdown",
                options=breed_options,
                placeholder="Select a breed",
            )
        ], style={'width': '25vw',
                  'margin-left': '10px',
                  'verticalAlign': 'top',
                  'display': 'inline-block'}
        ),

        # Animal gender dropdown
        html.Label([
            "Animal Gender:",
            dcc.Dropdown(
                id="genders-dropdown",
                options=gender_options,
                placeholder="Select a Gender",
            )
        ], style={'width': '15vw',
                  'margin-left': '10px',
                  'verticalAlign': 'top',
                  'display': 'inline-block'}
        ),

        # Animal age range slider
        html.Div([
            html.Center(id='slider-text',
                        style={'margin-bottom': 10},
                        children=['Age Range: 0 to {max_age} weeks'.format(max_age=int(age_range_max))]
                        ),
            dcc.RangeSlider(
                id='age-range-slider',
                min=0,
                max=age_range_max,
                value=[0, age_range_max],
                step=1,
                updatemode='mouseup',
                allowCross=False,
            ),
        ], style={'width': '30vw',
                  'margin-left': '10px',
                  'verticalAlign': 'top',
                  'display': 'inline-block'}
        ),
    ]),

    # Data table
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        style_header={'backgroundColor': table_title_color},
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,                         # Adjust cell width so data fits on screen
            'backgroundColor': table_background_color,
            'border': '1px solid ' + table_outline_color
        },
        data=df.to_dict('records'),
        editable=False,                            # Prevent column-level editing
        filter_action="native",                    # Enable UI filtering
        sort_action="native",                      # Allow columns to be sorted
        sort_mode="multi",                         # Enable multi-column sorting
        column_selectable=False,                   # Prevent columns from being selected
        row_selectable="single",                   # Enable single-row selection
        row_deletable=False,                       # Prevent rows from being deleted
        selected_columns=[],                       # Indices of the selected columns in table
        selected_rows=[],                          # Indices of the selected rows in table
        page_action="native",                      # Paging logic is handled by the table
        page_current=0,                            # Define start page
        page_size=10,                              # Define number of rows per page
        style_table={'overflowY': 'auto', 'height': '365px'}
    ),
    html.Br(),
    html.Hr(),

    # Map and pie chart
    html.Div(
        style={'display': 'flex'},
        children=[
        html.Div(id="map-id", style={'display': 'inline-block'}),
        html.Div(id="graph-id", style={'display': 'inline-block'})
    ]),
],
    style={'margin': '10px'}  # Create border around page
)


# Callbacks ############################################################################################################

# Callback to update text above age range slider
@app.callback(
    Output('slider-text', 'children'),
    [Input('age-range-slider', 'drag_value')]
)
def update_output(value):
    # Update text above age range slider to show min and max values
    return 'Age Range: {min_age} to {max_age} weeks'.format(min_age=value[0], max_age=value[1])


# Callback to reset all dropdown selections
@app.callback(
    [Output('types-dropdown', 'value'),
     Output('breeds-dropdown', 'value'),
     Output('genders-dropdown', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def update_dropdowns(reset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # Clear menus selections when reset is clicked
    if 'reset-button' in changed_id:
        return "", "", ""


# Callback to update the table when a menu selection is made
@app.callback(
    [Output('datatable-id', 'data'),
     Output('datatable-id', 'columns'),
     Output('datatable-id', 'selected_rows')],
    [Input('genders-dropdown', 'value'),
     Input('types-dropdown', 'value'),
     Input('breeds-dropdown', 'value'),
     Input('age-range-slider', 'value')]
)
def update_dashboard(genders_dropdown, types_dropdown, breeds_dropdown, age_range):

    # Define age range slider limits and prevent range settings where no animals appear
    age_min = max(age_range[0], 0)                # Ensure age_min is positive
    age_max = max(age_range[1] + 1, age_min + 1)  # Ensure age_max is 1 greater than age_min

    # Conditional block that determines which query to execute based on dropdown choices
    if genders_dropdown and types_dropdown and breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"sex_upon_outcome": genders_dropdown,
                                                      "animal_type": types_dropdown,
                                                      "breed": breeds_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif genders_dropdown and types_dropdown and not breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"sex_upon_outcome": genders_dropdown,
                                                      "animal_type": types_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif genders_dropdown and not types_dropdown and breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"sex_upon_outcome": genders_dropdown,
                                                      "breed": breeds_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif genders_dropdown and not types_dropdown and not breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"sex_upon_outcome": genders_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif not genders_dropdown and types_dropdown and breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": types_dropdown,
                                                      "breed": breeds_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif not genders_dropdown and types_dropdown and not breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": types_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif not genders_dropdown and not types_dropdown and breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"breed": breeds_dropdown,
                                                      "age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    elif not genders_dropdown and not types_dropdown and not breeds_dropdown:
        dff = pd.DataFrame.from_records(shelter.read({"age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    # If the reset button is selected
    else:
        dff = pd.DataFrame.from_records(shelter.read(
            {"age_upon_outcome_in_weeks": {"$gte": age_min, "$lte": age_max}}))

    # Table column labels
    columns = [{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns]

    # If there are no matches to selection, use empty data
    if dff.empty:
        dff = pd.DataFrame(columns=df.columns)

    # Convert dataframe to dictionary to display in table
    data = dff.to_dict('records')

    # Return data, columns, clear selected rows, set page number to 0
    return data, columns, []


# Callback to update other dropdowns and slider when a selection is made
@app.callback(
    [Output('types-dropdown', 'options'),
     Output('breeds-dropdown', 'options'),
     Output('genders-dropdown', 'options'),
     Output('age-range-slider', 'min'),
     Output('age-range-slider', 'max'),
     Output('age-range-slider', 'value'),
     Output('datatable-id', "page_current")],
    [Input('types-dropdown', 'value'),
     Input('breeds-dropdown', 'value'),
     Input('genders-dropdown', 'value')]
)
def update_dropdowns(animal_type, animal_breed, animal_gender):

    # Animal type selected
    if animal_type and animal_breed and animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": animal_type, "breed": animal_breed, "sex_upon_outcome": animal_gender}))
    elif animal_type and animal_breed and not animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": animal_type, "breed": animal_breed}))
    elif animal_type and not animal_breed and animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": animal_type, "sex_upon_outcome": animal_gender}))
    elif animal_type and not animal_breed and not animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"animal_type": animal_type}))

    # Breed selected
    elif not animal_type and animal_breed and animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"breed": animal_breed, "sex_upon_outcome": animal_gender}))
    elif not animal_type and animal_breed and not animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"breed": animal_breed}))

    # Gender selected
    elif not animal_type and not animal_breed and animal_gender:
        dff = pd.DataFrame.from_records(shelter.read({"sex_upon_outcome": animal_gender}))

    # Nothing selected
    elif not animal_type and not animal_breed and not animal_gender:
        dff = df

    # Define age range slider limits
    age_min = max(int(dff['age_upon_outcome_in_weeks'].min()), 0)        # Ensure age_min is positive
    age_max = max(int(dff['age_upon_outcome_in_weeks'].max()), age_min)  # Ensure age_max is >= age_min

    # Define menu options by sorting the unique values for each category
    selected_type = list(sorted(dff['animal_type'].unique()))
    selected_breeds = list(sorted(dff['breed'].unique()))
    selected_genders = list(sorted(dff['sex_upon_outcome'].unique()))
    selected_type_options = [{'label': str(o), 'value': str(o)} for o in selected_type]
    selected_breed_options = [{'label': str(o), 'value': str(o)} for o in selected_breeds]
    selected_gender_options = [{'label': str(o), 'value': str(o)} for o in selected_genders]

    # Return 0 for page number to reset table page when a selection is made
    return selected_type_options, selected_breed_options, selected_gender_options, age_min, age_max, [age_min, age_max], 0


# Callback to create a pie chart that displays the percentage of each breed shown in the current table view
@app.callback(
    Output('graph-id', "children"),
    Input('datatable-id', "derived_viewport_data")
)
def update_graphs(view_data):
    if view_data:

        # If the table data is empty do not update chart
        if len(view_data) == 0:
            return

        # Use table data in chart
        dff = pd.DataFrame.from_dict(view_data)                        # Create dataframe from table data
        dfb = dff['breed']                                             # Get breeds from current table page
        percent = dfb.value_counts(normalize=True).mul(100).round(2)   # Compute percentage of each breed in data
        labels = percent.index.tolist()                                # Get labels for pie chart
        values = percent.values.tolist()                               # Get percentages for pie chart

        # Keep label length fixed and set label font to courier to prevent pie chart from shifting around
        new_labels = ["{:<40}".format(label[:40]) for label in labels]

        # Create plotly express pie chart
        fig = px.pie(dfb, values=values, names=new_labels, hole=.4)

        # Update title and labels
        fig.update_layout({'title': {'text': 'Breeds',
                                     'x': 0.305, 'xanchor': 'center',  # Center chart title horizontally
                                     'y': 0.540, 'yanchor': 'top'},    # Center chart title vertically
                           'font': {'color': pie_chart_text_color},    # Text color
                           'paper_bgcolor': 'rgba(0, 0, 0, 0)',        # Make background transparent
                           'font_family': 'Courier New'})              # Use courier font to prevent chart from shifting

        # Return pie chart definition
        return [
           dcc.Graph(
               figure=fig
           )
        ]


# Callback to create a map showing the positions of the animals
@app.callback(
    Output('map-id', 'children'),
    [Input('datatable-id', "derived_viewport_data"),
     Input('datatable-id', "derived_viewport_selected_rows")]
)
def update_map(data, selected_rows):

    # If table is empty do not draw map
    if len(data) == 0:
        return

    # If a table row is selected, show the location of the animal on the map
    # otherwise show the locations of all animals in the current table view
    if selected_rows:
        # Create Pandas dataframe from selected animal data
        dff = pd.DataFrame.from_dict(data).iloc[selected_rows]
    else:
        # Create Pandas dataframe from current table data
        dff = pd.DataFrame.from_dict(data)

    # Load animal latitude and longitude
    lats = dff['location_lat'].to_list()
    lons = dff['location_long'].to_list()

    # Load animal information
    animal_names = dff['name'].to_list()
    animal_types = dff['animal_type'].to_list()
    animal_breeds = dff['breed'].to_list()
    animal_ages = dff['age_upon_outcome_in_weeks'].to_list()
    animal_sexes = dff['sex_upon_outcome'].to_list()

    # Generate markers for each animal
    markers = []
    for i in range(len(lats)):
        # Add a maker definition for each animal
        markers += [
            dict(lat=lats[i],
                 lon=lons[i],
                 tooltip=animal_names[i] if animal_names[i] else "Unnamed",
                 # if the animal name empty replace it with "Unnamed"
                 popup="<body><h4>Name: " + str(animal_names[i] if animal_names[i] else "Unnamed") + "</h4>"
                       + "Type: " + str(animal_types[i]) + "<br>"
                       + "Breed: " + str(animal_breeds[i]) + "<br>"
                       + "Age: " + str(int(animal_ages[i])) + " weeks<br>"
                       + "Sex: " + str(animal_sexes[i]) + "</body>"
            )
        ]

    # Convert markers to geojson format
    geojson_markers = dlx.dicts_to_geojson(markers)

    # Return map with markers
    return [
        dl.Map(style={'width': '50vw', 'height': '480px'},                     # make width 50% and height 45%
               center=[0.5*(max(lats)+min(lats)), 0.5*(max(lons)+min(lons))],  # center map within markers
               zoom=9,                                                         # zoom level smaller=closer
               children=[
                   dl.TileLayer(id="base-layer-id"),
                   dl.GeoJSON(data=geojson_markers)]
        )
    ]


if __name__ == '__main__':
    app.run_server(debug=False)