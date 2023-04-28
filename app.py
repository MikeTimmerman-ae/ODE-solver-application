#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created: 2023-03-20
Modified: 2023-04-27
@author: m. timmerman

WebApp: ODE tool
"""

## Import libraries
from src.ODE_solver import ODE, Trajectory
from dash import Dash, html, dcc, Input, Output, State, ctx, callback_context, ALL
import numpy as np

app = Dash(__name__)

app.layout = html.Div(children=[
    # Header container
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
               ' plot displays the region of convergence for the different solving methods.'),
    ], className='header-container'),

    html.Div(children=[

        html.Div(children=[
            # Choose ODE container
            html.Div(children=[
                html.H2('Choose ODE'),
                dcc.Markdown('''
                A. $$y'(x, y) = (y + 1) cos(y x)$$\n
                B. $$y'(x, y) = -y$$\n
                C. $$y'(x, y) = -5y$$\n
                D. $$y'(x, y) = cos(x)$$\n
                E. $$y'(x, y) = \\frac{3ysin(x)-2xy}{x^2+1}$$
                ''', mathjax=True, style={'color': '#d3d3d3',
                                          'font-family': 'Arial, Helvetica, sans-serif',
                                          'margin': '5px',
                                          'font-size': '13px'}),
                dcc.Dropdown(['A', 'B', 'C', 'D', 'E'], '', id='choose-ode'),
            ], className='secondary-container'),
            # Add new trajectory container
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
                step=0.1,
                marks={i: f' {i}' if i%2==0 else str("") for i in range(0, 11)},
                value=5,
            ),
        ], className='secondary-container', style={'flex': '2 1 70%'}),

    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Bottom container displaying 3 plots: ODE solution space, error plot, stability region
    html.Div(children=[
        dcc.Graph(
            mathjax=True,
            id='graph',
        )
        ], className='graph-container'),
])


# Switch ODE
@app.callback(Output("trajectory-container", "children", allow_duplicate=True),
              Input('choose-ode', 'value'),
              prevent_initial_call='initial_duplicate')
def choose_ode(ode_choice):
    if ctx.triggered_id == 'choose-ode' and ode_choice != "":
        if ode_choice == 'A':
            f = lambda t, x: (x + 1) * np.cos(x * t)
            ode.f = f
            ode.nf = 'A'
        elif ode_choice == 'B':
            f = lambda t, x: -1 * x
            ode.f = f
            ode.nf = 'B'
        elif ode_choice == 'C':
            f = lambda t, x: -5 * x
            ode.f = f
            ode.nf = 'C'
        elif ode_choice == 'D':
            f = lambda t, x: np.cos(t)
            ode.f = f
            ode.nf = 'D'
        elif ode_choice == 'E':
            f = lambda t, x: (3*x*np.sin(t)-2*t*x)/(t**2+1)
            ode.f = f
            ode.nf = 'E'
        ode.trajectories = []
        ode.n = 0
    div = ode.create_div()
    return div


# Print submit messages
@app.callback(Output('container-button', 'children'),
              Input('add-trajectory', 'n_clicks'),
              State('solving-method', 'value'))
def add_trajectory(btn, method):
    if "add-trajectory" == ctx.triggered_id:
        if ode.f != None:
            if method != None:
                if ode.n < 6:
                    return html.Label('Trajectory added!')
                else:
                    return html.Label('Max number of trajectories reached!')
            else:
                return html.Label('Choose a solving method!')
        else:
            return html.Label('First choose an ODE to solve!')

    else:
        return None


# Add trajectory to database
@app.callback(Output('trajectory-container', 'children', allow_duplicate=True),
              Input('add-trajectory', 'n_clicks'),
              State('timestep', 'value'),
              State('initcondition', 'value'),
              State('solving-method', 'value'),
              State('sliderinput', 'value'),
              prevent_initial_call='initial_duplicate')
def add_trajectory(btn, h, x0, method, tf):
    if "add-trajectory" == ctx.triggered_id:
        if ode.f != None:
            if method != None:
                if ode.n < 6:
                    trajectory = Trajectory(ode.n, h, x0, method)
                    ode.add_trajectory(trajectory, tf)
    div = ode.create_div()
    return div


# Delete trajectory from database
@app.callback(Output("trajectory-container", "children", allow_duplicate=True),
              Input({"index": ALL, "type": "delete"}, 'n_clicks'),
              prevent_initial_call='initial_duplicate')
def delete_trajectory(*args):
    trigger = callback_context.triggered[0]
    if trigger['value'] == 1:
        traj_id = int(trigger['prop_id'][9])
        del ode.trajectories[traj_id]
        ode.n = ode.n-1
    div = ode.create_div()
    return div


# Update trajectory traces in plots
@app.callback(Output('graph', 'figure', allow_duplicate=True),
              Input('sliderinput', 'value'),
              Input('choose-ode', 'value'),
              Input({"index": ALL, "type": "delete"}, 'n_clicks'),
              Input('add-trajectory', 'n_clicks'),
              prevent_initial_call='initial_duplicate')
def update_figure(*args):
    if args[1] != "":
        ode.update_trajectories(args[0])        # args[0] = final time
        ode.update_traces()
        ode.error_space()
        ode.stability_region()
    return ode.fig


if __name__ == '__main__':

    ode = ODE()

    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)
