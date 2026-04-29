import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 1. Load your consolidated dataset (Use the transactions/engagement data)
df = pd.read_csv("../data/meetmux_transactions.csv")
df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])
df['Month'] = df['PurchaseDate'].dt.strftime('%Y-%m')

# 2. Initialize the Dash App
app = dash.Dash(__name__)

# 3. Define the Layout
app.layout = html.Div([
    html.H1("Business Growth & Analytics Dashboard",
            style={'textAlign': 'center'}),

    # Dropdown for Category Filtering
    html.Div([
        html.Label("Select Activity Category:"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': i, 'value': i} for i in df['Category'].unique()],
            value=df['Category'].unique()[0]
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Graph Area
    html.Div([
        dcc.Graph(id='trend-graph'),
        dcc.Graph(id='revenue-pie')
    ])
])

# 4. Define Callbacks (The "Logic" that makes it interactive)
@app.callback(
    [Output('trend-graph', 'figure'),
     Output('revenue-pie', 'figure')],
    [Input('category-dropdown', 'value')]
)
def update_graphs(selected_category):
    filtered_df = df[df['Category'] == selected_category]

    # Trend Line Chart
    line_fig = px.line(filtered_df, x='PurchaseDate',
                       y='TransactionAmount',
                       title=f'Revenue Trend: {selected_category}')

    # Pie Chart
    pie_fig = px.pie(filtered_df, names='Region',
                     values='TransactionAmount',
                     title=f'Revenue Distribution by Region: {selected_category}')

    return line_fig, pie_fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
