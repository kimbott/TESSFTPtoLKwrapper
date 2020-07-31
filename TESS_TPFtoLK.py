##########################################################################
######## TESS TPF (Target Pixel File) to LK (Light Curve) script ########
######## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ########
#### this code will take a given object (give the common name or TIC id)
#### and derive the standard lightcurve from the TPF, find the most likely
#### phase of a 'planet' with a periodogram, and phase fold to show a transit
#### light curve.  It's just a script version of the tutorial at https://docs.lightkurve.org/tutorials/02-how-to-recover-the-first-tess-candidate.html
#### with a few extra steps. If there is nothing tricky about a system or
#### dataset it would find a planet (or activity). Some user input is needed
#### to determine steps to take.  Please complete the tutorials before using this.
###########################################################################

# forematter, import needed packages
import lightkurve as lk
import matplotlib.pyplot as plt
#import numpy as np

################################# VARIABLES ################################
###### change these as needed to your object or convert to list loop #####
###########################################################################

nameortic = "TIC231716612" #'TIC350673608'
#sectorofobject = 1 #use MAST to look up what sector the object data is in, or remove this variable in the script belo to find all
smoothingfilter = 'off' #turn off if looking for stellar activity

################################# CODE ###################################
####### you most likely won't need to change things below this line #######
###########################################################################
# find the relevant TPFs and download
search_result = lk.search_targetpixelfile(nameortic, mission='TESS')
print search_result

cont = raw_input("Continue? (Y|N): ").lower()

if cont in ["y","yes"]:
	tpf = search_result.download(quality_bitmask='default')
elif cont in ["n","no"]:
	print "K, bye."
	exit()
else: 
	print "Huh?"
	exit()
	
print "Have downloaded TPF: ", tpf

#plot the TPF with a mask, standard pipeline one for now
tpf.plot(aperture_mask=tpf.pipeline_mask);
plt.savefig(nameortic+'FTPpipeline.png')
tpf.plot(aperture_mask=tpf.pipeline_mask, mask_color='red');
plt.savefig(nameortic+'FTPpipelinemask.png')
plt.show()

#convert to a lightcurve and plot, ask if mask needs adjusting
lc = tpf.to_lightcurve()
lc.errorbar();
plt.show()

maskchange = raw_input("Do you want a different threshold on the aperture mask? (Y|N): ").lower()

if maskchange == "y" : #if you want to change the mask...

	modify = True

	while modify:

		threshold_value = raw_input('What threshold value do you want? (median flux > value) : ')
		aperture_mask = tpf.create_threshold_mask(threshold=int(threshold_value), reference_pixel='center')
		tpf.plot(aperture_mask=aperture_mask, mask_color='red');
		plt.show()
		print threshold_value
		print aperture_mask
		plt.savefig(nameortic+'FTPchosenemask_th'+str(threshold_value)+'.png')

		answer = raw_input("Would you like to try again? (Type 'N' to accept the mask) (Y|N): ").lower()
		while True:
			if answer == 'y':
				modify = True
				break
			elif answer == 'n':
				modify = False
				break
			else:
				answer = raw_input('Incorrect option. Type "Y" to try again or "N" to accept the mask.').lower()

elif maskchange == 'n' :
	print "Sticking with the default mask."
	aperture_mask=tpf.pipeline_mask
	print aperture_mask
	threshold_value = 'def'
else :
	print "ERROR - Huh?  We'll stick with the default then..."
	aperture_mask=tpf.pipeline_mask
	print aperture_mask
	threshold_value = 'def'

print "Please note range where data is noisy in the plot."

# Now that we've set the mask to what we want, convert it to a lightcurve
lc = tpf.to_lightcurve(aperture_mask=aperture_mask)
lc.errorbar();
plt.savefig(nameortic+'lc_wmask.png')
plt.show()

# apply a Savitzky Golay smoothing filter (tut suggests 5%) (if toggled 'on')
if smoothingfilter in ["on","ON"]:
	print 'Smoothing turned on'
	print(lc.time.shape[0])
	print "Please note values where data is noisy in next plot!"
	flatval = int(lc.time.shape[0] * 0.05)
	flat_lc = lc.flatten(window_length=flatval)
	flat_lc.errorbar();
	plt.savefig(nameortic+'lc_flattened.png')
	plt.show()
elif smoothingfilter in ["off","OFF"]:
	print 'Smoothing turned off'
	print "Please note x-axis range where data is noisy in next plot!"
	flat_lc=lc
	flat_lc.errorbar();
	plt.show()
else :
	print 'TERMINAL ERROR - possible typo in forematter'
	exit()

# clip out the noisy bits
# Flag the times on the x axis where you'd like to start and stop an exclusionary clip
clippy = raw_input("Do you want to clip any noisy data? (Y|N): ").lower()

if clippy in ["y","yes"]:
	minclip = raw_input('Minimum time of poor data clip:' )
	maxclip = raw_input('Maximum time of poor data clip:' )
	timemask = (flat_lc.time < float(minclip)) | (flat_lc.time > float(maxclip))
	masked_lc = flat_lc[timemask]
	masked_lc.errorbar();
	plt.savefig(nameortic+'lc_timemask.png')
	plt.show()	
elif clippy in ["n","no"]:
	masked_lc = flat_lc
else:
	print "ERROR - I can't understand what you're typin', homeslice."
	masked_lc = flat_lc
		

#clip outliers
clipped_lc = masked_lc.remove_outliers(sigma=6) #sigma of outlier exclusion
ax = clipped_lc.scatter(s=0.1)
clipped_lc.errorbar(ax=ax, alpha=0.2);  # alpha determines the transparency
plt.savefig(nameortic+'lc_outlierclip.png')
plt.show()	

#save that final version as a fits file; see https://docs.lightkurve.org/tutorials/03-making-fits-files.html
clipped_lc.to_fits(path=nameortic+threshold_value+'lk_fr_ftp.fits', overwrite=True)


# PERIODOGRAM 
#in frequency
pg = clipped_lc.to_periodogram(oversample_factor=1)
pg.plot();
plt.savefig(nameortic+'pg_freq.png')
plt.show()	

#in period
pg.plot(view='period', scale='log');
plt.savefig(nameortic+'pg_period.png')
plt.show()	

print 'Period at max power', pg.period_at_max_power



# FOLD
#folded_lc = clipped_lc.fold(period=6.27, t0=1325.504)  ##lc.fold(pg.period_at_max_power).scatter();
#folded_lc.errorbar();
#plt.savefig(nameortic+'lc_folded.png')
#plt.show()

#binned_lc = folded_lc.bin(binsize=10)  # Average 10 points per bin
#binned_lc.errorbar();
#plt.savefig(nameortic+'lc_binnedandfolded.png')
#plt.show()