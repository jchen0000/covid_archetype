# import shannon_entropy_by_lab
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import datetime
from matplotlib.colors import LogNorm
import glob
import os
import seaborn as sns



# Run Shannon Entropy code
def shannon_entropy_by_lab(df):
    """
    Calculates the shannon entropy for a lab over time
    df: a dataframe containing three components:
    lab_name = column that identifies the name of lab
    order_date = date time column in format %Y%m%d
    hour_order = categorical variable defining one hour block lab is ordered in. Can be engineered from date/time ordered
    returns a dataframe containing the date and entropy for that day
    """
    names = df.groupby("NAME")
    lab_name = df['NAME'].unique()[0]
    lab_name = lab_name[:-6]

    # get groups for each anchor day
    anchor_days = df.groupby("anchor_day")
    for k in range(len(names)):
        name = names.get_group((list(names.groups)[k]))
        anchor_days = name.groupby("anchor_day")
        # list to store value for each day
        shannon_entropy_by_day = []
        total_entropy = []
        name_list = []
        # loop through each anchor day
        for i in range(len(anchor_days)):
            # grab day we are analyzing
            day = anchor_days.get_group((list(anchor_days.groups)[i]))
            # get counts for the anchor day when the labs were ordered
            values_day = day.anchor_day.value_counts()
            # get total labs for the day
            total_orders_per_lab = len(df.index)
            # accumulating value (sum of p * plogp for each hour)
            shannon_entropy = 0
            # look through each anchor day
            for j in values_day:
                # probability for that hour
                probability = j / total_orders_per_lab
                log = np.log(probability)
                # entropy
                entropy = -np.log(probability) * probability
                # append entropy for that day
                total_entropy.append(entropy)
        # get unique list for days
        days = np.unique(df.anchor_day).reshape(len(np.unique(df.anchor_day)), 1)

        # create a result df. This will contain two columns. Date and shannon entropy for that day
        results_df = pd.DataFrame(list(zip(days.ravel(), total_entropy)), columns=['Anchor_days', lab_name])
        return results_df




