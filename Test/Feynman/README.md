# Feynman Equations Test Suite

A structured validation suite of 100 physics equations from the Feynman Lectures on Physics.

| Equation ID | Formula | Variables | Complexity | Group | Physics Description |
| :--- | :--- | :--- | :---: | :---: | :--- |
| [I.6.2a](file:///./I_6_2a/test.py) | `exp(-theta**2/2)/sqrt(2*pi)` | `theta` | 14 | Difficult | Gaussian probability density (standard normal error distribution) |
| [I.6.2](file:///./I_6_2/test.py) | `exp(-(theta/sigma)**2/2)/(sqrt(2*pi)*sigma)` | `sigma, theta` | 18 | Difficult | Gaussian probability density (error distribution) |
| [I.6.2b](file:///./I_6_2b/test.py) | `exp(-((theta-theta1)/sigma)**2/2)/(sqrt(2*pi)*sigma)` | `sigma, theta, theta1` | 20 | Difficult | Feynman Equation I.6.2b |
| [I.8.14](file:///./I_8_14/test.py) | `sqrt((x2-x1)**2+(y2-y1)**2)` | `x1, x2, y1, y2` | 13 | Difficult | Feynman Equation I.8.14 |
| [I.9.18](file:///./I_9_18/test.py) | `G*m1*m2/((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)` | `m1, m2, G, x1, x2, y1, y2, z1, z2` | 23 | Difficult | Gravitational force between two masses |
| [I.10.7](file:///./I_10_7/test.py) | `m_0/sqrt(1-v**2/c**2)` | `m_0, v, c` | 13 | Difficult | Feynman Equation I.10.7 |
| [I.11.19](file:///./I_11_19/test.py) | `x1*y1+x2*y2+x3*y3` | `x1, x2, x3, y1, y2, y3` | 11 | Difficult | Electric field of a charge distribution |
| [I.12.1](file:///./I_12_1/test.py) | `mu*Nn` | `mu, Nn` | 3 | Easy | Force of sliding friction |
| [I.12.2](file:///./I_12_2/test.py) | `q1*q2*r/(4*pi*epsilon*r**3)` | `q1, q2, epsilon, r` | 15 | Difficult | Feynman Equation I.12.2 |
| [I.12.4](file:///./I_12_4/test.py) | `q1*r/(4*pi*epsilon*r**3)` | `q1, epsilon, r` | 13 | Difficult | Feynman Equation I.12.4 |
| [I.12.5](file:///./I_12_5/test.py) | `q2*Ef` | `q2, Ef` | 3 | Easy | Viscous drag force on a sphere (Stokes' law) |
| [I.12.11](file:///./I_12_11/test.py) | `q*(Ef+B*v*sin(theta))` | `q, Ef, B, v, theta` | 11 | Difficult | Force on a charge in electromagnetic field (Lorentz force) |
| [I.13.4](file:///./I_13_4/test.py) | `1/2*m*(v**2+u**2+w**2)` | `m, v, u, w` | 17 | Difficult | Potential energy of gravity near Earth's surface |
| [I.13.12](file:///./I_13_12/test.py) | `G*m1*m2*(1/r2-1/r1)` | `m1, m2, r1, r2, G` | 13 | Difficult | Gravitational potential energy of two masses |
| [I.14.3](file:///./I_14_3/test.py) | `m*g*z` | `m, g, z` | 5 | Easy | Work done by a constant force |
| [I.14.4](file:///./I_14_4/test.py) | `1/2*k_spring*x**2` | `k_spring, x` | 9 | Difficult | Kinetic energy of a moving mass |
| [I.15.3x](file:///./I_15_3x/test.py) | `(x-u*t)/sqrt(1-u**2/c**2)` | `x, u, c, t` | 17 | Difficult | Lorentz position transformation (relativity) |
| [I.15.3t](file:///./I_15_3t/test.py) | `(t-u*x/c**2)/sqrt(1-u**2/c**2)` | `x, c, u, t` | 21 | Difficult | Lorentz time dilation (relativity) |
| [I.15.1](file:///./I_15_1/test.py) | `m_0*v/sqrt(1-v**2/c**2)` | `m_0, v, c` | 15 | Difficult | Feynman Equation I.15.1 |
| [I.16.6](file:///./I_16_6/test.py) | `(u+v)/(1+u*v/c**2)` | `c, v, u` | 13 | Difficult | Feynman Equation I.16.6 |
| [I.18.4](file:///./I_18_4/test.py) | `(m1*r1+m2*r2)/(m1+m2)` | `m1, m2, r1, r2` | 11 | Difficult | Feynman Equation I.18.4 |
| [I.18.12](file:///./I_18_12/test.py) | `r*F*sin(theta)` | `r, F, theta` | 7 | Easy | Torque on a particle (angular momentum change) |
| [I.18.14](file:///./I_18_14/test.py) | `m*r*v*sin(theta)` | `m, r, v, theta` | 9 | Difficult | Feynman Equation I.18.14 |
| [I.24.6](file:///./I_24_6/test.py) | `1/2*m*(omega**2+omega_0**2)*1/2*x**2` | `m, omega, omega_0, x` | 21 | Difficult | Energy of a harmonic oscillator |
| [I.25.13](file:///./I_25_13/test.py) | `q/C` | `q, C` | 3 | Easy | Impedance of a capacitor |
| [I.26.2](file:///./I_26_2/test.py) | `arcsin(n*sin(theta2))` | `n, theta2` | 7 | Easy | Refractive index of a medium (Snell's law coefficient) |
| [I.27.6](file:///./I_27_6/test.py) | `1/(1/d1+n/d2)` | `d1, d2, n` | 9 | Difficult | Feynman Equation I.27.6 |
| [I.29.4](file:///./I_29_4/test.py) | `omega/c` | `omega, c` | 3 | Easy | Intensity of electromagnetic radiation |
| [I.29.16](file:///./I_29_16/test.py) | `sqrt(x1**2+x2**2-2*x1*x2*cos(theta1-theta2))` | `x1, x2, theta1, theta2` | 21 | Difficult | Feynman Equation I.29.16 |
| [I.30.3](file:///./I_30_3/test.py) | `Int_0*sin(n*theta/2)**2/sin(theta/2)**2` | `Int_0, theta, n` | 19 | Difficult | Feynman Equation I.30.3 |
| [I.30.5](file:///./I_30_5/test.py) | `arcsin(lambd/(n*d))` | `lambd, d, n` | 7 | Difficult | Intensity of double-slit interference pattern |
| [I.32.5](file:///./I_32_5/test.py) | `q**2*a**2/(6*pi*epsilon*c**3)` | `q, a, epsilon, c` | 17 | Difficult | Radiated power by an accelerating charge (Larmor formula) |
| [I.32.17](file:///./I_32_17/test.py) | `(1/2*epsilon*c*Ef**2)*(8*pi*r**2/3)*(omega**4/(omega**2-omega_0**2)**2)` | `epsilon, c, Ef, r, omega, omega_0` | 35 | Difficult | Feynman Equation I.32.17 |
| [I.34.8](file:///./I_34_8/test.py) | `q*v*B/p` | `q, v, B, p` | 7 | Difficult | Magnetic moment of a current loop |
| [I.34.1](file:///./I_34_1/test.py) | `omega_0/(1-v/c)` | `c, v, omega_0` | 7 | Difficult | Feynman Equation I.34.1 |
| [I.34.14](file:///./I_34_14/test.py) | `(1+v/c)/sqrt(1-v**2/c**2)*omega_0` | `c, v, omega_0` | 19 | Difficult | Magnetic field of a dipole |
| [I.34.27](file:///./I_34_27/test.py) | `(h/(2*pi))*omega` | `omega, h` | 7 | Difficult | Feynman Equation I.34.27 |
| [I.37.4](file:///./I_37_4/test.py) | `I1+I2+2*sqrt(I1*I2)*cos(delta)` | `I1, I2, delta` | 15 | Difficult | Uncertainty principle relationship |
| [I.38.12](file:///./I_38_12/test.py) | `4*pi*epsilon*(h/(2*pi))**2/(m*q**2)` | `m, q, h, epsilon` | 19 | Difficult | De Broglie wavelength of a particle |
| [I.39.1](file:///./I_39_1/test.py) | `3/2*pr*V` | `pr, V` | 7 | Difficult | Feynman Equation I.39.1 |
| [I.39.11](file:///./I_39_11/test.py) | `1/(gamma-1)*pr*V` | `gamma, pr, V` | 9 | Difficult | Feynman Equation I.39.11 |
| [I.39.22](file:///./I_39_22/test.py) | `n*kb*T/V` | `n, T, V, kb` | 7 | Difficult | Mean molecular kinetic energy of gas |
| [I.40.1](file:///./I_40_1/test.py) | `n_0*exp(-m*g*x/(kb*T))` | `n_0, m, x, T, g, kb` | 14 | Difficult | Boltzmann distribution of gas density in atmosphere |
| [I.41.16](file:///./I_41_16/test.py) | `h/(2*pi)*omega**3/(pi**2*c**2*(exp((h/(2*pi))*omega/(kb*T))-1))` | `omega, T, h, kb, c` | 33 | Difficult | Rotational energy of a molecule |
| [I.43.16](file:///./I_43_16/test.py) | `mu_drift*q*Volt/d` | `mu_drift, q, Volt, d` | 7 | Difficult | Velocity distribution of gas molecules (Maxwell-Boltzmann) |
| [I.43.31](file:///./I_43_31/test.py) | `mob*kb*T` | `mob, T, kb` | 5 | Difficult | Thermal conductivity of a gas |
| [I.43.43](file:///./I_43_43/test.py) | `1/(gamma-1)*kb*v/A` | `gamma, kb, A, v` | 11 | Difficult | Viscosity of a gas |
| [I.44.4](file:///./I_44_4/test.py) | `n*kb*T*ln(V2/V1)` | `n, kb, T, V1, V2` | 11 | Difficult | Feynman Equation I.44.4 |
| [I.47.23](file:///./I_47_23/test.py) | `sqrt(gamma*pr/rho)` | `gamma, pr, rho` | 7 | Difficult | Feynman Equation I.47.23 |
| [I.48.2](file:///./I_48_2/test.py) | `m*c**2/sqrt(1-v**2/c**2)` | `m, v, c` | 17 | Difficult | Phase velocity of wave in a dispersive medium |
| [I.50.26](file:///./I_50_26/test.py) | `x1*(cos(omega*t)+alpha*cos(omega*t)**2)` | `x1, omega, t, alpha` | 17 | Difficult | Electric field from an oscillating dipole |
| [II.2.42](file:///./II_2_42/test.py) | `kappa*(T2-T1)*A/d` | `kappa, T1, T2, A, d` | 9 | Difficult | Electrostatic potential of a dipole |
| [II.3.24](file:///./II_3_24/test.py) | `Pwr/(4*pi*r**2)` | `Pwr, r` | 9 | Difficult | Flux of electric field (Gauss's law) |
| [II.4.23](file:///./II_4_23/test.py) | `q/(4*pi*epsilon*r)` | `q, epsilon, r` | 9 | Difficult | Energy density of electric field in vacuum |
| [II.6.11](file:///./II_6_11/test.py) | `1/(4*pi*epsilon)*p_d*cos(theta)/r**2` | `epsilon, p_d, theta, r` | 17 | Difficult | Feynman Equation II.6.11 |
| [II.6.15a](file:///./II_6_15a/test.py) | `p_d/(4*pi*epsilon)*3*z/r**5*sqrt(x**2+y**2)` | `epsilon, p_d, r, x, y, z` | 25 | Difficult | Feynman Equation II.6.15a |
| [II.6.15b](file:///./II_6_15b/test.py) | `p_d/(4*pi*epsilon)*3*cos(theta)*sin(theta)/r**3` | `epsilon, p_d, theta, r` | 21 | Difficult | Feynman Equation II.6.15b |
| [II.8.7](file:///./II_8_7/test.py) | `3/5*q**2/(4*pi*epsilon*d)` | `q, epsilon, d` | 15 | Difficult | Energy stored in a capacitor |
| [II.8.31](file:///./II_8_31/test.py) | `epsilon*Ef**2/2` | `epsilon, Ef` | 7 | Difficult | Feynman Equation II.8.31 |
| [II.10.9](file:///./II_10_9/test.py) | `sigma_den/epsilon*1/(1+chi)` | `sigma_den, epsilon, chi` | 9 | Difficult | Feynman Equation II.10.9 |
| [II.11.3](file:///./II_11_3/test.py) | `q*Ef/(m*(omega_0**2-omega**2))` | `q, Ef, m, omega_0, omega` | 13 | Difficult | Polarization of a dielectric material |
| [II.11.17](file:///./II_11_17/test.py) | `n_0*(1+p_d*Ef*cos(theta)/(kb*T))` | `n_0, kb, T, theta, p_d, Ef` | 15 | Difficult | Feynman Equation II.11.17 |
| [II.11.20](file:///./II_11_20/test.py) | `n_rho*p_d**2*Ef/(3*kb*T)` | `n_rho, p_d, Ef, kb, T` | 13 | Difficult | Refractive index of a gas (dispersion relation) |
| [II.11.27](file:///./II_11_27/test.py) | `n*alpha/(1-(n*alpha/3))*epsilon*Ef` | `n, alpha, epsilon, Ef` | 15 | Difficult | Transmission coefficient of electric field |
| [II.11.28](file:///./II_11_28/test.py) | `1+n*alpha/(1-(n*alpha/3))` | `n, alpha` | 13 | Difficult | Refractive index of a plasma |
| [II.13.17](file:///./II_13_17/test.py) | `1/(4*pi*epsilon*c**2)*2*I/r` | `epsilon, c, I, r` | 17 | Difficult | Magnetic field of a long straight wire |
| [II.13.23](file:///./II_13_23/test.py) | `rho_c_0/sqrt(1-v**2/c**2)` | `rho_c_0, v, c` | 13 | Difficult | Force between two parallel current-carrying wires |
| [II.13.34](file:///./II_13_34/test.py) | `rho_c_0*v/sqrt(1-v**2/c**2)` | `rho_c_0, v, c` | 15 | Difficult | Feynman Equation II.13.34 |
| [II.15.4](file:///./II_15_4/test.py) | `-mom*B*cos(theta)` | `mom, B, theta` | 8 | Difficult | Vector potential of a solenoid |
| [II.15.5](file:///./II_15_5/test.py) | `-p_d*Ef*cos(theta)` | `p_d, Ef, theta` | 8 | Difficult | Vector potential of a magnetic dipole |
| [II.21.32](file:///./II_21_32/test.py) | `q/(4*pi*epsilon*r*(1-v/c))` | `q, epsilon, r, v, c` | 15 | Difficult | Electric field of an accelerating point charge |
| [II.24.17](file:///./II_24_17/test.py) | `sqrt(omega**2/c**2-pi**2/d**2)` | `omega, c, d` | 17 | Difficult | Transmission line impedance |
| [II.27.16](file:///./II_27_16/test.py) | `epsilon*c*Ef**2` | `epsilon, c, Ef` | 7 | Difficult | Poynting vector (energy flux density of EM wave) |
| [II.27.18](file:///./II_27_18/test.py) | `epsilon*Ef**2` | `epsilon, Ef` | 5 | Difficult | Energy density of electromagnetic field |
| [II.34.2a](file:///./II_34_2a/test.py) | `q*v/(2*pi*r)` | `q, v, r` | 9 | Difficult | Magnetic susceptibility of a paramagnetic material |
| [II.34.2](file:///./II_34_2/test.py) | `q*v*r/2` | `q, v, r` | 7 | Difficult | Feynman Equation II.34.2 |
| [II.34.11](file:///./II_34_11/test.py) | `g_*q*B/(2*m)` | `g_, q, B, m` | 9 | Difficult | Magnetic moment of an electron spin |
| [II.34.29a](file:///./II_34_29a/test.py) | `q*h/(4*pi*m)` | `q, h, m` | 9 | Difficult | Gyromagnetic ratio / g-factor |
| [II.34.29b](file:///./II_34_29b/test.py) | `g_*mom*B*Jz/(h/(2*pi))` | `g_, h, Jz, mom, B` | 13 | Difficult | Feynman Equation II.34.29b |
| [II.35.18](file:///./II_35_18/test.py) | `n_0/(exp(mom*B/(kb*T))+exp(-mom*B/(kb*T)))` | `n_0, kb, T, mom, B` | 22 | Difficult | Work done on a magnetic dipole |
| [II.35.21](file:///./II_35_21/test.py) | `n_rho*mom*tanh(mom*B/(kb*T))` | `n_rho, mom, B, kb, T` | 13 | Difficult | Gibbs free energy of a magnetized material |
| [II.36.38](file:///./II_36_38/test.py) | `mom*H/(kb*T)+(mom*alpha)/(epsilon*c**2*kb*T)*M` | `mom, H, kb, T, alpha, epsilon, c, M` | 23 | Difficult | Free energy density of a superconductor (London equation) |
| [II.37.1](file:///./II_37_1/test.py) | `mom*(1+chi)*B` | `mom, B, chi` | 7 | Difficult | Feynman Equation II.37.1 |
| [II.38.3](file:///./II_38_3/test.py) | `Y*A*x/d` | `Y, A, d, x` | 7 | Difficult | Velocity of a particle in a cyclotron |
| [II.38.14](file:///./II_38_14/test.py) | `Y/(2*(1+sigma))` | `Y, sigma` | 7 | Difficult | Force on a current-carrying wire in magnetic field |
| [III.4.32](file:///./III_4_32/test.py) | `1/(exp((h/(2*pi))*omega/(kb*T))-1)` | `h, omega, kb, T` | 17 | Difficult | Feynman Equation III.4.32 |
| [III.4.33](file:///./III_4_33/test.py) | `(h/(2*pi))*omega/(exp((h/(2*pi))*omega/(kb*T))-1)` | `h, omega, kb, T` | 23 | Difficult | Feynman Equation III.4.33 |
| [III.7.38](file:///./III_7_38/test.py) | `2*mom*B/(h/(2*pi))` | `mom, B, h` | 11 | Difficult | Feynman Equation III.7.38 |
| [III.8.54](file:///./III_8_54/test.py) | `sin(E_n*t/(h/(2*pi)))**2` | `E_n, t, h` | 13 | Difficult | Amplitudes for a particle in a periodic potential |
| [III.9.52](file:///./III_9_52/test.py) | `(p_d*Ef*t/(h/(2*pi)))*sin((omega-omega_0)*t/2)**2/((omega-omega_0)*t/2)**2` | `p_d, Ef, t, h, omega, omega_0` | 33 | Difficult | Feynman Equation III.9.52 |
| [III.10.19](file:///./III_10_19/test.py) | `mom*sqrt(Bx**2+By**2+Bz**2)` | `mom, Bx, By, Bz` | 15 | Difficult | Energy eigenvalues of a two-state system with coupling |
| [III.12.43](file:///./III_12_43/test.py) | `n*(h/(2*pi))` | `n, h` | 7 | Difficult | Probability distribution of scattering angle |
| [III.13.18](file:///./III_13_18/test.py) | `2*E_n*d**2*k/(h/(2*pi))` | `E_n, d, k, h` | 15 | Difficult | Transition rate in a periodic lattice |
| [III.14.14](file:///./III_14_14/test.py) | `I_0*(exp(q*Volt/(kb*T))-1)` | `I_0, q, Volt, kb, T` | 13 | Difficult | Probability of a transition between energy levels |
| [III.15.12](file:///./III_15_12/test.py) | `2*U*(1-cos(k*d))` | `U, k, d` | 11 | Difficult | Dispersion relation for spin waves (magnons) |
| [III.15.14](file:///./III_15_14/test.py) | `(h/(2*pi))**2/(2*E_n*d**2)` | `h, E_n, d` | 15 | Difficult | Energy of a spin wave in a ferromagnet |
| [III.15.27](file:///./III_15_27/test.py) | `2*pi*alpha/(n*d)` | `alpha, n, d` | 9 | Difficult | Feynman Equation III.15.27 |
| [III.17.37](file:///./III_17_37/test.py) | `beta*(1+alpha*cos(theta))` | `beta, alpha, theta` | 9 | Difficult | Scattering amplitude in Born approximation |
| [III.19.51](file:///./III_19_51/test.py) | `-m*q**4/(2*(4*pi*epsilon)**2*(h/(2*pi))**2)*(1/n**2)` | `m, q, h, n, epsilon` | 30 | Difficult | Transmission coefficient of a potential barrier |
| [III.21.20](file:///./III_21_20/test.py) | `-rho_c_0*q*A_vec/m` | `rho_c_0, q, A_vec, m` | 8 | Difficult | Feynman Equation III.21.20 |
