import numpy as np
import numpy.typing as npt

# Type aliases
type UnitVector = npt.NDArray[np.float64]
"""A 3D unit vector that represents a direction in 3D space."""
type PositionVector = npt.NDArray[np.float64]
"""A 3D vector that represents a point in 3D space."""
type DisplacementVector = npt.NDArray[np.float64]
"""A 3D vector that represents the displacement between two points."""
type VelocityVector = npt.NDArray[np.float64]
"""A 3D vector that represents a velocity in 3D space."""
type AccelerationVector = npt.NDArray[np.float64]
"""A 3D vector that represents an acceleration in 3D space."""
type FieldVector = npt.NDArray[np.float64]
"""A 3D vector that represents a field at a point."""
type ForceVector = npt.NDArray[np.float64]
"""A 3D vector that represents a force."""
