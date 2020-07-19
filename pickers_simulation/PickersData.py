import pandas as pd
from collections import defaultdict

class PickersData:
	def __init__(self, number_pickers):
		self.items_per_order = []
		self.picker_times = {}
		self.number_pickers = number_pickers

		# Read items.
		self._read_items_data()
		self._read_picking_times()

	def _read_items_data(self):
		orders_file = 'data/orders.csv'
		data_orders = pd.read_csv(orders_file)

		self.items_per_order = data_orders['NUM_ITEMS']
		self.items_per_order = list(self.items_per_order.dropna())

	def _read_picking_times(self):
		pickings_file = 'data/picking_events.csv'
		data_picking_events = pd.read_csv(pickings_file)
		data_picking_events['TIMESTAMP'] = pd.to_datetime(data_picking_events['TIMESTAMP'])
		pick_times_by_picker = self._all_picks_time(data_picking_events)

		# Apply some filters to reduce noise.
		# 1. For a picker, only consider times shorter thatn 5 minutes.
		# 2. Only keep experienced pickers, i.e., having at least 1k picks.
		#pick_times_by_picker_filtered = {}
		index = 0
		for picker, pick_times in pick_times_by_picker.items():
			pick_times = [time for time in pick_times if time < 300]
			if len(pick_times) > 1000:
				#pick_times_by_picker_filtered[picker] = pick_times
				#self.picker_times[picker] = pick_times
				if index > 0:
					self.picker_times[index] = self.picker_times[0]
				else:
					self.picker_times[index] = pick_times
				index = index + 1
				if (len(self.picker_times) >= self.number_pickers):
					break

	def _all_picks_time(self, picks):
		picks = picks.sort_values('TIMESTAMP')
    
		# Adds Boolean for last pick of each order
		picks['LAST_PICK'] = 0
		indexes = picks.groupby('ORDER_ID').tail(1).index
		picks.loc[indexes,'LAST_PICK'] = 1

		# Adds the difference between consecutive picks
		picks['diff'] = picks.groupby('PICKER_ID')['TIMESTAMP'].diff()

		# Adds Boolean to check if this sample must be thrown (last from that order)
		picks = picks.sort_values(['PICKER_ID', 'TIMESTAMP'])
		picks['THROW_SAMPLE'] = picks['LAST_PICK'].shift(1)
		picks.head()

		# Creates dictionary (picker) -> list of deltas
		picks_times_by_picker = defaultdict(list)
		last_product = None
		for index, row in picks.iterrows():
			if last_product is not None and not pd.isnull(row['diff']) and abs(row['THROW_SAMPLE']) < 1e-8:
				picks_times_by_picker[row['PICKER_ID']].append(row['diff'].total_seconds())
			last_product = row['PRODUCT_ID']
			
		return picks_times_by_picker

