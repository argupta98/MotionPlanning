import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import tkinter as tk

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

        self.window.mainloop()

    def show_instruction(s):
        print(s)
        plt.title(s, fontsize=16)

    def on_alg_run(self):
        pass

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
            self.canvas.create_line(x_last, y_last, x, y)

        if np.linalg.norm(point_list[0] - point_list[-1]) < 15 and len(point_list) > 3:
            point_list = np.array(point_list[:-1])
            if self.building_polygon:
                self.canvas.create_polygon(*list(point_list.flatten()))
                self.obstacle_polygons.append(point_list)
                self.last_polygon = []
            else:
                self.canvas.create_polygon(*list(point_list.flatten()), fill="red")

    
    def on_obstacle_start_click(self):
        self.building_vehicle = False
        self.building_polygon = not self.building_polygon

    def on_vehicle_click(self):
        # Reset vehicle polygon
        self.building_polygon = False
        self.building_vehicle = not self.building_vehicle

    def run(self):
        pass