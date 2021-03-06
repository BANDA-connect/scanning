#author: Viviana Siless - vsiless@mgh.harvard.edu   #/space/erebus/1/users/jwang/jon2/bin/python3.6
import csv

import os
import math
import numpy as np
import nibabel as nib
import os.path
import matplotlib
print( matplotlib.get_cachedir())
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv
import utils
from collections import OrderedDict
import matplotlib
from scipy import stats
import statsmodels.api as sm

matplotlib.rcParams.update({'font.size': 34})

outliers=["BANDA051","BANDA104","BANDA131","BANDA134","BANDA129","BANDA137"]

subjects,  catdic = utils.getBandaLabels(outliers)

print(subjects)
control_subjects = catdic['control']
anx_subjects = catdic['anx']
dep_subjects = catdic['dep']
all_s = catdic['allsubjects']
all_ages = catdic['allages']
all_genders = np.array(catdic['allgenders'])
all_genders[all_genders=='F']=0
all_genders[all_genders=='F ']=0
all_genders[all_genders=='M']=1
all_genders = np.asarray(all_genders, dtype=int)
print(all_genders)
print(control_subjects)
print(anx_subjects)
print(dep_subjects)
#dep_and_anx_subjects = catdic['dep_anx']

partial_scan_subjects = catdic['partial_scan']
no_scan_subjects = catdic['no_scan']

colors=['#74c7a5', '#FF8600','#36649E']
labels=['CA', 'AA', 'DA']
labelGroups=['CA', 'AA', 'DA']
namesPerScan={"T1":"T1w" ,"T2":"T2w","Diffusion":"dMRI","Rest":"rfMRI", "Gambling":"IPT", "FaceMatching":"EPT","Conflict":"EIT", "T1 all vnavs - no reacq":"T1w (no vNavs)", "T2 all vnavs - no reacq":"T2w (no vNavs)"}
labels_sets={"T1_T2":"T1w-T2w","DiffusionDiffusion":"dMRI","RestRest":"rfMRI","GamblingGambling":"IPT","FaceMatchingFaceMatching":"EPT","ConflictConflict":"EIT"}
scansCSV=["T1","T2","Diffusion"] #,"Rest","Gambling","FaceMatching","Conflict"]
scansCSV=["Rest","Gambling","FaceMatching","Conflict"]
voxelSizeCSV=[.8,.8,1.5,2,2,2,2,.8,.8]	
scansBCSV=["T1_T2","DiffusionDiffusion","RestRest","GamblingGambling","FaceMatchingFaceMatching","ConflictConflict"]
headerCSV=["","T1w","T2w","dMRI"] #,"rfMRI","IPT","EPT","EIT"]
headerCSV=["rfMRI","IPT","EPT","EIT"]
headerBCSV=["","T1w-T2w","dMRI","rfMRI","IPT","EPT","EIT"]
voxelSizeBCSV=[.8,1.5,2,2,2,2]	
scores_CSV= ["MFQ","SHAPS_CNT","BIS","BAS", "STAIS", "STAIT", "RCADSA", "RCADSD","wasi"]
scores_header_CSV= ["MFQ","SHAPS","BIS","BAS", "STAI-S", "STAI-T", "RCADS-A", "RCADS-D","WASI-II"]
print(labels, colors)

