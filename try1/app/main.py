from dash import Dash
import dash_bootstrap_components as dbc
from app import server
from app.layout import layout
from app.callbacks import register_callbacks

app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.layout = layout
register_callbacks(app)