import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import tkinter as tk
from .polygon_triangulation import *
from .c_space import *

class GUI(object):
    """Implements functions for interacting with motion planning codebase through GUI environment."""

    def __init__(self, manual_configure=True):
        self.manual_configure = manual_configure
        self.obstacle_polygons = []
        self.last_polygon = []
        self.vehicle_polygon = []
        # Set matplotlib to interactive
        self.window = tk.Tk()

        self.building_polygon = False
        self.building_vehicle = False

        # top banner
        banner_frame = tk.Frame(master=self.window, width=250, height=10, bg="grey")
        banner_frame.pack(fill=tk.X, side=tk.TOP)

        # Main area + sidebar
        middle_frame = tk.Frame(master=self.window, width=900, height=200)
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

        start_triangulation = tk.Button(master=sidebar_frame, width=11, height=3, bg="grey", text="Run Triangulation", command=self.on_triangulation_run)
        start_triangulation.pack(side=tk.TOP)

        start_cspace = tk.Button(master=sidebar_frame, width=11, height=3, bg="grey", text="Compute C-Space", command=self.on_compute_cspace)
        start_cspace.pack(side=tk.TOP)
        self.window.mainloop()

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
    
    def on_compute_cspace(self):
        expanded_polygons = compute_cspace(self.obstacle_polygons, self.vehicle_polygon)
        for polygon in expanded_polygons:
            self.canvas.create_polygon(*list(polygon.astype(int).flatten()), tag="expanded_p")
        decomposition_lines = trapezoid_decomposition_linear(expanded_polygons)

        for x in decomposition_lines.keys():
            og_y, top, bottom = decomposition_lines[x]
            top = min(top, 800)
            self.canvas.create_line(x, top, x, bottom, tag="trapezoid_line")

    def left_mouse_callback(self, event):  
        point_list = None
        if self.building_polygon:
            point_list = self.last_polygon
        elif self.building_vehicle:
            point_list = self.vehicle_polygon
        else:
            return

        point_list.append(np.array([event.x, event.y]))
        x = event.x
        y = event.y
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
                self.canvas.create_polygon(*list(point_list.flatten()), fill="red")
                self.building_vehicle = False
                self.vehicle_polygon = np.array(self.vehicle_polygon, tag="vehicle")
            self.canvas.delete("polygon_lines")

    
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