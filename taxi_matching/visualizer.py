import shapefile
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from Instance import Instance

def read_file(filename):
	sf = shapefile.Reader(filename)
	return sf

def get_polygons(sf, zone_filter):
	r_shapes = []
	r_records = []
	shapes = sf.shapes()
	records = sf.records()
	for k in range(len(records)):
		shape = shapes[k]
		rec = records[k]
		if rec[5] in zone_filter:
			r_shapes.append(shape)
			r_records.append(rec)
	return r_shapes,r_records 

def get_zones_ids(sf, zone_filter):
	ret = []
	records = sf.records()
	for k in range(len(records)):
		#rec = records[k]
		if records[k][5] in zone_filter:
			# TODO: Esto quedo dependen al orden, ya que el ID empieza desde 1.
			ret.append(k+1)	

	return ret


def visualize_zones():
	filename = 'mygeodata/taxi_zones.shp'	
	sf = read_file(filename)

	zone_filter = ['Manhattan']
	shapes,records = get_polygons(sf, zone_filter)
	zone_filter_ids = get_zones_ids(sf, zone_filter)


	# Plot de shapes.
	for k in range(len(shapes)):
		shape = shapes[k]

		# Plot del polygon.
		x = [i[0] for i in shape.points[:]]
		y = [i[1] for i in shape.points[:]]
		plt.plot(x,y,'b')


def visualize_taxis(inst):
	for pnt in inst.taxis_longlat:
		plt.plot(pnt[0], pnt[1], '.g')

def visualize_paxs(inst):
	for pnt in inst.paxs_longlat:
		plt.plot(pnt[0], pnt[1], '.r')


def main():
	
	filename = 'input/small_0.csv'
	inst = Instance(filename)

	# Visualizamos zonas, pasajeros y taxis.
	visualize_zones()
	visualize_paxs(inst)
	visualize_taxis(inst)

	# Muestra el grafico.
	plt.show()

if __name__ == '__main__':
	main()


