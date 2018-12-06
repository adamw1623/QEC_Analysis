import os
import numpy as np
import pandas as pd
#os.chdir("./src")
import seeking_alpha_processor as sap
import sentiment_analysis_watson as sa


# =============================================================================
#               Create workable csv from bloomberg data
# old_csv_path = ""
# new_csv_path = ""
# bl.CSVconverter(old_path,new_path,0) #0 means no dates to replace/correct
# =============================================================================

#Use complete paths
aggregate_output_path = "C:/Users/Adam/Documents/Trading/Purple Power/Initial_Runs/output.csv"
sentieo_folder_path = "C:/Users/Adam/Documents/Trading/Purple Power/Initial_Runs/Seeking_Alpha"
trans_org_path = "C:/Users/Adam/Documents/Trading/Purple Power/Initial_Runs/transcript_organization.xlsx"
word_list_path = "C:/Users/Adam/Documents/Trading/Purple Power/Initial_Runs/henry_word_list.csv"
corr_output_path = "C:/Users/Adam/Documents/Trading/Purple Power/Initial_Runs/correlations.csv"

#read in word list
word_list = pd.read_csv(word_list_path)
pos_list = word_list.iloc[:, 0].dropna()
neg_list = word_list.iloc[:, 1].dropna()

#read in trans_org
org_df = pd.read_excel(trans_org_path)
# Create dataframe from Sentieo data
sentieo = sap.CreateDataframe(sentieo_folder_path, org_df)
print("Done Processing, Calculating NLP ...")
sentieo["CEOScore"]= sa.ColumnScoring(sentieo.CEO_Text)
sentieo["AnalystScore"]= sa.ColumnScoring(sentieo.Analyst_Text)
sentieo["OtherExecScore"]= sa.ColumnScoring(sentieo.Other_Exec_Text)
sentieo["CEO_Word_Count"] = sa.WordCounting(sentieo.CEO_Text)
sentieo["Analyst_Word_Count"] = sa.WordCounting(sentieo.Analyst_Text)
sentieo["OtherExec_Word_Count"] = sa.WordCounting(sentieo.Other_Exec_Text)
sentieo["CEO_Sent_Count"] = sa.SentenceCounting(sentieo.CEO_Text)
sentieo["Analyst_Sent_Count"] = sa.SentenceCounting(sentieo.Analyst_Text)
sentieo["OtherExec_Sent_Count"] = sa.SentenceCounting(sentieo.Other_Exec_Text)
sentieo["CEO_Pos_Fin"] = sa.CustomDict(sentieo.CEO_Text, pos_list)
sentieo["CEO_Neg_Fin"] = sa.CustomDict(sentieo.CEO_Text, neg_list)
# More steps needed to add the big5 traits


opennness_raw, conscientiousness_raw, extraversion_raw, agreeableness_raw, neuroticism_raw, opennness_perc,\
 conscientiousness_perc, extraversion_perc, agreeableness_perc, neuroticism_perc = sa.PersonalityScores(sentieo.CEO_Text)

sentieo['Openness Raw'] = opennness_raw
sentieo['Concientiousness Raw'] = conscientiousness_raw
sentieo['Extraversion Raw'] = extraversion_raw
sentieo['Agreeableness Raw'] = agreeableness_raw
sentieo['Neuroticism Raw'] = neuroticism_raw

sentieo['Openness Percentile'] = opennness_perc
sentieo['Concientiousness Percentile'] = conscientiousness_perc
sentieo['Extraversion Percentile'] = extraversion_perc
sentieo['Agreeableness Percentile'] = agreeableness_perc
sentieo['Neuroticism Percentile'] = neuroticism_perc


print("Done with NLP, writing out ...")
#sentieo["CEOSpin"]= sa.CEOspin(sentieo.CEOScore,sentieo.ContextScore)
# NEXT: Use some list unique(Tickers) to create a dataframe with overall CEO scores
# for each company. These are what will be merged with Bloomberg df

df = pd.DataFrame()
df['CEO'] = sentieo['CEO']
df["Ticker"] = sentieo["Ticker"]
df["Sector"] = sentieo["Sector"]
df["Quarter"] = sentieo["Quarter"]
df["Year"] = sentieo["Year"]
df["Date"] = sentieo["Date"]
df["CEOScore"] = sentieo["CEOScore"]
df["AnalystScore"] = sentieo["AnalystScore"]
df["OtherExecScore"] = sentieo["OtherExecScore"]
df["CEO_Word_Count"] = sentieo["CEO_Word_Count"]
df["Analyst_Word_Count"] = sentieo["Analyst_Word_Count"]
df["OtherExec_Word_Count"] = sentieo["OtherExec_Word_Count"]
df["CEO_Sent_Count"] = sentieo["CEO_Sent_Count"]
df["Analyst_Sent_Count"] = sentieo["Analyst_Sent_Count"]
df["OtherExec_Sent_Count"] = sentieo["OtherExec_Sent_Count"]
df["CEO_Pos_Fin"] = sentieo["CEO_Pos_Fin"]
df["CEO_Neg_Fin"] = sentieo["CEO_Neg_Fin"]
df["CEO_Fin_Score1"] = np.divide(sentieo["CEO_Pos_Fin"], sentieo["CEO_Neg_Fin"])
df["CEO_Fin_Score2"] = np.divide( np.subtract(sentieo["CEO_Pos_Fin"], sentieo["CEO_Neg_Fin"]),  np.add(sentieo["CEO_Pos_Fin"], sentieo["CEO_Neg_Fin"]))  

#Cam's additions
df['Openness Raw'] = sentieo['Openness Raw']
df['Concientiousness Raw'] = sentieo['Concientiousness Raw'] 
df['Extraversion Raw'] = sentieo['Extraversion Raw']
df['Agreeableness Raw'] = sentieo['Agreeableness Raw']
df['Neuroticism Raw'] = sentieo['Neuroticism Raw']

df['Openness Percentile'] = sentieo['Openness Percentile'] 
df['Concientiousness Percentile'] = sentieo['Concientiousness Percentile'] 
df['Extraversion Percentile'] = sentieo['Extraversion Percentile'] 
df['Agreeableness Percentile'] = sentieo['Agreeableness Percentile'] 
df['Neuroticism Percentile'] = sentieo['Neuroticism Percentile'] 




df.to_csv(aggregate_output_path, encoding='utf-8-sig')
correlations = df.corr()
correlations.to_csv(corr_output_path)
