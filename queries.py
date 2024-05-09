from typing import List

import pandas as pd
import pickle

OVERSEAS_DEPARTMENTS = [
    "GUADELOUPE",
    "GUYANE",
    "MARTINIQUE",
    "LA REUNION",
    "MAYOTTE",
    "SAINT-MARTIN"]



def get_stations() -> List[str]:
    f = open(r"data/distribution_pollutants.pickle", "rb")
    data = pickle.load(f)
    return list(data.groups.keys())

def get_data(s: str, p: str) -> List[pd.DataFrame]:
    '''
    Return the pandas dataframes (or None when not enough data)
    containing hourly average air concentrations of pollutant "p" 
    recorded by station "s" on both working_days and weekends.
    '''
    result = []
    for name in ["working_days","weekends"]:
        f = open(r"data/"+f"{name}.pickle", "rb")
        data = pickle.load(f)
        try:
            result.append(data.get_group((s,p)))
        except:
            result.append(None)
        f.close()
    return result

def get_items(
    file_name: str,
    group_name: str) -> List[str]:
    '''
    Extract the data from the appropriate pandas GroupBy object which are
    associated to group "group_name".

    Arguments:
    file_name -- string determining the name of the file containing the
             serialized pandas GroupBy object that we want to query.
    group_name -- name of the group whose data we want to extract.
    '''
    
    f = open(r"data/"+f"{file_name}.pickle", "rb")
    data = pickle.load(f)

    if file_name == "regions" and not(group_name):
        items = list(data.groups.keys())
        for e in OVERSEAS_DEPARTMENTS:
            items.remove(e)
        items.append("OUTRE-MER")
    else:
        if group_name == "OUTRE-MER":
            items = OVERSEAS_DEPARTMENTS
        else:
            data = data.get_group(group_name)
            if file_name == "cities":
                items = list(zip(
                    data["station"].to_list(),
                    data["coordinates"].to_list()))
            else:
                items = data.to_list()
                if file_name == "distribution_pollutants":
                    items = [e+" pollution" for e in items]
    f.close()
    return items
