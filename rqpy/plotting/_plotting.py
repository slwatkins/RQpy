import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from rqpy import utils


__all__ = ["hist", "scatter", "densityplot", "plot_gauss", "plot_n_gauss", "plot_saturation_correction"]


def hist(arr, nbins='sqrt', xlims=None, cutold=None, cutnew=None, lgcrawdata=True, 
         lgceff=True, lgclegend=True, labeldict=None, ax=None):
    """
    Function to plot histogram of RQ data. The bins are set such that all bins have the same size
    as the raw data
    
    Parameters
    ----------
    arr : array_like
        Array of values to be binned and plotted
    nbins : int, str, optional
        This is the same as plt.hist() bins parameter. Defaults is 'sqrt'.
    xlims : list of float, optional
        The xlimits of the histogram. This is passed to plt.hist() range parameter.
    cutold : array of bool, optional
        Mask of values to be plotted
    cutnew : array of bool, optional
        Mask of values to be plotted. This mask is added to cutold if cutold is not None. 
    lgcrawdata : bool, optional
        If True, the raw data is plotted
    lgceff : bool, optional
        If True, the cut efficiencies are printed in the legend. The total eff will be the sum of all the 
        cuts divided by the length of the data. The current cut eff will be the sum of the current cut 
        divided by the sum of all the previous cuts, if any.
    lgclegend : bool, optional
        If True, the legend is plotted.
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count', 
            'cutnew' : 'current', 'cutold' : 'previous'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to histrq()
    ax : axes.Axes object, optional
        Option to pass an existing Matplotlib Axes object to plot over, if it already exists.
    
    Returns
    -------
    fig : Figure
        Matplotlib Figure object. Set to None if ax is passed as a parameter.
    ax : axes.Axes object
        Matplotlib Axes object
        
    """
    
    labels = {'title'  : 'Histogram', 
              'xlabel' : 'variable', 
              'ylabel' : 'Count', 
              'cutnew' : 'current', 
              'cutold' : 'previous'}
    
    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 6))
    else:
        fig = None
        
    ax.set_title(labels['title'])
    ax.set_xlabel(labels['xlabel'])
    ax.set_ylabel(labels['ylabel'])

    if lgcrawdata:
        if xlims is None:
            hist, bins, _ = ax.hist(arr, bins=nbins, histtype='step', 
                                    label='full data', linewidth=2, color='b')
            xlims = (bins.min(), bins.max())
        else:
            hist, bins, _ = ax.hist(arr, bins=nbins, range=xlims, histtype='step', 
                                    label='full data', linewidth=2, color='b')            
    if cutold is not None:
        oldsum = cutold.sum()
        if cutnew is None:
            cuteff = oldsum/cutold.shape[0]
            cutefftot = cuteff
        if lgcrawdata:
            nbins = bins
        label = f"Data passing {labels['cutold']} cut"
        if xlims is not None:
            ax.hist(arr[cutold], bins=nbins, range=xlims, histtype='step', 
                    label=label, linewidth=2, color='r')
        else:
            res = ax.hist(arr[cutold], bins=nbins, histtype='step', 
                    label=label, linewidth=2, color='r')
            xlims = (res[1].min(), res[1].max())
    if cutnew is not None:
        newsum = cutnew.sum()
        if cutold is not None:
            cutnew = cutnew & cutold
            cuteff = cutnew.sum()/oldsum
            cutefftot = cutnew.sum()/cutnew.shape[0]
        else:
            cuteff = newsum/cutnew.shape[0]
            cutefftot = cuteff
        if lgcrawdata:
            nbins = bins
        if lgceff:
            label = f"Data passing {labels['cutnew']} cut, eff :  {cuteff:.3f}"
        else:
            label = f"Data passing {labels['cutnew']} cut "
        if xlims is not None:
            ax.hist(arr[cutnew], bins=nbins, range=xlims, histtype='step', 
                    linewidth=2, color='g', label=label)
        else:
            res = ax.hist(arr[cutnew], bins=nbins, histtype='step', 
                    linewidth=2, color='g', label=label)
            xlims = (res[1].min(), res[1].max())
    elif (cutnew is None) & (cutold is None):
        cuteff = 1
        cutefftot = 1
        
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax.tick_params(which="both", direction="in", right=True, top=True)
    ax.grid(linestyle="dashed")
    
    if lgceff:
        ax.plot([], [], linestyle=' ', label=f'Efficiency of total cut: {cutefftot:.3f}')
    if lgclegend:
        ax.legend()
    return fig, ax
    