def plotSNRPerScan():
	snr_perScan=dict()
	#with open('/space/erebus/1/users/data/scores/snr_output_old.csv', 'r') as csvfile:   #output csv file from: snr_patvscontrol snr()
	with open('/autofs/space/erebus_001/users/data/scores/new2/snr_avg_output_rjj020419.csv','r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			try:

				s=row[0]
				scan=row[1][:]
				snr=float(row[2])
				if snr>0:
					if not scan in snr_perScan:
						snr_perScan[scan]=[[],[],[]]

					if s in control_subjects:
						snr_perScan[scan][0].append(snr)
					elif s in anx_subjects:
						snr_perScan[scan][1].append(snr)
					elif s in dep_subjects:
						snr_perScan[scan][2].append(snr)
			except:
				print(row)

	f, axarr = plt.subplots(4, 5,figsize=(23,14))
	f.subplots_adjust(left=.03, bottom=.06, right=.97, top=.95, wspace=.18, hspace=.30)
	plotted=0

	for scanName, values in snr_perScan.items():
		i=plotted%4
		j=int(plotted/4)
		print (scanName)
		axarr[i,j].set_title(scanName)
		axarr[i, j].violinplot(values, [1,2,3], points=20, widths=0.3, showmeans=True) #,showmedians=True)
		axarr[i,j].set_ylim((5,30))

		f.savefig("/autofs/space/erebus_001/users/data/scores/new2/plots/snr",dpi=199)
		plotted+=1


	plt.show()


def getFormatedText_ttest(t_test, n, bonferoni):
	text= 'p=.%s' % format( t_test.pvalue,'.3f')[2:]
	text+= "\n"
	if t_test.pvalue*bonferoni >.999:
		text+='pc>.999'
		patch2 = mpatches.Patch(color='none', label=r'$pc>.999$')
	else:
		text+= 'pc=.%s' % format( t_test.pvalue*bonferoni,'.3f')[2:]
		patch2 = mpatches.Patch(color='none', label=r'$p=.%s$' % format( t_test.pvalue*bonferoni,'.3f')[2:])	
	text+= "\n"
	r2=(t_test.tvalue[0]**2/(t_test.tvalue[0]**2 +n -2))[0] 
	if r2 < .001:
		text+='rs<.001'
		patch1 = mpatches.Patch(color='none', label=r'$r^2<.001$')
	else:
		text+= 'rs=.%s' % format( r2,'.3f')[2:]
		patch1 = mpatches.Patch(color='none', label=r'$r^2=.%s$' % format( r2,'.3f')[2:])
	
	return text, patch1, patch2
def getFormatedText_regression(p_value, r_value, bonferoni):
	text=""
	if p_value <0.001:
		text="p<.001"
	else:
		text=r"p=.%s"%format(p_value, ".3f")[2:]
	text+= "\n"

	if p_value*bonferoni >.999:
		patch2 = mpatches.Patch(color='none', label=r'$p>.999$')
		text+=r'pc>.999'
	else:
		patch2 = mpatches.Patch(color='none', label=r'$p=.%s$' % format( p_value*7*4,'.3f')[2:])
		text+=r'pc=.%s' % format( p_value*bonferoni,'.3f')[2:]

	text+= "\n"
	if r_value **2 >0.001:
		patch1 = mpatches.Patch(color='none', label=r'$r^2=.%s$' % format( r_value**2,'.3f')[2:])
		text+=r'rs=.%s' % format( r_value**2,'.3f')[2:]
	else:
		patch1 = mpatches.Patch(color='none', label=r'$r^2<.001$')
		text+=r'rs<.001'

	return patch1, patch2, text
	
def plotSNRAvg():
	snr_perScan=dict()
	fsquared=[]
	with open('/autofs/space/erebus_001/users/data/scores/new2/snr_avg_output_vivs.csv', 'r') as csvfile:
	#with open('/autofs/space/erebus_001/users/data/scores/new/snr_output_newtest.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			try:
				s=row[0]
				if "T" in row[1]:
					scan= row[1]
				else:
					scan=row[1][:-1]
				#print(scan)
				snr=float(row[2])
				if snr>0:
					if not scan in snr_perScan:
						snr_perScan[scan]=[dict(),dict(),dict()]

					for a in range(3):
						if not s in snr_perScan[scan][a]:
							snr_perScan[scan][a][s]=[]
					if s in control_subjects:
						snr_perScan[scan][0][s].append(snr)
					elif s in anx_subjects:
						snr_perScan[scan][1][s].append(snr)
					elif s in dep_subjects:
						snr_perScan[scan][2][s].append(snr)
			except:
				print(row)
	scans=["T1","T2","Diffusion"] #,"Rest","Gambling","FaceMatching","Conflict"]
	header=["","T1w","T2w","dMRI"] #,"rfMRI","IPT","EPT","EIT"]
	table=dict()
	table["CA vs AA"] = ["CA vs AA"] 	
	table["CA vs DA"] = ["CA vs DA"]  	
	table["AA vs DA"] = ["AA vs DA"] 

	plotted=0
	nCA = len(snr_perScan["T1"][0])
	nAA = len(snr_perScan["T1"][1])
	nDA = len(snr_perScan["T1"][2])
	for scanName in scans:
		f=plt.figure(plotted, figsize=(5,5))
		categories = snr_perScan[scanName]
		plt.title(namesPerScan[scanName])
		values =[[],[],[]]
		x=[]
		y=[]
		for q in range(len(values)):
			for sub, snr in categories[q].items():
				if sub in subjects and len(snr)>0:
					values[q].append(sum(snr)/len(snr))
					y.append(sum(snr)/len(snr))
					cats = [0,0,0,0,0,0,0,0,0,0,0,0]
					cats[q*2+ all_genders[all_s.index(sub)]]=1
					cats[6+q*2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]

					x.append(cats)
			violin_parts = plt.violinplot(values[q], [q], points=20, widths=0.3, showmeans=True) #,showmedians=True)
			for pc in violin_parts['bodies']:
				pc.set_facecolor(colors[q])
				pc.set_edgecolor(colors[q])
				pc.set_linewidth(1)
				pc.set_alpha(0.5)
			for partname in ('cbars','cmins','cmaxes','cmeans'):
				vp = violin_parts[partname]
				vp.set_edgecolor(colors[q])
				vp.set_linewidth(1)
		min_y = min(y)
		plt.xticks([0,1,2],["CA","AA","DA"])
		plotted+=1
		
		est = sm.OLS( y,x)
		est2 = est.fit()
		#print("r",est2.summary(), est2.fvalue, est2.f_pvalue)
		fsquared.append(est2.rsquared/(1-est2.rsquared))

		print(scanName)
		#plt.text(1.1,min_y,'\n'.join((r'$f^2=.%s$' % format( est2.rsquared/(1-est2.rsquared),'.3f')[2:] ,  r'$p=.%s$' % format( est2.f_pvalue, '.3f')[2:]))) #, {'size':'14'})
		patch1 = mpatches.Patch(color='none', label=r'$f^2=.%s$' % format( est2.rsquared/(1-est2.rsquared),'.3f')[2:])
		if est2.f_pvalue*7 >.999:
			patch2 = mpatches.Patch(color='none', label=r'$pc>.999$')
		else:
			patch2 = mpatches.Patch(color='none', label=r'$pc=.%s$' % format( est2.f_pvalue*7,'.3f')[2:])
		plt.legend(handles=[patch1, patch2],frameon=False, loc='lower right')
		if  "T" in scanName:
			plt.ylim((0,600))
			if "T2" in scanName:
				plt.legend(handles=[patch1, patch2],frameon=False, loc='upper right')
		elif "Diffusion" in scanName:
			plt.ylim((0,100))
		else:
			plt.ylim((0,30))


		f.tight_layout()
		f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_cat_{scanName}.png")

		t_test= est2.t_test([.5, .5,0,0,-.5,-.5,0,0,0,0,0,0])
		table["CA vs DA"].append( getFormatedText_ttest(t_test, nCA+nDA, 3*7))

		t_test= est2.t_test([0, 0,.5,.5,-.5,-.5,0,0,0,0,0,0])
		table["AA vs DA"].append( getFormatedText_ttest(t_test, nAA+nDA, 3*7))

		t_test= est2.t_test([.5,.5, -.5,-.5,0,0,0,0,0,0,0,0])
		table["CA vs AA"].append( getFormatedText_ttest(t_test, nAA+nCA, 3*7))


	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_cat.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for k, v in table.items():
			writer.writerow(v)
		
	print("max f squared", max(fsquared), np.mean(fsquared)	, np.std(fsquared))
def plotWithinScanMotion():
	perScan=[dict(),dict(),dict(), dict()]
	tipo="within" #within" #"between"
	labels=["FD","Translation","Rotation", "FramewiseThreashold"]
	fsquared=[]
	with open('/space/erebus/1/users/data/scores/_motion_'+tipo+'_scan_FD_output_140.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			#try:
				s=row[0]
				for i in range(len(labels)):
					if labels[i] in row[1]:
						ind =i


				if "T" not in row[2]:
					scan=row[2][:-1]
				else:
					scan=row[2]


				val=float(row[3])

				if val>=0:
					if not scan in perScan[ind]:
						perScan[ind][scan]=[dict(),dict(),dict()]
	
					for a in range(3):
						if not s in perScan[ind][scan][a]:
							perScan[ind][scan][a][s]=[]

					if s in control_subjects:
						perScan[ind][scan][0][s].append(val)
					elif s in anx_subjects:
						perScan[ind][scan][1][s].append(val)
					elif s in dep_subjects:
						perScan[ind][scan][2][s].append(val)
				else:
					print(val)
	#sets={5:["T1","T2","Diffusion","T1 all vnavs - no reacq", "T2 all vnavs - no reacq"],4:["Rest","Gambling","FaceMatching","Conflict"]}
	scans=["T1","T2","Diffusion","Rest","Gambling","FaceMatching","Conflict","T1 all vnavs - no reacq", "T2 all vnavs - no reacq"]
	header=["","T1w","T2w","dMRI","rfMRI","IPT","EPT","EIT","T1w (no vNav)", "T2w (no vNav)"]
	voxelSize=[.8,.8,1.5,2,2,2,2,.8,.8]	
	table=dict()
	table["CA vs AA"] = ["CA vs AA"] 	
	table["CA vs DA"] = ["CA vs DA"]  	
	table["AA vs DA"] = ["AA vs DA"] 
	
	nCA = len(perScan[0]["T1"][0])
	nAA = len(perScan[0]["T1"][1])
	nDA = len(perScan[0]["T1"][2])

	labels=["FD",  "Translation","Rotation"]
	#labels=["Translation"] #,"Rotation"]
	plotted=0
	for i, l in enumerate(labels):
		for k,scanName in enumerate(scans):
			f = plt.figure(plotted, figsize=(5,5))
			plt.title(namesPerScan[scanName])
			categories= perScan[i][scanName]
			print (scanName)
			values =[[],[],[]]
			x=[]
			y=[]
			for q in range(len(values)):
				for sub, snr in categories[q].items():
					if sub in subjects and len(snr)>0:
						if "Translation" in l:
							values[q].append((sum(snr)/(len(snr) * voxelSize[k])))
							y.append(sum(snr)/(len(snr)* voxelSize[k]))
						else:
							values[q].append(sum(snr)/len(snr))
							y.append(sum(snr)/(len(snr)))
						cats = [0,0,0,0,0,0,0,0,0,0,0,0]
						cats[q*2+ all_genders[all_s.index(sub)]]=1
						cats[6+q*2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]
						#cats = [0,0,0]
						#cats[q]=1
						x.append(cats)
				
				print(values)
				violin_parts = plt.violinplot(values[q], [q], points=20, widths=0.3, showmeans=True) #,showmedians=True)
				for pc in violin_parts['bodies']:
					pc.set_facecolor(colors[q])
					pc.set_edgecolor(colors[q])
					pc.set_linewidth(1)
					pc.set_alpha(0.5)

				for partname in ('cbars','cmins','cmaxes','cmeans'):
					vp = violin_parts[partname]
					vp.set_edgecolor(colors[q])
					vp.set_linewidth(1)
			plt.xticks([0,1,2],["CA","AA","DA"])
			plt.ylim(0,.8)
			f.tight_layout()
			
			
			plotted+=1

			print( np.shape(x), np.shape(y))
			est = sm.OLS( y,x)
			est2 = est.fit()
			print(est2.summary())
			fsquared.append(est2.rsquared/(1-est2.rsquared))
			#plt.text(1,2.2,'\n'.join((r'$f^2=%.2f$' % (est2.rsquared/(1-est2.rsquared), ),	r'$p=%.2f$' % (est2.f_pvalue, )))) #, {'size':'14'})
			
			patch1 = mpatches.Patch(color='none', label=r'$f^2=.%s$' % format( est2.rsquared/(1-est2.rsquared),'.3f')[2:])
			if est2.f_pvalue*7 >.999:
				patch2 = mpatches.Patch(color='none', label=r'$pc>.999$')
			else:
				patch2 = mpatches.Patch(color='none', label=r'$pc=.%s$' % format( est2.f_pvalue*7,'.3f')[2:])
			plt.legend(handles=[patch1, patch2],frameon=False, loc='upper right')
			
			print(scanName)
					
			f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_{l}_cat_{scanName}.png")
			t_test= est2.t_test([.5,.5,0, 0,-.5,-.5,0,0,0,0,0,0])
			table["CA vs DA"].append( getFormatedText_ttest(t_test, nCA+nDA, 3*7))

			t_test= est2.t_test([0,0,.5, .5,-.5,-.5,0,0,0,0,0,0])
			table["AA vs DA"].append( getFormatedText_ttest(t_test, nAA+nDA, 3*7))

			t_test= est2.t_test([.5,.5,-.5, -.5,0,0,0,0,0,0,0,0])
			table["CA vs AA"].append( getFormatedText_ttest(t_test, nAA+nCA, 3*7))


	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_within_cat.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for k, v in table.items():
			writer.writerow(v)
	print("max f squared", max(fsquared), np.mean(fsquared)	, np.std(fsquared))

def plotBetweenScanMotion2():

	perScan=[dict(),dict()] #, dict(), dict()]
	tipo="between"
	labels=["Rotation","Translation"]
	fsquared=[]
	with open('/space/erebus/1/users/data/scores/motion_'+tipo+'_scan_FD_output_140.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			try:
				s=row[0]
				for i in range(len(labels)):
					if labels[i] in row[1]:
						ind =i

				if "T" not in row[2]:
					scan=''.join(filter(lambda x: x.isalpha(), row[2]))
				else:
					scan=row[2]
				print(scan)

				val=float(row[3])
				if val>0:
					if not scan in perScan[ind]:
						perScan[ind][scan]=[dict(),dict(),dict()]
	
					for a in range(3):
						if not s in perScan[ind][scan][a]:
							perScan[ind][scan][a][s]=[]

					if s in control_subjects:
						perScan[ind][scan][0][s].append(val)
					elif s in anx_subjects:
						perScan[ind][scan][1][s].append(val)
					elif s in dep_subjects:
						perScan[ind][scan][2][s].append(val)

			except:
				print(row)
	scans=["T1_T2","DiffusionDiffusion","RestRest","GamblingGambling","FaceMatchingFaceMatching","ConflictConflict"]
	header=["","T1w-T2w","dMRI","rfMRI","IPT","EPT","EIT"]
	voxelSize=[.8,1.5,2,2,2,2]	
	table=dict()
	table["CA vs AA"] = ["CA vs AA"] 	
	table["CA vs DA"] = ["CA vs DA"]  	
	table["AA vs DA"] = ["AA vs DA"] 
	labels=["Rotation", "Translation"]
	print(perScan[1])	
	nCA = len(perScan[1]["T1_T2"][0])
	nAA = len(perScan[1]["T1_T2"][1])
	nDA = len(perScan[1]["T1_T2"][2])
	print(nCA, nAA, nDA)	
	plotted=0
	for i,l in enumerate(labels):
		for si, scanName in enumerate(scans):
			f = plt.figure(plotted, figsize=(5,5))
			plt.title(labels_sets[scanName])
			print(i)
			categories= perScan[i][scanName]
			print (scanName)
			values =[[],[],[]]
			x=[]
			y=[]
			for q in range(len(values)):
				for sub, snr in categories[q].items():
					if sub in subjects and len(snr)>0:
						if "Translation" in l:
							values[q].append(sum(snr)/(len(snr) *voxelSize[si]))
							y.append(sum(snr)/(len(snr)* voxelSize[si]))
						else:
							values[q].append(sum(snr)/len(snr))
							y.append(sum(snr)/len(snr))

						cats = [0,0,0,0,0,0,0,0,0,0,0,0]
						cats[q*2+ all_genders[all_s.index(sub)]]=1
						cats[6+q*2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]
						x.append(cats)
				violin_parts =plt.violinplot(values[q], [q], points=20, widths=0.3, showmeans=True) #,showmedians=True)
				for pc in violin_parts['bodies']:
					pc.set_facecolor(colors[q])
					pc.set_edgecolor(colors[q])
					pc.set_linewidth(1)
					pc.set_alpha(0.5)
				for partname in ('cbars','cmins','cmaxes','cmeans'):
					vp = violin_parts[partname]
					vp.set_edgecolor(colors[q])
					vp.set_linewidth(1)

			plt.xticks([0,1,2],["CA","AA","DA"])
			if "T1" in scanName:
				plt.ylim(0,50)
			else:
				plt.ylim(0,20)
			f.tight_layout()
				
			print( np.shape(x), np.shape(y))
			est = sm.OLS( y,x)
			est2 = est.fit()
			fsquared.append(est2.rsquared/(1-est2.rsquared))
			#plt.text(1,40,'\n'.join((r'$f^2=%.2f$' % (est2.rsquared/(1-est2.rsquared), ),	r'$p=%.2f$' % (est2.f_pvalue, )))) #, {'size':'14'})
			patch1 = mpatches.Patch(color='none', label=r'$f^2=.%s$' % format( est2.rsquared/(1-est2.rsquared),'.3f')[2:])
			if est2.f_pvalue*6 >.999:
				patch2 = mpatches.Patch(color='none', label=r'$p>.999$')
			else:
				patch2 = mpatches.Patch(color='none', label=r'$p=.%s$' % format( est2.f_pvalue*6,'.3f')[2:])
			plt.legend(handles=[patch1, patch2],frameon=False, loc='upper right')
			
			print(scanName)
			f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_{l}_cat_{scanName}.png")
			
			plotted+=1
			t_test= est2.t_test([.5,.5,0, 0,-.5,-.5,0,0,0,0,0,0])
			table["CA vs DA"].append( getFormatedText_ttest(t_test, nCA+nDA, 2*6))

			t_test= est2.t_test([0,0,.5, .5,-.5,-.5,0,0,0,0,0,0])
			table["AA vs DA"].append( getFormatedText_ttest(t_test, nAA+nDA, 2*6))

			t_test= est2.t_test([.5,.5,-.5, -.5,0,0,0,0,0,0,0,0])
			table["CA vs AA"].append( getFormatedText_ttest(t_test, nAA+nCA, 2*6))


	plt.plot()
	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_between_cat.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for k, v in table.items():
			writer.writerow(v)

	#print("max f squared", max(fsquared), np.mean(fsquared)	, np.std(fsquared))
def subjectsHistograms():
	objects = ('CA', 'AA', 'DA')
	y_pos = np.arange(len(objects))
	performance = [len(control_subjects),len(anx_subjects), len(dep_subjects)]

	plt.bar(y_pos, performance, .35, align='center', color=['#74c7a5', '#FF8600','#36649E'] )
	plt.xticks(y_pos, objects)
	plt.ylabel('subjects')

	plt.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/histogram.png")
	

def ContinuousScoresHisto():
	subjects, sex, scores = utils.loadBANDAscores(outliers)

	for key, score in scores.items():
		plt.figure(key)
		# example data
		num_bins = 5
		# the histogram of the data
		n, bins, patches = plt.hist(score, num_bins, normed=1, facecolor='blue', alpha=0.5)

	plt.show()

def ContinuousScores():
	print("hola")
	try:
		subjects, sex, scores = utils.loadBANDAscores(outliers)
		print("ha")
		first=True
		for key, score in scores.items():

			if key in ["BIS","BAS","MFQ","SHAPS_CNT"]:
				plt.figure(key)
				# example data
				num_bins = 5
				for i,s in enumerate(score):
					c = colors[0]


					if subjects[i] in control_subjects:
						c=colors[0]
					elif subjects[i] in anx_subjects:
						c=colors[1]
					elif subjects[i] in dep_subjects:
						c=colors[2]

					plt.scatter(i,s, color=c, label=labelGroups[colors.index(c)])

				plt.ylabel(key)
				plt.xlabel("subject")
				plt.xlim(-2,140)
				plt.xticks([1,35,70,105,140])
				if key is "SHAPS_CNT":
					plt.ylabel("SHAPS")
					plt.plot(range(0,140), [2.5]*140, '--', color='black')

				#if first:
				#	first=False
				#	handles, labels = plt.gca().get_legend_handles_labels()
				#	by_label = OrderedDict(zip(labels, handles))
				#	plt.legend(by_label.values(), by_label.keys(),loc='upper left', bbox_to_anchor=(1, 1)) 
				plt.tight_layout()
				plt.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/scores_{key}.svg")
	except Exception  as e:
		print(e.message)

def ContinuousScoresDist():
	print("hola")
	try:
		subjects, sex, scores = utils.loadBANDAscores(outliers)
		print("ha")
		first=True
		for key, score in scores.items():

			if key in ["BIS","BAS","MFQ","SHAPS_CNT"]:
				groupedScores=[[],[],[]]
				plt.figure(key)
				# example data
				num_bins = 5
				mini=1000
				maxi=0
				for i,s in enumerate(score):
					c = colors[0]


					if subjects[i] in control_subjects:
						groupedScores[0].append(s)
					elif subjects[i] in anx_subjects:
						groupedScores[1].append(s)
					elif subjects[i] in dep_subjects:
						groupedScores[2].append(s)
					#plt.scatter(i,s, color=c, label=labelGroups[colors.index(c)])
				for i,g  in enumerate(groupedScores):
					mini=np.minimum(mini, min(g))
					maxi=np.maximum(maxi, max(g))
				for i,g  in enumerate(groupedScores):
					n, bins2= np.histogram(g, 50)
					mu= np.mean(g)
					sigma= np.std(g)
					bins=np.linspace(mini, maxi, 50)
					y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
							np.exp(-0.5 * (1 / sigma * (bins - mu))**2))*len(g)
					plt.plot(bins, y, color=colors[i])
				plt.xlabel(key)
				plt.ylabel("subjects")
				plt.xlim(mini,maxi)
				#plt.xticks([1,35,70,105,140])
				#if key is "SHAPS_CNT":
				#	plt.ylabel("SHAPS")
				#	plt.plot(range(0,140), [2.5]*140, '--', color='black')

				plt.tight_layout()
				plt.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/dist_scores_{key}.svg")
	except Exception  as e:
		print(e.message)

def plotSNRContinuousMeasures():
	snr_perScan=dict()
	rsquared=[]
	#with open('/autofs/space/erebus_001/users/data/scores/new2/snr_avg_output_vivs.csv', 'r') as csvfile:
	with open('/autofs/space/erebus_001/users/data/scores/new/snr_output_newtest.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			try:
				s=row[0]
				if "T" in row[1]:
					scan= row[1]
				else:
					scan=row[1][:-1]
				#print(scan)
				snr=float(row[2])
				if snr>0:
					if not scan in snr_perScan:
						snr_perScan[scan]=[dict(),dict(),dict()]

					for a in range(3):
						if not s in snr_perScan[scan][a]:
							snr_perScan[scan][a][s]=[]
					if s in control_subjects:
						snr_perScan[scan][0][s].append(snr)
					elif s in anx_subjects:
						snr_perScan[scan][1][s].append(snr)
					elif s in dep_subjects:
						snr_perScan[scan][2][s].append(snr)

			except:
				print(row)

	subjects, sex, scores = utils.loadBANDAscores(outliers)
	plotted=0
	print(scores.keys())
	
	table=dict()
	for i, a in enumerate(scores_CSV):
		table[a]=[scores_header_CSV[i]]
	
	for key, score in scores.items():
		if key in scores_CSV:
			print(key)
			for scanName in scansCSV:
				f= plt.figure(plotted, figsize=(5,5))

				categories = snr_perScan[scanName]
				plt.title(namesPerScan[scanName])
				x=[]
				y=[]
				allScores=[]
				for q in range(len(categories)):
					for sub, snr in categories[q].items():
						if sub in subjects and len(snr)>0:
							#try:
							plt.scatter(score[subjects.index(sub)], sum(snr)/len(snr), color=colors[q]) #, label=labelGroups[q]) #,showmedians=True)
							#x.append(score[subjects.index(sub)])
							y.append(sum(snr)/len(snr))
							#except Exception e:
							#	print(e)
							cats = [0,0,0,0,0,0]
							cats[all_genders[all_s.index(sub)]]=1
							cats[2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]
							cats[4+ all_genders[all_s.index(sub)]]=score[subjects.index(sub)]
							allScores.append(score[subjects.index(sub)])
							#print(cats)
							x.append(cats)
				plt.xlabel(key)
				if key is "SHAPS_CNT":
					plt.xlabel("SHAPS")
					plt.plot( [2.5]*600, range(0,600), '--', color='black')
				plotted+=1
				print(len(x))
				

				print( np.shape(x), np.shape(y))
				est = sm.OLS( y,x)
				est2 = est.fit()
				
				t_test= est2.t_test([0, 0,0,0,.5,.5])

				a,b,c = getFormatedText_ttest(t_test,len(y), 4*6)
				plt.legend(handles=[b,c],frameon=False, loc='lower right')
				print(est2.params)	
				if "T1" in scanName:
					plt.ylim(0,600)
				elif "T2" in scanName:
					plt.ylim(0,600)
					plt.legend(handles=[b,c],frameon=False, loc='upper right')
				elif "Diffusion" in scanName:
					plt.ylim(0,100)
				else:	
					plt.ylim(10,35)
					plt.legend(handles=[b,c],frameon=False, loc='upper right')
					#points= x_draw* (est2.params[4]+est2.params[5])/2.0 +( est2.params[0] + est2.params[1])/2.0
				

				slope, intercept, r_value, p_value, std_err = stats.linregress(allScores,y)
				x_draw =  np.array ( range(int(min(allScores)), int(max(allScores))))
				points= x_draw*slope +intercept
				plt.plot(x_draw, points ,'k-' ) 
				
				plt.xlim((min(allScores)-1, max(allScores)+1))	
				print(scanName)
				f.tight_layout()
				f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_continuous_{key}{scanName}.png")
				"""



				slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
				print(key, scanName)
				print("p=%10.3e"%p_value)
				pc= p_value*9*7
				if pc>1:
					print("pc=1")
				else:
					print("pc=%10.3e"% pc)
				print( "r=%10.3e"%r_value**2)
				rsquared.append(r_value**2)
				
				#print(key, scanName,p_value*9*7, r_value**2)
				x_draw =  np.array ( range(int(min(x)), int(max(x))))
				points= x_draw*slope +intercept
				
				plt.plot(x_draw, x_draw*slope + intercept ) #, label='\n'.join((r'$r^2=$%1.0e' % (r_value**2, ), r'$p=$%1.0e' % (p_value, )))) #,  ha='center', va='center', transform=ax.transAxes) #, {'size':'14'})
				#plt.legend(frameon=False)
				
				_,_, text = getFormatedText_regression(p_value, r_value, len(scansCSV)*len(scores_CSV))			
				patch1, patch2,_ = getFormatedText_regression(p_value, r_value, len(scansCSV)*4)			
				table[key].append(text)

				p4lt.legend(handles=[patch1, patch2],frameon=False) #, loc='upper right')
	
				f.tight_layout()
				f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_continuous_{key}{scanName}.png")

				"""
	
	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_scores.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(headerCSV)
		for k, v in table.items():
			writer.writerow(v)
	#print("rsquared max, mean, std", max(rsquared), np.mean(rsquared), np.std(rsquared))

def plotWithinScanMotionContinuousMeasures():
	perScan=[dict(),dict(), dict(), dict()]
	tipo="within" #within" #"between"
	labels=["FD" ,"Rotation","Translation", "FramewiseThreashold"]
	rsquared=[]
	with open('/space/erebus/1/users/data/scores/_motion_'+tipo+'_scan_FD_output_140.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			#try:
				if "vnav" not in  row[2]:
					s=row[0]
					for i in range(len(labels)):
						if labels[i] in row[1]:
							ind =i

					if "T" not in row[2]:
						scan=row[2][:-1]
					else:
						scan=row[2]

					val=float(row[3])
					if not scan in perScan[ind]:
						perScan[ind][scan]=[dict(),dict(),dict()]

					for a in range(3):
						if not s in perScan[ind][scan][a]:
							perScan[ind][scan][a][s]=[]
					if s in control_subjects:
						perScan[ind][scan][0][s].append(val)
					elif s in anx_subjects:
						perScan[ind][scan][1][s].append(val)
					elif s in dep_subjects:
						perScan[ind][scan][2][s].append(val)

			#except:
			#	print(row)

	subjects, sex, scores = utils.loadBANDAscores(outliers)
	labels=["FD","Rotation", "Translation" ]
	plotted=0
	table=dict()
	for i, a in enumerate(scores_CSV):
		table[a]=[scores_header_CSV[i]]
	
	for key, score in scores.items():
		if key in scores_CSV:
			print(key)
			for si, scanName in enumerate( scansCSV):
				for i, l in enumerate(labels):
					categories = perScan[i][scanName]
					print (scanName)
					f = plt.figure(plotted, figsize=(5,5))	
					plt.title(namesPerScan[scanName])
					x=[]
					y=[]
					allScores=[]
					for q in range(len(categories)):
						for sub, snr in categories[q].items():
							if sub in subjects:
								try:
									if len(snr)>0:
										if "Translation" in l:
											plt.scatter(score[subjects.index(sub)], sum(snr)/(len(snr)*voxelSizeCSV[si]), color=colors[q]) #, label=labelGroups[q]) #,showmedians=True)
											y.append(sum(snr)/(len(snr)*voxelSizeCSV[si]) )
										else:
											plt.scatter(score[subjects.index(sub)], sum(snr)/len(snr), color=colors[q]) #, label=labelGroups[q]) #,showmedians=True)
											y.append(sum(snr)/(len(snr)) )
										#x.append(score[subjects.index(sub)])
										cats = [0,0,0,0,0,0]
										cats[all_genders[all_s.index(sub)]]=1
										cats[2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]
										cats[4+ all_genders[all_s.index(sub)]]=score[subjects.index(sub)]
										allScores.append(score[subjects.index(sub)])
										x.append(cats)
								except:
									print(sub)

					
					if "SHAPS" in key:
						plt.xlabel("SHAPS")
						plt.plot( [2.5]*int(max(allScores)+1), range(0,int(max(allScores))+1), '--', color='black')
					else:
						plt.xlabel(key)
	
					if "FD" in l:
						plt.ylim((-.05,2.2))
					elif "Translation" in l:
						plt.ylim((-.05,1))
					else:
						plt.ylim((-.05,1))

					print( np.shape(x), np.shape(y))
					est = sm.OLS( y,x)
					est2 = est.fit()
					
					t_test= est2.t_test([0, 0,0,0,.5,.5])

					a,b,c = getFormatedText_ttest(t_test,len(y), 4*6*2)
					plt.legend(handles=[b,c],frameon=False, loc='upper right')
					print(est2.params)	
					#points= x_draw* (est2.params[4]+est2.params[5])/2.0 +( est2.params[0] + est2.params[1])/2.0
					

					slope, intercept, r_value, p_value, std_err = stats.linregress(allScores,y)
					x_draw =  np.array ( range(int(min(allScores)), int(max(allScores))))
					points= x_draw*slope +intercept
					plt.plot(x_draw, points ,'k-' ) 
					plt.xlim((min(allScores)-1, max(allScores)+1))	
					print(scanName)
					f.tight_layout()
					f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_{l}_continuous_{scanName}_{key}.png")
					plotted+=1
	
					"""f.tight_layout()
					slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
					print(key, scanName)
					print("p=%10.3e"%p_value)
					pc= p_value*9*7
					if pc>1:
						print("pc=1")
					else:
						print("pc=%10.3e"% pc)
					print( "r=%10.3e"%r_value**2)

					rsquared.append(r_value**2)
					x_draw =  np.array ( range(int(min(x)), int(max(x))))
					plt.plot(x_draw, x_draw*slope + intercept ) #, label='\n'.join((r'$r^2=$%1.0e' % (r_value**2, ), r'$p=$%1.0e' % (p_value, )))) #,  ha='center', va='center', transform=ax.transAxes) #, {'size':'14'})
					
					_,_, text = getFormatedText_regression(p_value, r_value, len(scansCSV)*len(scores_CSV))			
					patch1, patch2,_ = getFormatedText_regression(p_value, r_value, len(scansCSV)*4)			
					table[key].append(text)
					
					plt.legend(handles=[patch1, patch2],frameon=False) #, loc='upper right')
					f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_{l}_continuous_{scanName}_{key}.png")
					plotted+=1"""
	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/FD_within_scores.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(headerCSV)
		for k, v in table.items():
			writer.writerow(v)


	#print("rsquared max, mean, std", max(rsquared), np.mean(rsquared), np.std(rsquared))
def plotBetweenScanMotionContinuousMeasures():
	perScan=[dict(),dict(), dict(), dict()]
	tipo="between" #within" #"between"
	labels=["Rotation","Translation"] #,"FD", "FramewiseThreashold"]
	rsquared=[]
	with open('/space/erebus/1/users/data/scores/motion_'+tipo+'_scan_FD_output_140.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			try:
				if "vnav" not in  row[2]:
					s=row[0]
					for i in range(len(labels)):
						if labels[i] in row[1]:
							ind =i

					if "T" not in row[2]:
						scan=''.join(filter(lambda x: x.isalpha(), row[2]))
					else:
						scan=row[2]
					print(scan)

					val=float(row[3])
					if not scan in perScan[ind]:
						perScan[ind][scan]=[dict(),dict(),dict()]

					for a in range(3):
						if not s in perScan[ind][scan][a]:
							perScan[ind][scan][a][s]=[]
					if s in control_subjects:
						perScan[ind][scan][0][s].append(val)
					elif s in anx_subjects:
						perScan[ind][scan][1][s].append(val)
					elif s in dep_subjects:
						perScan[ind][scan][2][s].append(val)

			except:
				print(row)

	subjects, sex, scores = utils.loadBANDAscores(outliers)
	#labels=["FD"]
	plotted=0
	table=dict()
	for i, a in enumerate(scores_CSV):
		table[a]=[scores_header_CSV[i]]
	
	for key, score in scores.items():
		if key in scores_CSV:
			print(key)
			for si , scanName in enumerate( scansBCSV):
				for i, l in enumerate(labels):
					categories = perScan[i][scanName]
					f = plt.figure(plotted, figsize=(5,5))	
					plt.title(labels_sets[scanName])
					x=[]
					y=[]
					allScores=[]
					for q in range(len(categories)):
						for sub, snr in categories[q].items():
							if sub in subjects:
								try:
									if len(snr) >0:
										if "Translation" in l:
											plt.scatter(score[subjects.index(sub)], sum(snr)/(len(snr)*voxelSizeBCSV[si]), color=colors[q]) #, label=labelGroups[q]) #,showmedians=True)
											y.append(sum(snr)/(len(snr) *voxelSizeBCSV[si]))
										else:
											plt.scatter(score[subjects.index(sub)], sum(snr)/(len(snr)), color=colors[q]) #, label=labelGroups[q]) #,showmedians=True)
											y.append(sum(snr)/len(snr))
										cats = [0,0,0,0,0,0]
										cats[all_genders[all_s.index(sub)]]=1
										cats[2+ all_genders[all_s.index(sub)]]=all_ages[all_s.index(sub)]
										cats[4+ all_genders[all_s.index(sub)]]=score[subjects.index(sub)]
										allScores.append(score[subjects.index(sub)])
										x.append(cats)
										#x.append(score[subjects.index(sub)])
								except:
									print(sub)

					#slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
					#pc= p_value*9*7
					#if pc>1:
					#	print("pc=1")
					#else:
					#	print("pc=%10.3e"% pc)
					#print( "r=%10.3e"%r_value**2)
					#rsquared.append(r_value**2)				
					#x_draw =  np.array ( range(int(min(x)), int(max(x))))
					
					#plt.plot(x_draw, x_draw*slope + intercept ) #, label='\n'.join((r'$r^2=$%1.0e' % (r_value**2, ), r'$p=$%1.0e' % (p_value, )))) #,  ha='center', va='center', transform=ax.transAxes) #, {'size':'14'})
					
					if "SHAPS" in key:
						plt.xlabel("SHAPS")
						plt.plot( [2.5]*40, range(0,40), '--', color='black')
					else:
						plt.xlabel(key)
	
					if "T1" in scanName:
						plt.ylim((-.05,50))
					else:
						plt.ylim((-.05,20))

					print( np.shape(x), np.shape(y))
					est = sm.OLS( y,x)
					est2 = est.fit()
					
					t_test= est2.t_test([0, 0,0,0,.5,.5])

					a,b,c = getFormatedText_ttest(t_test,len(y), 4*6*2)
					plt.legend(handles=[b,c],frameon=False, loc='upper right')
					print(est2.params)	
					#points= x_draw* (est2.params[4]+est2.params[5])/2.0 +( est2.params[0] + est2.params[1])/2.0
					

					slope, intercept, r_value, p_value, std_err = stats.linregress(allScores,y)
					x_draw =  np.array ( range(int(min(allScores)), int(max(allScores))))
					points= x_draw*slope +intercept
					plt.plot(x_draw, points ,'k-' ) 
					plt.xlim((min(allScores)-1, max(allScores)+1))	
					print(scanName)
					f.tight_layout()
					#_,_, text = getFormatedText_regression(p_value, r_value, 4*6*2)			
					#patch1, patch2,_ = getFormatedText_regression(p_value, r_value, len(scansCSV)*4)			
					#table[key].append(text)

					#plt.legend(handles=[patch1, patch2],frameon=False) #, loc='upper right')
				
					#plt.xlabel(key)
					#if "T1" in scanName:
					#	plt.ylim((-.1,60))
					#else:
					#	plt.ylim((-.1,20))
	
					#f.tight_layout()
					#if key is "SHAPS_CNT":
					#	plt.xlabel("SHAPS")
					#	plt.plot( [2.5]*60,np.linspace(0,60,60), '--', color='black')

					plotted+=1
					f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/motion_{l}_continuous_{scanName}_{key}.png")

	with open("/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/FD_between_scores.csv", 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(headerBCSV)
		for k, v in table.items():
			writer.writerow(v)

	#print("rsquared max, mean, std", max(rsquared), np.mean(rsquared), np.std(rsquared))
def plotFSThreashold():
	snr_perScan=dict()
	tipo="within" #"between"
	labels=["FramewiseThreashold"]
	with open('/space/erebus/1/users/data/scores/motion_'+tipo+'_scan_FD_output_140.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			try:
				s=row[0]
				if labels[0]  in row[1]:
					if "T" in row[2]:
						scan= row[2]
					else:
						scan=row[2] #[:-1]
					snr=float(row[3])
					if snr>0:
						if not scan in snr_perScan:
							snr_perScan[scan]=[]

					snr_perScan[scan].append(snr)
			except:
				print(row)

	sets={4:["Rest1","Rest2","Rest3", "Rest4", "Gambling1", "Gambling2", "FaceMatching1", "FaceMatching2", "Conflict1", "Conflict2", "Conflict3", "Conflict4"]} #"Gambling","FaceMatching","Conflict"]}
	frames={"Rest1":420,"Rest2":420,"Rest3":420, "Rest4":420, "Gambling1":215, "Gambling2":215, "FaceMatching1":405, "FaceMatching2":405, "Conflict1":280, "Conflict2":280, "Conflict3":280, "Conflict4":280} 

	plotted=0
	f=plt.figure(plotted, figsize=(5,5))
	total=0
	discarded=0
	for sizeFig, scansInFigure  in sets.items():
		for i, scanName in enumerate(scansInFigure):
			values = snr_perScan[scanName]
			violin_parts = plt.violinplot(np.array(values)*100/frames[scanName], [i], points=20, widths=0.3, showmedians=True) #, showextrema=False) #,showmedians=True)
			discarded += sum(np.array(values)*100/frames[scanName]>20)
			total+= len(values)
			f.tight_layout()
			f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/FDThreashold.png")

			plotted+=1

	plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11],["rfMRI1","rfMRI2","rfMRI3", "rfMRI4", "IPT1", "IPT2", "EPT1", "EPT2", "EIT1", "EIT2", "EIT3", "EIT4"])
	#plt.show()
	print(discarded*100/total)
	print(discarded, total)	
	#f.savefig(f"/space/erebus/2/users/vsiless/latex_git/latex/BANDA_MRI_paper/figs/SNR_cat_{figName}.png")
def questionaires():
	caffeine=[]
	antidepresants = []
	hold_still =[]
	money=[]
	face=[]
	conflict=[]
	feeling=[]
	thoughts=[]

	with open('/space/erebus/1/users/data/scores/All_Pre-Post_Scan_Questions.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		for row in spamreader:
			
			if int(row[2].replace("BANDA",""))<141 :
				for i in [12,13,14,15,25,27,28,29,30,31]:
					print(row[i])	
					if  "Yes" in row[i] or len(row[i]) >3:
						row[i]="1"
					if "No" in row[i] or len(row[i])==0:
						row[i]="0"

				if "es" in row[14] or int(row[14]) >0:
					caffeine.append(3)
				elif "es" in row[13] or int(row[13]) >0:
					caffeine.append(2)
				elif "es" in row[12] or int(row[12]) >0:
					caffeine.append(1)
				else:
					caffeine.append(0)
				
				if "es" in row[15] or int(row[15])>0:
					antidepresants.append(1)
				else:
					antidepresants.append(0)

				if "es" in row[25] or int(row[25])>0:
					hold_still.append(1)
				else:
					hold_still.append(0)
				
				money.append(int(float(row[27])))
				face.append(int(float(row[28])))
				conflict.append(int(float(row[29])))
				feeling.append(int(float(row[30])))
				thoughts.append(int(float(row[31])))

	
	print(caffeine)
	hist_caffeine,b = np.histogram(caffeine,4)
	hist_antidepresants,b = np.histogram(antidepresants,4)
	hist_still,b = np.histogram(hold_still,4)
	hist_money,b = np.histogram(money,4)
	hist_face,b = np.histogram(face,4)
	hist_conflict,b = np.histogram(conflict,4)
	hist_feeling,b = np.histogram(feeling,4)
	hist_thoughts,b = np.histogram(thoughts,4)


	print(hold_still, hist_still)
	print(antidepresants, hist_antidepresants)

	level1= np.array([hist_caffeine[0], hist_antidepresants[0], hist_still[0], hist_money[0],  hist_face[0], hist_conflict[0], hist_feeling[0], hist_thoughts[0]]) *100/140.
	level2= np.array([hist_caffeine[1], hist_antidepresants[1], hist_still[1], hist_money[1],  hist_face[1], hist_conflict[1], hist_feeling[1], hist_thoughts[1]]) *100/140.
	level3= np.array([hist_caffeine[2], hist_antidepresants[2], hist_still[2], hist_money[2],  hist_face[2], hist_conflict[2], hist_feeling[2], hist_thoughts[2]]) *100/140.
	level4=np.array( [hist_caffeine[3], hist_antidepresants[3], hist_still[3], hist_money[3],  hist_face[3], hist_conflict[3], hist_feeling[3], hist_thoughts[3]])*100/140.
	print(level1)
	print(level2)
	plt.barh(range(0,8),level4 , left=level1+level2+level3 )
	plt.barh(range(0,8),level3, left=level1+level2)
	plt.barh(range(0,8),level2,  left=level1)
	plt.barh(range(0,8),level1)
	plt.xlim =1.0
	plt.xlabel("Percentage of subjects")
	plt.yticks(range(0,8),["Have you consume any caffeine caffeine in the last  \n (24hrs/10hrs/5hrs/2hrs)?","Have you taken any antidepressants today?  \n (No/Yes)","Did you encounter any difficuilties to hold still? \n (No/Yes) ","How motivated you were to perform the IPT? \n (very little/little/some/very)","How motivated you were to perform the EPT? \n (very little/little/some/very)", "How motivated you were to perfom the EIT? \n (very little/little/some/very)", "How was your mood after the scan? \n (very bad/bad/good/very good)" , "How were your thoughts during resting portions of scan? \n (very unpleasant/unpleasant/pleasant/very pleasant)"])

	# rotate axis labels
	plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

	plt.show()


#subjectsHistograms()
#ContinuousScores()
#ContinuousScoresHisto()
ContinuousScoresDist()
#plotSNRAvg()
#plotSNRContinuousMeasures()

#plotWithinScanMotion()
#plotBetweenScanMotion2()

#plotWithinScanMotionContinuousMeasures()
#plotBetweenScanMotionContinuousMeasures()

#plotFSThreashold()
#questionaires()
#plt.show()

#plotSNRPerScan()
#plt.show()
