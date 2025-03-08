import numpy as np

import vectors

class BarnesHutCell():
    def __init__(self, x_bounds: np.ndarray[np.float64], y_bounds: np.ndarray[np.float64], z_bounds: np.ndarray[np.float64]):
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.z_bounds = z_bounds

        self.children_particles = []
        self.children_cells = []

    def getCenterofMass() -> vectors.PositionVector:
        pass