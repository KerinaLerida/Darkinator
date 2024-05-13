import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import common
from database import SimpleSQLiteDatabase
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# Création de l'application Dash
app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/cyborg/bootstrap.min.css'], suppress_callback_exceptions=True)

"""annees_sco={
    #'2023-2024': {"date1": datetime.strptime("2023-09-01","%Y-%m-%d"),"date2":datetime.strptime("2024-08-30","%Y-%m-%d")},
    '2022-2023': {"date1": datetime.strptime("2022-09-01","%Y-%m-%d"),"date2":datetime.strptime("2023-08-30","%Y-%m-%d")}
}"""

annees_sco={'2023-2024': {"date1": datetime.strptime("2023-09-01","%Y-%m-%d"),"date2":datetime.strptime("2024-08-30","%Y-%m-%d")}}

def get_annees_sco():
    bdd = SimpleSQLiteDatabase('my_database.db')
    years = bdd.get_years_from_transactions()  # Cette méthode doit être implémentée dans votre classe de base de données
    for y in years:
        y=int(y[0])
        sp=str(y-1)
        sn=str(y+1)
        y=str(y)
        p=f"{sp}-{str(y)}"
        n=f"{str(y)}-{sn}"
        if p not in annees_sco.keys():
            annees_sco[p] = {"date1": datetime.strptime(f"{sp}-09-01","%Y-%m-%d"),"date2":datetime.strptime(f"{y}-08-30","%Y-%m-%d")}
        if n not in annees_sco.keys() and bdd.has_transactions_after_or_on_september(y):
            annees_sco[n] = {"date1": datetime.strptime(f"{y}-09-01","%Y-%m-%d"),"date2":datetime.strptime(f"{sn}-08-30","%Y-%m-%d")}
    bdd.close_connection()
    return annees_sco

first_page_content = html.Div([])
second_page_content = html.Div([])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button("Dashboard", id='btn-dashboard', href='/dashboard/dashboard', style={'margin-right': '10px', 'color': 'rgb(255, 20, 147)', 'background-color': 'rgb(0, 0, 139)'}),
    dbc.Button("More Informations", id='btn-champions', href='/dashboard/moreinformations', style={'margin-right': '10px', 'color': 'rgb(255, 215, 0)', 'background-color': 'rgb(0, 0, 205)'}),
    html.Div(id='content'),
])

@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard/moreinformations':
        return second_page_content
    else:
        return first_page_content

