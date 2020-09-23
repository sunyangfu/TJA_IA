# * TJA Doc-level output
# * TJA NLP System Process operative reports to classify a patient's status of approach, fixation and bearing surface
# * @author Sunyang Fu, Sunghwan Sohn, Hilal Maradit Kremers, Walter Kremers, Ahmad Pahlavan Tafti, Elham Sagheb Hossein Pour, Cody Wyles, Meagan Tibbo, David Lewallen, Daniel Berry
 
import csv
import sys
import re
import os
import string
import glob

dir_path = os.path.dirname(os.path.realpath(__file__)).replace('THA/model', '')

def rad_parser(line):
	line = str(line.encode('utf-8'))
	line = line.replace('[', '')
	line = line.replace(']', '')
	line = line.replace('\'', '')
	line = line.replace('}', '')
	# line = line.replace('', '')
	line = line[121:]
	line = line.split('\par')
	line_str = ''
	for m in line:
		line_str += m + '\n' 
	line = line_str
	return line

def read_file_list(indir, deli):
	opt_notes = []
	with open(indir, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=deli)
		for row in spamreader:
			opt_notes += [row]
	return opt_notes

def read_file_dict(indir, k, v, d):
	opt_notes = {}
	with open(indir, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=d)
		for row in spamreader:
			opt_notes[row[k]] = row[v]
	return opt_notes

def apply_rules(k):
    myMap = {}
    maximum = ( '', 0 ) # (occurring element, occurrences)
    for n in k:
        if n in myMap: myMap[n] += 1
        else: myMap[n] = 1
        # Keep track of maximum on the go
        if myMap[n] > maximum[1]: maximum = (n,myMap[n])
    return maximum

def negation_exclusion(sent):
	sent = sent.split('"')[1]
	tokens = sent.lower().split(' ')
	for t in tokens:
		if "no:" == t or "no." == t:
			return True
	return False


def run_eval_approach(indir, outdir, sys):
	if sys == '0':
		deli = '/'
	else:
		deli = '\\'
	dir_list = indir+deli+'*.ann'
	l = glob.glob(dir_list)
	output = []
	with open(dir_path+outdir+deli+'doc_level_approach.csv', 'w') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='|')
		for d in l:
			fxt = ''
			fname = d.split(deli)[-1]
			norms = []
			ann_list = read_file_list(d,'\t')
			for row in ann_list:
				if len(row) == 11:
					continue
				certainty = row[6]
				status = row[7]
				exp = row[8]
				norm = row[9]
				sent = row[-1]
				isExl = False
				if 'Negated' in certainty:
					isExl = negation_exclusion(sent)
				if isExl:
					certainty = 'Possible'
				if ('Positive' in certainty or 'Possible' in certainty) and 'Present' in status and 'Patient' in exp:
					#Direct
					if 'anterolateral' in norm:
						norms += ['ANTERIOR']
					if 'anterior' in norm:
						norms += ['DirectAnterior']
					if 'posterior' in norm:
						norms += ['Posterior']

			fxt = apply_rules(norms)
			spamwriter.writerow([fname, fxt[0]])

