import numpy as np

''' Type aliases '''
# 3D vector that represents a point in 3D space
type PositionVector = np.ndarray[np.float64, np.float64, np.float64]
# 3D vector that represents a velocity in 3D space
type VelocityVector = np.ndarray[np.float64, np.float64, np.float64]
# 3D vector that represents an acceleration in 3D space
type AccelerationVector = np.ndarray[np.float64, np.float64, np.float64]
# 3D vector that represents a field at a point
type FieldVector = np.ndarray[np.float64, np.float64, np.float64]
# 3D vector that represents a force
type ForceVector = np.ndarray[np.float64, np.float64, np.float64]
