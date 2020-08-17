import os
import config
os.chdir(config.path)
import pandas as pd
import numpy as np
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Import
laps = pd.read_csv('lap_times.csv')
laps.drop(columns = ['time'], inplace = True)

races = pd.read_csv('races.csv')
races = races[['raceId', 'year', 'round', 'name']]

drivers = pd.read_csv('drivers.csv')
drivers['pilot'] = drivers['forename'] + " " + drivers['surname']
drivers = drivers[['driverId', 'pilot']]

results = pd.read_csv('results.csv')
results = results.merge(races, on = 'raceId', how = 'left')
results = results[results['year'] > 1995]
results = results[['raceId', 'driverId', 'constructorId', 'position']]
results.columns = ['raceId', 'driverId', 'constructorId', 'fin_position']
results.drop_duplicates(inplace = True)

constructors = pd.read_csv('constructors.csv')
constructors = constructors[['constructorId', 'name']]
constructors.columns = ['constructorId', 'constructor_name']

# Check data level
laps.groupby(['raceId', 'driverId', 'lap']).ngroups == laps.shape[0]
races['raceId'].nunique() == races.shape[0]
drivers['driverId'].nunique() == drivers.shape[0]
results.groupby(['raceId', 'driverId']).ngroups == results.shape[0]
constructors['constructorId'].nunique() == constructors.shape[0]

# Merge
laps = laps.merge(races, on = 'raceId', how = 'left')
laps = laps.merge(drivers, on = 'driverId', how = 'left')
laps = laps.merge(results, on = ['raceId', 'driverId'], how = 'left')
laps = laps.merge(constructors, on = 'constructorId', how = 'left')

# Create unique ID for each lap
laps2 = laps[laps['fin_position'] == "1"]
laps2.groupby(['year', 'round', 'lap']).ngroups == laps2.shape[0]
laps2.sort_values(['year', 'round', 'lap'], inplace = True)
laps2.reset_index(inplace = True)
laps2['lap_id'] = laps2.index
laps2['lap_id'] = laps2['lap_id'] + 1
laps2['lap_id'].nunique() == laps2.shape[0]
laps2 = laps2[['year', 'round', 'lap', 'lap_id']]
laps = laps.merge(laps2, on = ['year', 'round', 'lap'], how = 'left')

# Normalize lap times
laps['seconds'] = laps['milliseconds']/1000
laps['seconds'].describe()
laps = laps[laps['seconds'] < 600]
laps['worst_time'] = laps.groupby('lap_id')['seconds'].transform(np.max)
laps['best_time'] = laps.groupby('lap_id')['seconds'].transform(np.min)
laps['temp1'] = -laps['seconds'] + 600
laps['temp2'] = -laps['worst_time'] + 600
laps['temp3'] = -laps['best_time'] + 600
laps['std_time'] = (laps['temp1'] - laps['temp2'])/(laps['temp3'] - laps['temp2'])
laps['std_time'].describe()

# Clean up
laps.drop(columns = ['temp1', 'temp2', 'temp3'], inplace = True)

# Export
laps.sort_values('lap_id', inplace = True)
laps.to_excel('laps_cleaned.xlsx', index = False)

###END###