def run_eval_bearing(indir, outdir, sys):
	if sys == '0':
		deli = '/'
	else:
		deli = '\\'
	dir_list = indir+deli+'*.ann'
	l = glob.glob(dir_list)
	output = []
	with open(dir_path+outdir+deli+'doc_level_bearing.csv', 'w') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='|')
		for d in l:
			fname = d.split(deli)[-1]
			fxt = ''
			isDirectMetalonPoly = False
			isDirectCeramiconPoly = False
			isDirectMetalonMetal = False
			isDirectCeramiconCeramic = False
			isPoly = False
			isMetal = False
			isCeramic = False
			isPolybrand = False
			isHead = False
			metalCounter, ceramicCounter = 0, 0

			ann_list = read_file_list(d,'\t')

			for row in ann_list:
				if len(row) == 11:
					continue
				certainty = row[6]
				status = row[7]
				exp = row[8]
				norm = row[9]
				sent = row[-1]
				isExl = False
				if 'Negated' in certainty:
					isExl = negation_exclusion(sent)
				if isExl:
					certainty = 'Possible'				
				if ('Positive' in certainty or 'Possible' in certainty) and 'Present' in status and 'Patient' in exp:
					#Direct
					if 'di_meta-on-poly' in norm:
						isDirectMetalonPoly = True
					if 'di_ceramic-on-poly' in norm:
						isDirectCeramiconPoly = True
					if 'di_metal-on-metal' in norm:
						isDirectMetalonMetal = True
					if 'di_ceramic-on-ceramic' in norm:
						isDirectCeramiconCeramic = True
					#Indirect
					if 'indi_poly' in norm:
						isPoly = True
					if 'indi_metal' in norm:
						isMetal = True
						metalCounter += 1
					if 'indi_ceramic' in norm:
						isCeramic = True
						ceramicCounter += 1
					if 'indi_poly_brand' in norm:
						isPolybrand = True
					if 'indi_head' in norm:
						isHead = True
			if isDirectMetalonPoly:
				fxt = "DirectMetalonPoly"
			elif isDirectMetalonMetal: 
				fxt = "DirectMetalonMetal"
			elif isDirectCeramiconCeramic:
				fxt = "DirectCeramiconCeramic"
			elif isDirectCeramiconPoly:
				fxt = "DirectCeramiconPoly"
			elif isPoly:
				if (isMetal and not isCeramic):
					fxt = "InDirectMetalonPoly"
				elif (not isMetal and isCeramic):
					fxt = "InDirectCeramiconPoly"
				elif (ceramicCounter>=2 and (ceramicCounter-metalCounter)>=1):
					fxt = "InDirectCeramiconPoly"
				elif (isMetal and isCeramic):
					fxt = "InDirectMetalonPoly"
				elif (not isMetal and not isCeramic and isHead):
					fxt = "InDirectMetalonPoly"
				else: 
					fxt = "InDirectMetalonPoly"
			elif isPolybrand:
				if (isMetal and not isCeramic):
					fxt = "InDirectMetalonPoly"
				elif (not isMetal and isCeramic):
					fxt = "InDirectCeramiconPoly"
				elif (isMetal and isCeramic):
					fxt = "InDirectMetalonPoly"
				elif (not isMetal and not isCeramic and isHead):
					fxt = "InDirectMetalonPoly"
				else: 
					fxt = "InDirectMetalonPoly"		
			elif isMetal:
				fxt = "InDirectMetalonMetal"
			elif isCeramic: 
				fxt = "InDirectCeramiconCeramic"
			elif isHead:
				fxt = "InDirectMetalonPoly"
			else:
				fxt = "InDirectMetalonPoly"
			spamwriter.writerow([fname, fxt])