def scatter(xvals, yvals, xlims=None, ylims=None, cutold=None, cutnew=None, 
            lgcrawdata=True, lgceff=True, lgclegend=True, labeldict=None, ms=1, a=.3, ax=None):
    """
    Function to plot RQ data as a scatter plot.
    
    Parameters
    ----------
    xvals : array_like
        Array of x values to be plotted
    yvals : array_like
        Array of y values to be plotted
    xlims : list of float, optional
        This is passed to the plot as the x limits. Automatically determined from range of data
        if not set.
    ylims : list of float, optional
        This is passed to the plot as the y limits. Automatically determined from range of data
        if not set.
    cutold : array of bool, optional
        Mask of values to be plotted
    cutnew : array of bool, optional
        Mask of values to be plotted. This mask is added to cutold if cutold is not None. 
    lgcrawdata : bool, optional
        If True, the raw data is plotted
    lgceff : bool, optional
        If True, the cut efficiencies are printed in the legend. The total eff will be the sum of all the 
        cuts divided by the length of the data. The current cut eff will be the sum of the current cut 
        divided by the sum of all the previous cuts, if any.
    lgclegend : bool, optional
        If True, the legend is plotted.
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count', 
            'cutnew' : 'current', 'cutold' : 'previous'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to histrq()
    ms : float, optional
        The size of each marker in the scatter plot. Default is 1
    a : float, optional
        The opacity of the markers in the scatter plot, i.e. alpha. Default is 0.3
    ax : axes.Axes object, optional
        Option to pass an existing Matplotlib Axes object to plot over, if it already exists.
    
    Returns
    -------
    fig : Figure
        Matplotlib Figure object. Set to None if ax is passed as a parameter.
    ax : axes.Axes object
        Matplotlib Axes object
        
    """

    labels = {'title'  : 'Scatter Plot',
              'xlabel' : 'x variable', 
              'ylabel' : 'y variable', 
              'cutnew' : 'current', 
              'cutold' : 'previous'}
    
    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 6))
    else:
        fig = None
    
    ax.set_title(labels['title'])
    ax.set_xlabel(labels['xlabel'])
    ax.set_ylabel(labels['ylabel'])
    
    if xlims is not None:
        xlimitcut = (xvals>xlims[0]) & (xvals<xlims[1])
    else:
        xlimitcut = np.ones(len(xvals), dtype=bool)
    if ylims is not None:
        ylimitcut = (yvals>ylims[0]) & (yvals<ylims[1])
    else:
        ylimitcut = np.ones(len(yvals), dtype=bool)

    limitcut = xlimitcut & ylimitcut
    
    if lgcrawdata and cutold is not None: 
        ax.scatter(xvals[limitcut & ~cutold], yvals[limitcut & ~cutold], 
                   label='Full Data', c='b', s=ms, alpha=a)
    elif lgcrawdata and cutnew is not None: 
        ax.scatter(xvals[limitcut & ~cutnew], yvals[limitcut & ~cutnew], 
                   label='Full Data', c='b', s=ms, alpha=a)
    elif lgcrawdata:
        ax.scatter(xvals[limitcut], yvals[limitcut], 
                   label='Full Data', c='b', s=ms, alpha=a)
        
    if cutold is not None:
        oldsum = cutold.sum()
        if cutnew is None:
            cuteff = cutold.sum()/cutold.shape[0]
            cutefftot = cuteff
            
        label = f"Data passing {labels['cutold']} cut"
        if cutnew is None:
            ax.scatter(xvals[cutold & limitcut], yvals[cutold & limitcut], 
                       label=label, c='r', s=ms, alpha=a)
        else: 
            ax.scatter(xvals[cutold & limitcut & ~cutnew], yvals[cutold & limitcut & ~cutnew], 
                       label=label, c='r', s=ms, alpha=a)
        
    if cutnew is not None:
        newsum = cutnew.sum()
        if cutold is not None:
            cutnew = cutnew & cutold
            cuteff = cutnew.sum()/oldsum
            cutefftot = cutnew.sum()/cutnew.shape[0]
        else:
            cuteff = newsum/cutnew.shape[0]
            cutefftot = cuteff
            
        if lgceff:
            label = f"Data passing {labels['cutnew']} cut, eff : {cuteff:.3f}"
        else:
            label = f"Data passing {labels['cutnew']} cut"
            
        ax.scatter(xvals[cutnew & limitcut], yvals[cutnew & limitcut], 
                   label=label, c='g', s=ms, alpha=a)
    
    elif (cutnew is None) & (cutold is None):
        cuteff = 1
        cutefftot = 1
        
    if xlims is None:
        if lgcrawdata:
            xrange = xvals.max()-xvals.min()
            ax.set_xlim([xvals.min()-0.05*xrange, xvals.max()+0.05*xrange])
        elif cutold is not None:
            xrange = xvals[cutold].max()-xvals[cutold].min()
            ax.set_xlim([xvals[cutold].min()-0.05*xrange, xvals[cutold].max()+0.05*xrange])
        elif cutnew is not None:
            xrange = xvals[cutnew].max()-xvals[cutnew].min()
            ax.set_xlim([xvals[cutnew].min()-0.05*xrange, xvals[cutnew].max()+0.05*xrange])
    else:
        ax.set_xlim(xlims)
        
    if ylims is None:
        if lgcrawdata:
            yrange = yvals.max()-yvals.min()
            ax.set_ylim([yvals.min()-0.05*yrange, yvals.max()+0.05*yrange])
        elif cutold is not None:
            yrange = yvals[cutold].max()-yvals[cutold].min()
            ax.set_ylim([yvals[cutold].min()-0.05*yrange, yvals[cutold].max()+0.05*yrange])
        elif cutnew is not None:
            yrange = yvals[cutnew].max()-yvals[cutnew].min()
            ax.set_ylim([yvals[cutnew].min()-0.05*yrange, yvals[cutnew].max()+0.05*yrange])
        
    else:
        ax.set_ylim(ylims)
        
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax.tick_params(which="both", direction="in", right=True, top=True)
    ax.grid(linestyle="dashed")
    
    if lgceff:
        ax.plot([], [], linestyle=' ', label=f'Efficiency of total cut: {cutefftot:.3f}')
    if lgclegend:
        ax.legend(markerscale=6, framealpha=.9)
    
    return fig, ax



