import pandas as pd
import matplotlib as plt

def shannon_entropy_by_lab(df, lab_name):
    """
    Calculates the shannon entropy for a lab over time
    df: a dataframe containing three components:
    lab_name = column that identifies the name of lab
    order_date = date time column in format %Y%m%d
    hour_order = categorical variable defining one hour block lab is ordered in. Can be engineered from date/time ordered
    returns a dataframe containing the date and entropy for that day
    """
    # filter for specific lab you are analyzing
    df = df[df["lab_name"]==lab_name]
    # get groups for each individual day
    days = df.groupby("order_date")
    # list to store value for each day
    shannon_entropy_by_day = []
    # loop through each day
    for i in range(len(days)):
        # grab day we are analyzing
        day = days.get_group((list(days.groups)[i]))
        # get counts for the hours the labs were ordered
        values_day = day.hour_ordered.value_counts()
        # get total labs for the day
        total_labs_that_day = sum(values_day)
        # accumulating value (sum of p * plogp for each hour)
        shannon_entropy = 0
        # look through each hour
        for j in values_day:
            # probability for that hour
            probability = j/total_labs_that_day
            # entropy
            entropy = -np.log(probability) * probability
            # add to total for the day. max will be approx 3.178
            shannon_entropy = shannon_entropy+ entropy
        # add entropy for the day to list
        shannon_entropy_by_day.append(shannon_entropy)
    # get unique list for days
    days = np.unique(df.order_date)
    # create a result df. This will contain two columns. Date and shannon entropy for that day
    results_df = pd.DataFrame(list(zip(days, average_surprisal_by_day)),
               columns =['Date', 'Entropy'])
    # matplot of results over time
    plt.plot(results_df.Date, results_df.Entropy)
    plt.title(label="Entropy of "+lab_name+" Over Time")
    return results_df