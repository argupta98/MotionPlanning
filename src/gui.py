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
        self.obstacle_polygons = []
        self.window_bounds = [0, 0, 1200, 1200]

        self.last_polygon = []
        self.vehicle_polygon = []
        self.endpoint = None
        # Set matplotlib to interactive
        self.window = tk.Tk()

        self.choose_endpoint = False
        self.building_polygon = False
        self.building_vehicle = False

        # top banner
        self.banner_frame = tk.Text(master=self.window, width=100, height=1, bg="grey", font='Helvetica 18 bold')
        self.banner_frame.pack(fill=tk.X, side=tk.TOP)
        self.banner_frame.tag_configure("center", justify='center')

        # Main area + sidebar
        middle_frame = tk.Frame(master=self.window, width=1000, height=200)
        middle_frame.pack(fill=tk.BOTH, side=tk.TOP)

        # Make the canvas for drawing the shapes
        self.canvas = tk.Canvas(master=middle_frame, width=1200, height=1200, bg="white")
        self.canvas.pack(fill=tk.BOTH, side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.left_mouse_callback) 
        sidebar_frame = tk.Frame(master=middle_frame, width=100, height=800)
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT)

        self.start_polygon_button = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Draw Polygons", command=self.on_obstacle_start_click)
        self.start_polygon_button.pack(side=tk.TOP)

        self.random_polygon_button = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Random Polygons", command=self.on_random)
        self.random_polygon_button.pack(side=tk.TOP)

        # self.start_vehicle_button = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Draw Vehicle", command=self.on_vehicle_click)
        # self.start_vehicle_button.pack(side=tk.TOP)

        self.start_cspace = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Compute C-Space", command=self.on_compute_cspace)
        self.start_cspace.pack(side=tk.TOP)

        self.choose_end = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Choose Endpoint", command=self.on_choose_end)
        self.choose_end.pack(side=tk.TOP)

        self.plan_path = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Plan Path", command=self.on_plan_path)
        self.plan_path.pack(side=tk.TOP)

        self.start_minkowski = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Run minkowski", command=self.on_minkowski)
        self.start_minkowski.pack(side=tk.TOP)

        self.trap_decomp = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Start Decomposition", command=self.on_start_trap_decomposition)
        self.trap_decomp.pack(side=tk.TOP)

        self.trap_step = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Decomposition Step", command=self.on_trap_step)
        self.trap_step.pack(side=tk.TOP)

        self.clear_polygons = tk.Button(master=sidebar_frame, width=20, height=3, bg="grey", text="Clear", command=self.clear)
        self.clear_polygons.pack(side=tk.TOP)
        self.show_instruction("Select Obstacle Polygons")
        self.start_polygon_button.configure(bg="PaleGreen3")
        self.random_polygon_button.configure(bg="PaleGreen3")
        self.window.mainloop()
    
    def on_random(self):
        bounds = [self.window_bounds[0] + 100, self.window_bounds[1] + 100, self.window_bounds[2] - 100, self.window_bounds[3] - 100]
        self.obstacle_polygons = Polygons.make_random(bounds, 50, num_initial_partitions=40)
        self.start_polygon_button.configure(bg="grey")
        self.random_polygon_button.configure(bg="grey")

        for polygon in self.obstacle_polygons:
            self.canvas.create_polygon(*polygon.flatten(), tag="obstacle")
        
        self.show_instruction("Draw the vehicle shape.")
        self.building_vehicle=True

    def on_choose_end(self):
        self.choose_endpoint = True
        self.building_vehicle = False
        self.building_polygon = False
        self.show_instruction("Click a point to Choose an Endpoint.")
        self.clear_polygons.configure(bg="grey")

    def show_instruction(self, instr):
        """ Show the instruction in the banner. """
        self.banner_frame.delete("1.0", tk.END)
        # self.banner_frame.insert(tk.INSERT, instr)
        self.banner_frame.insert("1.0", instr)
        self.banner_frame.tag_add("center", "1.0", "end")

    def clear(self):
        """ Reset the GUI back to initial state. """
        self.canvas.delete("all")
        self.vehicle_polygon = []
        self.obstacle_polygons = []
        self.last_polygon = []

        self.choose_endpoint = False
        self.building_polygon = False
        self.building_vehicle = False
        self.clear_polygons.configure(bg="grey")
        self.choose_end.configure(bg="grey")

        self.banner_frame.configure(bg="grey")
        self.show_instruction("Select Obstacle Polygons")
        self.start_polygon_button.configure(bg="PaleGreen3")
        self.random_polygon_button.configure(bg="PaleGreen3")

    def on_minkowski(self):
        self.start_minkowski.configure(bg="grey")
        expanded_polygons = compute_cspace(self.obstacle_polygons, self.vehicle_polygon)
        for polygon in expanded_polygons:
            self.canvas.create_polygon(*list(polygon.astype(int).flatten()), tag="expanded_p")
        self.trap_decomp.configure(bg="PaleGreen3")
        self.start_cspace.configure(bg="PaleGreen3")
        self.show_instruction("To get Step-by-Step decomposition click, Start Trapezoid, otherwise click Start C-Space.")

    def on_compute_cspace(self):
        self.start_cspace.configure(bg="grey")
        self.start_minkowski.configure(bg="grey")
        self.trap_decomp.configure(bg="grey")
        expanded_polygons = compute_cspace(self.obstacle_polygons, self.vehicle_polygon)
        for polygon in expanded_polygons:
            self.canvas.create_polygon(*list(polygon.astype(int).flatten()), tag="expanded_p")
        self.polygons = Polygons(expanded_polygons)
        self.point_locator = PointLocator(self.window_bounds)
        for edge in self.polygons.random_edge_sampler():
            self.canvas.create_line(*edge.flatten(), tag="trapezoid_line", fill="red")
            intersecting = self.point_locator.add_line(edge)

            if intersecting:
                self.show_instruction("Polygons Intersect! Please click Clear to restart.")
                self.banner_frame.configure(bg="coral2")
                self.clear_polygons.configure(bg="coral2")
                return

            self.canvas.delete("trapezoid_line")
            lines = self.point_locator.lines()
            for line in lines:
                self.canvas.create_line(*line.flatten(), tag="trapezoid_line")
        self.point_locator.remove_traps_within_polygons(self.polygons)
        self.choose_end.configure(bg="PaleGreen3")
        self.show_instruction("Choose a Destination Point.")

    def on_start_trap_decomposition(self):
        self.trap_decomp.configure(bg="grey")
        self.start_cspace.configure(bg="grey")
        self.polygons = Polygons(self.obstacle_polygons)
        self.point_locator = PointLocator(self.window_bounds)
        self.random_edge_sampler = self.polygons.random_edge_sampler()
        self.decomp_idx = 0
        self.trap_step.configure(bg="PaleGreen3")
        self.show_instruction("Click Trap Step to perform the next step of the decomposition.")
    
    def on_trap_step(self):
        # self.canvas.delete("all")
        try: # When there are more edges left to add
            edge = self.random_edge_sampler.next()
            self.canvas.create_line(*edge.flatten(), tag="trapezoid_line", fill="red")
            print("\n\n ------ iteration: {} -----".format(self.decomp_idx))
            print("Adding Edge: {}".format(edge))
            intersecting = self.point_locator.add_line(edge)

            if intersecting:
                self.show_instruction("Polygons Intersect! Please click Clear to restart.")
                self.banner_frame.configure(bg="coral2")
                self.clear_polygons.configure(bg="coral2")
                return

            self.canvas.delete("trapezoid_line")
            lines = self.point_locator.lines()
            for line in lines:
                self.canvas.create_line(*line.flatten(), tag="trapezoid_line")
            self.decomp_idx += 1

        except Exception as e: # When we are done.
            print(e)
            self.choose_end.configure(bg="PaleGreen3")
            self.trap_step.configure(bg="grey")
            self.show_instruction("Choose a Destination Point.")
    
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
            self.canvas.delete("endpoint")
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="green", tag="endpoint")
            self.choose_end.configure(bg="grey")
            self.plan_path.configure(bg="PaleGreen3")
            self.show_instruction("Click the Plan Path button to get the path.")
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
                self.show_instruction("Re-click the Draw Polygon Button to Finish, or Draw Another Obstacle.")
                self.last_polygon = []
            else:
                self.canvas.create_polygon(*list(point_list.flatten()), fill="red", tag="vehicle")
                self.building_vehicle = False
                self.vehicle_polygon = point_list
                self.show_instruction("Click Compute C-Space to get full C-Space computation. Click Minkowski to get just the Minkowski sum.")
                self.start_cspace.configure(bg="PaleGreen3")
                self.start_minkowski.configure(bg="PaleGreen3")
            self.canvas.delete("polygon_lines")

    def on_plan_path(self):
        self.canvas.delete("path")
        start = np.array(self.vehicle_polygon).mean(axis=0)
        graph = Graph(self.point_locator, self.window_bounds[0])
        point_list = graph.search(start, self.endpoint)
        print("path length: {}".format(len(point_list)))
        last_point = point_list[0]
        for point in point_list[1:]:
            self.canvas.create_line(last_point[0], last_point[1], point[0], point[1], fill="green", tag="path", width=3.0)
            last_point = point
        self.show_instruction("Choose a new endpoint, or Clear the screen and start new.")
        self.clear_polygons.configure(bg="PaleGreen3")
        self.choose_end.configure(bg="PaleGreen3")
        self.plan_path.configure(bg="grey")
    
    def on_obstacle_start_click(self):
        self.random_polygon_button.configure(bg="grey")
        self.building_vehicle = False
        if self.building_polygon:
            self.start_polygon_button.configure(bg="grey")
            self.show_instruction("Draw the vehicle shape.")
            self.building_vehicle=True
        else:
            self.show_instruction("Click on Canvas to Select Polygons. Polygons auto-close when you click close to the start point.")
            self.start_polygon_button.configure(bg="PaleGreen3")
        self.building_polygon = not self.building_polygon

    def run(self):
        pass