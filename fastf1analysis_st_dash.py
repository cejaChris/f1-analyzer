from main import FastF1Analysis
import pandas as pd
import streamlit as st

# streamlit run fastf1analysis_st_dash.py

def get_drivers():  
    all_drivers = st.button('Analyze all drivers')
    top_ten = st.button('Analyze the top 10')
    team = st.button('Analyze each teams leading driver')

    if all_drivers:
        figs = race.plot_quali_analysis(return_figs=True)
        return figs
    if top_ten:
        figs = race.plot_quali_analysis(top_ten=True, return_figs=True)
        return figs
    if team:
        figs = race.plot_quali_analysis(teams=True, return_figs=True)
        return figs

def get_tracks():
    tracks = pd.read_csv('./events/race_list.csv')['Race Name'].to_list()
    tracks = pd.Series(tracks).drop_duplicates().tolist()
    return tracks
st.set_page_config(layout="wide")

if 'race' not in st.session_state:
    st.session_state['race'] = None


if st.session_state['race'] is None:
    if 'year' not in st.session_state:
        st.session_state['year'] = None
    
    if 'track' not in st.session_state:
        st.session_state['track'] = None
    
    if 'session' not in st.session_state:
        st.session_state['session'] = None
    
    year = st.slider('Year', 2018, 2026)
    session = st.selectbox('Session', ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'SR', 'R'])
    track = st.selectbox('Track', get_tracks())
    done = st.button('Done')

    if done:

        race = FastF1Analysis(year, track, session)

        st.session_state['race'] = race
        st.session_state['session'] = session
        st.rerun()




