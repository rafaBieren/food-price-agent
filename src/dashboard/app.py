import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL, DASHBOARD_HOST, DASHBOARD_PORT, DASHBOARD_DEBUG
from src.database.models import Product, Price, Supermarket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Supermarket Price Tracker"

def get_price_data(days=30):
    """Get price data for the last N days."""
    session = Session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query recent prices with product and supermarket information
        prices = session.query(
            Price.price,
            Price.collected_at,
            Product.name.label('product_name'),
            Product.size,
            Product.unit,
            Supermarket.name.label('supermarket_name')
        ).join(
            Product
        ).join(
            Supermarket
        ).filter(
            Price.collected_at >= cutoff_date
        ).all()
        
        # Convert to DataFrame
        df = pd.DataFrame(prices)
        return df
    finally:
        session.close()

def get_product_list():
    """Get list of unique products."""
    session = Session()
    try:
        products = session.query(Product.name).distinct().all()
        return [{'label': p[0], 'value': p[0]} for p in products]
    finally:
        session.close()

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Supermarket Price Tracker", className="text-center my-4"),
            html.P("Compare prices across different supermarket chains", className="text-center")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Price Comparison", className="card-title"),
                    dcc.Dropdown(
                        id='product-dropdown',
                        options=get_product_list(),
                        placeholder="Select a product"
                    ),
                    dcc.Graph(id='price-comparison-graph')
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Price Trends", className="card-title"),
                    dcc.Graph(id='price-trends-graph')
                ])
            ])
        ], width=12)
    ])
], fluid=True)

@app.callback(
    [Output('price-comparison-graph', 'figure'),
     Output('price-trends-graph', 'figure')],
    [Input('product-dropdown', 'value')]
)
def update_graphs(selected_product):
    if not selected_product:
        return {}, {}
    
    df = get_price_data()
    df = df[df['product_name'] == selected_product]
    
    # Price comparison graph
    comparison_fig = px.box(
        df,
        x='supermarket_name',
        y='price',
        title=f'Price Comparison for {selected_product}',
        labels={'supermarket_name': 'Supermarket', 'price': 'Price (₪)'}
    )
    
    # Price trends graph
    trends_fig = px.line(
        df,
        x='collected_at',
        y='price',
        color='supermarket_name',
        title=f'Price Trends for {selected_product}',
        labels={'collected_at': 'Date', 'price': 'Price (₪)', 'supermarket_name': 'Supermarket'}
    )
    
    return comparison_fig, trends_fig

def run_server():
    """Run the Dash server."""
    app.run_server(
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        debug=DASHBOARD_DEBUG
    )

if __name__ == '__main__':
    run_server() 