first_page_content = html.Div([
    html.Div(id='dummy'),
    html.Br(),
    html.H3("FridgeFund : Le BOT du club NPC d'ESIEE Paris", style={'textAlign': 'center','font-weight': 'bold','font-family': 'Press Start 2P', 'color': 'rgb(27, 223, 245)'}),
    html.H6("Pensez à rafraichir la page pour actualiser les données & dévoiler tous les graphiques : [F5]",style={'textAlign': 'center', 'font-style': 'italic', 'font-family': 'Press Start 2P', 'color': 'rgb(109, 63, 201)'}),
    html.Br(),
    html.H5("Sélectionne la période scolaire :",style={'font-family': 'Press Start 2P','font-weight': 'bold'}),
    html.Br(),
    dcc.Dropdown(
        id='dropdown-annees-sco',
        options=[opt for opt in get_annees_sco().keys()],
        value=list(get_annees_sco().keys())[0],
        clearable=False,
        style={'width': '33%','color': 'green'}
    ),
    html.Div(id='date-display',style={'font-style': 'italic'}),
    html.Br(),
    html.Br(),
    html.H5("________________________ User(s) ________________________", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='dropdown-users',
        options=[],
        value='all',
        clearable=False,
        style={'width': '33%','color': 'blue'}
    ),
    html.Div(id='users-display',style={'font-style': 'italic'}),
    html.Br(),
    html.Div(id='users-info-table',style={'width': '60%', 'margin': 'auto'}),
    html.Br(),
    html.Div([
        dcc.Graph(id='ba', style={'display': 'inline-block','width': '33%'}),
        dcc.Graph(id='ca', style={'display': 'inline-block','width': '33%'}),
        dcc.Graph(id='pa', style={'display': 'inline-block','width': '33%'}),
    ],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
    html.Br(),
    html.Div([
        dcc.Graph(id='pie-chart'),
    ],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),

    html.Br(),
    html.Br(),
    html.H5("________________________ Item(s) ________________________", style={'textAlign': 'center'}),
    html.H6("Les graphiques ci-dessous ne sont pas disponibles pour l'option 'all' dans le dropdown 'Items'",style={'textAlign': 'center', 'font-style': 'italic', 'font-family': 'Press Start 2P', 'color': 'rgb(109, 63, 201)'}),
    dcc.Dropdown(
        id='dropdown-items',
        options=[],
        value='all',
        clearable=False,
        style={'width': '33%','color': 'orange'}
    ),
    html.Div(id='items-display',style={'font-style': 'italic'}),
    html.Br(),
    html.Div(id='items-info-table',style={'width': '60%', 'margin': 'auto'}),
    html.Br(),
    html.Div([
        dcc.Graph(id='pr', style={'display': 'inline-block','width': '33%'}),
        dcc.Graph(id='ch', style={'display': 'inline-block','width': '33%'}),
        dcc.Graph(id='qu', style={'display': 'inline-block','width': '33%'}),
    ],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),


    html.Br(),
    html.Br(),
])

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('dropdown-annees-sco', 'value'),
     Input('dropdown-users', 'value')]
)
def update_pie_chart(selected_year, selected_user):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    user_id = bdd.get_id_by_name(selected_user)
    if selected_user == 'all':
        purchase_info=bdd.get_all_item_purchase_info(date1, date2)
    else:
        purchase_info = bdd.get_user_item_purchase_info(user_id, date1, date2)
    bdd.close_connection()
    try:
        item_names = [info[0] for info in purchase_info]
        total_quantity_purchased = [info[1] for info in purchase_info]
        total_amount_spent = [round(info[2],2) for info in purchase_info]
        labels = [f"{q} {name} acheté(e)(s) pour {-amount}€)" for name, amount,q in zip(item_names, total_amount_spent,total_quantity_purchased)]
        fig = px.pie(names=labels, values=total_quantity_purchased, title=f'Achats de {selected_user} par item', color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_layout(template='plotly_dark')
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('qu', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-items', 'value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_qu(selected_year,selected_item):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    l_tuples = bdd.get_date_price_change_quantity_for_item(selected_item,date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date', 'price', 'change', 'quantity']).drop(['change','price'], axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try:
        fig = px.scatter(df, x='date', y='quantity', title='Quantité par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title="Quantité de l'item",
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark'
        )
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('ch', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-items', 'value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_ch(selected_year,selected_item):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    l_tuples = bdd.get_date_price_change_quantity_for_item(selected_item, date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date', 'price', 'change', 'quantity']).drop(['quantity', 'price'],                                                                                 axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try:
        fig = px.scatter(df, x='date', y='change', title='Evolution du prix en pourcentage par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title="Evolution du prix en pourcentage",
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark'
        )
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('pr', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-items', 'value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_pr(selected_year,selected_item):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    l_tuples = bdd.get_date_price_change_quantity_for_item(selected_item, date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date', 'price', 'change', 'quantity']).drop(['change', 'quantity'],axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try :
        fig = px.scatter(df, x='date', y='price', title='Prix par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title="Prix de l'item",
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark')
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('pa', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-users','value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_pa(selected_year, selected_user):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    if selected_user == 'all':
        l_tuples=bdd.get_date_ba_ca_pa_for_users(date1, date2)
    else:
        user_id = bdd.get_id_by_name(selected_user)
        l_tuples=bdd.get_date_ba_ca_pa_for_user(user_id, date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date','ba','ca','pa']).drop(['ca','ba'], axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try:
        fig = px.scatter(df, x='date', y='pa', title='Paiements par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Prix payé',
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark',
        )
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('ca', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-users','value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_ca(selected_year,selected_user):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    if selected_user == 'all':
        l_tuples=bdd.get_date_ba_ca_pa_for_users(date1, date2)
    else:
        user_id = bdd.get_id_by_name(selected_user)
        l_tuples=bdd.get_date_ba_ca_pa_for_user(user_id, date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date','ba','ca','pa']).drop(['pa','ba'], axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try:
        fig = px.scatter(df, x='date', y='ca', title='Crédits par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Crédits ajoutés',
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark'
        )
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('ba', 'figure'),  # Output: propriété figure du graphique avec l'ID 'graph-id'
    [Input('dropdown-annees-sco', 'value'),Input('dropdown-users','value')]  # Input: valeur sélectionnée dans le dropdown avec l'ID 'dropdown-id'
)
def update_graph_ba(selected_year,selected_user):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    if selected_user == 'all':
        l_tuples=bdd.get_date_ba_ca_pa_for_users(date1, date2)
    else:
        user_id = bdd.get_id_by_name(selected_user)
        l_tuples=bdd.get_date_ba_ca_pa_for_user(user_id, date1, date2)
    bdd.close_connection()
    df = pd.DataFrame(l_tuples, columns=['date','ba','ca','pa']).drop(['pa','ca'], axis=1).dropna()
    df['date'] = pd.to_datetime(df['date'])
    try:
        fig = px.scatter(df, x='date', y='ba', title='Solde par date', trendline="lowess")
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Solde',
        font=dict(family='Arial', size=12, color='white'),  # Changement de la couleur de la police en blanc
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='closest',
        template='plotly_dark'
        )
    except:
        fig = go.Figure()
    return fig

@app.callback(
    Output('items-info-table', 'children'),
    [Input('dropdown-items', 'value'),
     Input('dropdown-annees-sco', 'value')]
)
def display_item_info(item_name, selected_year):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    if item_name == 'all':
        quantity_purchased=bdd.get_all_SOM_quantity_purchased(date1, date2)
    else:
        quantity_purchased=bdd.get_item_SOM_quantity_purchased(item_name,date1, date2)
    bdd.close_connection()

    columns = [{'name': 'Quantité achetée par les utilisateurs', 'id': 'quantity_purchased'}]
    data = [{'quantity_purchased': quantity_purchased}]
    return dash_table.DataTable(
        id='item-info-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto', 'maxHeight': '400px'},
        style_cell={'textAlign': 'center', 'whiteSpace': 'normal','backgroundColor': 'rgb(148, 111, 148)'},
        style_header={'backgroundColor': 'rgb(109, 67, 163)', 'fontWeight': 'bold', 'whiteSpace': 'normal'},
    )

@app.callback(
    Output('users-info-table', 'children'),
    [Input('dropdown-users', 'value'),
     Input('dropdown-annees-sco', 'value')]
)
def display_user_info(user_value, selected_year):
    bdd = SimpleSQLiteDatabase('my_database.db')
    date1 = annees_sco[selected_year]['date1']
    date2 = annees_sco[selected_year]['date2']
    if user_value == 'all':
        balance=bdd.get_SOM_date_balance(date1, date2)
        credit=bdd.get_all_SOM_credits(date1, date2)
        payment=bdd.get_all_SOM_payments(date1, date2)
    else:
        id_user= bdd.get_id_by_name(user_value)
        if id_user is None:
            return "Aucune information disponible pour cet utilisateur."
        balance = bdd.get_balance_date_by_id(id_user,date1, date2)
        credit = bdd.get_user_SOM_credits(id_user,date1, date2)
        payment = bdd.get_user_SOM_payments(id_user,date1, date2)
    bdd.close_connection()

    columns = [{'name': 'Balance', 'id': 'balance'},
                       {'name': 'Crédit', 'id': 'credit'},
                       {'name': 'Paiement', 'id': 'payment'}]
    if balance is not None:
        balance = round(balance,2)
    if credit is not None:
        credit = round(credit,2)
    if payment is not None:
        payment = round(payment,2)
    data = [{'balance': balance,
                     'credit': credit,
                     'payment': payment}]
    return dash_table.DataTable(
        id='user-info-table',
        columns=columns,
        data=data,
        style_table={'overflowX': 'auto', 'maxHeight': '400px'},
        style_cell={'textAlign': 'center', 'whiteSpace': 'normal','backgroundColor': 'rgb(255, 54, 201)'},
        style_header={'backgroundColor': 'rgb(48, 30, 59)', 'fontWeight': 'bold', 'whiteSpace': 'normal'},
    )

@app.callback(
    Output('users-display', 'children'),
    [Input('dropdown-users', 'options')]
)
def display_user_msg(options):
    if not options:
        return "Aucun utilisateur trouvé pour cette période."
    else:
        return "Des utilisateurs ont été trouvés pour cette période." #return ""

@app.callback(
    Output('items-display', 'children'),
    [Input('dropdown-items', 'options')]
)
def display_item_msg(options):
    if not options:
        return "Aucun article trouvé pour cette période."
    else:
        return "Des articles ont été trouvés pour cette période." #return ""

@app.callback(
    Output('dropdown-items', 'options'),
    [Input('dropdown-annees-sco', 'value')]
)
def fill_item_dropdown(selected_year):
    if selected_year is None:
        return []
    else:
        bdd = SimpleSQLiteDatabase('my_database.db')
        date1 = annees_sco[selected_year]['date1']
        date2 = annees_sco[selected_year]['date2']
        items = bdd.get_items_about_price_or_quantity(date1, date2)
        bdd.close_connection()
        if items:
            item_options = [{'label': 'All', 'value': 'all'}]
            item_options += [{'label': item[0], 'value': item[0]} for item in items]
            return item_options
        else:
            return []


@app.callback(
    Output('dropdown-users', 'options'),
    [Input('dropdown-annees-sco', 'value')]
)
def fill_user_dropdown(selected_year):
    if selected_year is None:
        return []
    else:
        bdd= SimpleSQLiteDatabase('my_database.db')
        date1 = annees_sco[selected_year]['date1']
        date2 = annees_sco[selected_year]['date2']
        users = bdd.get_users_about_buy_or_balance(date1, date2)
        bdd.close_connection()
        if not users:
            return []
        user_options=[{'label': 'All', 'value': 'all'}]
        user_options += [{'label': user[0], 'value': user[0]} for user in users]
        return user_options

@app.callback(
    Output('date-display', 'children'),
    [Input('dropdown-annees-sco', 'value')]
)
def display_dates(selected_year):
    if selected_year is None:
        return "Sélectionnez une période scolaire"
    else:
        dates = annees_sco[selected_year]
        return f"Date de début : {dates['date1'].strftime('%Y-%m-%d')} - Date de fin : {dates['date2'].strftime('%Y-%m-%d')}"

second_page_content = html.Div([
    html.Br(),
    html.H3("FridgeFund : Le BOT du club NPC d'ESIEE Paris", style={'textAlign': 'center','font-weight': 'bold','font-family': 'Press Start 2P', 'color': 'rgb(27, 223, 245)'}),
    html.H6("Pensez à rafraichir la page pour actualiser les données & dévoiler tous les graphiques : [F5]",style={'textAlign': 'center', 'font-style': 'italic', 'font-family': 'Press Start 2P', 'color': 'rgb(109, 63, 201)'}),
    html.Br(),
    html.Br(),
    html.H5("________________________ Top 10 of the biggest consumers ________________________", style={'textAlign': 'center'}),
    html.H6("Si il y a moins de 10 users, il y aura moins de 10 lignes dans le tableau",
            style={'textAlign': 'center', 'font-style': 'italic', 'font-family': 'Press Start 2P',
                   'color': 'rgb(109, 63, 201)'}),
    html.Br(),
    #html.Div(id='top-payers'),
    dash_table.DataTable(
        id='top-payers',
        columns=[{"name": "Name", "id": "id_name"}, {"name": "Money consumed", "id": "id_money"}],
        data=[{'id_name': row[0], 'id_money': round(row[1],2)} for row in SimpleSQLiteDatabase('my_database.db').get_top_payees()],
        style_cell={'textAlign': 'center', 'backgroundColor': '#e599a6', 'color': 'white'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'},
        style_table={'width': '50%', 'minWidth': '50%', 'maxWidth': '50%', 'margin': 'auto'}
    ),
    html.Br(),
    html.Br(),
    html.H5("________________________ Users with a non-zero balance ________________________", style={'textAlign': 'center'}),
    html.Br(),
    #html.Div(id='non-zero-balance-users'),
    dash_table.DataTable(
        id='non-zero-balance-users',
        columns=[{"name": "Name", "id": "id_name"}, {"name": "Balance", "id": "id_balance"}],
        data=[{'id_name': row[1], 'id_balance': row[3]} for row in SimpleSQLiteDatabase('my_database.db').get_users_with_positive_balance()],
        style_cell={'textAlign': 'center', 'backgroundColor': '#2ca02c', 'color': 'white'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'},
        style_table={'width': '50%', 'minWidth': '50%', 'maxWidth': '50%', 'margin': 'auto'}
    ),
    html.Br(),
    html.Br(),
    html.H5("________________________ Items with non-zero quantity ________________________", style={'textAlign': 'center'}),
    html.Br(),
    #html.Div(id='non-zero-quantity-items'),
    dash_table.DataTable(
        id='non-zero-quantity-items',
        columns=[{"name": "Name", "id": "id_name"}, {"name": "Quantity", "id": "id_quantity"}],
        data=[{'id_name': row[0], 'id_quantity': row[1]} for row in SimpleSQLiteDatabase('my_database.db').get_items_with_positive_quantity()],
        style_cell={'textAlign': 'center', 'backgroundColor': '#1f77b4', 'color': 'white'},
        style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'},
        style_table={'width': '50%', 'minWidth': '50%', 'maxWidth': '50%', 'margin': 'auto'}
    ),
    html.Br(),
    html.Br(),
])

# Exécution de l'application
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0', port=8050) #Par défaut, Dash utilise le port 8050. Vous pouvez le changer avec l'argument port=8051 par exemple.

# Exemple, si l'adresse IP de votre serveur est 192.168.1.100
# et que votre application Dash écoute sur le port 8050,
# vous entrerez http://192.168.1.100:8050 dans la barre d'adresse du navigateur.

