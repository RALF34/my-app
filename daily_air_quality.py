from datetime import date, timedelta
from statistics import mean

import streamlit as st

import queries
import visualization


def main():
    st.title("Daily air pollution")
    st.write('''
            ### Select a place in France
            Identify the air quality monitoring station whose pollution data you are interested in.
            ''')
    
    s = open(r"data/last_update.txt", "r").read()
    ending_date = date.fromisoformat(s)-timedelta(days=1)
    st.session_state["starting_date"] = ending_date-timedelta(days=90)
    st.session_state["current_data"] = [None, None]
    st.session_state["y-values"] = [None, None]
    st.session_state["first_choice"] = True
    st.session_state["no_data"] = True
    
    try:
        def update_values() -> None:
            counter = 0
            for i, data in enumerate(st.session_state["current_data"]):
                if data:
                    # Initialize "dictionary" which will contain the average
                    # concentration values (set to zero when no data are
                    # available) associated to the 24 hours of the day.
                    dictionary = {str(x): 0 for x in range(24)}
                    for hour in data.groups.keys():
                        # Extract only air concentration values being less than
                        # "n_days" days old.
                        history = list(zip(data["value"],data["date"]))[::-1]
                        j = 0
                        limit = len(history)
                        while (
                            j < limit and 
                            (st.session_state["starting_date"] <= history[j][1])):
                            j += 1
                        if j == limit:
                            j -= 1
                        # Update "dictionary".
                        dictionary[str(hour)] = \
                        mean([e[0] for e in history[:j]])
                    st.session_state["y-values"][i] = list(dictionary.values())
                else:
                    counter += 1
            if counter < 2:
                st.session_state["no_data"] = False

    except Exception as e:
        st.error(e)
        st.stop()
    
    col1, col2 = st.columns((5,1))
    with col1:
        
        kwargs = {"index": None, "placeholder": ""}
        
        try:
            region = st.selectbox(
                "Select a French region",
                queries.get_items("regions", ""),
                **kwargs)
            
            department = st.selectbox(
                "Select a French department",
                queries.get_items("regions", region),
                **kwargs)
            
            city = st.selectbox(
                "Select a French city",
                queries.get_items("departments", department),
                **kwargs)
            
            station = st.selectbox(
                "Select a station",
                [e[0] for e in queries.get_items("cities", city)],
                **kwargs)
            
            if station not in queries.get_stations():
                st.error("Sorry, no data available for this station.")
                st.stop()
            else:
                pollution = st.selectbox(
                    "Select a type of pollution",
                    queries.get_items(
                        "distribution_pollutants",
                        station),
                    **kwargs)
                
                pollutant = pollution.split()[0]

                data = queries.get_data(station, pollutant)
                for i, gb in enumerate([e.groupby("hour") for e in data]):
                    st.session_state["current_data"][i] = gb
                update_values()
                
                if st.session_state["no_data"]:
                    st.error("No pollution data are available for the given period.")
                    st.stop()
                else:
                    starting_date = st.slider(
                        "When does the air pollution analysis start?",
                        ending_date-timedelta(days=180),
                        ending_date,
                        ending_date-timedelta(days=90),
                        format="DD/MM/YY",
                        key="starting_date",
                        on_change=update_values)
                    st.pyplot(
                        visualization.plot_variation(
                            st.session_state["y-values"],
                            pollutant,
                            station))
        
        except Exception as e:
            st.error(e)
            st.stop()

if __name__=="__main__":
    main()
