from api import data_api
from transforming import transforming
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash, time


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([
    html.Img(src='https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
    html.H1('Generador automático de informes', style={'width': '100%', 'color':'#878786', 'margin-top': '-10px', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'}),
    dcc.Input(id='email', type='email', placeholder='Enter email', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    dcc.Input(id='password', type='password', placeholder='Enter password', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    dcc.Input(id='client', type='text', placeholder='Enter client', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    html.Button('Run Dash', id='login-button', n_clicks=0, style={'width': '102%', 'height': '50px', 'margin-top': '10px'}),
    html.Div(id='output-container-button', children='Enter your credentials and press "Login"', style={'margin-top': '20px'}),
    html.Div(id='time-display'),  # Added this line
    html.Div(id='loading-output', style={'display': 'none'}),
    dcc.Loading(id="loading", type="circle", children=html.Div(id="loading-output"))
], style={'width': '30%', 'margin-left': 'auto', 'margin-right': 'auto'})
@app.callback(
    [
        Output('output-container-button', 'children'),
        Output('time-display', 'children'),
    ],
    [
        Input('login-button', 'n_clicks'),
    ],
    [
        State('email', 'value'),
        State('password', 'value'),
        State('client', 'value')
    ]
)
def update_output(n_clicks, email, password, client):
    if n_clicks > 0:
        start_time = time.time()  # Start time
        if email == 'test@test.com' and password == 'password':
            data = data_api(client)  # Assuming data_api is a function you've defined
            layout_dashboard = transforming(client, data)  # Assuming transforming is a function you've defined
            app.layout = layout_dashboard
            execution_time = round(time.time() - start_time, 2)  # Calculate execution time
            return dcc.Link('Go to Dashboard', href=f'/Dashboard_{client}'), f'Execution time: {execution_time} seconds'  # Include execution time in return
        else:
            return 'Access denied. Please check your credentials.', None  # Return None if no execution time to display
    else:
        return None, None  # Return None if button hasn't been clicked yet

if __name__ == '__main__':
    app.run_server(debug=True)
