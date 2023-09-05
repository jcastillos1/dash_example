from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from io import BytesIO
import requests, base64


def transforming(cliente, data):
    data = data.copy()
    lista_separada = [valor.split('-') for valor in data.columns]
    fases = [elemento[1] for elemento in lista_separada if len(elemento) == 2]
    etiquetas = [elemento[1] for elemento in lista_separada if len(elemento) == 3]
    circuito = [elemento[2] for elemento in lista_separada if len(elemento) == 3]
    data.columns = ['Time Bucket'] + fases + circuito
    data_ = data.copy()
    data_.columns = ['Time Bucket'] + fases + etiquetas
    data_ = data_.groupby(data_.columns, axis=1).sum()
    data = data.merge(data_, on='Time Bucket')
    data = data[[col for col in data.columns if not col.endswith('_y')]]
    data = data.rename(columns=lambda col: col.replace('_x', ''))
    data['Consumo total'] = data[fases].sum(axis=1)
    data = data.drop(columns = fases).rename(columns=lambda col: col.replace(' (kWhs)', ''))
    data['Time Bucket'] = pd.to_datetime(data['Time Bucket'], format='%m/%d/%Y %H:%M:%S')


    etiq_df = data.drop(['Consumo total']+list(set(etiquetas)),axis=1,inplace=False)
    #Fig1
    fig1 = px.line(x=data["Time Bucket"], y=data["Consumo total"])
    fig1.update_traces(line=dict(color='#668616'))
    fig1.update_layout(title="Consumo Total histórico",
                    xaxis_title="Fecha", yaxis_title="Consumo total (kWh)",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    #Fig2
    base_color = '#668616'
    num_colors = 7  # Número de tonos en la paleta
    lighten_factor = 1.5  # Factor de aclarado
    color_palette = [base_color]
    for i in range(1, num_colors):
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        r_new = min(255, r + int((255 - r) * (lighten_factor * i / num_colors)))
        g_new = min(255, g + int((255 - g) * (lighten_factor * i / num_colors)))
        b_new = min(255, b + int((255 - b) * (lighten_factor * i / num_colors)))
        color = "#{:02x}{:02x}{:02x}".format(r_new, g_new, b_new)
        color_palette.append(color)
    fig2 = px.pie(values=etiq_df.drop(['Time Bucket'], axis=1).sum().sort_values(ascending=False)[:7].values,
                names=etiq_df.drop(['Time Bucket'], axis=1).sum().sort_values(ascending=False)[:7].index,
                hole=0.5, title="Distribución de consumo por circuito (dispositivos)",
                color_discrete_sequence=color_palette)
    fig2.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))
    #Fig3
    fig3 = px.pie(values=data[list(set(etiquetas))].sum().values, 
                names=data[list(set(etiquetas))].sum().index,
                hole=0.5, title="Distribución de consumo por tipo de carga (etiqueta)",
                color_discrete_sequence=color_palette)
    fig3.update_traces(marker=dict(line=dict(color='#FFFFFF', width=2)))
    # Fig4
    df_mes_actual = data[data["Time Bucket"] >= data["Time Bucket"].max()-pd.DateOffset(months=1)]
    df_mes_anterior = data[(data["Time Bucket"] >= data["Time Bucket"].max()-pd.DateOffset(months=2)) & 
                        (data["Time Bucket"] <= data["Time Bucket"].max()-pd.DateOffset(months=1))]
    fig4 = px.line()
    fig4.add_scatter(x=df_mes_actual["Time Bucket"], y=df_mes_actual["Consumo total"], mode="lines", name="Mes Actual")
    fig4.add_scatter(x=df_mes_actual["Time Bucket"], y=df_mes_anterior["Consumo total"], mode="lines", name="Mes Anterior")
    fig4.update_traces(line=dict(color='#668616'), selector=dict(name="Mes Actual"))
    fig4.update_traces(line=dict(color='#C0cea2'), selector=dict(name="Mes Anterior"))
    fig4.update_layout(legend_title="Tipo de consumo", title='Comparación del consumo con el periodo anterior',
                    legend=dict(orientation="h", yanchor="bottom", y=0.97, xanchor="right", x=1),
                    xaxis_title="Fecha", yaxis_title="Consumo total (kWh)",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    # Fig5
    df = pd.DataFrame()
    for col in etiq_df.columns[1:]:
        df[col] = etiq_df[col][etiq_df[col] > etiq_df[col].mean()+2*etiq_df[col].std()]
    fig5 = px.bar(df.sum()[df.sum()>1], barmode='group')
    fig5.update_traces(marker_color='#668616')
    fig5.update_layout(title='Consumos principales por circuito', xaxis_title='', 
                    yaxis_title='Consumo total (kWh)', showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    #Fig6
    df = data.loc[df.index,:]
    df_mes_actual = df[df["Time Bucket"] >= df["Time Bucket"].max()-pd.DateOffset(months=1)]
    df_mes_anterior = df[(df["Time Bucket"] >= df["Time Bucket"].max()-pd.DateOffset(months=2)) & 
                        (df["Time Bucket"] <= df["Time Bucket"].max()-pd.DateOffset(months=1))]
    extra = (df_mes_anterior.reset_index()-df_mes_actual.reset_index()).iloc[:,2:]
    extra.drop(['Consumo total']+list(set(etiquetas)),axis=1,inplace=True) 
    fig6 = px.bar(extra.sum()[extra.sum()>0], orientation='h')
    fig6.update_traces(marker_color='#668616')
    fig6.update_layout(title='Comparación de consumos principales con periodo anterior (µ+2σ)', 
                    xaxis_title="Consumo total (kWh)", showlegend=False, yaxis_title="",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    

    fases_ = data_[fases].rename(columns=lambda col: col.replace(' (kWhs)', ''))
    table1 = pd.DataFrame(fases_.sum())
    table1.columns = ['Consumo (kWh)']
    table1.loc['Total',:] = fases_.sum().sum()
    table1 = table1.applymap(lambda x: '{:.4f}'.format(x))
    circuitos = etiq_df.drop(['Time Bucket'],axis=1,inplace=False).sum()
    table2 = pd.DataFrame(circuitos)
    table2.columns = ['Consumo (kWh)']
    table2.loc['Otras Cargas',:] = fases_.sum().sum()-circuitos.sum()
    table2['%'] = (table2)/(table2.sum().sum())*100
    table2.loc['Total',:] = table2.sum()
    table2 = table2.sort_values(by='%', ascending=True)
    table2 = table2.applymap(lambda x: '{:.2f}'.format(x))
    table3 = pd.DataFrame()
    actual = df_mes_actual['Consumo total']
    anterior = df_mes_anterior['Consumo total']
    if actual.sum() < anterior.sum():
        table3.loc['Tendencia de Consumo', 'Análisis'] = '↓'
    else: table3.loc['Tendencia de Consumo', 'Análisis'] = '↑'
    table3.loc['Aumento / Disminución de línea base por suma', 'Análisis'] = f'{round((actual.sum()-anterior.sum())/actual.sum()*100,2)} %'
    table3.loc['Aumento / Disminución de línea base por promedio', 'Análisis'] = f'{round((actual.mean()-anterior.mean())/actual.mean()*100,2)} %'
    table3.loc['Potencial de ahorro próximo periodo', 'Análisis'] = f'{round(extra.sum()[extra.sum()>0].sum().sum()/actual.sum()*100,2)} %'
    table3.loc['Beneficio esperado', 'Análisis'] = f'{round(extra.sum()[extra.sum()>0].sum().sum(),2)} kWh'
    table1.insert(0, 'Fase', table1.index)
    table2.insert(0, 'Circuito', table2.index)
    table3.insert(0, '', table3.index)


    url = "https://media.licdn.com/dms/image/C560BAQEkLah7iU0OXg/company-logo_200_200/0/1622576378267?e=1701907200&v=beta&t=jHOKiWYubvJbIHNss3cvWPgbf5Rv_427P9tq7jcd5pY"
    response = requests.get(url)
    image_bytes = BytesIO(response.content)
    encoded_image = base64.b64encode(image_bytes.read()).decode("utf-8")
    layout_dashboard = html.Div([
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width':'12.5%', 'float':'left', 'margin-left': '150px', 'margin-top': '-35px'}),
            html.H1(f'Reporte cliente: {cliente}', style={'font-size': '40px', 'color': '#668616', 'font-family': 'Arial, sans-serif'}),
            html.P(f'Desde: {df["Time Bucket"].max()}. Hasta: {df["Time Bucket"].max()-pd.DateOffset(months=1)}', style={'text-align':'center', 'font-family': 'Arial, sans-serif'}),
            html.P(f"Generado el día: {pd.Timestamp.now().strftime('%Y-%m-%d - %H:%M:%S')}", style={'text-align':'center', 'font-family': 'Arial, sans-serif'}),
        ], style={'width': '100%', 'text-align': 'center'}),
        html.Div(style={'height': '-10px'}),
        html.Div([
            html.Div([
                dash_table.DataTable(
                    id='Consumo por fases',
                    columns=[{'name': col, 'id': col} for col in table1.columns],
                    data=table1.to_dict('records'),
                    style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif', 'font-size': '14px'},
                    style_header={'backgroundColor': '#668616', 'color': 'white', 'fontWeight': 'bold'},
                    style_table={'height': 'auto'}
                ),
                dash_table.DataTable(
                    id='Consumo por circuito',
                    columns=[{'name': col, 'id': col} for col in table2.columns],
                    data=table2.to_dict('records'),
                    style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif', 'font-size': '14px'},
                    style_header={'backgroundColor': '#668616', 'color': 'white', 'fontWeight': 'bold'},
                    style_table={'height': 'auto'}
                ),
                html.Div(style={'height': '30px'}),  # This is a spacer Div
                dash_table.DataTable(
                    id='Análisis',
                    columns=[{'name': col, 'id': col} for col in table3.columns],
                    data=table3.to_dict('records'),
                    style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif', 'font-size': '14px'},
                    style_header={'backgroundColor': '#668616', 'color': 'white', 'fontWeight': 'bold'},
                    style_table={'height': 'auto'}
                ),
            ], style={'width': '25%', 'float': 'left'}),
            html.Div([
                dcc.Graph(figure=fig1),
                dcc.Graph(figure=fig2),
                dcc.Graph(figure=fig3),
                dcc.Graph(figure=fig4),
                dcc.Graph(figure=fig5),
                dcc.Graph(figure=fig6),
            ], style={'display': 'grid', 'grid-template-columns': 'repeat(2, 1fr)', 'grid-template-rows': 'repeat(3, 1fr)', 'width': '75%', 'float': 'right'}),
        ], style={'width': '100%'}),
    ], style={'display': 'grid', 'grid-template-rows': 'auto auto', 'width': '100vw', 'height': '100vh', 'font-family': 'Arial, sans-serif'})
    
    return layout_dashboard