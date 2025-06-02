"""
Web dashboard for the supermarket price tracking system.

This module provides a web-based dashboard built with Dash for visualizing
price comparisons and trends across different supermarkets.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, List, Optional

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
from sqlalchemy.orm import sessionmaker, Session

from config.settings import DATABASE_URL, DASHBOARD_HOST, DASHBOARD_PORT, DASHBOARD_DEBUG, DASHBOARD
from src.database.models import Product, Price, Supermarket, get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Supermarket Price Tracker"

def get_price_data(session: Session, days: int = 30) -> pd.DataFrame:
    """
    Retrieve price data from the database.
    
    Args:
        session: Database session
        days: Number of days of historical data to retrieve
        
    Returns:
        pd.DataFrame: DataFrame containing price data
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = session.query(
        Price, Product, Supermarket
    ).join(
        Product, Price.product_id == Product.id
    ).join(
        Supermarket, Price.supermarket_id == Supermarket.id
    ).filter(
        Price.collected_at >= start_date
    )
    
    data = []
    for price, product, supermarket in query:
        data.append({
            'date': price.collected_at,
            'product_name': product.name,
            'product_size': f"{product.size} {product.unit}",
            'supermarket': supermarket.name,
            'price': price.price,
            'original_price': price.original_price,
            'discount_price': price.discount_price
        })
    
    return pd.DataFrame(data)

def get_products(session: Session) -> List[Dict]:
    """
    Get list of unique products from the database.
    
    Args:
        session: Database session
        
    Returns:
        List[Dict]: List of product dictionaries
    """
    products = session.query(Product).all()
    return [{'label': f"{p.name} ({p.size} {p.unit})", 'value': p.id} for p in products]

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Supermarket Price Comparison Dashboard", className="text-center my-4"),
            html.P("Compare prices across different supermarkets and track price trends over time.",
                  className="text-center mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4("Select Product", className="mb-3"),
            dcc.Dropdown(
                id='product-dropdown',
                options=get_products(get_session()),
                placeholder="Select a product..."
            )
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.H4("Current Price Comparison", className="mb-3"),
            dcc.Graph(id='price-comparison-graph')
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.H4("Price Trends", className="mb-3"),
            dcc.Graph(id='price-trends-graph')
        ], width=12)
    ])
], fluid=True)

@app.callback(
    [Output('price-comparison-graph', 'figure'),
     Output('price-trends-graph', 'figure')],
    [Input('product-dropdown', 'value')]
)
def update_graphs(selected_product_id: Optional[int]):
    """
    Update the dashboard graphs based on selected product.
    
    Args:
        selected_product_id: ID of the selected product
        
    Returns:
        Tuple[go.Figure, go.Figure]: Price comparison and trends figures
    """
    if not selected_product_id:
        return go.Figure(), go.Figure()
    
    session = get_session()
    df = get_price_data(session)
    
    # Filter data for selected product
    product_df = df[df['product_id'] == selected_product_id]
    
    # Create price comparison bar chart
    comparison_fig = px.bar(
        product_df.groupby('supermarket')['price'].last().reset_index(),
        x='supermarket',
        y='price',
        title='Current Price Comparison',
        labels={'price': 'Price (₪)', 'supermarket': 'Supermarket'}
    )
    
    # Create price trends line chart
    trends_fig = px.line(
        product_df,
        x='date',
        y='price',
        color='supermarket',
        title='Price Trends Over Time',
        labels={'price': 'Price (₪)', 'date': 'Date', 'supermarket': 'Supermarket'}
    )
    
    return comparison_fig, trends_fig

def run_server():
    """
    Run the Dash web server.
    """
    app.run_server(
        host=DASHBOARD['host'],
        port=DASHBOARD['port'],
        debug=DASHBOARD['debug']
    )

if __name__ == '__main__':
    run_server() 