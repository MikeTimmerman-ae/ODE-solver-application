import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import Dash, html


class ODE:
    def __init__(self):
        self.f = None
        self.n = 0
        self.fig = make_subplots(1, 3, subplot_titles=('ODE solution space', 'Error plot', 'Region of Convergence'))
        self.trajectories = []

    def frwd_euler(self, t, h, xi, f):
        xip = xi + h*f(t, xi)
        return xip

    def bkwrd_euler(self, t, h, xi, f):
        xip = fsolve(lambda xip: xip - (xi + h*f(t+h, xip)), xi)
        return xip[0]

    def RK2(self, t, h, xi, f):
        k1 = f(t, xi)
        k2 = f(t+h, xi+k1*h)
        xip = xi + h*(1/2*k1 + 1/2*k2)
        return xip

    def RK4(self, t, h, xi, f):
        k1 = f(t, xi)
        k2 = f(t + h / 2, xi + k1 * h / 2)
        k3 = f(t + h / 2, xi + k2 * h / 2)
        k4 = f(t + h, xi + k3 * h)
        xip = xi + h * (1 / 6 * k1 + 1 / 3 * k2 + 1 / 3 * k3 + 1 / 6 * k4)
        return xip

    def solve(self, trajectory, tf):
        t = 0
        xi = trajectory.x0
        x_ls = [xi]
        while t < tf:
            if trajectory.method == 'Forward Euler':
                xi = self.frwd_euler(t, trajectory.h, xi, self.f)
            elif trajectory.method == 'Backward Euler':
                xi = self.bkwrd_euler(t, trajectory.h, xi, self.f)
            elif trajectory.method == 'Runge Kutta 2':
                xi = self.RK2(t, trajectory.h, xi, self.f)
            elif trajectory.method == 'Runge Kutta 4':
                xi = self.RK4(t, trajectory.h, xi, self.f)
            x_ls.append(xi)
            t += trajectory.h
        trajectory.t = np.arange(0, t + trajectory.h, trajectory.h)
        trajectory.x = x_ls

    def add_trajectory(self, trajectory, tf):
        self.trajectories.append(trajectory)
        self.solve(trajectory, tf)
        self.n += 1

    def update_trajectories(self, tf):
        for idx, trajectory in enumerate(self.trajectories):
            self.solve(trajectory, tf)
            trajectory.id = idx

    def create_div(self):
        div = []

        for i in range(self.n):
            div.append(html.Div(children=[

                html.Div(children=[
                    html.Label('Trajectory ' + str(i+1), style={'padding': '10px 0px 0px 5px',
                                                                'margin': '0px'})
                ], style={'padding': '15px 0px 0px 10px',
                          'position': 'relative',
                          'height': '1em'}),

                html.Div(children=[
                    html.Div(children=[
                        html.Label('Solver: ' + str(self.trajectories[i].method))
                    ], style={'flex': '1 1 30%', 'padding': '5px'}),

                    html.Div(children=[
                        html.Label('Timestep: ' + str(self.trajectories[i].h))
                    ], style={'flex': '2 1 25%', 'padding': '5px'}),

                    html.Div(children=[
                        html.Label('Initial Condition: ' + str(self.trajectories[i].x0))
                    ], style={'flex': '3 1 25%', 'padding': '5px'}),

                    # html.Div(children=[
                    #     html.Button('Select', id={"index": i, "type": "selected"}, n_clicks=0),
                    # ], style={'flex': '4 1 10%', 'padding': '5px'}),

                    html.Div(children=[
                        html.Button('Delete', id={"index": i, "type": "delete"}, n_clicks=0),
                    ], style={'flex': '5 1 20%', 'padding': '5px'})
                ], style={'display': 'flex',
                          'flex-direction': 'row',
                          'padding': '5px',
                          'height': '2.5em',
                          'position': 'relative'})

            ], style={'border-style': 'solid solid solid solid',
                      'margin': '10px',
                      'padding': '0px',
                      'border-radius': '5px',
                      'background': '#a1cca5'}, className='container-trajectory')
            )

        return div

    def update_traces(self):
        self.fig = make_subplots(1, 3, subplot_titles=('ODE solution space', 'Error convergence plot', 'Region of Convergence'))
        self.solution_space()
        for i, trajectory in enumerate(self.trajectories):
            self.add_traces(trajectory, i)

    def add_traces(self, trajectory, i):
        self.fig.add_trace(go.Scatter(name='Trajectory ' + str(i+1),
                                      x=trajectory.t, y=trajectory.x,
                                      mode='lines',
                                      line=dict(color='rgb'+str(trajectory.color)),
                                      hovertemplate='%{y:.4f}'
                                      ),
                           row=1, col=1)

    def solution_space(self):
        x0s = np.linspace(0, 10, 11)
        for x0 in x0s:
            t = 0
            h = 0.01
            xi = x0
            x_ls = [x0]
            while t < 10:
                xi = self.RK4(t, h, xi, self.f)
                x_ls.append(xi)
                t += h
            self.fig.add_trace(go.Scatter(name='Trajectory x0='+str(x0),
                                          x=np.arange(0, t + h, h), y=x_ls,
                                          opacity=0.7,
                                          mode='lines',
                                          line=dict(color='#D3D3D3', dash='dash'),
                                          hovertemplate='%{y:.4f}'
                                          ),
                               row=1, col=1)

    def error_space(self):
        methods = []
        for trajectory in self.trajectories:
            methods.append(trajectory.method)
        methods = np.unique(methods)
        for method in methods:
            if method == "Forward Euler":
                Oh = 1
            elif method == "Backward Euler":
                Oh = 1
            elif method == "Runge Kutta 2":
                Oh = 2
            elif method == "Runge Kutta 4":
                Oh = 4
            else:
                Oh = 0

            self.fig.add_trace(go.Scatter(name='Order of Convergence '+str(method),
                                          x=np.geomspace(1/1024, 1, 11), y=1*np.power(np.geomspace(1/1024, 1, 11), Oh),
                                          mode='lines',
                                          line=dict(color='#000000'),
                                          hovertemplate='%{y:.4f}'
                                          ), row=1, col=2)
            self.fig.update_xaxes(type="log", row=1, col=2)
            self.fig.update_yaxes(type="log", row=1, col=2)

    def stability_region(self):
        delta = 0.025
        x = np.arange(-4.0, 4.0, delta)
        y = np.arange(-4.0, 4.0, delta)
        X, Y = np.meshgrid(x, y)
        methods = []
        for trajectory in self.trajectories:
            methods.append(trajectory.method)
        methods = np.unique(methods)
        for method in methods:
            if method == "Forward Euler":
                Z1=np.sqrt(np.square(1+X)+np.square(Y))
                trace = go.Contour(name='Stability Region '+str(method), z=Z1, x=x, y=y, contours_coloring='lines',
                                   line_width=2, contours=dict(start=1, end=1, size=2), hovertemplate='%{y:.4f}')
                self.fig.append_trace(trace, 1, 3)
            elif method == "Backward Euler":
                Z2 = 1/np.sqrt(np.square(1-X)+np.square(Y))
                trace = go.Contour(name='Stability Region '+str(method), z=Z2, x=x, y=y, contours_coloring='lines',
                                   line_width=2, contours=dict(start=1, end=1, size=2), hovertemplate='%{y:.4f}')
                self.fig.append_trace(trace, 1, 3)
            elif method == "Runge Kutta 2":
                Z3 = np.sqrt(np.square(1+X+1/2*(np.square(X)-np.square(Y))) + np.square(Y*(1+X)))
                trace = go.Contour(name='Stability Region '+str(method), z=Z3, x=x, y=y, contours_coloring='lines',
                                   line_width=2, contours=dict(start=1, end=1, size=2), hovertemplate='%{y:.4f}')
                self.fig.append_trace(trace, 1, 3)
            elif method == "Runge Kutta 4":
                Z41 = 1+X+1/2*(np.square(X)-np.square(Y))+1/6*(np.power(X, 3)-3*X*np.square(Y))+1/24*(np.power(X, 4)-6*np.square(X)*np.square(Y)+np.power(Y, 4))
                Z42 = Y+X*Y+1/6*(3*np.square(X)*Y-np.power(Y, 3))+1/6*(np.power(X, 3)*Y-X*np.power(Y, 3))
                Z4 = np.sqrt(np.square(Z41)+np.square(Z42))
                trace = go.Contour(name='Stability Region '+str(method), z=Z4, x=x, y=y, contours_coloring='lines',
                                   line_width=2, contours=dict(start=1, end=1, size=2), hovertemplate='%{y:.4f}')
                self.fig.append_trace(trace, 1, 3)


class Trajectory:
    def __init__(self, id, h, x0, method):
        self.id = id

        self.h = h
        self.x0 = x0
        self.method = method
        self.color = tuple(np.random.choice(range(256), size=3))

        self.t = []
        self.x = []