def densityplot(xvals, yvals, xlims=None, ylims=None, nbins = (500,500), cut=None, 
                labeldict=None, lgclognorm = True, ax=None):
    """
    Function to plot RQ data as a density plot.
    
    Parameters
    ----------
    xvals : array_like
        Array of x values to be plotted
    yvals : array_like
        Array of y values to be plotted
    xlims : list of float, optional
        This is passed to the plot as the x limits. Automatically determined from range of data
        if not set.
    ylims : list of float, optional
        This is passed to the plot as the y limits. Automatically determined from range of data
        if not set.
    nbins : tuple, optional
        The number of bins to use to make the 2d histogram (nx, ny).
    cut : array of bool, optional
        Mask of values to be plotted
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to densityplot()
    lgclognorm : bool, optional
        If True (default), the color normilization for the density will be log scaled, rather 
        than linear
    ax : axes.Axes object, optional
        Option to pass an existing Matplotlib Axes object to plot over, if it already exists.
    
    Returns
    -------
    fig : Figure
        Matplotlib Figure object. Set to None if ax is passed as a parameter.
    ax : axes.Axes object
        Matplotlib Axes object
        
    """
    
    labels = {'title'  : 'Density Plot',
              'xlabel' : 'x variable', 
              'ylabel' : 'y variable'}
    
    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 6))
    else:
        fig = None
    
    ax.set_title(labels['title'])
    ax.set_xlabel(labels['xlabel'])
    ax.set_ylabel(labels['ylabel'])
    
    if xlims is not None:
        xlimitcut = (xvals>xlims[0]) & (xvals<xlims[1])
    else:
        xlimitcut = np.ones(len(xvals), dtype=bool)
    if ylims is not None:
        ylimitcut = (yvals>ylims[0]) & (yvals<ylims[1])
    else:
        ylimitcut = np.ones(len(yvals), dtype=bool)

    limitcut = xlimitcut & ylimitcut
    
    if cut is None:
        cut = np.ones(shape = xvals.shape, dtype=bool)

    cax = ax.hist2d(xvals[limitcut & cut], yvals[limitcut & cut], bins = nbins, 
              norm = colors.LogNorm(), cmap = 'icefire')
    cbar = fig.colorbar(cax[-1], label = 'Density of Data')
    cbar.ax.tick_params(direction="in")
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax.tick_params(which="both", direction="in", right=True, top=True)
    ax.grid(linestyle="dashed")

    return fig, ax

