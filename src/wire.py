import numpy as np

import scipy.integrate

from particle import PointParticle


class Wire():
    """A straight current-carrying wire with a specified position, length, and resistance.
    """
    def __init__(self, end1: np.array, end2: np.array, resistance: np.float64) -> None:
        """Initiate a an electric wire

        Parameters
        ----------
        end1 : np.array
            The coordinates of one end of the wire
        end2 : np.array
            The coordinates of the other end of the wire
        resistance : np.float64
            The total resistance of the wire
        """
        self.end1 = end1
        self.end2 = end2
        self.resistance = resistance

    def electromotive_force(self, particle: PointParticle):
        """Calculate the electromotive force(emf) across the wire from the particle.

        Parameters
        ----------
        particle : PointParticle
            The particle that is exerting a electric field across the wire.
        """
        # Find the negative integral of the electric field from one end of the wire to the other
        return -scipy.integrate.tplquad(lambda z, y, x: particle.electric_field(np.array(x, y, z)),
                                        a=self.end1[0],
                                        b=self.end2[0],
                                        gfun=self.end1[1],
                                        hfun=self.end2[1],
                                        qfun=self.end1[2],
                                        rfun=self.end2[2]
                                        )[0]
    def current(self):
        return self.electromotive_force() / self.resistance
    
    def magnetic_field(self, position: np.array):
        pass