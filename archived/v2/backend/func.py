import numpy as np

"""
Function to calculate GMPE using a specific magnitude
"""

def cal_GK15(M, R, VS30, Bdepth, F, Q_0, flag='m'):
    amp = 1 if flag == 'm' else 1/1.12
    c1, c2, c3, c4, c5 = 0.14, -6.25, 0.37, 2.237, -7.542
    c6, c7, c8, c9, c10 = -0.125, 1.19, -6.15, 0.6, 0.345
    bv, VA = -0.24, 484.5
    m1, m2, m3, m4 = -0.0012, -0.38, 0.0006, 3.9
    a1, a2, a3 = 0.01686, 1.2695, 0.0001
    Dsp = 0.75
    t1, t2, t3, t4 = 0.001, 0.59, -0.0005, -2.3
    s1, s2, s3 = 0.001, 0.077, 0.3251

    G1 = np.log(( c1 * np.arctan(M + c2) + c3) * F)
    Ro = c4*M + c5
    Do = c6 * np.cos(c7 * (M + c8)) + c9
    G2 = -0.5 * np.log((1-R/Ro)**2 + 4 * (Do**2) * (R/Ro))
    G3 = -c10 * R / Q_0
    G4 = bv * np.log(VS30 / VA)
    A_Bdepth = 1.077/np.sqrt((1-(1.5/(Bdepth+0.1))**2)**2+4*0.7**2*(1.5/(Bdepth+0.1))**2)
    A_Bdist = 1/np.sqrt((1-(40/(R+0.1))**2)**2+4*0.7**2*(40/(R+0.1))**2)
    G5 = np.log(1 + A_Bdepth * A_Bdist)
    InPGA = G1 + G2 + G3 + G4 + G5
    PGA = np.exp(InPGA) * amp

    I = (a1*M+a2)*np.exp(a3*R)
    mu = m1*R + m2*M + m3*VS30 + m4
    S = s1*R - (s2*M + s3)
    Tsp_o = np.max([0.3, np.abs(t1*R + t2*M + t3*VS30 + t4)])
    zay = 1.763-0.25*np.arctan(1.4*(Bdepth-1))
    
    t = 0.3
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_03 = Y*np.exp(InPGA)*amp

    t = 1.0
    F1 = I*np.exp(-0.5*((np.log(t)+mu)/S)**2)
    F2 = 1/np.sqrt((1-(t/Tsp_o)**zay)**2 + 4*Dsp**2*(t/Tsp_o)**zay)
    Y = F1 + F2
    SA_10 = Y*np.exp(InPGA)*amp

    return PGA, SA_03, SA_10