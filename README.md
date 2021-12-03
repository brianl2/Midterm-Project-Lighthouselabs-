# Welcome to our flight prediction midterm project

# --- info about main files in root directory ---

# --- our chosen model ---


# Training:

In order to predict the arrival delays of flights in the first week of january 2020, we trained our model with all available samples from the last week of December 2019 for their proximity in time, as well as all available samples from the first week of January 2019 to introduce variance and prevent overfitting to a single week.

This decision came about through an analysis of the data that showed no decernable trends base on season, but instead ebbs and flows over time. December 2019 therefore gives us a baseline of what is happening in that moment in time prior to our target, while January 2019 provides us with a greater possibility of unexpected weather variance apropriate to that time of year.

# Features:

![Alt text](/data/features.png?raw=true "Features")
    The above image is a graph of the features our model is using, and their correlation with the arrival_delay.

##### arr_time_sin, arr_time_cos, dep_time_sin, dep_time_cos:
- The sine and cosine of arrival time and departure time.
##### fl_num_avg_arr_delay, fl_num_avg_dep_delay, fl_num_avg_late_aircraft_delay, fl_num_avg_taxi_out:
- The historical average arrival delay, departure delay, late aircraft delay, and taxi out time for that flightpath.
##### tail_num_avg_arr_delay, tail_num_avg_dep_delay, tail_num_avg_late_aircraft_delay, tail_num_avg_taxi_out:
- The historical average arrival delay, departure delay, late aircraft delay, and taxi out time for that that specific plane.
##### carrier_avg_arr_delay, carrier_avg_dep_delay, carrier_avg_carrier_delay, 
- The historical average arrival delay, departure delay, and carrier related delays for flights conducted by that carrier.
##### dest_avg_arr_delay, dest_avg_dep_delay, dest_avg_taxi_in:
- The historical average arrival delay, departure delay, and taxi time for flights arriving at the destination airport.
##### origin_avg_arr_delay, origin_avg_dep_delay, origin_avg_taxi_out:
- The historical average arrival delay, departure delay, and taxi time for flights departing from the origin airport.
##### distance:
- The distance of the flight
##### crs_elapsed_time
- The scheduled duration of the flight
##### origin_cold, origin_fog, origin_hail, origin_rain, origin_snow,origin_storm:
- The severity of weather at the origin airport on the day of the flight
##### dest_cold, dest_fog, dest_hail, dest_rain, dest_snow, dest_storm:
- The severity of weather at the destination airport on the day of the flight
##### day_of_week:
- The day of the week, Monday through to Sunday.