from api import data_api
from transforming import transforming
from dash.dependencies import Input, Output, State
from dash import dcc, html
from io import BytesIO
import requests, base64
import dash, time


tokens = {'test@test.com': 2}
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
url = "https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY"
response = requests.get(url)
image_bytes = BytesIO(response.content)
encoded_image = base64.b64encode(image_bytes.read()).decode("utf-8")
app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width':'12.5%', 'float':'left', 'margin-left':'150px', 'margin-top':'-35px'}),
    dcc.Input(id='email', type='email', placeholder='Ingrese su correo'),
    dcc.Input(id='client', type='text', placeholder='Ingrese el cliente'),
    html.Button('Generar informe', id='generate_button', n_clicks=0, style={'width':'12.5%'}),
    html.Div(id='text_info'),
    html.Div(id='title_output'),
    html.Div(id='dash_output'),
], style={'width':'100%', 'text-align':'center'})
@app.callback(
    Output('text_info', 'children'),
    Output('title_output', 'children'),
    Output('dash_output', 'children'),
    Input('generate_button', 'n_clicks'),
    State('email', 'value'),
    State('client', 'value')
)
def update_output(n_clicks, email, client):
    if n_clicks  != 0:
        start_time = time.time()
        if email in tokens.keys() and tokens[email] >= 1:
            data = data_api(client)
            title_output, dash_output = transforming(client, data)
            execution_time = round(time.time() - start_time, 2)
            tokens[email] -= 1
            return f'Tiempo de ejecución: {execution_time}s',title_output, dash_output
        else:
            return 'Acceso denegado. Verifica tus credenciales o revisa tus tokens.', None, None
    else:
        return 'Tiempo estimado en generar Dash: 20s', None, None
if __name__ == '__main__':
    app.run_server(debug=True)