def run_eval_fixation(indir, outdir, sys):
	if sys == '0':
		deli = '/'
	else:
		deli = '\\'
	dir_list = indir+deli+'*.ann'
	l = glob.glob(dir_list)
	output = []
	with open(dir_path+outdir+deli+'doc_level_fixation.csv', 'w') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='|')
		for d in l:
			fname = d.split(deli)[-1]
			isDirectCemented = False
			isDirectHybrid = False
			isDirectRHybrid = False
			isDirectUnCemented = False
			isCemented = False
			isHybrid = False
			isRHybrid = False
			isUnCemented = False
			isShell = False
			isNegShell = False
			isStem = False
			isNegStem = False
			isCement = False
			isLiner = False
			sentIntShell, sentIntStem, sentIntNoShell, sentIntNoStem, sentIntCement = [],[],[],[],[]
			ann_list = read_file_list(d,'\t')
			for row in ann_list:
				certainty = row[6]
				status = row[7]
				exp = row[8]
				norm = row[9]
				sent = row[-1]
				isExl = False
				if 'Negated' in certainty:
					isExl = negation_exclusion(sent)
				if isExl:
					certainty = 'Possible'				
				if len(row) == 11:
					continue
				try:
					sentid = int(row[12].split(':')[-1].replace('"', ''))
				except:
					sentid = -1
				if ('Positive' in certainty or 'Possible' in certainty) and 'Present' in status and 'Patient' in exp:
					#Direct
					if 'di_cement' in norm:
						isDirectCemented = True
					if 'di_uncement' in norm:
						isDirectUnCemented = True
					if 'di_hybrid' in norm:
						isDirectHybrid = True
					if 'di_rehybrid' in norm:
						isDirectRHybrid = True
					#Indirect
					if 'shell' in norm:
						isShell = True
						sentIntShell += [sentid]
					if 'stem' in norm:
						isStem = True
						sentIntStem += [sentid]
					if 'cement' in norm:
						isCement = True
						sentIntCement += [sentid]
					if 'stem-neg' in norm:
						isNegStem = True
						isStem = False
						sentIntNoStem += [sentid]
					if 'shell-neg' in norm:
						isNegShell = True
						isShell = False
						sentIntNoShell += [sentid]
					if 'liner' in norm:
						isLiner = True
						sentIntNoShell += [sentid]

			if(isStem and isCement):			
				for i in sentIntStem:
					for j in  sentIntCement:
						m = j - i
						if (m == 0 or m == 1):
							isHybrid = True

			if(isNegShell and isCement):
				# for i in sentIntNoShell:
				# 	for j in sentIntCement:
						# int m = j - i
				isHybrid = True
				isRHybrid = False


			if((isNegShell or not isShell) and (isNegStem or not isStem)):
				isUnCemented = True
			
			if(isHybrid and isRHybrid):
				isCemented = True
				isHybrid = False
				isRHybrid = False
			
			if(not isHybrid and  not isRHybrid and  not isCemented):
				isUnCemented = True
			
			if (isRHybrid and isCement):
				isRHybrid = False
				isCemented = True
			
			cnt1, cnt2 = 0, 0
			if isDirectCemented:
				cnt1 += 1
			if isDirectHybrid:
				cnt1 += 1
			if isDirectRHybrid:
				cnt1 += 1
			if isDirectUnCemented:
				cnt1 += 1
			# if isCemented:
			# 	cnt2 += 1
			# if isHybrid:
			# 	cnt2 += 1
			# if isRHybrid:
			# 	cnt2 += 1
			# if isUnCemented:
			# 	cnt2 += 1
			if (cnt1 > 1): 
				print ("Check direct conflict fixation: ", fname)
			
			fxt = ""
			if(isDirectUnCemented): 
				fxt = "UNCEMENTED"
			elif(isDirectHybrid): 
				fxt = "HYBRID"
			elif(isDirectRHybrid): 
				fxt = "RHYBRID"
			elif(isDirectCemented):
				fxt = "CEMENTED"
			else:
				if(isLiner and isHybrid):
					fxt = "HYBRID"
				elif(isLiner):
					 fxt = "UNCEMENTED"
				elif(isHybrid): 
					fxt = "HYBRID"
				elif(isCemented): 
					fxt = "CEMENTED"
				elif(isRHybrid):
					fxt = "RHYBRID"
				elif(isUnCemented):
					fxt = "UNCEMENTED"
				# else:
				# 	print("NO fixation Check:" 
				# 			 + DELIM + date)
			spamwriter.writerow([fname, fxt])

def main():
	args = sys.argv[1:]
	run_eval_bearing(args[0]+'bearing', args[1], args[2])
	run_eval_fixation(args[0]+'fixation', args[1], args[2])
	run_eval_approach(args[0]+'approach', args[1], args[2])
	print ('Process Finished.')

if __name__== "__main__":
	main()





