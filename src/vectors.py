import numpy as np
import numpy.typing as npt

# Type aliases
"""3D vector that represents a point in 3D space"""
type PositionVector = npt.NDArray[np.float64]
"""3D vector that represents a velocity in 3D space"""
type VelocityVector = npt.NDArray[np.float64]
"""3D vector that represents an acceleration in 3D space"""
type AccelerationVector = npt.NDArray[np.float64]
"""3D vector that represents a field at a point"""
type FieldVector = npt.NDArray[np.float64]
"""3D vector that represents a force"""
type ForceVector = npt.NDArray[np.float64]
