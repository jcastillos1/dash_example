from api import data_api
from transforming import transforming
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash, time


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([
    html.Img(src='https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY', style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
    html.H1('Generador automático de informes', style={'width': '100%', 'color': '#878786', 'margin-top': '-10px', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'}),
    dcc.Input(id='email', type='email', placeholder='Ingrese su correo', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    dcc.Input(id='password', type='password', placeholder='Ingrese su contraseña', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    dcc.Input(id='client', type='text', placeholder='Ingrese el cliente', style={'width': '100%', 'height': '50px', 'margin-top': '10px'}),
    html.Button('Run Dash', id='login-button', n_clicks=0, style={'width': '101.5%', 'height': '50px', 'margin-top': '10px'}),
    html.Div(id='output-container-button', style={'margin-top': '20px'})
], style={'width': '30%', 'margin-left': 'auto', 'margin-right': 'auto'})
@app.callback(
    Output('output-container-button', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('email', 'value'),
     State('password', 'value'),
     State('client', 'value')]
)
def update_output(n_clicks, email, password, client):
    if n_clicks != 0:
        start_time = time.time()
        if email == 'test@test.com' and password == 'password':
            data = data_api(client)
            layout_dashboard = transforming(client, data)
            app.layout = layout_dashboard
            execution_time = round(time.time() - start_time, 2)
            return dcc.Link('Go to Dashboard', href=f'/Dashboard_{client}'), html.P(f'Execution time: {execution_time} seconds')
        else:
            return 'Access denied. Please check your credentials.'
    else:
        return html.P('Tiempo estimado para generar el Dash: 20s')
    
if __name__ == '__main__':
    app.run_server(debug=True)