def plot_gauss(x, bins, y, fitparams, errors, background, labeldict=None):
    """
    Hidden helper function to plot Gaussian plus background fits
    
    Parameters
    ----------
    x : array
        Array of x data
    bins : array
        Array of binned data
    y : array
        Array of y data
    fitparams : tuple
        The best fit parameters from the fit
    errors : tuple
        The unccertainy in the best fit parameters
    background : float
        The average background rate
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to _plot_gauss()
        
    Returns
    -------
    fig : Figure
        Matplotlib Figure object. Set to None if ax is passed as a parameter.
    ax : axes.Axes object
        Matplotlib Axes object
        
    """
    
    x_fit = np.linspace(x[0], x[-1], 250) #make x data for fit
        
    labels = {'title'  : 'Gaussian Fit',
              'xlabel' : 'x variable', 
              'ylabel' : 'Count'} 
    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_title(labels['title'])
    ax.set_xlabel(labels['xlabel'])
    ax.set_ylabel(labels['ylabel'])
    ax.plot([],[], linestyle = ' ', label = f' μ = {fitparams[1]:.2f} $\pm$ {errors[1]:.3f}')
    ax.plot([],[], linestyle = ' ', label = f' σ = {fitparams[2]:.2f} $\pm$ {errors[2]:.3f}')
    ax.plot([],[], linestyle = ' ', label = f' A = {fitparams[0]:.2f} $\pm$ {errors[0]:.3f}')
    ax.plot([],[], linestyle = ' ', label = f' Offset = {fitparams[3]:.2f} $\pm$ {errors[3]:.3f}')

    ax.hist(x, bins = bins, weights = y, histtype = 'step', linewidth = 1, label ='Raw Data', alpha = .9)
    ax.axhline(background, label = 'Average Background Rate', linestyle = '--', alpha = .3)

    ax.plot(x_fit, utils.gaussian_background(x_fit, *fitparams), label = 'Gaussian Fit')
    ax.legend()
    ax.grid(True, linestyle = 'dashed')
    
    return fig, ax
    
def plot_n_gauss(x, y, bins, fitparams, labeldict=None, ax=None):
    """
    Helper function to plot and arbitrary number of Gaussians plus background fit
    
    Parameters
    ----------
    x : ndarray
        Array of x data
    y : ndarray
        Array of y data
    bins : ndarray
        Array of binned data
    fitparams : tuple
        The best fit parameters from the fit
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Histogram', 'xlabel' : 'variable', 'ylabel' : 'Count'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}, to _plot_n_gauss()
        
    Returns
    -------
    fig : Figure
        Matplotlib Figure object. Set to None if ax is passed as a parameter.
    ax : axes.Axes object
        Matplotlib Axes object
        
    """
    
    n = int((len(fitparams)-1)/3)
    
    x_fit = np.linspace(x[0], x[-1], 250) #make x data for fit
        
    labels = {'title'  : 'Gaussian Fit',
              'xlabel' : 'x variable', 
              'ylabel' : 'Count'} 
    for ii in range(n):
        labels[f'peak{ii+1}'] = f'Peak{ii+1}'
    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 6))
    else:
        fig = None

    
    ax.set_title(labels['title'])
    ax.set_xlabel(labels['xlabel'])
    ax.set_ylabel(labels['ylabel'])
    ax.hist(x, bins = bins, weights = y, histtype = 'step', linewidth = 1, label ='Raw Data', alpha = .9)
    

    y_fits = utils.n_gauss(x_fit, fitparams, n)
    ax.plot(x_fit, y_fits.sum(axis = 0), label = 'Total Fit')
    for ii in range(y_fits.shape[0] - 1):
        ax.plot(x_fit, y_fits[ii], alpha = .5, label = labels[f'peak{ii+1}'])
    ax.plot(x_fit, y_fits[-1], alpha = .5, linestyle = '--', label = 'Background')
    ax.grid(True, linestyle = 'dashed')
    ax.set_ylim(1, y.max()*1.05)
    ax.legend()
    
    return fig, ax    



