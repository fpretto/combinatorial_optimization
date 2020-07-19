
class Instance:
	def __init__(self, filename):
		self.n = 0
		self.taxis_longlat = []
		self.paxs_longlat = []
		self.paxs_trip_dist = []
		self.paxs_tot_fare = []
		self.dist_matrix = []
		self.var_idx = {}
		self._read_instance(filename)

	def _read_instance(self, filename):
		f = open(filename, 'r')

		# number of taxis/paxs
		line = f.readline()
		self.n = int(line)

		# read taxis info.
		for i in range(self.n):
			line = f.readline().split(',')
			point = (float(line[0]), float(line[1])) 
			self.taxis_longlat.append(point)

		# read paxs info.
		for i in range(self.n):
			line = f.readline().split(',')
			point = (float(line[0]), float(line[1]))
			self.paxs_longlat.append(point)
			self.paxs_trip_dist.append(round(float(line[2]),2))
			self.paxs_tot_fare.append(float(line[3]))

		#print(self.taxis_longlat)
		#print(self.paxs_longlat)
		#print(self.paxs_trip_dist)
		#print(self.paxs_tot_fare)

		# read distance matrix. 
		for i in range(self.n):
			line = [round(float(i),2) for i in f.readline().split(',')]
			self.dist_matrix.append(line)

		#for i in range(self.n):
		#	s = ''
		#	for j in range(self.n):
		#		s += str(self.dist_matrix[i][j]) + ' '
		#	print(s)
				
		f.close()

