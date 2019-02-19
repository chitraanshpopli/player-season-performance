import pandas as pd
import numpy as np
import os

def verify_headers(df):
    """Verifies that correct table has been copied. 
    Note: This only verifies the headers.
    Results can still go wrong if all rows/columns are not copied."""

    if list(df) == ['Season', 'Team', 'Tournament', 'Apps', 'Mins', 'Goals', 'Assists', 'Yel', 'Red', 'SpG', 'PS%', 'AerialsWon', 'MotM', 'Rating']:
        print('\nFile with table from whoscored.com found.')
    else:
        print('Headers missing from table. Please copy the complete table.\nFor instructions for the format of the file, please refer github repo.')
        exit()

def initial_cleanup(df):
    """Removes NaN. Drops unnecessary columns. Also creates list (set) of tournaments player has played in."""
    
    global tournaments
    df.fillna(value='', inplace = True)
    tournaments = create_tournament_list(df)
    df.drop(columns = ['Yel', 'Red', 'MotM', 'Rating', 'Tournament'], inplace = True)
    df.replace(to_replace = '-', value = 0, inplace = True)


def create_tournament_list(df):
    """Create list (set) of all tournaments player has played in before dropping the column."""
    
    tournaments = set()
    for tournament in df['Tournament']:
        tournaments.add(tournament)
    tournaments.remove('')
    return tournaments

def split_apps(df):
    """Splits Apps column into two: Starting appearances and substitute appearances."""
    
    appearances_list = list()   #List of lists. Each sublist of format: [start_app, sub_app]
    start_total, sub_total =  0,0
    for row in range((df.shape[0])):     #df.shape[0] gives number of rows
        appearance = (df.loc[row]['Apps']).split(sep = '(')
        if len(appearance) == 1:    #No substitute appearances
            appearance.append(0)
        else:   #Remove ')' from sub appearances
            appearance[1] = appearance[1][:-1]
        appearance = [int(x) for x in appearance]   #string to int
        start_total += appearance[0]
        sub_total += appearance[1]
        appearances_list.append(appearance)
    #Subtract last appearance since last value in original table is the sum of all appearances.
    appearances_list[-1] = [start_total-appearances_list[-1][0], sub_total-appearances_list[-1][1]]
    
    df.drop(columns = 'Apps', inplace = True)
    df['Apps_Start'] = [appearance[0] for appearance in appearances_list]
    df['Apps_Sub'] = [appearance[1] for appearance in appearances_list]

def merge_rows(df, row):
    """Merge rows for same (team and season) but different competitions. (Same season different competitions)"""

    df.at[row+1, 'Mins'] = int(df.loc[row+1, 'Mins']) + int(df.loc[row, 'Mins'])
    df.at[row+1, 'Goals'] = int(df.loc[row+1, 'Goals']) + int(df.loc[row, 'Goals'])
    df.at[row+1, 'Assists'] = int(df.loc[row+1, 'Assists']) + int(df.loc[row, 'Assists'])
    df.at[row+1, 'Apps_Start'] = int(df.loc[row+1, 'Apps_Start']) + int(df.loc[row, 'Apps_Start'])
    df.at[row+1, 'Apps_Sub'] = int(df.loc[row+1, 'Apps_Sub']) + int(df.loc[row, 'Apps_Sub'])
    df.at[row+1, 'SpG'] = (float(df.loc[row+1, 'SpG']) + float(df.loc[row, 'SpG']))/2
    df.at[row+1, 'PS%'] = (float(df.loc[row+1, 'PS%']) + float(df.loc[row, 'PS%']))/2
    df.at[row+1, 'AerialsWon'] = (float(df.loc[row+1, 'AerialsWon']) + float(df.loc[row, 'AerialsWon']))/2

def add_team_total_rows(df):
    """Add rows with player's total stats at a team."""

    teams = set()
    for team in df['Team']:     #Create a set of all teams player has played in.
        teams.add(team)
    teams.remove('')
    
    for team in teams:
        df.at[(df.shape[0])+1, 'Season'] = 'Combined'   #Add new row in the end.
        df.at[df.shape[0], 'Team'] = team   #Removed +1 since new row is already added.
        df.fillna(value=0, inplace = True)
        fill_team_total(df, team)

