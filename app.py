import fastf1
import fastf1.exceptions
from f1_analyzer import FastF1Analysis
import pandas as pd
import streamlit as st
import os
from f1_analyzer import FastF1Analysis

# streamlit run app.py

def plot_stints(figs):
    fig_titles = []

    for fig in figs[:6]:
        fig_titles.append(fig.layout.title.text)
        fig.update_layout(title='')
    
    st.header(f'{race.year} {race.title}', text_alignment='center')
    
    st.text(fig_titles[0], text_alignment='center')
    st.plotly_chart(figs[0], width='stretch', height='content')

    r_col1, r_col2 = st.columns(2)

    r_col1.text(fig_titles[1], text_alignment='center')
    r_col2.text(fig_titles[2], text_alignment='center')
    r_col1.plotly_chart(figs[1], width='stretch', height='content')
    r_col2.plotly_chart(figs[2], width='stretch', height='content')

    st.header(f'Fuel Correction', text_alignment='center')
    
    st.text(fig_titles[3], text_alignment='center')
    st.plotly_chart(figs[3], width='stretch', height='content')

    r_col3, r_col4 = st.columns(2)
    
    r_col3.text(fig_titles[4], text_alignment='center')
    r_col4.text(fig_titles[5], text_alignment='center')
    r_col3.plotly_chart(figs[4], width='stretch', height='content')
    r_col4.plotly_chart(figs[5], width='stretch', height='content')

    st.header(f'Average Sector Times & Speed Trap', text_alignment='center')

    r_col5, r_col6, r_col7, r_col8 = st.columns(4)
    
    
    r_col5.plotly_chart(figs[6], width='stretch', height='content')
    r_col6.plotly_chart(figs[7], width='stretch', height='content')       
    r_col7.plotly_chart(figs[8], width='stretch', height='content')
    r_col8.plotly_chart(figs[9], width='stretch', height='content')

    st.header('Fastest Laps', text_alignment='center')

    st.plotly_chart(figs[10], width='stretch', height='content')

def fast_lap_plot(figs):
    st.plotly_chart(figs[0], width='stretch')

    a_col1, a_col2, a_col3, a_col4 = st.columns(4)

    a_col1.plotly_chart(figs[1], width='content')
    a_col2.plotly_chart(figs[2], width='content')
    a_col3.plotly_chart(figs[3], width='content')
    a_col4.plotly_chart(figs[4], width='content')

    if race.year < 2026:
        a_col5, a_col6, a_col7, a_col8 = st.columns(4)
        
        a_col5.plotly_chart(figs[5], width='content')
        a_col6.plotly_chart(figs[6], width='content')
        a_col7.plotly_chart(figs[7], width='content')
        a_col8.plotly_chart(figs[8], width='content')

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

def get_tracks(year):
    df = pd.read_csv('./events/finished.csv')
    return df[df['Year'] == year]['EventName'].to_list()

def get_sessions(year, track):
    df = pd.read_csv('./events/finished.csv')
    df = df[df['Year'] == year]
    df = df[df['EventName'] == track].reset_index(drop=True)
    df_list = []
    for x in list(range(1,6)):
        session = str(df[f'Session{x}'].item())
        if session != 'nan':
            df_list.append(session)
    return df_list

def df_format(df, x):
    x.dataframe(
            df, 
            hide_index=True, height='content', width='stretch',
            column_config={col: st.column_config.Column(alignment='center') for col in df.columns},
        )
    
st.set_page_config(layout="wide")

if 'race' not in st.session_state:
    st.session_state['race'] = None


if st.session_state['race'] is None:
    
    if 'value_error' not in st.session_state:
        st.session_state['value_error'] = False
    if 'year' not in st.session_state:
        st.session_state['year'] = None
    
    if 'track' not in st.session_state:
        st.session_state['track'] = None
    
    if 'session' not in st.session_state:
        st.session_state['session'] = None
    
    year = st.slider('Year', 2018, 2026)
    track = st.selectbox('Track', get_tracks(year))
    session = st.selectbox('Session', get_sessions(year,track))
    
    done = st.button('Done')


    if st.session_state['value_error']:
        st.error('Data for this session is not available. Please select a different session, track, or year.')
        
    if done:
        st.session_state['value_error'] = False

        try:
            with st.spinner('Loading data...'):
                race = FastF1Analysis(year, track, session)
            
            st.session_state['race'] = race
            st.session_state['session'] = session
            st.rerun()
        
        except fastf1.exceptions.DataNotLoadedError:
            fastf1.Cache.clear_cache()
            st.rerun()
        



