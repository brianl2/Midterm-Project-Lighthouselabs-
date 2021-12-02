# Welcome to our flight prediction midterm project

# --- info about main files in root directory ---

# --- our chosen model ---

# --- image of our features graph ---

# Training:

In order to predict the arrival delays of flights in the first week of january 2020, we trained our model with all available samples from the last week of December 2019 for their proximity in time, as well as all available samples from the first week of January 2019 to introduce variance and prevent overfitting to a single week.

This decision came about through an analysis of the data that showed no decernable trends base on season, but instead ebbs and flows over time. December 2019 therefore gives us a baseline of what is happening in that moment in time prior to our target, while January 2019 provides us with a greater possibility of variance that happens within the target time, making our model more robust.