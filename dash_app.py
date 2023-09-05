from scraping import scraping
from transforming import transforming
from dash.dependencies import Input, Output, State
from dash import dcc, html
from flask import Flask
from dash import Dash

server = Flask(__name__)
app1 = Dash(server=server, url_base_pathname='/Home_Scraping/')
app2 = Dash(server=server, url_base_pathname='/Dashboard_CIGE/')
app1.layout = html.Div([
    html.Img(src='https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
    dcc.Input(id='email', type='email', placeholder='Enter email', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    dcc.Input(id='password', type='password', placeholder='Enter password', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    dcc.Input(id='client', type='text', placeholder='Enter client', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    html.Button('Login', id='login-button', n_clicks=0, style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    html.Div(id='output-container-button', children='Enter your credentials and press "Login"', style={'margin-top': '20px'})
], style={'width': '30%', 'margin-left': 'auto', 'margin-right': 'auto'})
@app1.callback(
    Output('output-container-button', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('email', 'value'),
    State('password', 'value'),
    State('client', 'value')]
)
def update_output(n_clicks, email, password, client):
    if n_clicks > 0:
        if email == 'test@test.com' and password == 'password':
            data = scraping(client)
            layout_dashboard = transforming(client, data)
            app2.layout = layout_dashboard
            return dcc.Link('Go to Dashboard', href='https://tu-usuario.pythonanywhere.com/Dashboard_CIGE/')
        else:
            return 'Access denied. Please check your credentials.'

if __name__ == '__main__':
    server.run(debug=True, port=9000)