import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import tkinter as tk
from .polygon_triangulation import *
from .c_space import *
from .graph import *
import time

class GUI(object):
    """Implements functions for interacting with motion planning codebase through GUI environment."""

    def __init__(self, manual_configure=True):
        self.manual_configure = manual_configure
        self.obstacle_polygons = [np.array([[200, 100], [240, 30], [280, 100]]), 
                                  np.array([[100, 300], [400, 300], [400, 200]])]

        self.last_polygon = []
        self.vehicle_polygon = []
        self.endpoint = None
        # Set matplotlib to interactive
        self.window = tk.Tk()

        self.choose_endpoint = False
        self.building_polygon = False
        self.building_vehicle = False

        # top banner
        banner_frame = tk.Frame(master=self.window, width=250, height=10, bg="grey")
        banner_frame.pack(fill=tk.X, side=tk.TOP)

        # Main area + sidebar
        middle_frame = tk.Frame(master=self.window, width=1000, height=200)
        middle_frame.pack(fill=tk.BOTH, side=tk.TOP)

        self.canvas = tk.Canvas(master=middle_frame, width=800, height=800, bg="white")
        self.canvas.pack(fill=tk.BOTH, side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.left_mouse_callback) 

        sidebar_frame = tk.Frame(master=middle_frame, width=100, height=800)
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT)

        start_polygon_button = tk.Button(master=sidebar_frame, width=11, height=3, bg="grey", text="Draw Polygons", command=self.on_obstacle_start_click)
        start_polygon_button.pack(side=tk.TOP)

        start_vehicle_button = tk.Button(master=sidebar_frame, width=11, height=3, bg="grey", text="Draw Vehicle", command=self.on_vehicle_click)
        start_vehicle_button.pack(side=tk.TOP)

        start_triangulation = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Run Triangulation", command=self.on_triangulation_run)
        start_triangulation.pack(side=tk.TOP)

        start_cspace = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Compute C-Space", command=self.on_compute_cspace)
        start_cspace.pack(side=tk.TOP)

        trap_decomp = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Start Decomposition", command=self.on_start_trap_decomposition)
        trap_decomp.pack(side=tk.TOP)

        trap_step = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Decomposition Step", command=self.on_trap_step)
        trap_step.pack(side=tk.TOP)

        remove_poly = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Remove Inside Poly", command=self.on_remove_within_polygons)
        remove_poly.pack(side=tk.TOP)

        choose_end = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Choose Endpoint", command=self.on_choose_end)
        choose_end.pack(side=tk.TOP)

        plan_path = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Plan Path", command=self.on_plan_path)
        plan_path.pack(side=tk.TOP)

        clear_polygons = tk.Button(master=sidebar_frame, width=11, height=3, bg="grey", text="Clear Polygons", command=self.clear_polygons)
        clear_polygons.pack(side=tk.TOP)
        self.window.mainloop()
    
    def on_choose_end(self):
        self.choose_endpoint = True
        self.building_vehicle = False
        self.building_polygon = False

    def show_instruction(s):
        print(s)
        plt.title(s, fontsize=16)

    def draw_split(self, point):
        point_0 = (point[0], point[1] + 5)
        point_1 = (point[0] - 5, point[1] - 5)
        point_2 = (point[0] + 5, point[1] - 5)
        self.canvas.create_polygon(point_0[0], point_0[1], point_1[0], point_1[1], point_2[0], point_2[1], fill="cyan", tag="ms")

    def draw_merge(self, point):
        point_0 = (point[0], point[1] - 5)
        point_1 = (point[0] - 5, point[1] + 5)
        point_2 = (point[0] + 5, point[1] + 5)
        self.canvas.create_polygon(point_0[0], point_0[1], point_1[0], point_1[1], point_2[0], point_2[1], fill="cyan", tag="ms")

    def on_triangulation_run(self):
        # Show per-vertex labels for the monotone partitioning
        print("running_triangulation: len obstacles: {}".format(len(self.obstacle_polygons)))
        for polygon in self.obstacle_polygons:
            labels = compute_vertex_labels(polygon)
            for idx, label in enumerate(labels):
                if label == "merge":
                    self.draw_merge(polygon[idx])
                elif label == "split":
                    self.draw_split(polygon[idx])

        # Show monotone pieces

        # Show final Triangulation

    def clear_polygons(self):
        self.canvas.delete("obstacle")

    def on_compute_cspace(self):
        expanded_polygons = compute_cspace(self.obstacle_polygons, self.vehicle_polygon)
        for polygon in expanded_polygons:
            self.canvas.create_polygon(*list(polygon.astype(int).flatten()), tag="expanded_p")
        #decomposition_lines = trapezoid_decomposition_linear(expanded_polygons)
        self.polygons = Polygons(expanded_polygons)
        bounds = [10, 10, 790, 790]
        self.point_locator = PointLocator(bounds)
        for edge in self.polygons.random_edge_sampler():
            self.canvas.create_line(*edge.flatten(), tag="trapezoid_line", fill="red")
            # print("\n\n ------ iteration: {} -----".format(self.decomp_idx))
            self.point_locator.add_line(edge)
            self.canvas.delete("trapezoid_line")
            lines = self.point_locator.lines()
            for line in lines:
                self.canvas.create_line(*line.flatten(), tag="trapezoid_line")
            # self.decomp_idx += 1
        self.point_locator.remove_traps_within_polygons(self.polygons)

    
    def on_start_trap_decomposition(self):
        print(self.obstacle_polygons)
        self.polygons = Polygons(self.obstacle_polygons)
        bounds = [10, 10, 790, 790]
        self.point_locator = PointLocator(bounds)
        self.random_edge_sampler = self.polygons.random_edge_sampler()
        self.decomp_idx = 0
    
    def on_trap_step(self):
        # self.canvas.delete("all")
        edge = self.random_edge_sampler.next()
        self.canvas.create_line(*edge.flatten(), tag="trapezoid_line", fill="red")
        print("\n\n ------ iteration: {} -----".format(self.decomp_idx))
        print("Adding Edge: {}".format(edge))
        self.point_locator.add_line(edge)
        self.canvas.delete("trapezoid_line")
        lines = self.point_locator.lines()
        for line in lines:
            self.canvas.create_line(*line.flatten(), tag="trapezoid_line")
        self.decomp_idx += 1
    
    def on_remove_within_polygons(self):
        self.point_locator.remove_traps_within_polygons(self.polygons)
        self.canvas.delete("trapezoid_line")
        traps = self.point_locator.traps()
        for trap in traps:
            self.canvas.create_polygon(*trap.flatten(), tag="trapezoid_line", fill="grey", outline="black")

    def left_mouse_callback(self, event):  
        point_list = None
        if self.building_polygon:
            point_list = self.last_polygon
        elif self.building_vehicle:
            point_list = self.vehicle_polygon
        elif self.choose_endpoint:
            point_list = []
        else:
            return

        point_list.append(np.array([event.x, event.y]))
        x = event.x
        y = event.y

        if self.choose_endpoint:
            self.endpoint = np.array([x, y])
            self.choose_endpoint = False
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="green")
            return

        self.canvas.create_oval(x-1, y-1, x+1, y+1)

        if len(point_list) > 1:
            x_last = point_list[-2][0]
            y_last = point_list[-2][1]
            self.canvas.create_line(x_last, y_last, x, y, tag="polygon_lines")

        if np.linalg.norm(point_list[0] - point_list[-1]) < 15 and len(point_list) > 3:
            point_list = np.array(point_list[:-1])
            if self.building_polygon:
                self.canvas.create_polygon(*list(point_list.flatten()), tag="obstacle")
                self.obstacle_polygons.append(point_list)
                self.last_polygon = []
            else:
                self.canvas.create_polygon(*list(point_list.flatten()), fill="red", tag="vehicle")
                self.building_vehicle = False
                self.vehicle_polygon = np.array(self.vehicle_polygon)
            self.canvas.delete("polygon_lines")

    def on_plan_path(self):
        start = np.array(self.vehicle_polygon).mean(axis=0)
        graph = Graph(self.point_locator, 10)
        trapezoid_list = graph.search(start, self.endpoint)
        for trap in trapezoid_list:
            self.canvas.create_polygon(*trap.flatten(), tag="path_trap", fill="green", outline="black")
    
    def on_obstacle_start_click(self):
        self.building_vehicle = False
        self.building_polygon = not self.building_polygon

    def on_vehicle_click(self):
        # Reset vehicle polygon
        self.building_polygon = False
        self.building_vehicle = not self.building_vehicle
        self.vehicle_polygon = []

    def run(self):
        pass