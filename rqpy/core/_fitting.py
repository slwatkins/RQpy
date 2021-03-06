import numpy as np
from scipy.optimize import curve_fit
from rqpy import plotting, utils


__all__ = ["fit_multi_gauss", "fit_gauss", "fit_saturation"]


def fit_multi_gauss(arr, guess, ngauss, xrange=None, nbins='sqrt', lgcplot=True, 
                    labeldict=None, lgcfullreturn=False):
    """
    Function to multiple Gaussians plus a flat background. Note, depending on
    the spectrum, this function can ber very sensitive to the inital guess parameters. 
    
    Parameters
    ----------
    arr : array
        Array of values to be binned
    guess : tuple
        The initial guesses for the Gaussian peaks. The order must be as follows:
        (amplitude_i, mu_i, std_i,
        ....,
        ....,
        background),
        where the guess for the background is the last element
    ngauss : int
        The number of peaks to fit
    xrange : tuple, optional
        The range over which to fit the peaks
    nbins : int, str, optional
        This is the same as plt.hist() bins parameter. Defaults is 'sqrt'.
    lgcplot : bool, optional
        If True, the fit and spectrum will be plotted 
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are: 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count'}
            Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to fit_multi_gauss()
    lgcfullreturn : bool, optional
        If True, the binned data is returned along with the fit parameters
        
    Returns
    -------
    peaks : array
        Array of locations of Gaussians maximums, sorted by magnitude in 
        increasing order
    amps : array
        Array of amplitudes, corresponding to order of 'peaks'
    stds : array
        Array of sqrt of variance, corresponding to order of 'peaks'
    background_fit : float
        The magnitude of the background
    fitparams : array, optional
        The best fit parameters, in the same order as the input guess
    errors : array, optional
        The uncertainty in the best fit parameters
    cov : array, optional
        The covariance matrix returned by scipy.optimize.curve_fit()
    bindata : tuple, optional
        The binned data from _bindata(), in order (x, y, bins)
        
    Raises
    ------
    ValueError
        If the number or parameters given in the guess is in conflict with ngauss,
        a ValueError is raised.
        
    """
    
    if ngauss != (len(guess)-1)/3:
        raise ValueError('Number of parameters in guess must match the number of Gaussians being fit (ngauss)')

    fit_n_gauss = lambda x, *params: utils.n_gauss(x, params, ngauss).sum(axis=0)
    
    x,y, bins = utils.bindata(arr,  xrange=xrange, bins=nbins)
    yerr = np.sqrt(y)
    yerr[yerr == 0] = 1 # make errors 1 if bins are empty
    
   
    fitparams, cov = curve_fit(fit_n_gauss, x, y, guess, sigma=yerr, absolute_sigma=True)
    errors = np.sqrt(np.diag(cov))
    
    peaks = fitparams[1:-1:3]
    amps =  fitparams[0:-1:3]
    stds = fitparams[2:-1:3]
    background_fit = fitparams[-1]
    
    peakssort = peaks.argsort()
    peaks = peaks[peakssort]
    amps = amps[peakssort]
    stds = stds[peakssort]
    
    if lgcplot:
        plotting.plot_n_gauss(x, y, bins, fitparams, labeldict)
        
    if lgcfullreturn:
        return peaks, amps, stds, background_fit, fitparams, errors, cov, (x, y, bins)
    else:
        return peaks, amps, stds, background_fit


