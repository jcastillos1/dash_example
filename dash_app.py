from scraping import scraping
from transforming import transforming
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash


app1,app2 = dash.Dash(), dash.Dash()
app1.layout = html.Div([
    html.Img(src='https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
    dcc.Input(id='email', type='email', placeholder='Enter email', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    dcc.Input(id='password', type='password', placeholder='Enter password', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    dcc.Input(id='client', type='text', placeholder='Enter client', style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
    html.Button('Run Dash', id='login-button', n_clicks=0, style={'width': '100%', 'height': '50px', 'margin-top': '20px'}),
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
            return dcc.Link('Go to Dashboard', href='http://localhost:8090')
        else:
            return 'Access denied. Please check your credentials.'
        
if __name__ == '__main__':
    app1.run_server(debug=True, port=8080)
    app2.run_server(debug=True, port=8090)