if st.session_state['race']:
    race = st.session_state['race']

    st.sidebar.title('Analytics')
    
    if st.session_state['session'] in ['FP1', 'FP2', 'FP3']:
        options = st.sidebar.radio('Select what you want to display:', [
            'Home', 'Quali/Fastest Lap Analysis', 'Quali/Fastest Lap Telemetry', 'Stint Analysis'])
    elif st.session_state['session'] in ['Q', 'SQ']:
        options = st.sidebar.radio('Select what you want to display:', [
            'Home', 'Quali/Fastest Lap Analysis', 'Quali/Fastest Lap Telemetry'])
    elif st.session_state['session'] == 'R':
        options = st.sidebar.radio('Select what you want to display:', [
            'Home', 'Quali/Fastest Lap Analysis', 'Quali/Fastest Lap Telemetry', 'Race Analysis', 'Race Strategies','Stint Analysis'])
        if 'strategies' not in st.session_state:
            strategies_fig = race.plot_strategies(return_figs=True)
            race_pos_fig = race.plot_all_drivers_positions(return_figs=True)
            st.session_state['strategies'] = [race_pos_fig, strategies_fig]

    if options == 'Home':
        st.header(f'{race.title} {race.year} {race.type}')
        st.dataframe(race.results, hide_index=True)
        restart = st.button('Restart')
        if restart:
            st.session_state.clear()
            st.rerun()
    
    if options == 'Quali/Fastest Lap Analysis':

        if 'quali_analysis_figs' not in st.session_state:
            st.session_state['quali_analysis_figs'] = None

        if st.session_state['quali_analysis_figs'] is None:
            figs = get_drivers()

            if figs:
                st.session_state['quali_analysis_figs'] = figs
                st.rerun()
        
        if st.session_state['quali_analysis_figs']:

            for fig in st.session_state['quali_analysis_figs']:
                st.plotly_chart(fig)
            
            restart = st.button('Restart')

            if restart:
                st.session_state['quali_analysis_figs'] = None
                st.rerun()
    if options == 'Race Strategies':
        
        for fig in st.session_state['strategies']:
            st.plotly_chart(fig)
        


 
    if options == 'Quali/Fastest Lap Telemetry':


        if 'telem_type' not in st.session_state:
            st.session_state['telem_type'] = None
        if 'telem_fig' not in st.session_state:
            st.session_state['telem_fig'] = None
        
        if st.session_state['telem_type'] == None:
            
            all_drivers = st.button('Get all drivers')
            top_ten = st.button('Get top 10')
            teams = st.button("Get each team's leading driver")
            spec_drivers = st.button('Select drivers manually')

            if all_drivers:
                telem_type = 'all_drivers'
                st.session_state['telem_type'] = telem_type
                st.rerun()
            elif top_ten:
                telem_type = 'top_ten'
                st.session_state['telem_type'] = telem_type
                st.rerun()
            elif teams:
                telem_type = 'teams'
                st.session_state['telem_type'] = telem_type
                st.rerun()
            elif spec_drivers:
                telem_type = 'spec_drivers'
                st.session_state['telem_type'] = telem_type
                st.rerun()

        
        if st.session_state['telem_fig'] == None:
        
            if st.session_state['telem_type']:
                if st.session_state['telem_type'] == 'all_drivers':
                    fig = race.plot_lap_telem(all_drivers=True, return_figs=True)
                    st.session_state['telem_fig'] = fig

                elif st.session_state['telem_type'] == 'top_ten':
                    fig = race.plot_lap_telem(top_ten=True, return_figs=True)
                    st.session_state['telem_fig'] = fig

                elif st.session_state['telem_type'] == 'teams':
                    fig = race.plot_lap_telem(teams=True, return_figs=True)
                    st.session_state['telem_fig'] = fig
                elif st.session_state['telem_type'] == 'spec_drivers':

                    if 'telem_lap_type' not in st.session_state:
                        st.session_state['telem_lap_type'] = None
                    if 'telem_spec_drivers' not in st.session_state:
                        st.session_state['telem_spec_drivers'] = None
                    if 'telem_laps' not in st.session_state:
                        st.session_state['telem_laps'] = None
                    if 'telem_spec_drivers' not in st.session_state:
                        st.session_state['telem_spec_drivers'] = None
                    if 'step_1' not in st.session_state:
                        st.session_state['step_1'] = None
                    
                    if st.session_state['telem_lap_type'] == None:

                        button_1 = st.button('Fastest lap')
                        button_2 = st.button('Specific lap')
                    
                        if button_1:
                            st.session_state['telem_lap_type'] = 'fastest'
                            st.rerun()
                        if button_2:
                            st.session_state['telem_lap_type'] = 'spec'
                            st.rerun()
                    
                    
                    if st.session_state['telem_lap_type'] == 'fastest':
                        
                        st.session_state['telem_spec_drivers_default'] = []

                        selection = st.multiselect(
                            "Choose items:", 
                            race.drivers, 
                            default=st.session_state['telem_spec_drivers_default']
                        )
                        done = st.button('Done')
                        back_out = st.button('Cancel')

                        if back_out:
                            st.session_state['telem_lap_type'] = None
                            st.rerun()
                        if done:
                            fig = race.plot_lap_telem(drivers=selection, return_figs=True)
                            st.session_state['telem_fig'] = fig
                            st.rerun()
                    
                    if st.session_state['telem_lap_type'] == 'spec':

                        if st.session_state['telem_spec_drivers']:

                            # st.session_state['step_1'] = None
                            # st.rerun()

                            

                            st.session_state['telem_laps'] = []

                            drivers = st.session_state['telem_spec_drivers']



                            for driver in drivers:
                                df = race.show_drivers_laps(driver_initials=driver)
                                slider = st.slider(
                                    f'{driver}: Enter the lap you want to analyze',
                                    df['LapNumber'].iloc[0].astype(int),
                                    df['LapNumber'].iloc[-1].astype(int),
                                )
                                st.dataframe(df, hide_index=True)

                                st.session_state['telem_laps'].append(slider)
                            
                            done = st.button('Done')
                            restart = st.button('Restart')
                            
                            if restart:
                                st.session_state['telem_lap_type'] = None
                                st.session_state['telem_spec_drivers'] = None
                                st.session_state['telem_lap'] = None
                                st.session_state['telem_fig'] = None
                                st.session_state['telem_type'] = None
                                st.rerun()

                            if done:

                                fig = race.plot_lap_telem(drivers=st.session_state['telem_spec_drivers'], laps=st.session_state['telem_laps'], return_figs=True)
                                st.session_state['telem_fig'] = fig

                                st.rerun()

                        
                        elif st.session_state['telem_spec_drivers'] == None:
                            
                            st.session_state['telem_spec_drivers_default'] = []

                            selection = st.multiselect(
                                "Choose drivers:", 
                                race.drivers, 
                                default=st.session_state['telem_spec_drivers_default']
                            )
                            done = st.button('Done')
                            back_out = st.button('Cancel')

                            if done:
                                st.session_state['telem_spec_drivers'] = selection 
                                st.rerun()


                            if back_out:
                                st.session_state['telem_lap_type'] = None
                                st.session_state['telem_spec_drivers'] = None
                                st.rerun()
                            

        
        
        if st.session_state['telem_fig']:
            fig = st.session_state['telem_fig']
            st.plotly_chart(fig)

            restart = st.button('Restart')
            if restart:
                st.session_state['telem_lap_type'] = None
                st.session_state['telem_spec_drivers'] = None
                st.session_state['telem_lap'] = None
                st.session_state['telem_fig'] = None
                st.session_state['telem_type'] = None
                st.rerun()



        



    if options == 'Race Analysis':
        if 'race_type' not in st.session_state:
            st.session_state['race_type'] = None
        if 'race_figs' not in st.session_state:
            st.session_state['race_figs'] = None
        
        if st.session_state['race_type'] == None:
            
            all_drivers = st.button('Get all drivers')
            top_ten = st.button('Get top 10')
            teams = st.button("Get each team's leading driver")
            spec_drivers = st.button('Select drivers manually')

            if all_drivers:
                telem_type = 'all_drivers'
                st.session_state['race_type'] = telem_type
                st.rerun()
            elif top_ten:
                telem_type = 'top_ten'
                st.session_state['race_type'] = telem_type
                st.rerun()
            elif teams:
                telem_type = 'teams'
                st.session_state['race_type'] = telem_type
                st.rerun()
            elif spec_drivers:
                telem_type = 'spec_drivers'
                st.session_state['race_type'] = telem_type
                st.rerun()

        
        if st.session_state['race_figs'] == None:
        
            if st.session_state['race_type']:
                if st.session_state['race_type'] == 'all_drivers':
                    fig = race.plot_race_stint(all_drivers=True, return_figs=True)
                    st.session_state['race_figs'] = fig

                elif st.session_state['race_type'] == 'top_ten':
                    fig = race.plot_race_stint(top_ten=True, return_figs=True)
                    st.session_state['race_figs'] = fig

                elif st.session_state['race_type'] == 'teams':
                    fig = race.plot_race_stint(teams=True, return_figs=True)
                    st.session_state['race_figs'] = fig
                elif st.session_state['race_type'] == 'spec_drivers':

                    st.session_state['race_spec_drivers'] = []

                    selection = st.multiselect(
                        "Choose items:", 
                        race.drivers, 
                        default=st.session_state['race_spec_drivers']
                    )
                    done = st.button('Done')
                    back_out = st.button('Cancel')

                    if done:
                        fig = race.plot_race_stint(drivers=selection, return_figs=True)
                        st.session_state['race_figs'] = fig
                        st.rerun()
                    if back_out:
                        st.session_state['race_type'] = None
                        st.session_state['race_figs'] = None
                        st.rerun()

        
        if st.session_state['race_figs']:
            figs = st.session_state['race_figs']
            for fig in figs:
                st.plotly_chart(fig)

            restart = st.button('Restart')
            if restart:
                st.session_state['race_type'] = None
                st.session_state['race_figs'] = None
                st.rerun()
    

    if options == 'Stint Analysis':


        if 'stint_figs' not in st.session_state:
            st.session_state['stint_figs'] = None

        if 'stint_drivers' not in st.session_state:
            st.session_state['stint_drivers'] = None

        if st.session_state['stint_drivers'] == None:

            st.session_state['choose_drivers'] = []
            
            selection = st.multiselect(
                    "Choose Drivers:", 
                    race.drivers, 
                    default=st.session_state['choose_drivers']
                )
            done_button = st.button('Done')

            if done_button:
                st.session_state['stint_drivers'] = selection
                st.rerun()
        if st.session_state['stint_drivers']:

            if 'stint_figs' not in st.session_state or not st.session_state['stint_figs']:

                if 'stint' not in st.session_state:
                    st.session_state['stints'] = []

                    for driver in st.session_state['stint_drivers']:


                        df = race.show_drivers_laps(driver_initials=driver)
                        laps = df['LapNumber'].to_list()
                        laps_range = [df['LapNumber'].iloc[0].astype(int), df['LapNumber'].iloc[-1].astype(int)]
                        slider_range = st.slider(
                            f'{driver}: Enter the laps you want to analyze',
                            min_value=laps_range[0],
                            max_value=laps_range[1],
                            value=(laps_range[0], laps_range[1]),
                            step=1)
                        st.dataframe(df, hide_index=True)

                        st.session_state['stints'].append(slider_range)
                    
                    
                    done = st.button('Done')

                    if done:

                        figs = race.plot_by_lap_numbers(drivers_initials=st.session_state['stint_drivers'], lap_ranges=st.session_state['stints'], return_figs=True, order_by_pace=True)

                        st.session_state['stint_figs'] = figs

                        st.rerun()

                
        if st.session_state['stint_figs']:
            for fig in st.session_state['stint_figs']:
                st.plotly_chart(fig)
            
            restart = st.button('Restart')

            if restart:
                st.session_state['stint_figs'], st.session_state['stint_drivers'] = None, None
                st.rerun()
                
