import numpy as np
from globals import g

def mVORTEX(x, y, z, X1, Y1, Z1, X2, Y2, Z2, GAMA):
    """
    Calculates the induced velocity [u, v, w] at a point [x, y, z]
    due to multiple line segements with the same side belonging to
    multiple vortex elements with strength GAMA per unit length
    pointing in the direction [X2, Y2, Z2] - [X1, Y1, Z1]

    Parameters
    ----------
    x, y, z: floats
        Observation point coordinates
    X1, Y1, Z1: ndarray     # TODO: Ask questions about this
        Vectors of size m, where m is the number of vortex elements.
        Endpoints 1 of the lines for all vortex element with the common side.
    X2, Y2, Z2: ndarray
        Vectors of size m, where m is the number of vortex elements.
        Endpoints 2 of the lines for all vortex element with the common side.
    GAMA: ndarray
        # TODO

    Returns
    -------
    u, v, w: floats
        Velocity components at the observation point [x, y, z] due to 
        all lines with common sides, belonging to all vortex elements
    """
    # TODO: Optimize out repeated calculations
    # Calculate R1 x R2
    R1R2X = (y - Y1) * (z - Z2) - (z - Z1) * (y - Y2)
    R1R2Y = (z - Z1) * (x - X2) - (x - X1) * (z - Z2)
    R1R2Z = (x - X1) * (y - Y2) - (y - Y1) * (x - X2)
    
    # Calculate (R1 x R2) ** 2
    SQUARE = R1R2X * R1R2X + R1R2Y * R1R2Y + R1R2Z * R1R2Z
    
    # Calculate R0(R1/R(R1) - R2/R(R2))
    R1 = np.sqrt((x-X1) * (x-X1) + (y-Y1) *(y-Y1) + (z-Z1) *(z-Z1))
    R2 = np.sqrt((x-X2) * (x-X2) + (y-Y2) *(y-Y2) + (z-Z2) *(z-Z2))    
    ROR1 = (X2-X1) * (x-X1) + (Y2-Y1) * (y-Y1) + (Z2-Z1) * (z-Z1)
    ROR2 = (X2-X1) * (x-X2) + (Y2-Y1) * (y-Y2) + (Z2-Z1) * (z-Z2)

    zshape = np.shape(X1)
    COEF = np.zeros(zshape)
    U = np.zeros(zshape)
    V = np.zeros(zshape)
    W = np.zeros(zshape)

    # Find all line segments not located on the observation point
    i = (R1 > g.RCUT) * (R2 > g.RCUT) * (np.sqrt(SQUARE) > g.LCUT)

    # SQUARE = 0 when (X,Y,Z) lies in the middle of the line
    #    warning: = 0 also (X,Y,Z) lies on the extension of the line
    # R1 = 0 or R2 = 0 when [X,Y,Z] is at the end point.
    # When [X,Y,Z] lies on vortex element, its induced velocity is
    #   U = 0, V = 0, W = 0.
    # Contributions from the line segments on the observation points are excluded 
    # and assigned 0 values for each of the following vector outputs.
    # This way, their contributions are effectively set to zero.
    COEF[i] = GAMA[i] / (4.0 * np.pi * SQUARE[i]) * (ROR1[i] / R1[i] - ROR2[i] / R2[i])
    U[i] = R1R2X[i] * COEF[i]
    V[i] = R1R2Y[i] * COEF[i]
    W[i] = R1R2Z[i] * COEF[i]

    # For each velocity component, sum contributions from all line segments 
    # into a single scalar.
    # Only non-zero components (indicated by index i) are summed (Zero
    # components are skipped, but they have no contribution to the sum anyway.)
    u = np.sum(U[i])
    v = np.sum(V[i])
    w = np.sum(W[i])

    return u, v, w