if st.session_state['race']:
    race = st.session_state['race']

    st.sidebar.title('Analytics')

    if race.year != 2018:
    
        if st.session_state['session'] in ['Practice 1', 'Practice 2', 'Practice 3']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home', 'Fast Lap Analysis', 'Fast Lap Telemetry', 'Stint Analysis'])
        elif st.session_state['session'] in ['Qualifying', 'Sprint Qualifying']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home', 'Fast Lap Telemetry','Q1 Analysis', 'Q2 Analysis', 'Q3 Analysis'])
        elif st.session_state['session'] in ['Sprint', 'Race']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home', 'Race Strategies', 'Race Analysis','Stint Analysis', 'Fast Lap Analysis', 'Fast Lap Telemetry'])
            if 'strategies' not in st.session_state:
                strategies_fig = race.plot_strategies(return_figs=True)
                race_pos_fig = race.plot_all_drivers_positions(return_figs=True)
                st.session_state['strategies'] = [race_pos_fig, strategies_fig]
    
    else:
        if st.session_state['session'] in ['Practice 1', 'Practice 2', 'Practice 3']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home','Stint Analysis'])
        elif st.session_state['session'] in ['Qualifying', 'Sprint Qualifying']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home'])
        elif st.session_state['session'] in ['Sprint', 'Race']:
            options = st.sidebar.radio('Select what you want to display:', [
                'Home', 'Race Strategies', 'Race Analysis','Stint Analysis'])
            
            if 'strategies' not in st.session_state:
                strategies_fig = race.plot_strategies(return_figs=True)
                race_pos_fig = race.plot_all_drivers_positions(return_figs=True)
                st.session_state['strategies'] = [race_pos_fig, strategies_fig]

    if options == 'Home':
        st.header(f'{race.year} {race.title} {race.type}', text_alignment='center')
        df = race.results
        st.dataframe(
            df, 
            hide_index=True, height='content', width='stretch',
            column_config={col: st.column_config.Column(alignment='center') for col in df.columns},
        )

        st.header(f'Top Ten Laps', text_alignment='center')
        df_format(race.top_ten_lap_details[0],st)
        
        st.header(f'Sector Times & Speed Trap', text_alignment='center')

        s_col1, s_col2, s_col3 = st.columns(3)

        for x, y, z in zip(
            [s_col1, s_col2, s_col3],
            ['Sector 1', 'Sector 2', 'Sector 3'],
            [1, 2, 3]
        ):
            x.header(y, text_alignment='center')
            df_format(race.top_ten_lap_details[z], x)
        
        st.header(f'Speed Trap', text_alignment='center')
        df_format(race.top_ten_lap_details[4], st)


        # WEATHER BREAKS TELEMETRY AND FAST LAP ANALYSIS

        # # WEATHER

        # if 'weather_fig' not in st.session_state:
        #     st.session_state['weather_fig'] = None
        # if st.session_state['weather_fig'] == None:
        #     st.session_state['weather_fig'] = race.plot_weather()
        
        # st.header('Weather', text_alignment='center')
        
        # df_format(race.weather_data[1], st)

        # st.plotly_chart(st.session_state['weather_fig'], width='stretch', height='content')

        restart = st.button('Restart')
        
        if restart:
            st.session_state.clear()
            st.rerun()
    if options == 'Q1 Analysis':
        if 'q1_figs' not in st.session_state:
            st.session_state['q1_figs'] = None
        if st.session_state['q1_figs'] == None:
            figs = race.plot_quali_analysis(session='Q1', return_figs=True)
            st.session_state['q1_figs'] = figs
        
        if st.session_state['q1_figs'] != None:
            figs = st.session_state['q1_figs']

            st.header('Q1 Analysis', text_alignment='center')

            fast_lap_plot(figs)
    
    if options == 'Q2 Analysis':
        if 'q2_figs' not in st.session_state:
            st.session_state['q2_figs'] = None
        if st.session_state['q2_figs'] == None:
            figs = race.plot_quali_analysis(session='Q2', return_figs=True)
            st.session_state['q2_figs'] = figs
        
        if st.session_state['q2_figs'] != None:
            figs = st.session_state['q2_figs']

            st.header('Q2 Analysis', text_alignment='center')

            fast_lap_plot(figs)
    
    if options == 'Q3 Analysis':
        if 'q3_figs' not in st.session_state:
            st.session_state['q3_figs'] = None
        if st.session_state['q3_figs'] == None:
            figs = race.plot_quali_analysis(session='Q3', return_figs=True)
            st.session_state['q3_figs'] = figs
        
        if st.session_state['q3_figs'] != None:
            figs = st.session_state['q3_figs']

            st.header('Q3 Analysis', text_alignment='center')

            fast_lap_plot(figs)
        
    
    if options == 'Fast Lap Analysis':

        if 'quali_analysis_figs' not in st.session_state:
            st.session_state['quali_analysis_figs'] = None

        if st.session_state['quali_analysis_figs'] is None:
            figs = get_drivers()

            if figs:
                st.session_state['quali_analysis_figs'] = figs
                st.rerun()
        
        if st.session_state['quali_analysis_figs']:

            figs = st.session_state['quali_analysis_figs']

            st.header('Fast Lap Analysis', text_alignment='center')

            fast_lap_plot(figs)
            
            restart = st.button('Restart')

            if restart:
                st.session_state['quali_analysis_figs'] = None
                st.rerun()
    if options == 'Race Strategies':
        
        for fig in st.session_state['strategies']:
            st.plotly_chart(fig, width='stretch', height='content')
        


 
    if options == 'Fast Lap Telemetry':


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
                    fig = race.plot_race_stint(all_drivers=True, gap_to_leader=True, return_figs=True)
                    st.session_state['race_figs'] = fig

                elif st.session_state['race_type'] == 'top_ten':
                    fig = race.plot_race_stint(top_ten=True, gap_to_leader=True, return_figs=True)
                    st.session_state['race_figs'] = fig

                elif st.session_state['race_type'] == 'teams':
                    fig = race.plot_race_stint(teams=True, gap_to_leader=True, return_figs=True)
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

            plot_stints(figs)

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

                        figs = race.plot_by_lap_numbers_(
                            drivers_initials=st.session_state['stint_drivers'], 
                            lap_ranges=st.session_state['stints'], 
                            return_figs=True, order_by_pace=True
                            )

                        st.session_state['stint_figs'] = figs
                        

                        st.rerun()

                
        if st.session_state['stint_figs']:
            
            figs = st.session_state['stint_figs']

            plot_stints(figs)
            
            restart = st.button('Restart')

            if restart:
                st.session_state['stint_figs'], st.session_state['stint_drivers'] = None, None
                st.rerun()
                