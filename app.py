#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2023-03-20
Modified: 2023-03-20
@author: mtimmerm

Example ODE tool.
"""

## Import libraries
from src.ODE_solver import ODE, Trajectory
from dash import Dash, html, dcc, Input, Output, State, ctx, callback_context, ALL
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)


app.layout = html.Div(children=[
    html.Div(children=[
        html.H1(children='ODE solver'),
        html.P('This is an ordinary differential equation WebApp showing some basic characteristics of'
               ' ODEs, specifically numerically solving these ordinary differential equations.'
               ' In the \'Choose ODE\' box, a specific ODE can be chosen for further analysis.'
               ' In the \'Add new trajectory\' the parameters for solving the ODE can be set.'
               ' The \'Overview of trajectories\' shows all trajectories which have been added.'
               ' The slider allows you to select to final time till which the ODE is solved.'
               ' At the bottom of the page, the left graph shows the solution space with some'
               ' standard trajectories given as reference as well as the references added by the user.'
               ' The middle graph gives the order of the error vs. the time step while the most right'
               ' plot displays the region of convergence for the different solving methods.'
               ' Note: for the plots to update, change the value of the slider.'),
    ], className='header-container'),

    html.Div(children=[

        html.Div(children=[

            html.Div(children=[
                html.H2('Choose ODE'),
                dcc.Markdown(f'''
                A. $$y'(x, y) = (y + 1) cos(y x)$$
                ''', mathjax=True),
                dcc.Dropdown(['A', 'B', 'C', 'D'], 'A', id='choose-ode'),
            ], className='secondary-container'),

            html.Div(children=[
                html.H2('Add new trajectory'),
                html.Label('Timestep:'),
                html.Br(),
                dcc.Input(id='timestep',
                          min=0.001,
                          max=1,
                          value=0.01,
                          type='number',
                          placeholder='h',
                          step=0.001
                          ),
                html.Br(),
                html.Label('Initial Condition:'),
                html.Br(),
                dcc.Input(id='initcondition',
                          value=0.0,
                          type='number',
                          placeholder='initial condition',
                          min=-10,
                          max=10,
                          step=0.1
                          ),
                html.Br(),
                html.Label('ODE solving method:'),
                html.Br(),
                dcc.Dropdown(['Forward Euler', 'Backward Euler', 'Runge Kutta 2', 'Runge Kutta 4'],
                             'Forward Euler',
                             id='solving-method'
                             ),
                html.Br(),
                html.Button('Add', id='add-trajectory', n_clicks=0),
                html.Div(id='container-button', style={'margin': '5px 0px 0px 0px'})
            ], className='secondary-container', id='container-add-trajectory'),

        ], style={'flex': '2 1 30%'}),

        html.Div(children=[
            html.H2('Overview of trajectories'),

            html.Div(children=[

            ], id='trajectory-container'),

            html.Label('Final time:'),
            dcc.Slider(
                id='sliderinput',
                min=0,
                max=10,
                step=1,
                marks={i: f' {i}' if i%2==0 else str("") for i in range(0, 11)},
                value=5,
            ),
        ], className='secondary-container', style={'flex': '2 1 70%'}),

    ], style={'display': 'flex', 'flex-direction': 'row'}),

    html.Div(children=[
        dcc.Graph(
            mathjax=True,
            id='example-graph',
        )
        ], className='graph-container'),
])


# Print submit messages
@app.callback(Output('container-button', 'children'),
              Input('add-trajectory', 'n_clicks'),
              State('solving-method', 'value'))
def add_trajectory(btn, method):
    if "add-trajectory" == ctx.triggered_id:
        if method != None:
            if ode.n < 5:
                return html.Label('Trajectory added!')
            else:
                return html.Label('Max number of trajectories reached!')
        else:
            return html.Label('Choose method!')
    else:
        return None


# Add trajectory to db
@app.callback(Output('trajectory-container', 'children', allow_duplicate=True),
              Input('add-trajectory', 'n_clicks'),
              State('timestep', 'value'),
              State('initcondition', 'value'),
              State('solving-method', 'value'),
              State('sliderinput', 'value'),
              prevent_initial_call='initial_duplicate')
def add_trajectory(btn, h, x0, method, tf):
    if "add-trajectory" == ctx.triggered_id:
        if method != None:
            if ode.n < 5:
                trajectory = Trajectory(ode.n, h, x0, method)
                ode.add_trajectory(trajectory, tf)
    div = ode.create_div()
    return div


# Delete trajectory from db
@app.callback(Output("trajectory-container", "children", allow_duplicate=True),
              Input({"index": ALL, "type": "delete"}, 'n_clicks'),
              prevent_initial_call='initial_duplicate'
              )
def delete_trajectory(*args):
    trigger = callback_context.triggered[0]
    if trigger['value'] == 1:
        traj_id = int(trigger['prop_id'][9])
        del ode.trajectories[traj_id]
        ode.n = ode.n-1
    div = ode.create_div()
    return div


# Update trajectory traces in figure
@app.callback(Output('example-graph', 'figure', allow_duplicate=True),
              Input('sliderinput', 'value'),
              Input({"index": ALL, "type": "delete"}, 'n_clicks'),
              Input('add-trajectory', 'n_clicks'),
              prevent_initial_call='initial_duplicate')
def update_figure(*args):
    trigger = callback_context.triggered[0]
    if ctx.triggered_id == "add-trajectory" or ctx.triggered_id == "sliderinput" or trigger['value'] == 1:
        ode.update_trajectories(args[0])        # args[0] = final time
        ode.update_traces()
        ode.error_space()
        ode.stability_region()
    return ode.fig


if __name__ == '__main__':
    f = lambda t, x: (x + 1) * np.cos(x * t)

    ode = ODE(f)

    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)
