import numpy as np
from globals import g
from Wing import Wing
from nd_data import nd_data
from wing_total import wing_total
from lr_set_matrix import lr_set_matrix
from wing_m import wing_m
from lr_mass_L2GT import lr_mass_L2GT
from lrs_wing_NVs import lrs_wing_NVs
from n_vel_T_by_W import n_vel_T_by_W
from cross_matrix import cross_matrix
from assemble_matrix import assemble_matrix
from solution import solution
# from plot_GAM import plot_GAM
# from plot_WB import plot_WB
from s_impulse_WT import s_impulse_WT
from divide_GAM import divide_GAM
from b_vel_B_by_T_matrix import b_vel_B_by_T_matrix
from vel_B_by_T import vel_B_by_T
from cross_vel_B_by_T import cross_vel_B_by_T
from assemble_vel_B_by_T import assemble_vel_B_by_T

def tombo():
    # SETUP
    # -----

    # g.xb_f, g.nxb_f, g.nb_f, g.xc_f, g.nxc_f, g.nc_f, g.l_f, g.c_f, g.h_f,  \
    # g.xb_r, g.nxb_r, g.nb_r, g.xc_r, g.nxc_r, g.nc_r, g.l_r, g.c_r, g.h_r = \
    #     Wing()

    # TEMPORARY WHILE WING() IS NOT IMPLEMENTED
    import temp_arrays
    # xb_f and xb_r from temp_arrays
    g.nxb_f = 10;                   g.nxb_r = 10
    g.nb_f = np.zeros((3, 10));     g.nb_r = np.zeros((3, 10))
    g. nb_f[2, :] = 1;              g. nb_r[2, :] = 1
    # xc_f and xc_r from temp_arrays
    g.nxc_f = 7;                    g.nxc_r = 7
    g.nc_f = np.zeros((3, 7));      g.nc_r = np.zeros((3, 7))
    g.nc_f[2, :] = 1;               g.nc_r[2, :] = 1
    g.l_f = 3.732050807568878;      g.l_r = 1.866025403784439
    g.c_f = 2.0;                    g.c_r = 1.0
    g.h_f = 0.2;                    g.h_r = 0.1
    ###########################################
    
    l, c, h, phiT, phiB, a, beta, delta, gMax, U, \
    xb_f, xc_f, xb_r, xc_r, b_f, b_r, e, d =      \
        nd_data(g.l_f, g.c_f, g.h_f, g.l_r, g.c_r, g.h_r, 
                g.phiT_, g.phiB_, g.a_, g.beta_, g.delta_, g.gMax_, g.U_, 
                g.xb_f, g.xc_f, g.xb_r, g.xc_r, g.b_f, g.b_r)
    
    g.LCUT = 0.1 * h[0]  
    
    check_input()
    log_input(c, a, d, gMax)

    # Front right wing
    xc_f, xb_f, xt_f, nxt_f, xC_f, nC_f = \
        wing_total(xb_f, g.nxb_f, g.nb_f, xc_f, g.nxc_f, g.nc_f)
    # Rear right wing
    xc_r, xb_r, xt_r, nxt_r, xC_r, nC_r = \
        wing_total(xb_r, g.nxb_r, g.nb_r, xc_r, g.nxc_r, g.nc_r)
    
    # Wake vortex magnitude array
    GAMw_f = np.zeros((g.nwing, g.nxb_f))
    GAMw_r = np.zeros((g.nwing, g.nxb_r))
    # Total wake vortex number
    nxw_f = 0; nxw_r = 0
    # Wake vortex location array (after convection)
    Xw_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    Xw_r = np.zeros((3, 4, g.nxb_r, g.nwing))
    # Shed vortex location array 
    Xs_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    Xs_r = np.zeros((3, 4, g.nxb_r, g.nwing))

    if g.nstep > 3:
        # Initialize the linear and angular impulse arrays
        limpa_f = np.zeros((3, g.nstep, g.nwing))
        limpa_r = np.zeros((3, g.nstep, g.nwing))
        aimpa_f = np.zeros((3, g.nstep, g.nwing))
        aimpa_r = np.zeros((3, g.nstep, g.nwing))
        limpw_f = np.zeros((3, g.nstep, g.nwing))
        limpw_r = np.zeros((3, g.nstep, g.nwing))
        aimpw_f = np.zeros((3, g.nstep, g.nwing))
        aimpw_r = np.zeros((3, g.nstep, g.nwing))

    # Normal velocity on the wing due to the wing motion & wake vortices
    Vnc_f  = np.zeros((g.nwing, nxt_f))
    Vnc_r  = np.zeros((g.nwing, nxt_r))
    Vncw_f = np.zeros((g.nwing, nxt_r))
    Vncw_r = np.zeros((g.nwing, nxt_f))

    # Sub-matrix for the non-penetration condition (self-terms)
    MVNs_f = np.zeros((nxt_f, nxt_f, g.nwing))
    MVNs_r = np.zeros((nxt_r, nxt_r, g.nwing))

    # Velocity value matrices
    VBW_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    VBW_r = np.zeros((3, 4, g.nxb_r, g.nwing))

    # TODO: Document Xc_f/r
    Xc_f = np.zeros((3, 4, g.nxc_f, 2))
    Xc_r = np.zeros((3, 4, g.nxc_r, 2))
    # Space-fixed system coords of border elements on the wing
    Xb_f = np.zeros((3, 4, g.nxb_f, 2))
    Xb_r = np.zeros((3, 4, g.nxb_r, 2))
    # Global coords of total elements on the wing
    Xt_f = np.zeros((3, 4, nxt_f, 2))
    Xt_r = np.zeros((3, 4, nxt_r, 2))
    # Global coords of the collocation points on the wing
    XC_f = np.zeros((3, nxt_f, 2))
    XC_r = np.zeros((3, nxt_r, 2))
    # Unit normals at the collocation points on the wing
    NC_f = np.zeros((3, nxt_f, 2))
    NC_r = np.zeros((3, nxt_r, 2))


    # TIME MARCH
    # ----------
    for w in range(g.nwing):
        MVNs_f[:, :, w] = lr_set_matrix(w, xt_f, nxt_f, xC_f, nC_f)
        MVNs_r[:, :, w] = lr_set_matrix(w, xt_r, nxt_r, xC_r, nC_r)

    for g.istep in range(g.nstep):
        t = g.istep * g.dt

        # Get wing motion parameters
        phi = np.zeros(g.twing)
        theta = np.zeros(g.twing)
        dph = np.zeros(g.twing)
        dth = np.zeros(g.twing)

        for i in range(g.twing):
            phi[i], theta[i], dph[i], dth[i] = \
                wing_m(g.mpath[i], t, g.rt[i], g.tau[i], e[i], 
                       gMax[i], g.p[i], g.rtOff[i], phiT[i], phiB[i])
            
        # Get global coordinates of the points on the wing
        for i in range(g.nwing):
            # Front wing
            Xc_f[:,:,:,i], Xb_f[:,:,:,i], Xt_f[:,:,:,i], XC_f[:,:,i], NC_f[:,:,i] = \
                lr_mass_L2GT(i, beta[i], delta, phi[i], theta[i], a[i], U, t, b_f,
                            xc_f, xb_f, xt_f, xC_f, nC_f)
            # Rear wing                                                                       
            Xc_r[:,:,:,i], Xb_r[:,:,:,i], Xt_r[:,:,:,i], XC_r[:,:,i], NC_r[:,:,i] = \
                lr_mass_L2GT(i, beta[i+2], delta, phi[i+2], theta[i+2], a[i+2], U, t, b_r,
                             xc_r, xb_r, xt_r, xC_r, nC_r)

        # Find velocity of the wing
        for i in range(g.nwing):
            # Front wing
            Vnc_f[i,:] = lrs_wing_NVs(0, i, xC_f, XC_f[:,:,i], NC_f[:,:,i], t, theta[i],
                                      phi[i], dph[i], dth[i], a[i], beta[i], U)
            # Rear wing
            Vnc_r[i,:] = lrs_wing_NVs(1, i, xC_r, XC_r[:,:,i], NC_r[:,:,i], t, theta[i+2],
                                      phi[i+2], dph[i+2], dth[i+2], a[i+2], beta[i+2], U)

        # Normal vel on each airfoil by front & rear, right & left wake vortices
        # For each wing, there are 4 wake vortex contributions
        for i in range(g.nwing): 
            # Front wing
            Vncw_f[i,:] = n_vel_T_by_W(g.istep, nxt_f, XC_f[:,:,i], NC_f[:,:,i], 
                                       Xw_f, GAMw_f, nxw_f, Xw_r, GAMw_r, nxw_r)   
            # Rear wing  
            Vncw_r[i,:] = n_vel_T_by_W(g.istep, nxt_r, XC_r[:,:,i], NC_r[:,:,i], 
                                       Xw_f, GAMw_f, nxw_f, Xw_r, GAMw_r, nxw_r) 

        # Calculation of the time-dependent sub-matrices MVNs_ij (i~=j)
        # target wing=1, source wing=2
        MVNs_12 = cross_matrix(XC_f[:,:,0], NC_f[:,:,0], nxt_f, Xt_f[:,:,:,1], nxt_f)
        # target wing=1, source wing=3
        MVNs_13 = cross_matrix(XC_f[:,:,0], NC_f[:,:,0], nxt_f, Xt_r[:,:,:,0], nxt_r) 
        # target wing=1, source wing=4
        MVNs_14 = cross_matrix(XC_f[:,:,0], NC_f[:,:,0], nxt_f, Xt_r[:,:,:,1], nxt_r) 
        # target wing=1, source wing=2
        MVNs_21 = cross_matrix(XC_f[:,:,1], NC_f[:,:,1], nxt_f, Xt_f[:,:,:,0], nxt_f)
        # target wing=1, source wing=3
        MVNs_23 = cross_matrix(XC_f[:,:,1], NC_f[:,:,1], nxt_f, Xt_r[:,:,:,0], nxt_r) 
        # target wing=1, source wing=4
        MVNs_24 = cross_matrix(XC_f[:,:,1], NC_f[:,:,1], nxt_f, Xt_r[:,:,:,1], nxt_r)     
        # target wing=1, source wing=2
        MVNs_31 = cross_matrix(XC_r[:,:,0], NC_r[:,:,0], nxt_r, Xt_f[:,:,:,0], nxt_f)
        # target wing=1, source wing=3
        MVNs_32 = cross_matrix(XC_r[:,:,0], NC_r[:,:,0], nxt_r, Xt_f[:,:,:,1], nxt_f) 
        # target wing=1, source wing=4
        MVNs_34 = cross_matrix(XC_r[:,:,0], NC_r[:,:,0], nxt_r, Xt_r[:,:,:,1], nxt_r) 
        # target wing=1, source wing=2
        MVNs_41 = cross_matrix(XC_r[:,:,1], NC_r[:,:,1], nxt_r, Xt_f[:,:,:,0], nxt_f)
        # target wing=1, source wing=3
        MVNs_42 = cross_matrix(XC_r[:,:,1], NC_r[:,:,1], nxt_r, Xt_f[:,:,:,1], nxt_f) 
        # target wing=1, source wing=4
        MVNs_43 = cross_matrix(XC_r[:,:,1], NC_r[:,:,1], nxt_r, Xt_r[:,:,:,0], nxt_r) 
    
        # Assemble the total matrix using MVNs_f[:,:,1], MVNs_r[:,:,1], MVNs_ij[:,:]
        MVN = assemble_matrix(nxt_f, nxt_r, MVNs_f, MVNs_r,
                             MVNs_12, MVNs_13, MVNs_14,
                             MVNs_21, MVNs_23, MVNs_24,
                             MVNs_31, MVNs_32, MVNs_34,
                             MVNs_41, MVNs_42, MVNs_43)
        
        # Solve the system of equations
        GAMA = solution(nxt_f, nxt_r, MVN, Vnc_f, Vncw_f, Vnc_r, Vncw_r)

        # Split GAMA into 4 parts
        GAM_f = np.zeros((2, nxt_f))
        GAM_r = np.zeros((2, nxt_r))

        GAM_f[0, 0:nxt_f] = GAMA[0:nxt_f]                               # Front right wing
        GAM_f[1, 0:nxt_f] = GAMA[nxt_f:(2*nxt_f)]                       # Front left  wing
        GAM_r[0, 0:nxt_r] = GAMA[(2*nxt_f):(2*nxt_f + nxt_r)]           # Rear right wing
        GAM_r[1, 0:nxt_r] = GAMA[(2*nxt_f + nxt_r):(2*nxt_f + 2*nxt_r)] # Rear left  wing

        # Plot GAMA at the collocation points of the elements
        # using the unit normal direction: positive up and negative down
        # if g.gplot:
        #     for i in range(g.nwing):
        #         # Front wing
        #         plot_GAM(0, i, t, GAM_f[i,:], XC_f[:,:,i], NC_f[:,:,i])
        #         # Rear wing
        #         plot_GAM(1, i, t, GAM_r[i,:], XC_r[:,:,i], NC_r[:,:,i])

        # Plot locations, Xb & Xw, of border & wake vortices (space-fixed sys)
        # plot_WB(0, g.istep, g.nxb_f, nxw_f, Xb_f, Xw_f)     # Front wing
        # plot_WB(1, g.istep, g.nxb_r, nxw_r, Xb_r, Xw_r)     # Rear wing

        if g.nstep > 3:     # At least 4 steps needed to calculate forces and moments
            # Calculate impulses in the body-translating system
            # Include all of the bound vortices and wake vortices
            # For istep=1, there are no wake vortices
            # Front wing
            limpa, aimpa, limpw, aimpw = \
                s_impulse_WT(g.istep, U, t, Xt_f, Xw_f, GAM_f, GAMw_f, 
                             beta[0:2], phi[0:2], theta[0:2], a[0:2])
            for j in range(3):
                for w in range(g.nwing):
                    limpa_f[j, g.istep, w] = limpa[j, w]
                    aimpa_f[j, g.istep, w] = aimpa[j, w]
                    limpw_f[j, g.istep, w] = limpw[j, w]
                    aimpw_f[j, g.istep, w] = aimpw[j, w]
            # Rear wing
            limpa, aimpa, limpw, aimpw = \
                s_impulse_WT(g.istep, U, t, Xt_r, Xw_r, GAM_r, GAMw_r,
                             beta[2:4], phi[2:4], theta[2:4], a[2:4]) 
            for j in range(3):
                for w in range(g.nwing):
                    limpa_r[j, g.istep, w] = limpa[j, w]
                    aimpa_r[j, g.istep, w] = aimpa[j, w]
                    limpw_r[j, g.istep, w] = limpw[j, w]
                    aimpw_r[j, g.istep, w] = aimpw[j, w]  

        # Extract GAMAb (border & shed ) from GAM
        GAMAb_f = divide_GAM(GAM_f, g.nxb_f)
        GAMAb_r = divide_GAM(GAM_r, g.nxb_r)

        # Calculate velocity of border and wake vortices to be shed or convected
        # Influence coeff for the border elem vel due to the total wing elem
        # Self-influence coeff for each wing; calculated at each time step
        cVBT_f = b_vel_B_by_T_matrix(g.nxb_f, nxt_f, Xb_f, Xt_f)
        cVBT_r = b_vel_B_by_T_matrix(g.nxb_r, nxt_r, Xb_r, Xt_r)

        # Border element veocity due to the total wing elements: self-influence
        # VBTs_m(j,n,ixb,w);  vel on wing w due to total elem on wing w
        VBTs_f = vel_B_by_T(cVBT_f, GAM_f, nxt_f)
        VBTs_r = vel_B_by_T(cVBT_r, GAM_r, nxt_r)

        # Border element veocity due to the total wing elements: cross-influence
        VBTs_12 = cross_vel_B_by_T(Xb_f[:,:,:,0], g.nxb_f, Xt_f[:,:,:,1], GAM_f[1,:], nxt_f)
        VBTs_13 = cross_vel_B_by_T(Xb_f[:,:,:,0], g.nxb_f, Xt_r[:,:,:,0], GAM_r[0,:], nxt_r)
        VBTs_14 = cross_vel_B_by_T(Xb_f[:,:,:,0], g.nxb_f, Xt_r[:,:,:,1], GAM_r[1,:], nxt_r)
        VBTs_21 = cross_vel_B_by_T(Xb_f[:,:,:,1], g.nxb_f, Xt_f[:,:,:,0], GAM_f[0,:], nxt_f)
        VBTs_23 = cross_vel_B_by_T(Xb_f[:,:,:,1], g.nxb_f, Xt_r[:,:,:,0], GAM_r[0,:], nxt_r)
        VBTs_24 = cross_vel_B_by_T(Xb_f[:,:,:,1], g.nxb_f, Xt_r[:,:,:,1], GAM_r[1,:], nxt_r)
        VBTs_31 = cross_vel_B_by_T(Xb_r[:,:,:,0], g.nxb_r, Xt_f[:,:,:,0], GAM_f[0,:], nxt_f)
        VBTs_32 = cross_vel_B_by_T(Xb_r[:,:,:,0], g.nxb_r, Xt_f[:,:,:,1], GAM_f[1,:], nxt_f)
        VBTs_34 = cross_vel_B_by_T(Xb_r[:,:,:,0], g.nxb_r, Xt_r[:,:,:,1], GAM_r[1,:], nxt_r)
        VBTs_41 = cross_vel_B_by_T(Xb_r[:,:,:,1], g.nxb_r, Xt_f[:,:,:,0], GAM_f[0,:], nxt_f)
        VBTs_42 = cross_vel_B_by_T(Xb_r[:,:,:,1], g.nxb_r, Xt_f[:,:,:,1], GAM_f[1,:], nxt_f)
        VBTs_43 = cross_vel_B_by_T(Xb_r[:,:,:,1], g.nxb_r, Xt_r[:,:,:,0], GAM_r[0,:], nxt_r)
                        
        # Assemble the total border element velocity due to two wings
        VBT_f,VBT_r = assemble_vel_B_by_T(g.nxb_f, VBTs_f, VBTs_12, VBTs_13, VBTs_14, VBTs_21, VBTs_23, VBTs_24,
                                          g.nxb_r, VBTs_r, VBTs_31, VBTs_32, VBTs_34, VBTs_41, VBTs_42, VBTs_43)


