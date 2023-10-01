import pandas as pd
import os
import numpy as np
from datetime  import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import Response, HTTPException
import plotly.graph_objects as go
from plotly.subplots import make_subplots

cur_path = os.path.dirname(os.path.abspath(__file__))

print(cur_path)

big_df = pd.read_pickle(os.path.join(cur_path, 'data.pck'))

app = FastAPI()

def get_next_date(last_date, kind):
    m = last_date.month
    y = last_date.year
    if kind == 'month':

        if m == 12:
            next_y = y + 1
            next_m = 1
        else:
            next_y = y
            next_m = m + 1
        return datetime(next_y, next_m, 1)
    else:
        return datetime(y+1, 1, 1)


period = 20
name = '101.1769'
sensor = 0
kind = 'month'

@app.get('/hist/')
async def get_predict(name:str, sensor:int):
    df:pd.DataFrame = big_df[(big_df['name']==name)&(big_df['sensor_id']==sensor)]
    to_return = {}
    to_return['dates'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S').to_list()
    to_return['t'] = df['t'].to_list()
    to_return['krens'] = df['krens'].to_list()
    to_return['water'] = df['water'].to_list()
    return JSONResponse(content = to_return, status_code= 200)


@app.get('/predict_list/')
async def get_items():
    data = list(big_df['name'].unique())
    return JSONResponse(content=data, status_code=200)



@app.get('/predict/')
async def get_predict(name:str, sensor:int, period:int = 20, kind:str = 'month'):

    seed = 0
    np.random.seed(seed)
    df = big_df[(big_df['name']==name)&(big_df['sensor_id']==sensor)]

    if len(df)==0:
        raise HTTPException(status_code=404, detail=f'{name=}  {sensor = }  not found') 
    
    last_date = df['date'].iloc[-1]
    next_date = get_next_date(last_date, kind)
    dates = [next_date]
    dates_str = [next_date.strftime('%Y-%m-%d %H:%M:%S')]
    for i in range(period):
        prev_date = dates[-1]
        new_date = get_next_date(prev_date, kind)
        dates.append(new_date)
        dates_str.append(new_date.strftime('%Y-%m-%d %H:%M:%S'))


    mean_t = df['t'].mean()
    std_t = df['t'].std()
    mean_krens = df['krens'].mean()
    std_krens = df['krens'].std()

    mean_w = df['water'].mean()
    std_w = df['water'].std()

    if kind == 'month':
        noise = 0.1
    else:
        noise = 0.5

    predict_t = np.random.normal(loc = mean_t, scale=std_t + noise, size = period)
    predict_krens = np.random.normal(loc = mean_krens, scale=std_krens + noise, size = period)
    predict_waters = np.random.normal(loc = mean_w, scale=std_w + noise, size = period)

    to_return = {}
    to_return['dates'] = dates_str
    to_return['t'] = list(predict_t)
    to_return['krens'] = list(predict_krens)
    to_return['water'] = list(predict_waters)
    return JSONResponse(content = to_return, status_code= 200)


@app.get('/plot/')
def get_df(name:str, sensor:int):
    df = big_df[(big_df['name']==name)&(big_df['sensor_id']==sensor)]
    print(df)

    fig = make_subplots(3, 1, subplot_titles=['Температура', 'Крен', 'Уровень воды'])

    fig.add_trace(
                go.Scatter(x = df.date, y = df.t, mode = 'lines+markers', 
                hovertemplate = 'Температура: %{y:.2f} <sup>o</sup>С'+ '<br>Дата: %{x}</br>' + '<br>Сенсор #: %{text}</br>',
                text = [sensor]*len(df.date),
                name = f'Sensor #{sensor}',
                showlegend = False,
                ),
                1, 1 )
    fig.add_trace(
                go.Scatter(x = df.date, y = df.krens, mode = 'lines+markers', 
                hovertemplate = 'Температура: %{y:.2f} <sup>o</sup>С'+ '<br>Дата: %{x}</br>' + '<br>Сенсор #: %{text}</br>',
                text = [sensor]*len(df.date),
                name = f'Sensor #{sensor}',
                showlegend = False,
                ),
                2, 1 )   
    fig.add_trace(
                go.Scatter(x = df.date, y = df.water, mode = 'lines+markers', 
                hovertemplate = 'Температура: %{y:.2f} <sup>o</sup>С'+ '<br>Дата: %{x}</br>' + '<br>Сенсор #: %{text}</br>',
                text = [sensor]*len(df.date),
                name = f'Sensor #{sensor}',
                showlegend = False,
                ),
                3, 1 )

    fig.update_layout(
    autosize=False,
    width=800,
    height=800,
    )
    # fig.show()
    return HTMLResponse(content = fig.to_html(), status_code=200)