def fill_team_total(df, team):
    """Add rows for different season to row holding combined stat for the team."""

    count = 0
    for row in range((df.shape[0]-1)):     #-1 since we don't have to check the current last row (that is the combined row) 
        row += 1    #For some reason (probably due to reindexing), row = 0 does not exist while it earlier did.
        if df.at[row, 'Team'] == team:
            count += 1 
            df.at[df.shape[0], 'Apps_Start'] = int(df.at[df.shape[0], 'Apps_Start']) + int(df.at[row, 'Apps_Start'])
            df.at[df.shape[0], 'Apps_Sub'] = int(df.at[df.shape[0], 'Apps_Sub']) + int(df.at[row, 'Apps_Sub'])
            df.at[df.shape[0], 'Mins'] = int(df.at[df.shape[0], 'Mins']) + int(df.at[row, 'Mins'])
            df.at[df.shape[0], 'Goals'] = int(df.at[df.shape[0], 'Goals']) + int(df.at[row, 'Goals'])
            df.at[df.shape[0], 'Assists'] = int(df.at[df.shape[0], 'Assists']) + int(df.at[row, 'Assists'])
            df.at[df.shape[0], 'SpG'] = float(df.at[df.shape[0], 'SpG']) + float(df.at[row, 'SpG'])
            df.at[df.shape[0], 'PS%'] = float(df.at[df.shape[0], 'PS%']) + float(df.at[row, 'PS%'])
            df.at[df.shape[0], 'AerialsWon'] = float(df.at[df.shape[0], 'AerialsWon']) + float(df.at[row, 'AerialsWon'])
            
    df.at[df.shape[0], 'SpG'] = (df.at[df.shape[0], 'SpG'])/count
    df.at[df.shape[0], 'PS%'] = (df.at[df.shape[0], 'PS%'])/count
    df.at[df.shape[0], 'AerialsWon'] = (df.at[df.shape[0], 'AerialsWon'])/count

def add_new_columns(df):
    """Add Goals+Assists column. Add per90 stats."""

    df['G+A'] = [int(df.at[row+1, 'Goals']) + int(df.at[row+1, 'Assists']) for row in range(df.shape[0])]
    df['90s_played'] = [(df.at[row+1, 'Mins'])/90 for row in range(df.shape[0])]
    df['Goalsp90'] = [int((df.at[row+1, 'Goals']))/(df.at[row+1, '90s_played']) for row in range(df.shape[0])]
    df['Assistsp90'] = [int((df.at[row+1, 'Assists']))/(df.at[row+1, '90s_played']) for row in range(df.shape[0])]
    df['(G+A)p90'] = [int((df.at[row+1, 'G+A']))/(df.at[row+1, '90s_played']) for row in range(df.shape[0])]
    
def final_cleanup(df):
    """Convert integer colums to ints. Round off float colums to upto 2 decimal places. Reorder columns."""

    set_datatypes(df)
    df = df.round(2)    #Round off floats
    df = df[[       #Reorder Columns
        'Season', 
        'Team', 
        'Apps_Start', 
        'Apps_Sub', 
        'Mins', 
        '90s_played', 
        'Goals', 
        'Goalsp90', 
        'Assists', 
        'Assistsp90', 
        'G+A', 
        '(G+A)p90', 
        'SpG', 
        'PS%', 
        'AerialsWon',
        ]]      
    return df
    
def set_datatypes(df):
    df['Apps_Start']=df.Apps_Start.astype('uint16')
    df['Apps_Sub']=df.Apps_Sub.astype('uint16')
    df['Mins']=df.Mins.astype('uint32')
    df['Goals']=df.Goals.astype('uint16')
    df['Assists']=df.Assists.astype('uint16')
    df['Assistsp90']=df.Assistsp90.astype('float')


def main():

    df = pd.read_csv(csv_path)  #Create dataframe
    verify_headers(df)
    initial_cleanup(df)
    split_apps(df)
    print('\nList of all tournaments:\n', tournaments,'\n\n')

    rows_to_delete = set()
    #df.shape[0] gives number of rows. -1 because we are comparing row and row+1. 
    for row in range((df.shape[0])-1):  
        if (df.at[row, 'Team'] == df.at[row+1, 'Team']) and (df.at[row, 'Season'] == df.at[row+1, 'Season']):
            rows_to_delete.add(row)
            merge_rows(df, row)
    
    #Delete merged rows.
    df.drop(list(rows_to_delete), axis = 0, inplace = True)

    df.index = np.arange(1, len(df) + 1)    #Reset index.
    add_team_total_rows(df)
    add_new_columns(df)
    df = final_cleanup(df)
    print(df)

    csv_path
    df.to_csv(csv_path)
    with open(csv_path, 'a') as mf:
        mf.write('\nList of all tournaments:')
        mf.write(str(tournaments))
        mf.write('\nOriginal table obtained from whoscored.com')
        mf.write('\nAll float values are rounded off upto 2 decimal digits.')
    print('\nModified table saved at: ', csv_path)




csv_path = input("Please enter path to .csv file: ")

if not (os.path.isfile(csv_path)):
    print('Invalid path.')
else:
    main()