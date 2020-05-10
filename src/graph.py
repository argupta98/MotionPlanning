""" Class to hold graph information after trapezoid decomposition. """

from collections import defaultdict
import numpy as np

class Interface(object):
    """ Defines the edge the connects two trapezoids. """
    def __init__(self, trap_left, trap_right):
        # self.trap_left = trap_left
        # self.trap_right = trap_right
        top_choices = np.array([trap_left.top()[1], trap_right.top()[0]])
        bottom_choices = np.array([trap_left.bottom()[1], trap_right.bottom()[0]])
        top_point = top_choices[np.argmin(top_choices[:, 1])]
        bottom_point = bottom_choices[np.argmax(bottom_choices[:, 1])]
        self.interface_line = np.array([top_point, bottom_point])
        assert(self.interface_line[0, 0] == self.interface_line[1, 0])
        self.center = self.interface_line.mean(axis=0)

class SearchNode(object):
    """ Defines a search node structure to keep track of parents. """
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent

class Graph(object):
    def __init__(self, point_locator, left_boundary):
        """
        Args:
            trapezoids (Trapezoids): A Trapezoids object with the freespace trapezoids.
            left_boundary(int): The left boundary of the configuration space used to get the trapezoid decomposition.
        """
        self.pl = point_locator 
        self.traps = point_locator.trapezoids
        self.interfaces = defaultdict(dict)
        self.build(left_boundary)
    
    def build(self, leftmost):
        """Turns trapezoids into a searchable graph."""
        # iteratively link all trapezoids to the right of it
        print("[Graph] building.")
        # Basically a BFS over trapezoids to get the connectivity
        next_traps = self.traps.right_adjacent_to(leftmost)
        traps_to_add_queue = []
        for _, trap in next_traps.items():
            traps_to_add_queue.append(trap.index)

        print("[Graph] Queue: {}".format(traps_to_add_queue))
        seen_trap_indices = set()
        for trap in traps_to_add_queue:
            # print("[Graph] adding {}.".format(self.traps[trap]))
            # Get right adjacent
            right_adjacent = self.traps.right_adjacent(trap)
            print("[Graph] Current: {} Right Adjacent: {}".format(trap, right_adjacent))

            for next_trap_idx in right_adjacent:
                # Add unseen traps to the queue
                if next_trap_idx not in seen_trap_indices:
                    seen_trap_indices.add(next_trap_idx)
                    traps_to_add_queue.append(next_trap_idx)
                
                # make an undirected edge between the two
                interface = Interface(self.traps[trap], self.traps[next_trap_idx])
                self.interfaces[trap][next_trap_idx] = interface
                self.interfaces[next_trap_idx][trap] = interface
    
    def search(self, start, end):
        print("[Graph] searching.")
        start_trap_idx = self.pl.query(start)
        end_trap_idx = self.pl.query(end)
        expansion_queue = [SearchNode(start_trap_idx, None)]
        seen = set()
        final_node = None

        # Run a BFS until we get to the end trapezoid idx
        for trap_idx in expansion_queue:
            adjacent_traps = self.interfaces[trap_idx.value]
            for next_idx in adjacent_traps:
                if next_idx not in seen:
                    seen.add(next_idx)
                    next_search = SearchNode(next_idx, trap_idx)
                    expansion_queue.append(next_search)
                if next_idx == end_trap_idx:
                    final_node = next_search
                    break
            if final_node is not None:
                break
        
        # Reconstruct the set of trapezoids
        path = []
        curr_node = final_node
        while curr_node is not None:
            path.append(curr_node.value)
            curr_node = curr_node.parent

        path.reverse()

        # Get the corresponding trapezoids for visualization
        for i, trap_idx in enumerate(path):
            path[i] = self.traps[trap_idx].raw()

        print("[Graph] search complete.")
        return path
        

