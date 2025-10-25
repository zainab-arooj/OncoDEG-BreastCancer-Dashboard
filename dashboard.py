# dashboard.py - FULLY INDEPENDENT ONCODEG DASHBOARD
# RUN WITH: py dashboard.py

import dash
from dash import html, dash_table
import pandas as pd
import base64
import os

#  FILE PATHS 
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

conds_path = os.path.join(BASE_DIR, 'conditions.csv')
sig_degs_path = os.path.join(BASE_DIR, 'significant_degs_relaxed.csv')
volcano_path = os.path.join(BASE_DIR, 'volcano_plot.html')
heatmap_path = os.path.join(BASE_DIR, 'heatmap_top50_improved.png')

#  LOAD DATA (NO LARGE FILE) 
conds = pd.read_csv(conds_path, index_col=0)['Subtype']
conds = conds.dropna()

sig_degs = pd.read_csv(sig_degs_path)

#  STATS (FIXED) 
total = len(conds)
normal = (conds == 'normal').sum()
cancer = total - normal
sig_count = len(sig_degs)
unique_subtypes = [s for s in conds.unique() if pd.notna(s)]
subtype_str = ', '.join(sorted(unique_subtypes))

#  ENCODE IMAGES 
with open(heatmap_path, "rb") as f:
    encoded_image = base64.b64encode(f.read()).decode()

with open(volcano_path, 'r', encoding='utf-8') as f:
    volcano_html_content = f.read()

#  DASH APP 
app = dash.Dash(__name__)
app.title = "OncoDEG: Breast Cancer DEG Explorer"

app.layout = html.Div([
    html.H1("OncoDEG: Global Breast Cancer DEG Explorer", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),

    # Summary + Volcano
    html.Div([
        html.Div([
            html.H3("Project Summary", style={'color': '#2980b9'}),
            html.Div([
                f"• Total Samples: {total}",
                f"• Cancer: {cancer} | Normal: {normal}",
                f"• Significant DEGs: {sig_count:,}",
                f"• Subtypes: {subtype_str}"
            ], style={'fontSize': 16, 'lineHeight': '1.8'})
        ], className="four columns", 
           style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'}),

        html.Div([
            html.H3("Interactive Volcano Plot", style={'color': '#2980b9'}),
            html.Iframe(
                srcDoc=volcano_html_content,
                style={'width': '100%', 'height': '550px', 'border': 'none'}
            )
        ], className="eight columns")
    ], className="row", style={'marginBottom': '40px'}),

    html.Hr(),
    html.H3("DEG Table (Filter & Sort)", style={'color': '#2980b9'}),
    dash_table.DataTable(
        data=sig_degs.to_dict('records'),
        columns=[{"name": i, "id": i} for i in ['Gene', 'Log2FoldChange', 'PValue', 'AdjustedPValue']],
        filter_action="native",
        sort_action="native",
        page_size=20,
        style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'fontSize': '12px'},
        style_data_conditional=[
            {'if': {'filter_query': '{AdjustedPValue} < 0.1'}, 'backgroundColor': '#fadbd8'}
        ]
    ),

    html.Hr(),
    html.H3("Heatmap: Top 50 DEGs (Clustered)", style={'color': '#2980b9'}),
    html.Img(src=f'data:image/png;base64,{encoded_image}', 
             style={'width': '100%', 'maxWidth': '1200px', 'border': '1px solid #ddd'}),

    html.Footer([
        html.P("OncoDEG © 2025 | Data: GEO GSE45827 | Built with Python, Dash, Plotly", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '50px', 'fontSize': '12px'})
    ])
], style={'fontFamily': 'Arial', 'margin': '30px'})

# RUN (INDEPENDENT) 
if __name__ == '__main__':
    app.run(debug=False, port=8051)