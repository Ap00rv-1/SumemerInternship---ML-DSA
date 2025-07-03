# SumemerInternship---ML-DSA
Detection of QPOs using ML from X-ray Binaries
The objective of this project is to detect quasi-periodic oscillations (QPOs) in the X-ray
emission from low-mass X-ray binaries (LMXBs) using machine learning techniques.
QPOs appear as narrow peaks in the Power Density Spectrum (PDS) of the X-ray light
curve data, which is derived from the event files collected by X-ray observatories.
The process begins with the construction of the PDS from event data corresponding to
individual observations of X-ray binaries. These PDS are then modeled using Lorentzian
functions, which are suitable for capturing both broad noise components and narrow QPO
peaks. Each Lorentzian fit provides parameters such as the centroid frequency, full-width at
half maximum (FWHM), and amplitude.
Some event files yield no QPOs, while others may contain one or multiple QPOs. The
variability across observations makes automatic and reliable QPO detection a challenging
task.
To address this, a machine learning-based tool named QPOML is employed. QPOML takes
in features derived from the fitted Lorentzian models and other engineered features, and it
classifies which candidate peaks are likely to be genuine QPOs. In addition to classification,
the model may also estimate the number of QPOs present in a given observation.
This approach combines physical modeling (via Lorentzian fitting) with data-driven
techniques (via machine learning), aiming to improve the automation, reliability, and
scalability of QPO detection across large observational datasets.