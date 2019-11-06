import pandas as pd

# ======================================================================================================================
"""
Evaluation of wet-bulb data from Changi
"""
# ======================================================================================================================
wet_bulb_data = pd.read_csv(
            'data/changi_wet-bulb/wet-bulb-temperature-hourly.csv',
            index_col=1
        )

overall_mean = wet_bulb_data['wet_bulb_temperature'].mean()

hours_of_a_day = list(range(1, 25))
hourly_means_dict = {}
for hour in hours_of_a_day:
    hourly_means_dict[hour] = wet_bulb_data['wet_bulb_temperature'][hour].mean()
hourly_means_df = pd.Series(
            data=hourly_means_dict,
            index=hourly_means_dict.keys()
        )

print(wet_bulb_data)
print(overall_mean)
print(hourly_means_df)