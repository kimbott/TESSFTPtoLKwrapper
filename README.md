# TESSFTPtoLKwrapper
get lightcurve from a TESS TPF file

30/07/20: Version takes user input (TIC or other ID and toggle smoothing filter (should be turned off if producing plots for stellar activity) in forematter and additional options as raw input) to derive a lightcurve with the Lightkurve software package.  The packages are all described in the tutorial materials https://docs.lightkurve.org/.  
The wrapper finds the appropriate TPF, converts it, allows the mask to be adjusted, smooths if appropriate, applies an outlier clip (sigma clip), produces a periodogram and finds a probable period for a planet (see tutorials for caveats to this) producing relevant plots to be saved along the way.  A fits file is also produced of the send product.
Todos are : 
1) Address the issue of reintroducing the omitted time clips when user choses not to clip anything
1b) Make possible to clip more than one area
1c) Ensure the warning to note where to clip is seen before the window pops up
2) Allow the period to be adjusted
3) Add folding
4) better handling of nonsense (loop instead of exit)
