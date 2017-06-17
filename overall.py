import MySQLdb
import numpy
import scipy.stats as stats

db = MySQLdb.connect(host = "bm185s-mysql.ucsd.edu", user = "bm185saa", passwd = "Spi95kes", db = "bm185saa_db") ## REMEMBER TO REDACT PASSWORD
c = db.cursor()

finalouts = []
finalstats = []

c.execute("SELECT * from final_microarray;")

first = True;
out = open('overallcorrel63.txt', 'w')


##normalize data.  This allows for direct prediction between variables of different units
for i in range(c.rowcount):
        a = list(c.fetchone())
        values = []
        for entry in a[1:]:
                values.append(float(entry))
        mean = numpy.mean(values)
        stdev = numpy.std(values)

        for p, entry in enumerate(values):
                values[p] -= mean
                values[p] /= stdev
				
	for i, _j in enumerate(a):
		if i > 0:
			a[i] = str(values[i-1])
		else:
			a[i] = str(a[i])
				
        finalouts.append(a)
	finalstats.append([mean, stdev])
	if first:
		first = False
		
c.execute("SELECT patient, survival FROM outcomes;")

finalcompare = []
finalpat = []

for i in range(c.rowcount):
		a = list(c.fetchone())
		finalcompare.append(int(a[1]))
		finalpat.append(a[0])


def abstu(x):
        return abs(x[5])


for testval in range(1):

	tuplesorter = []
	findata = []

	for i in range(len(finalouts)):
		tuplesorter.append([])
		for x in range(1, len(finalouts[i])):
			#if x == testval:
				#continue;
			tuplesorter[i].append([float(finalouts[i][x]), finalcompare[x-1]])
		tuplesorter[i].sort(key= lambda x:x[1])

		exp = []
		life = []

		for q in tuplesorter[i]:
			exp.append(q[0])
			life.append(q[1])

		slope, intercept = numpy.polyfit(exp, life, 1)
		pearsonc = stats.pearsonr(exp, life)

		findata.append([finalouts[i][0], slope, intercept, finalstats[i][0], finalstats[i][1], pearsonc[0]])


	acfindata = sorted(findata, key=abstu, reverse=True)


	##testing data
	
	maxrankval = 0
	for i in acfindata:
		if abstu(i) > 0.63:
			maxrankval += 1
		else:
			break
	


	consensus = []

	for rankval in range(maxrankval):
		#print rankval
		inputstr = ("select * from final_microarray where name = '" + acfindata[rankval][0] + "';")

		c.execute(inputstr)

		for r in range(c.rowcount):
					
			a = c.fetchone()
			for l, x in enumerate(a[1:]):
				if rankval == 0:
					consensus.append(0)
				normal = (x - acfindata[rankval][3]) / acfindata[rankval][4]
				#print x, (acfindata[rankval][1]*normal+intercept)
				consensus[l] += (acfindata[rankval][1]*normal+intercept)

	for num, line in enumerate(consensus):

		consensus[num] /= float(maxrankval)

		#if num == testval:
		#out.write(finalpat[num] + '\n')
	for i in range(maxrankval):
		out.write(acfindata[i][0] + '\t' + str(acfindata[i][5]) + '\n')