if __name__ == '__main__':
    # load & filter labs data
    data_dictionary_file = r'meta\var_dictionary_updated_2022.1.19_BW_4.xlsx'
    xl = pd.ExcelFile(data_dictionary_file)
    data_dir = r'\\prometheus.neuro.columbia.edu\NeurocriticalCare\data\Projects\32_COVID_Archetype_data\labs_btwn_vis\\'

   # Load covid positive patient data
    data_dir2 = r'\\prometheus.neuro.columbia.edu\NeurocriticalCare\data\Projects\32_COVID_Archetype_data\\'
    pat_cov = 'raw_cov.csv'
    pat_vis = 'raw_vis.csv'
    pat_cov_data = pd.read_csv(data_dir2 + pat_cov, low_memory=False)
    pat_vis_data = pd.read_csv(data_dir2 + pat_vis, low_memory=False)

    # Filter the cov patient data
    pat_vis_data = pat_vis_data[['PAT_ID', 'DEPARTMENT_NAME', 'HOSP_ADMSN_TIME', 'INP_ADM_DATE', 'HOSP_DISCH_TIME']]
    pat_cov_data = pat_cov_data[pat_cov_data['ORD_VALUE'].isin(['Detected', 'Detected..', 'DETECTED'])]
    pat_cov_data = pat_cov_data.rename(columns={'ORD_VALUE': 'cov_test'})
    pat_cov_data = pat_cov_data[['PAT_ID', 'cov_test', 'RESULT_TIME']]

    # Merge cov patient data with lab data
    pat_cov_pos_vis = pd.merge(pat_vis_data, pat_cov_data, how='inner', on='PAT_ID')
    pat_cov_pos_vis = pat_cov_pos_vis[(pat_cov_pos_vis['RESULT_TIME'] >= pat_cov_pos_vis['INP_ADM_DATE']) & (pat_cov_pos_vis['RESULT_TIME'] <= pat_cov_pos_vis['HOSP_DISCH_TIME'])]
    pat_cov_pos_vis.sort_values('RESULT_TIME', inplace=True)
    pat_unique_visits = pat_cov_pos_vis.groupby(['PAT_ID']).first().reset_index()

    # Filter data included in var_dictionary file
    notes_data_dictionary = pd.read_excel(data_dictionary_file, sheet_name='Notes')
    stats_all = pd.DataFrame([])
    stats_all_all_pts_mean = pd.DataFrame([])
    notes_data_dictionary['Worksheet'] = notes_data_dictionary['Worksheet'].str.strip()
    data_to_cluster = pd.DataFrame([])

    df = pd.DataFrame([])
    pd_se_lab_all = pd.DataFrame([])
    lab_names_ytick = []

    #for sname in test_data:
    for sname in xl.sheet_names:
        if 'Notes' in sname:
            print(sname)
            continue
        # missing admn time & discharge time
        if 'total protein' in sname:
            print(sname)
            continue
        # empty dataset
        if 'totalprotein'in sname:
            print(sname)
            continue
        if np.sum(notes_data_dictionary['Worksheet'] == sname.strip()) > 0:
            print(sname)
            # print(notes_data_dictionary.loc[notes_data_dictionary['Worksheet'] == sname,'combine'])
            if ~ pd.isna(notes_data_dictionary.loc[notes_data_dictionary['Worksheet'] == sname.strip(), 'variable name']).any():
                print(notes_data_dictionary.loc[notes_data_dictionary['Worksheet'] == sname.strip(), 'variable name'])
                varname = notes_data_dictionary.loc[notes_data_dictionary['Worksheet'] == sname.strip(), 'variable name'].values[0]
            else:
                varname = sname.strip()
        else:
            varname = sname.strip()

        # get only the included data
        sname_data_dictionary = pd.read_excel(data_dictionary_file, sheet_name=sname)
        sname_data_dictionary = sname_data_dictionary.rename(columns={'include': 'Include', 'incldue': 'Include'})
        sname_data_dictionary = sname_data_dictionary[sname_data_dictionary['Include'] == 1]
        sname_data_dictionary.keys()
        lab_data = pd.read_csv(data_dir + sname + '.csv', encoding='cp1252')

        if len(lab_data) == 0:
            continue
        lab_data_filt = lab_data.loc[(lab_data['NAME'].isin(sname_data_dictionary['NAME'])) & (
            lab_data['description'].isin(sname_data_dictionary['description']))]

        # filter data if it is in pat_cov_pos_vis
        pat_unique_visits = pat_unique_visits[['PAT_ID', 'INP_ADM_DATE']]

        lab_cov_pos = pd.merge(lab_data_filt, pat_unique_visits, how='inner', on='PAT_ID')
        try:
            if varname == 'totalProtein' :
                lab_cov_pos = lab_cov_pos[(lab_cov_pos['RESULT_TIME'] >= lab_cov_pos['INP_ADM_DATE'])]
            else:
                lab_cov_pos = lab_cov_pos[(lab_cov_pos['RESULT_TIME'] >= lab_cov_pos['INP_ADM_DATE']) &
                                          (lab_cov_pos['RESULT_TIME'] <= lab_cov_pos['HOSP_DISCH_TIME'])]
        except:
            lab_cov_pos = lab_cov_pos[(lab_cov_pos['RESULT_TIME'] >= lab_cov_pos['INP_ADM_DATE']) &
                                      (lab_cov_pos['RESULT_TIME'] <= lab_cov_pos['HOSP_DISCH_TIME'])]
            lab_cov_pos = lab_cov_pos.rename(columns={'pat_mrn_id': 'IDENTITY_ID'})

        if len(lab_cov_pos) == 0:
            continue
        lab_cov_pos.loc[lab_cov_pos['ORD_NUM_VALUE'] > 9999, 'ORD_NUM_VALUE'] = np.nan

        # Anchor day
        day1 = pd.to_datetime(lab_cov_pos['HOSP_ADMSN_TIME']).dt.date
        day2 = pd.to_datetime(lab_cov_pos['ordering_date']).dt.date
        anchor_day = day2 - day1
        anchor_day = anchor_day/(pd.offsets.Day(1))
        anchor_day = anchor_day.fillna(-1) # converts nans to -1
        anchor_day = anchor_day.astype(int) # converts to integers

        # Merge dataset with anchor day
        lab_cov_pos['anchor_day'] = anchor_day
        df = lab_cov_pos[lab_cov_pos['anchor_day'] > -1]
        se_lab = shannon_entropy_by_lab(df)
        se_lab = se_lab.set_index('Anchor_days')
        if len(pd_se_lab_all) == 0:
            pd_se_lab_all = se_lab
        else:
            pd_se_lab_all = pd_se_lab_all.join(se_lab, on=['Anchor_days'], how='left', lsuffix='left', rsuffix='right')
        lab_names_ytick.append(sname)

    # Plot entropy heatmap
    pd_se_lab_all = pd_se_lab_all.reset_index()
    ax = plt.gca()
    data_to_plot = pd_se_lab_all.loc[:, pd_se_lab_all.columns[3:]]
    fig = ax.imshow(data_to_plot.to_numpy().astype('float').T, aspect=5.8)  # delete the first row
    ax.set_yticks(np.arange(0, len(data_to_plot.columns)), data_to_plot.columns)  # delete the first 2 columns
    plt.show()
    plt.colorbar(fig, ax=ax)