def fit_gauss(arr, xrange=None, nbins='sqrt', noiserange=None, lgcplot=False, labeldict=None):
    """
    Function to fit Gaussian distribution with background to peak in spectrum. 
    Errors are assumed to be poissonian. 
    
    Parameters
    ----------
    arr : ndarray
        Array of data to bin and fit to gaussian
    xrange : tuple, optional
        The range of data to use when binning
    nbins : int, str, optional
        This is the same as plt.hist() bins parameter. Defaults is 'sqrt'.
    noiserange : tuple, optional
        nested 2-tuple. should contain the range before 
        and after the peak to be used for subtracting the 
        background
    lgcplot : bool, optional
        If True, the fit and spectrum will be plotted 
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to fit_gauss()
            
    Returns
    -------
    peakloc : float
        The mean of the distribution
    peakerr : float
        The full error in the location of the peak
    fitparams : tuple
        The best fit parameters of the fit; A, mu, sigma
    errors : ndarray
        The uncertainty in the fit parameters
        
    """
    
    x,y, bins = utils.bindata(arr,  xrange, bins=nbins)
    yerr = np.sqrt(y)
    yerr[yerr == 0] = 1 # make errors 1 if bins are empty
    
    if noiserange is not None:
        if noiserange[0][0] >= xrange[0]:
            clowl = noiserange[0][0]
        else:
            clow = xrange[0]
            
        clowh = noiserange[0][1]
        chighl = noiserange[1][0]
        
        if noiserange[1][1] <= xrange[1]:
            chighh = noiserange[1][1] 
        else:
            chighh = xrange[1]
            
        indlowl = (np.abs(x - clowl)).argmin()
        indlowh = (np.abs(x - clowh)).argmin() 
        indhighl = (np.abs(x - chighl)).argmin()
        indhighh = (np.abs(x - chighh)).argmin() - 1
        background = np.mean(np.concatenate((y[indlowl:indlowh],y[indhighl:indhighh])))  
    else:
        background = 0
        
    y_noback = y - background
    
    # get starting values for guess
    A0 = np.max(y_noback)
    mu0 = x[np.argmax(y_noback)]
    sig0 = np.abs(mu0 - x[np.abs(y_noback - np.max(y_noback)/2).argmin()])
    p0 = (A0, mu0, sig0, background)
    
    #do fit
    fitparams, cov = curve_fit(utils.gaussian_background, x, y, p0, sigma=yerr, absolute_sigma=True)
    errors = np.sqrt(np.diag(cov))    
    peakloc = fitparams[1]
    peakerr = np.sqrt((fitparams[2]/np.sqrt(fitparams[0]))**2)
    
    if lgcplot:
        plotting.plot_gauss(x, bins, y, fitparams, errors, background, labeldict)
    
    return peakloc, peakerr, fitparams, errors


def fit_saturation(x, y, yerr, guess, labeldict=None, lgcplot=True, ax=None):
    """
    Function to fit the saturation of the measured calibration spectrum. 
    
    Parameters
    ----------
    x : array_like
        The true energy of the spectral peaks in eV
    y : array_like
        The measured energy (or similar quantity) of the spectral peaks in eV
    yerr : array_like
        The errors in the measured energy of the spectral peaks in eV
    guess : array_like
        Array of initial guess parameters (a,b) to be passed to saturation_func(). See Notes
        for the functional form these parameters apply to.
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Energy Saturation Correction', 
                      'xlabel' : 'True Energy [eV]',
                      'ylabel' : 'Measured Energy [eV]',
                      'nsigma' : 2} # Note, nsigma is the number of sigma error bars 
                                      to plot 
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}
    lgcplot : bool, optional
            If True, the fit and spectrum will be plotted    
    ax : axes.Axes object, optional
        Option to pass an existing Matplotlib Axes object to plot over, if it already exists.
        
    Returns
    -------
    popt : ndarray
        Array of best fit paramters
    pcov : ndarray
        Covariance matrix from fit
    slope_linear : float
        The slope of the Taylor expansion of the saturation function 
        evaluated at the best fit parameters
        
    Notes
    -----
    This function fits the function y = a(1-exp(-x/b)) to the given data. This function
    is then Taylor expanded about x=0 to find the linear part of the calibration at
    low energies. There errors in this taylor expanded function y~ax/b, are determined
    via the covariance matrix returned from the initial fit.
    
    """
    
    popt, pcov = curve_fit(utils.saturation_func, x, y, sigma = yerr, p0 = guess, 
                           absolute_sigma=True, maxfev = 10000)
    if lgcplot:
        plotting.plot_saturation_correction(x, y, yerr, popt, pcov, labeldict, ax)
        
    slope_linear = utils.sat_func_expansion(1, *popt)
    
    return popt, pcov, slope_linear
    
    
