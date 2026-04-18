# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 16:27:54 2024

@author: BIPAN,PAVAN,PRASHANT,EKSHITH
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import sympy as sp

# Define symbolic variables for Laplace domain and time domain
s, t = sp.symbols('s t')

class CircuitComponent:
    def __init__(self, component_type, value, start_node, end_node):
        self.component_type = component_type
        self.value = value
        self.start_node = start_node
        self.end_node = end_node

    def impedance(self):
        """Return the impedance of the component in the Laplace domain."""
        if self.component_type == "Resistor":
            return self.value
        elif self.component_type == "Capacitor":
            return 1 / (s * self.value)
        elif self.component_type == "Inductor":
            return s * self.value
        else:
            raise ValueError("Unknown component type")

    def label(self):
        """Return a label for the component."""
        if self.component_type == "Resistor":
            return f"R={self.value}Ω"
        elif self.component_type == "Capacitor":
            return f"C={self.value}F"
        elif self.component_type == "Inductor":
            return f"L={self.value}H"

class CircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("General Circuit Solver with Real-Time Visualization")

        self.components = []
        self.voltage_source = None
        self.graph = nx.MultiGraph()
        self.figure, self.ax = plt.subplots(figsize=(5, 4))

        self.start_node = tk.StringVar()
        self.end_node = tk.StringVar()
        self.component_type = tk.StringVar(value="Resistor")
        self.component_value = tk.DoubleVar(value=1.0)

        self.ac_voltage_amplitude = tk.DoubleVar(value=1.0)
        self.frequency = tk.DoubleVar(value=0.159154943)
        self.voltage_start_node = tk.StringVar()
        self.ground_node = "GND"
        self.voltage_type =  tk.StringVar(value="cos")

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        # Component Input UI
        ttk.Label(self.root, text="Component Type:").grid(row=0, column=0)
        component_menu = ttk.Combobox(self.root, textvariable=self.component_type, values=["Resistor", "Capacitor", "Inductor"])
        component_menu.grid(row=0, column=1)

        ttk.Label(self.root, text="Value:").grid(row=1, column=0)
        ttk.Entry(self.root, textvariable=self.component_value).grid(row=1, column=1)

        ttk.Label(self.root, text="Start Node:").grid(row=2, column=0)
        ttk.Entry(self.root, textvariable=self.start_node).grid(row=2, column=1)

        ttk.Label(self.root, text="End Node:").grid(row=3, column=0)
        ttk.Entry(self.root, textvariable=self.end_node).grid(row=3, column=1)

        ttk.Button(self.root, text="Add Component", command=self.add_component).grid(row=4, column=0, columnspan=2)

        # Voltage Source Input UI
        ttk.Label(self.root, text="AC Voltage Amplitude (V):").grid(row=5, column=0)
        ttk.Entry(self.root, textvariable=self.ac_voltage_amplitude).grid(row=5, column=1)

        ttk.Label(self.root, text="Frequency (Hz):").grid(row=6, column=0)
        ttk.Entry(self.root, textvariable=self.frequency).grid(row=6, column=1)

        ttk.Label(self.root, text="Voltage Source Start Node:").grid(row=7, column=0)
        ttk.Entry(self.root, textvariable=self.voltage_start_node).grid(row=7, column=1)

        ttk.Button(self.root, text="Add Voltage Source", command=self.add_voltage_source).grid(row=9, column=0, columnspan=2)
        ttk.Button(self.root, text="Solve Circuit", command=self.solve_circuit).grid(row=10, column=0, columnspan=2)

        ttk.Label(self.root, text="Voltage Type:").grid(row=8, column=0)
        component_menu = ttk.Combobox(self.root, textvariable=self.voltage_type, values=["sin", "cos", "DC"])
        component_menu.grid(row=8, column=1)
        
        # Circuit Visualization Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=11, column=0, columnspan=2)
        self.draw_circuit()

    def add_component(self):
        component = CircuitComponent(self.component_type.get(), self.component_value.get(), self.start_node.get(), self.end_node.get())
        self.components.append(component)
        self.graph.add_edge(component.start_node, component.end_node, label=component.label())
        self.draw_circuit()

    def add_voltage_source(self):
        amplitude = self.ac_voltage_amplitude.get()
        frequency = self.frequency.get()
        start_node = self.voltage_start_node.get()
        voltagetype=self.voltage_type.get()
        
        if voltagetype == "sin":
            laplace_voltage = amplitude / (s**2 + (2 * np.pi * frequency)**2)
        if voltagetype == "cos":
            laplace_voltage = amplitude * s / (s**2 + (2 * np.pi * frequency)**2)
        if voltagetype == "DC":
            laplace_voltage = amplitude/s

        self.voltage_source = {
            "amplitude": amplitude,
            "frequency": frequency,
            "start_node": start_node,
            "end_node": self.ground_node,
            "laplace_transform": laplace_voltage
        }
        self.graph.add_edge(start_node, self.ground_node, label=f"V={amplitude}V{voltagetype} ")
        self.draw_circuit()

    def draw_circuit(self):
        """Draw the circuit graph using NetworkX and Matplotlib."""
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, ax=self.ax, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10)

        # Handle multiedge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        for (u, v, key), label in edge_labels.items():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx = (x2 - x1) * 0.05  # Offset for clarity
            dy = (y2 - y1) * 0.05
            mid_x, mid_y = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
            self.ax.text(mid_x, mid_y, label, fontsize=9, color='black', ha='center', va='center')

        self.ax.set_title("Real-Time Circuit Diagram")
        self.canvas.draw()

    def solve_circuit(self):
       
        node_voltages = {self.ground_node: 0}
        nodal_equations = {}

        for component in self.components:
            if component.start_node not in node_voltages:
                node_voltages[component.start_node] = sp.symbols(f"V_{component.start_node}")
            if component.end_node not in node_voltages:
                node_voltages[component.end_node] = sp.symbols(f"V_{component.end_node}")

        vs_start = self.voltage_source["start_node"]
        vs_end = self.voltage_source["end_node"]
        node_voltages[vs_start] = self.voltage_source["laplace_transform"] + node_voltages[vs_end]

        for node in node_voltages:
            if node == self.ground_node:
                continue
            equation = 0
            for component in self.components:
                Z = component.impedance()
                if component.start_node == node:
                    equation += (node_voltages[component.start_node] - node_voltages[component.end_node]) / Z
                elif component.end_node == node:
                    equation += (node_voltages[component.end_node] - node_voltages[component.start_node]) / Z
            nodal_equations[node] = sp.Eq(equation, 0)

        solutions = sp.solve(list(nodal_equations.values()), list(node_voltages.values()))
        solutions.popitem()
        for var, laplace_expr in solutions.items():
            print(f"node {var} voltage:",sp.inverse_laplace_transform(laplace_expr, s, t))
            print(f"Node{var}laplace eqn :", laplace_expr)
        self.plot_solutions(solutions)
        
    def plot_solutions(self, solutions):
         time_vals = np.linspace(0, 10, 1000)
         plt.figure(figsize=(10, 6))

         for var, laplace_expr in solutions.items():
             if laplace_expr != 0:
                 time_expr = sp.inverse_laplace_transform(laplace_expr, s, t)
                 time_func = sp.lambdify(t, time_expr, "numpy")
                 voltage_vals = time_func(time_vals)
                 plt.plot(time_vals, voltage_vals, label=str(var))

         plt.xlabel("Time (s)")
         plt.ylabel("Voltage (V)")
         plt.title("Node Voltages Over Time")
         plt.legend()
         plt.grid(True)
         plt.show()      
        

# Run the application
root = tk.Tk()
app = CircuitApp(root)
root.mainloop()
