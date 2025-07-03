from astropy.io import fits
import numpy as np
from stingray import Lightcurve
from stingray import AveragedPowerspectrum
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import pandas as pd

df = pd.read_csv("qpo_results.csv")

def lorentzian_with_background(f, f0, gamma, K, C):
    return K * (0.5 * gamma)**2 / ((f - f0)**2 + (0.5 * gamma)**2) + C
    return result
# This script processes cleaned event files to compute the power spectrum
# and detect peaks in the frequency domain, which may indicate QPOs.

for i in range(1, 170):  # Assuming you have 5 cleaned files named 'cleaned_file_1.evt', ..., 'cleaned_file_5.evt'
    if i==24 or i == 21:
        continue
    try:
        print(f"Processing cleaned file {i}...")
        # Load the cleaned event file
        evt_file = f"cleaned_file_{i}.evt"

        
        with fits.open(evt_file) as hdul:
            data = hdul[1].data
            times = data['TIME']
            pis = data['PI']
            hdr = hdul[0].header  # primary header; you can also check hdul[1].header if needed
            obs_id = hdr.get('OBS_ID', 'Not found') 

        # Filter for 2–6 keV range (PI ~ 200–600)
        mask = (pis >= 200) & (pis <= 600)
        filtered_times = times[mask]
        print(f'creating Lightcurve for obs id {i}')
        dt = 1/1000 
        t_start = filtered_times.min()
        t_end = filtered_times.max()
        bins = np.arange(t_start, t_end, dt)
        counts, _ = np.histogram(filtered_times, bins=bins)
        lc = Lightcurve(time=bins[:-1], counts=counts, dt=dt)
        print('Light curve Created')
        # Compute the power spectrum
        segment_size = 16.0
        aps = AveragedPowerspectrum(lc, segment_size=segment_size, norm='leahy')
        freq = aps.freq
        power = aps.power
        plt.figure(figsize=(10, 6))
        plt.loglog(freq, power, label='Power Spectrum', color='blue')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power')
        # Find peaks in the power spectrum
        peaks, properties = find_peaks(aps.power, height=np.mean(aps.power) + 3*np.std(aps.power))
        print('Detected peak frequencies:', aps.freq[peaks])
        
        

        # --- Load / Simulate PDS data ---
        # Replace with real PDS data from your source
        # Simulated structure (you already have something like this)
        freq = aps.freq
        power = aps.power

        # Filter PDS to reasonable region
        mask = (freq > 4) & (freq < 10)
        freq_fit = freq[mask]
        power_fit = power[mask]

        # --- Initial guesses for f0 ---
        initial_guesses_f0 = [4.5, 5.0, 5.5, 6.0, 6.5]
        gamma_guess = 0.5
        lower_bounds = [4.0, 0.05, 0.0, 0.0]   # e.g. gamma > 0.05 to avoid sharp spikes
        upper_bounds = [10, 5.0, 100.0, 10.0]
        K_guess = np.max(power_fit)
        C_guess = np.min(power_fit)

        fit_success = False
        # results = []
        # plt.figure(figsize=(8, 5))
        # plt.plot(freq_fit, power_fit, label="PDS", color="black")\
        print('Pds completedd')
        print('starting the guess for lorentzian')
        for i, f0 in enumerate(initial_guesses_f0):
            try:
                p0 = [f0, gamma_guess, K_guess, C_guess]
                popt, pcov = curve_fit(lorentzian_with_background, freq_fit, power_fit, p0=p0, bounds=(lower_bounds, upper_bounds))
                # print(popt)
                f0_fit, gamma_fit, K_fit, C_fit = popt
                Q = f0_fit / gamma_fit
                model_fit = lorentzian_with_background(freq_fit, *popt)

                # Reduced Chi²
                residuals = power_fit - model_fit
                chi2 = np.sum(residuals**2)
                red_chi2 = chi2 / (len(freq_fit) - len(popt))

                print(f"\nTrial {i+1}")
                print(f"f₀ = {f0_fit:.3f}, γ = {gamma_fit:.3f}, K = {K_fit:.3f}, Q = {Q:.2f}")
                print(f"Reduced χ² = {red_chi2:.4f}")

                if K_fit>0:
                    plt.plot(freq_fit, model_fit, label=f'Lorentzian Fit {i+1}')

                # Significance check
                if Q > 2 and Q<50:
                    print("Q > 2, significant Lorentzian detected.")
                    fit_success = True
                    # results.append([obs_id, f0_fit, gamma_fit, K_fit])
                    new_data = pd.DataFrame([{
                                "Obs ID": obs_id,
                                "freq": f'{f0_fit:.3f}',
                                "width": gamma_fit,
                                "amplitude": K_fit
                            }])
                    new_data.to_csv("qpo_results.csv", mode='a', header=False, index=False)
                    print("✅ New row appended to qpo_results.csv")

            except RuntimeError:
                print(f" Fit failed at guess f₀ = {f0}")
                continue
            
        
    except Exception as e:
        print(f"An error occurred: {e}")
        continue