def plot_saturation_correction(x, y, yerr, popt, pcov, labeldict, ax = None):
    
    """
    Helper function to plot the fit for the saturation correction
    
    Parameters
    ----------
    x : array
        Array of x data
    y : array
        Array of y data
    yerr : array-like
        The errors in the measured energy of the spectral peaks
    guess : array-like
        Array of initial guess parameters (a,b) to be passed to saturation_func()
    popt : array
        Array of best fit parameters from fit_saturation()
    pcov : array
        Covariance matrix returned by fit_saturation()
    
    labeldict : dict, optional
        Dictionary to overwrite the labels of the plot. defaults are : 
            labels = {'title' : 'Energy Saturation Correction', 
                      'xlabel' : 'True Energy [eV]',
                      'ylabel' : 'Measured Energy [eV]'}
        Ex: to change just the title, pass: labeldict = {'title' : 'new title'}
    ax : axes.Axes object, optional
        Option to pass an existing Matplotlib Axes object to plot over, if it already exists.
        
    Returns
    -------
    fig : matrplotlib figure object
    
    ax : matplotlib axes object
    
    """
    
    
    
    labels = {'title'  : 'Energy Saturation Correction',
              'xlabel' : 'True Energy [eV]', 
              'ylabel' : 'Measured Energy [eV]',
              'nsigma' : 2} 

    if labeldict is not None:
        for key in labeldict:
            labels[key] = labeldict[key]
    n = labels['nsigma'] 
    
    
    x_fit = np.linspace(0, x[-1], 100)
    y_fit = utils.saturation_func(x_fit, *popt)
    y_fit_lin = utils.sat_func_expansion(x_fit, *popt)
    
    
        
    err_full = utils.prop_sat_err(x_fit,popt,pcov)
    err_lin = utils.prop_sat_err_lin(x_fit,popt,pcov)
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    else:
        fig = None
    
    ax.set_title(labels['title'], fontsize = 16)
    ax.set_xlabel(labels['xlabel'], fontsize = 14)
    ax.set_ylabel(labels['ylabel'], fontsize = 14)
    ax.grid(True, linestyle = 'dashed')
    
    ax.scatter(x,y, marker = 'x', label = 'Spectral Peaks' , s = 100, zorder = 100, color ='b')
    ax.errorbar(x,y, yerr=yerr, linestyle = ' ')
    ax.plot(x_fit, y_fit, label = f'$y = a[1-exp(x/b)]$ $\pm$ {n} $\sigma$', color = 'g')
    ax.fill_between(x_fit, y_fit - n*err_full, y_fit + n*err_full, alpha = .5, color = 'g')
    ax.plot(x_fit, y_fit_lin, linestyle = '--', color = 'r', 
            label = f'Taylor Expansion of Saturation Function $\pm$ {n} $\sigma$')
    ax.fill_between(x_fit, y_fit_lin - n*err_lin, y_fit_lin + n*err_lin, alpha = .2, color = 'r')
    
    ax.legend(loc = 2, fontsize = 14)
    ax.tick_params(which="both", direction="in", right=True, top=True)
    plt.tight_layout()
    
    return fig, ax

    
