import plotly.express as px
# import fastapi
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

dataframe = px.data.gapminder().rename(columns={
    'year': 'Year', 
    'lifeExp': 'Life Expectancy', 
    'pop': 'Population', 
    'gdpPercap': 'GDP Per Capita'
})


@app.get('/worldviz')
async def worldviz(metric, country):
    """
    Visualize world metrics from Gapminder data

    ### Query Parameters
    - `metric`: 'Life Expectancy', 'Population', or 'GDP Per Capita'
    - `country`: [country name](https://www.gapminder.org/data/geo/), case sensitive

    ### Response
    JSON string to render with react-plotly.js
    """
    subset = dataframe[dataframe.country == country]
    fig = px.line(subset, x='Year', y=metric, title=f'{metric} in {country}')
    return HTMLResponse(content = fig.to_html(), status_code = 200)