def check_input():
    if g.b_r - g.b_f >= 0.5 * (g.c_r + g.c_f):
        print("Wing clearance checked")
    else:
        raise ValueError("rear and forward wings interfere")
    
    if np.any(g.p < 4):
        raise ValueError("p must >=4 for all wings")
    
    if np.any(np.abs(g.rtOff) > 0.5):
        raise ValueError("-0.5 <= rtOff <= 0.5 must be satisfied for all wings")
    
    if np.any((g.tau < 0) | (g.tau >= 2)):
        raise ValueError("0 <= tau < 2 must be satisfied for all wings")

def log_input(c, a, d, gMax):
    # TODO: Print delta_, b_f, b_r
    # TODO: Print nxb_f, nxc_f, nxb_r, nxc_r
    # TODO: Print mpath
    # TODO: Print phiT_, phiB_
    # TODO: Print a_, beta_, f_
    # TODO: Print gMax_, p, rtOff, tau, 
    # TODO: Print U_
    # TODO: Print nstep, dt
    
    air = np.sqrt(np.sum(g.U_**2))
    # TODO: Print air speed
    if air > 1.0E-03:
        # Flapping/Air Seed Ratio
        fk = 2 * g.f_ * g.d_ / air
        # TODO: Print fk
        # Pitch/Flapping Speed Ratio
        r = 0.5 * ((0.5*c + a) / d) * (g.p / g.t_) * (gMax / g.f_)
        # TODO: Print r
        # Pitch/Air Speed Ratio
        k = fk * r
        # TODO: Print k
    else:
        # Pitch/Flapping Speed Ratio
        r = 0.5 * ((0.5*c + a) / d) * (g.p / g.t_) * (gMax / g.f_)
        # TODO: Print r


if __name__ == "__main__":
    tombo()
