import fastf1
from fastf1 import plotting
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import numpy as np

 

class FastF1Analysis:

    def __init__(self, year, track, session):
        self.year = year
        self.track = track
        self.session = fastf1.get_session(year,track,session)
        self.session.load() 
        self.teams = self._get_teams()
        self.location = self.session.session_info['Meeting']['Location']
        self.races = pd.read_csv('./events/race_list.csv')['Race Name'].to_list()
        self.type_2 = self.session.session_info['Type']
        self.drivers = self._get_all_drivers_names()
        self.results = self._get_results_clean()[1]
        self.results_raw = self._get_results_clean()[0]
        self.lead_drivers = self._get_lead_driver()
        self.time_loss = self._get_time_loss_per_kg()
        self.title = self._get_session_title()
        self.type = self._get_session_type()
        self.fuel_capacity = self._get_fuel_capacity()
        self.location = self._get_location()
        self.race_distance_ref = self._get_previous_race_distances()[1]
        self.race_distance_ref_2 = self._get_previous_race_distances()[0]
        self.race_distance = self._get_race_distance()
        self.avg_fuel_usage = self._get_avg_fuel_usage()
        self.driver_line_type = self._driver_line_type()

    
    def _get_session_title(self):
        x = pd.DataFrame(self.session.session_info).reset_index(drop=True)
        session_title = x.loc[1,'Meeting']

        return session_title
    
    def _get_session_type(self):
        x = pd.DataFrame(self.session.session_info).reset_index(drop=True)
        session_type = x.loc[0,'Name']

        return session_type
    
    def _get_previous_race_distances(self):

        df = pd.read_csv('./events/combined_data.csv')
        df_2 = pd.read_csv('./events/race_list.csv')

        return [df, df_2]
    

    def _get_compound_color(self, compound):
        try:
            color = plotting.get_compound_color(compound=compound, session=self.session)
        except: 
            color = 'black'

        return color
    
    def _get_grid_position(self, driver):

        df = self.results_raw[['Abbreviation', 'GridPosition']].reset_index(drop=True)
        pos = df.loc[df['Abbreviation'] == driver]['GridPosition'].item()

        if pos == 0:
            return pd.NA


        return pos

    def _get_fuel_capacity(self):

        if self.year < 2026:
            capacity = 110
        else:
            capacity = 70
        return capacity

    def _get_location(self):
        df = pd.DataFrame(self.session.session_info)
        location = df.loc['Location', 'Meeting']

        return location

    def _get_race_distance(self):
        if self.type == 'Race':
            laps = self.session.results['Laps'].max()
            if not laps > 1:
                laps = self.race_distance_ref[self.race_distance_ref['Race Name'] == self.title]['Laps'].iloc[0]
            return laps

        elif self.title in self.race_distance_ref['Race Name'].to_list():
            return self.race_distance_ref[self.race_distance_ref['Race Name'] == self.title]['Laps'].iloc[0]
        elif self.location in self.race_distance_ref_2['Location'].to_list():
            return self.race_distance_ref_2[self.race_distance_ref_2['Location'] == self.location]['Laps'].iloc[0]
        else:
            return self.race_distance_ref['Laps'].mean().astype(int)

        


    def _get_results_clean(self):
        if self.type_2 == 'Practice':
            drivers = self._get_all_drivers_names()
            driver_dict = {
                'DriverNumber': [],
                'Abbreviation': [],
                'TeamName': [],
                'Lap': []
            }
            for driver in drivers:
                try:
                    df = self.session.laps.pick_drivers(driver).pick_fastest()
                except:
                    break
                driver_dict['TeamName'].append(df['Team'])
                driver_dict['DriverNumber'].append(df['DriverNumber'])
                driver_dict['Lap'].append(df['LapTime'].total_seconds())
                driver_dict['Abbreviation'].append(df['Driver'])
            df = pd.DataFrame(driver_dict)
            df = df.sort_values(by='Lap')
            df['Position'] = list(range(1, len(df.index) + 1))
            df_2 = df.copy()
            df['Lap'] = df['Lap'].apply(self.convert_seconds_to_m_s_ms)
            df['Position'] = list(range(1, len(df.index) + 1))
            df = df[['Position', 'DriverNumber', 'Abbreviation','TeamName', 'Lap']]
            df_2 = df_2[['Position', 'DriverNumber', 'Abbreviation','TeamName', 'Lap']]
            df_2['Lap'] = df_2['Lap'].apply(self.convert_seconds_to_m_s_ms)

            for df_ in [df, df_2]:
                df_ = df_.set_index('Position').copy()

            return [df, df_2]

        elif self.type_2 in ['Qualifying', "Sprint Qualifying"]:
            df = self.session.results
            df_2 = df[['Position', 'Abbreviation', 'TeamName', 'DriverNumber','Q1', 'Q2', 'Q3']].reset_index(drop=True)
            for session in ['Q1', 'Q2', 'Q3']:
                df_2[session] = df_2[session].dt.total_seconds()
                df_2[session] = df_2[session].apply(self.convert_seconds_to_m_s_ms)

                for df_ in [df, df_2]:
                    df_ = df_.set_index('Position').copy()
            
            return [df, df_2]
        else:
            df = self.session.results
            df_2 = df[['Position', 'DriverNumber', 'Abbreviation', 'TeamName','Points', 'Laps']].reset_index(drop=True)
            return [df, df_2]
        

    def _get_avg_fuel_usage(self):

        fuel_usage = self.fuel_capacity / (self.race_distance - 1)

        return fuel_usage
    
    def _get_teams(self):
        total_teams = self.session.results['TeamName'].to_list()
        teams = []
        for x in total_teams:
            if x not in teams:
                teams.append(x)
        
        return teams
    
    def _get_lead_driver(self):
        drivers_by_order = []
        df = self.session.results

        if self.type_2 != 'Practice':
        
            for team in self.teams:
                drivers_df = df[df['TeamName'] == team].reset_index(drop=True)
                driver = drivers_df.loc[0, 'Abbreviation']
                drivers_by_order.append(driver)
        
            return drivers_by_order
            
        else:
            drivers_by_order = []
            df = self.results
            for team in self.teams:
                team_df = df[df['TeamName'] == team].reset_index(drop=True)
                driver = team_df.loc[0, 'Abbreviation']
                drivers_by_order.append(driver)
            
            return drivers_by_order
    
    def _get_time_loss_per_kg(self):
        fastest_time = self.session.laps.pick_fastest()['LapTime'].total_seconds()

        time_loss_per_kg = (fastest_time / 90) *  .035

        return time_loss_per_kg

    def _time_loss_calc(self, laps):

        if not isinstance(laps, list):
            laps = list(range(1, laps + 1))
        
        fuel_lvl = 0
        time_loss = []

        for lap in laps:
            fuel_lvl += self.avg_fuel_usage
            time_loss.append(fuel_lvl * self.time_loss)
        

        return time_loss[::-1]

    def get_drivers_laps(self, drivers=None, top_ten=False, csv_path=None, print_laps=False, return_dfs=False):
        if drivers:
            if not isinstance(drivers, list):
                drivers = [drivers]
        else:
            drivers = self._get_all_drivers_names()
        
        if top_ten:
            drivers = drivers[:10]
        
        dfs = []
        
        for driver in drivers:

            df = self.session.laps.pick_drivers(driver)[['Driver', 'LapNumber', 'LapTime', 'Stint', 'Compound', 'TyreLife']].copy()
            df['LapTime'] = df['LapTime'].dt.total_seconds()
            df['LapTime'] = df['LapTime'].apply(self.convert_seconds_to_m_s_ms)

            dfs.append(df)
        
        df = pd.concat(dfs, ignore_index=True).reset_index(drop=True)

        if csv_path:
            df.to_csv(csv_path)

        if print_laps:
            print(df)
    
        if return_dfs:
            return df

    def _get_all_drivers_names(self):
        drivers_names = []
        results = self.session.results.reset_index(drop=True)

        if self.session.session_info['Type'] in ['Qualifying', 'Race']:
            drivers = self.session.results['Abbreviation'].to_list()
            for driver in drivers:
                try:
                    self.session.laps.pick_drivers(driver).pick_fastest().get_telemetry()
                    drivers_names.append(driver)
                except:
                    continue
                
        
        elif self.type_2 == 'Practice':
            drivers = results['Abbreviation'].to_list()
            drivers_valid = []
            fastest_lap = []
            for driver in drivers:
                try:
                    fastest_lap.append(self.session.laps.pick_drivers(driver).pick_fastest()['LapTime'].total_seconds())
                    drivers_valid.append(driver)
                except:
                    continue
                

            df = pd.DataFrame({'Drivers': drivers_valid, 'FastestLap': fastest_lap})
            df = df.sort_values(by='FastestLap')
            drivers_names = df['Drivers'].to_list()


        else:
            for x in results.index:
                if results.loc[x, 'Laps'] > 0:
                    drivers_names.append(results.loc[x, 'Abbreviation'])


        return drivers_names
    
    def show_drivers_laps(self, driver_initials, short=True, return_dfs=True):
        if not isinstance(driver_initials, list):
            driver_initials = [driver_initials]
        data = []
        for driver in driver_initials:
            driver_df = self._convert_stint_times(driver)
            driver_df['LapTime'] = driver_df['LapTime'].apply(self.convert_seconds_to_m_s_ms)
            if short:
                driver_df = driver_df[['Driver', 'LapNumber','LapTime', 'Compound', 'TyreLife', 'Stint' , 'Position']]
            data.append(driver_df)
        if return_dfs:
            if len(data) == 1:
                return data[0]
            else:
                return data

    def _order_by_finishing_pos(self, initials):
        if not isinstance(initials, list):
            initials = [initials]
        
        formatted_initials = []

        for initial in initials:
            formatted_initials.append(initial.upper().strip())
        
        finishing_order = self._get_all_drivers_names()


        sorted_initials = []

        for x in finishing_order:
            if x in formatted_initials:
                sorted_initials.append(x)

        return sorted_initials
    
    def _order_by_avg_pace(self, initials, fuel_corrected=False):
        if not isinstance(initials,list):
            initials = [initials]
        
        driver_df_list = []
        
        for x in initials:
            driver = self._convert_stint_times(x)
            driver_df_list.append(driver)
        if fuel_corrected:
            timed_lap_time = 'TimedLapTimeFc'
        else:
            timed_lap_time = 'TimedLapTime'
        
        driver_names = []
        driver_pace = []

        for x in driver_df_list:
            driver_names.append(x.loc[0,'Driver'])
            driver_pace.append(x[timed_lap_time].mean())
        
        driver_pace_df = pd.DataFrame()

        driver_pace_df['Driver'] = driver_names
        driver_pace_df['AvgPace'] = driver_pace

        driver_pace_df = driver_pace_df.sort_values(by='AvgPace')

        sorted_initials = driver_pace_df['Driver'].to_list()
        
        return sorted_initials
        
    def _convert_fastest_lap(self, driver_initials, lap=None):

        if lap:
            driver_lap_details = self.session.laps.pick_drivers(driver_initials).reset_index(drop=True)
            driver_lap_details = driver_lap_details[driver_lap_details['LapNumber'] == lap].iloc[0]
            driver_lap_telem = self.session.laps.pick_drivers(driver_initials).pick_laps(lap).get_telemetry().add_distance()
        
        else:
            driver_lap_details = self.session.laps.pick_drivers(driver_initials).pick_fastest()
            driver_lap_telem = self.session.laps.pick_drivers(driver_initials).pick_fastest().get_telemetry().add_distance()

        driver_lap_details = driver_lap_details.copy()

        
        
        driver_lap_details['LapTime'] = FastF1Analysis.convert_seconds_to_m_s_ms(driver_lap_details['LapTime'].total_seconds())

        driver_lap_details['Color'] = plotting.get_driver_color(driver_initials, self.session)
        driver_lap_telem['Brake'] = driver_lap_telem['Brake'].astype(int) * 100
        driver_dict = {}
        driver_dict['Details'] = [driver_lap_details, driver_lap_telem]

        return driver_dict
    



    def _driver_line_type(self):
        df = self.results.copy()
        teams = df['TeamName'].drop_duplicates().to_list()

        teams_dfs = [df[df['TeamName'] == team] for team in teams]

        team_dict = {}

        for team in teams_dfs:
            team_dict[team['Abbreviation'].iloc[0]] = 'solid'
            try:
                team_dict[team['Abbreviation'].iloc[1]] = 'dot'
            except:
                continue

        return team_dict



    def  _convert_stint_times(self, driver_initials):

        try:
            self.session.laps.pick_drivers(driver_initials).pick_fastest()
        except:
            return
        
        driver_laps = self.session.laps.pick_drivers(driver_initials).reset_index(drop=True)
        driver_laps['LapTime'] = driver_laps['LapTime'].dt.total_seconds()
        driver_laps['TimedLapTime'] = driver_laps['LapTime']
        
        color = plotting.get_driver_color(driver_initials, self.session)
        color_list = []
        for x in driver_laps.index:
            color_list.append(color)

        
        # Instead of using for loops which is rly slow, I can use boolean indexing with pandas
        # it basically works like this:
        # df.loc[df['column_name'] condition, 'column_to_modify'] = new_value
        # this is much faster than the for x in df.index:
        # ` reverses the condition from True to False and vice versa, so it selects all rows where the condition is not met`

        if self.type_2 in ['Race', 'Sprint']:
            driver_laps.loc[driver_laps['LapNumber'].isin([1,2]), 'TimedLapTime'] = pd.NA
        driver_laps.loc[driver_laps['TrackStatus'] != '1', 'TimedLapTime'] = pd.NA
        driver_laps.loc[driver_laps['Deleted'] == True, 'TimedLapTime'] = pd.NA
        driver_laps.loc[driver_laps['IsAccurate'] == False, 'TimedLapTime'] = pd.NA

        driver_laps['Roll'] = driver_laps['TimedLapTime'].rolling(window=7).median()
        driver_laps['Roll2'] = driver_laps['TimedLapTime'].rolling(window=2).median()
        driver_laps.loc[driver_laps['Roll'].isna(), 'Roll'] = driver_laps['Roll2']
        driver_laps['Roll'] = driver_laps['Roll'].bfill().ffill()
        driver_laps['Diff'] = (driver_laps['TimedLapTime'] - driver_laps['Roll']).abs()
        threshold = driver_laps['Diff'].mean() * 2.5
        driver_laps.loc[driver_laps['TimedLapTime'] - driver_laps['Roll'] > threshold,'TimedLapTime'] = pd.NA
        driver_laps.loc[driver_laps['TimedLapTime'] == driver_laps['TimedLapTime'].max(), 'TimedLapTime'] = pd.NA

            
            # if not driver_laps.loc[x, 'IsAccurate']:
            #     driver_laps.loc[x,'TimedLapTime'] = pd.NA
            # if driver_laps.loc[x, 'TrackStatus'] != '1':
            #     driver_laps.loc[x, 'TimedLapTime'] = pd.NA
            # if driver_laps.loc[x,'LapNumber'] == 1 or driver_laps.loc[x,'LapNumber'] == 2:
            #     driver_laps.loc[x,'TimedLapTime'] = pd.NA
            # if driver_laps.loc[x,'Deleted']:
            #     driver_laps.loc[x,'TimedLapTime'] = pd.NA
            # if driver_laps.loc[x,'TimedLapTime']  - driver_laps['TimedLapTime'].mean() > 2:
            #     driver_laps.loc[x,'TimedLapTime'] = pd.NA
        
   
        driver_laps['Color'] = color_list

        
        return driver_laps



    def _format_practice_laps(self, initials, lap_list):

        df = self._convert_stint_times(initials)

        df = df[df['LapNumber'].isin(lap_list)].copy().reset_index(drop=True)

        df['LapNumber'] = list(range(1, len(df.index) + 1))

        df['FuelLvl'] = df['LapNumber'] * self.avg_fuel_usage
        df['FuelLvl'] = df['FuelLvl'].values[::-1]
        df['TimeLoss'] = df['FuelLvl'] * self.time_loss
        df['LapTimeFc'] = df['LapTime'] - df['TimeLoss']
        df['TimedLapTimeFc'] = df['TimedLapTime'] - df['TimeLoss']

        
        return df



    
    def _format_session_laps(self, initials):
        if not isinstance(initials, list):
            initials = [initials]
        
        time_loss = pd.Series(self._calculate_time_loss())
        data = [self._convert_stint_times(x) for x in initials]
        
        
        for x in data:
            # if len(time_loss) < len(x.index):

            #     while len(time_loss) < len(x.index):
            #         time_loss.append(pd.NA)
                
            x['TimeLoss'] = time_loss[:len(x.index)]
            x['LapTimeFc'] = x['LapTime'] - x['TimeLoss']
            x['TimedLapTimeFc'] = x['TimedLapTime'] - x['TimeLoss']
        
        return data
    
    def _calculate_time_loss(self):
        race_distance = self.race_distance
        if self.year < 2026:
            capacity = 105
        else:
            capacity = 70
        fuel_burn = capacity / race_distance
        total_fuel = capacity
        fuel_lvl_per_lap = []

        try:
            for x in list(range(1, race_distance + 1)):
                fuel_lvl_per_lap.append(total_fuel)
                total_fuel -= fuel_burn
        except:
            for x in list(range(1, race_distance.astype(int) + 1)):
                fuel_lvl_per_lap.append(total_fuel)
                total_fuel -= fuel_burn
        time_loss_per_lap = []

        for x in fuel_lvl_per_lap:
            time_loss_per_lap.append(x * self.time_loss)
        
        if self.type == 'Sprint':
            new_time_loss = []
            for x in time_loss_per_lap:
                time = x * (1/3)
                new_time_loss.append(time)
            return new_time_loss
            
        
        return time_loss_per_lap
    
    def plot_all_drivers_positions(self, show_figs=False, return_figs=False):
        drivers = self.drivers

        dfs = self._format_session_laps(drivers)

        fig = make_subplots()

        for df in dfs:
            self._plot_race_position_tool(df, fig)
        
        if return_figs:
            return fig
        if show_figs:
            fig.show()

    def _plot_race_position_tool(self, df, fig):

        

        # tryna add the staarting grid position as lap 0

        df_2 = df.iloc[0:1].copy()

        df_2['LapNumber'] = 0

        df_2['Position'] = self._get_grid_position(df['Driver'].iloc[0])

        template = [(
            f'{df_2['Driver'].iloc[0]}<br>'
            f'Grid Pos {df_2['Position'].iloc[0]}'
        )]


        for lap, position, time, tyre, age in zip(df['LapNumber'], df['Position'], df['LapTimeFc'], df['Compound'], df['TyreLife']):
            try:
                age = int(age)
            except:
                pass
            text = (f"{df.loc[0, 'Driver']} | Lap {lap:.0f} | Pos {position:.0f}<br>"
                f"Time: {FastF1Analysis.convert_seconds_to_m_s_ms(time)}<br>" 
                f"Tyre: {tyre} ({(age)})"
            )
            template.append(text)
        
        df = pd.concat([df_2, df]).reset_index()
        
        fig.add_trace(go.Scatter(
            x=df['LapNumber'], y=df['Position'],
            name=df.loc[0, 'Driver'],
            hovertext=template,
            mode='lines+markers',
            marker=dict(color=df.loc[0, 'Color']),
            hoverinfo='text'           
        ))

        fig.update_layout(
            showlegend=True, 
            yaxis=dict(tickformat=','),
            title=f'{self.year} {self.title} {self.type}',
            template='plotly_dark', 
            margin=dict(l=5, r=5, t=30, b=40), 
            width=1200, height=680, 
        )
        fig.update_yaxes(title_text='Position', range=[self.results['Position'].max() + .5, .5])
        fig.update_xaxes(title_text='Lap', range=[-1, self.results['Laps'].max() + 1])
    
    def _plot_lap_times_tool(
        self, df, line_plot_fig=None, violin_plot_fig=None, line_plot_title=None, 
        violin_plot_title=None, fuel_corrected=False, driver_label=None, positions=False
    ):

        if fuel_corrected:
            lap_time = 'LapTimeFc'
            timed_lap_time = 'TimedLapTimeFc'
        else:
            lap_time = 'LapTime'
            timed_lap_time = 'TimedLapTime'
        
        if not driver_label:
            driver_label = f'{df.loc[0, 'Driver']} {FastF1Analysis.convert_seconds_to_m_s_ms(df[timed_lap_time].mean())}'

        if not line_plot_title:
            line_plot_title = f'{self.year} {self.title} {self.type}'
        if not violin_plot_title:
            violin_plot_title = f'{self.year} {self.title} {self.type}'

        if fuel_corrected:
            line_plot_title = f'{line_plot_title} Fuel Corrected'
            violin_plot_title = f'{violin_plot_title} Fuel Corrected'
            

        if line_plot_fig:
            
            template = []

            for lap, time, tyre, age in zip(df['LapNumber'], df[lap_time], df['Compound'], df['TyreLife']):
                    try:
                        age = int(age)
                    except:
                        pass
                    text = (
                        f"{df.loc[0, 'Driver']} | Lap {int(lap)}<br>"
                        f"Time: {FastF1Analysis.convert_seconds_to_m_s_ms(time)}<br>"
                        f"Tyre: {tyre[0]} ({(age)})"
                        )
                    template.append(text)
                
            line_plot_fig.add_trace(go.Scatter(
                x=df['LapNumber'], y=df[lap_time],
                name=driver_label,
                hovertext=template,
                mode='lines+markers',
                marker=dict(color=df.loc[0, 'Color']),
                line=dict(
                    color=df['Color'].iloc[0],
                    dash=self.driver_line_type[df['Driver'].iloc[0]]
                ),
                hoverinfo='text'  
            ))       

            line_plot_fig.update_layout(
                showlegend=True,
                legend=dict(orientation='h'),
                yaxis=dict(tickformat='.1f'),
                title=line_plot_title, 
                template='plotly_dark', 
                margin=dict(l=5, r=5, t=30, b=40), 
                width=1200, height=680, 
            )
            line_plot_fig.update_yaxes(title_text='Time (S)')
            line_plot_fig.update_xaxes(title_text='Lap')

        if violin_plot_fig:

            template = []

            for lap, time, tyre in zip(df['LapNumber'], df[lap_time], df['Compound']):
                text = f"{df.loc[0, 'Driver']} | Lap {int(lap)} | Time: {FastF1Analysis.convert_seconds_to_s_ms_short(time)} | Tyre: {tyre[0]}"
                template.append(text)

            violin_plot_fig.add_trace(go.Violin(
                y=df[timed_lap_time],
                name=driver_label,
                box_visible=True,
                meanline_visible=True,
                opacity=0.6,
                fillcolor=df.loc[0, 'Color'],
                line_color='white',
            ))

            violin_plot_fig.update_layout(
                showlegend=False, 
                yaxis=dict(tickformat='.2f'),
                xaxis=dict(tickformat=','),
                title=violin_plot_title,  
                template='plotly_dark',  
                margin=dict(l=5, r=5, t=30, b=40), 
                width=1200, height=680, 
            )

    def _get_drivers_pace(self, df_list):

        drivers = []
        color = []
        avg_pace = []
        avg_pace_fc = []
        color = []


        for df in df_list:
            drivers.append(df.loc[0, 'Driver'])
            avg_pace.append(df['TimedLapTime'].mean())
            avg_pace_fc.append(df['TimedLapTimeFc'].mean())
            color.append(df.loc[0,'Color'])
        avg_pace_dict = {
            'Driver': drivers,
            'Color': color,
            'Pace': avg_pace,
            'PaceFc': avg_pace_fc
        }

        avg_pace_df = pd.DataFrame(avg_pace_dict)

        avg_pace_df['GapS'] = avg_pace_df['Pace'] - avg_pace_df['Pace'].min()
        avg_pace_df['GapFcS'] = avg_pace_df['PaceFc'] - avg_pace_df['PaceFc'].min()
        avg_pace_df['Gap%'] = ((avg_pace_df['Pace'].min() - avg_pace_df['Pace']) / avg_pace_df['Pace'].min() * 100).abs().round(2)
        avg_pace_df['GapFc%'] = ((avg_pace_df['PaceFc'].min() - avg_pace_df['PaceFc']) / avg_pace_df['PaceFc'].min() * 100).abs().round(2)

        return avg_pace_df
    
    def _quali_analysis(self, top_ten=False, teams=False):

        name = 'Driver'
        text_name = 'Driver'

        if teams:
            drivers = self.lead_drivers

        else:
            drivers = self._get_all_drivers_names()

            if top_ten:
                drivers = drivers[:10]

        drivers_data = []

        for driver in drivers:
            try:
                telem_df = self.session.laps.pick_drivers(driver).pick_fastest().get_telemetry().add_distance()
            except:
                break
            top_speed = telem_df['Speed'].max()
            avg_speed = telem_df['Speed'].mean()
            min_speed = telem_df['Speed'].min()
            full_throttle_percentage = (len(telem_df[telem_df['Throttle'] == 100]) / len(telem_df.index)) * 100



            data = self.session.laps.pick_drivers(driver).pick_fastest()
            data_df = pd.DataFrame(data).T.reset_index(drop=True)
            data_df = data_df.copy()
            data_df.loc[0, 'LapTime'] = data_df.loc[0, 'LapTime'].total_seconds()
            data_df.loc[0,'Color'] = plotting.get_driver_color(driver,self.session)
            data_df.loc[0,'TopSpeed'] = top_speed
            data_df.loc[0,'MinSpeed'] = min_speed
            data_df.loc[0,'AvgSpeed'] = avg_speed 
            data_df.loc[0,'FullThrottle%'] = full_throttle_percentage
            data_df.loc[0,'Sector1Time'] = data_df.loc[0,'Sector1Time'].total_seconds()
            data_df.loc[0,'Sector2Time'] = data_df.loc[0,'Sector2Time'].total_seconds()
            data_df.loc[0,'Sector3Time'] = data_df.loc[0,'Sector3Time'].total_seconds()

            drivers_data.append(data_df)

            df = pd.concat(drivers_data, ignore_index=True)
        
        return df
    
    def _quali_session_analysis(self, session):

        qual_s = self.results_raw[~self.results_raw[session].isna()][['Abbreviation', session]].sort_values(by=session).reset_index(drop=True)
        drivers = qual_s['Abbreviation'].to_list()

        drivers_data = []

        for driver in drivers:

            df = qual_s[qual_s['Abbreviation'] == driver].reset_index(drop=True)
            driver_lap_time = df[session].iloc[0]

            driver_laps = self.session.laps.pick_drivers(driver)
            driver_lap = driver_laps[driver_laps['LapTime'] == driver_lap_time].reset_index(drop=True)
            lap_number = driver_lap['LapNumber'].iloc[0].item()
            
            telem_df = self.session.laps.pick_drivers(driver).pick_laps(lap_number).get_telemetry().add_distance()
            data_df = self.session.laps.pick_drivers(driver).pick_laps(lap_number)[['Driver', 'LapTime','Sector1Time','Sector2Time','Sector3Time', 'SpeedST']].reset_index(drop=True)

            
            top_speed = telem_df['Speed'].max()
            avg_speed = telem_df['Speed'].mean()
            min_speed = telem_df['Speed'].min()
            full_throttle_percentage = (len(telem_df[telem_df['Throttle'] == 100]) / len(telem_df.index)) * 100


            data_df['LapTime'] = data_df['LapTime'].dt.total_seconds()
            data_df['Sector1Time'] = data_df['Sector1Time'].dt.total_seconds()
            data_df['Sector2Time'] = data_df['Sector2Time'].dt.total_seconds()
            data_df['Sector3Time'] = data_df['Sector3Time'].dt.total_seconds()
            
            data_df.loc[0,'Color'] = plotting.get_driver_color(driver,self.session)
            data_df.loc[0,'TopSpeed'] = top_speed
            data_df.loc[0,'MinSpeed'] = min_speed
            data_df.loc[0,'AvgSpeed'] = avg_speed 
            data_df.loc[0,'FullThrottle%'] = full_throttle_percentage

            drivers_data.append(data_df)

            df = pd.concat(drivers_data, ignore_index=True)
        
        return df


    def plot_quali_analysis(self, top_ten=False, teams=False, session=None, show=False, return_figs=False):


        if teams:
            name = 'Team'
        else:
            name = 'Driver'
        
        if session:
            drivers_df = self._quali_session_analysis(session)
        else:
            drivers_df = self._quali_analysis(top_ten=top_ten, teams=teams)

        fig_lap_time = make_subplots()
        fig_speed_trap = make_subplots()
        fig_full_throttle = make_subplots()
        fig_sector_one = make_subplots()
        fig_sector_two = make_subplots()
        fig_sector_three = make_subplots()

        if self.year == 2026:
            figs = [fig_lap_time, fig_sector_one, fig_sector_two, fig_sector_three, fig_speed_trap]
            values = ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedST']
        else:

            fig_top_speed = make_subplots()
            fig_min_speed = make_subplots()
            fig_avg_speed = make_subplots()
            fig_full_throttle = make_subplots()

            figs = [fig_lap_time, fig_sector_one, fig_sector_two, fig_sector_three, fig_speed_trap, fig_top_speed, fig_min_speed, fig_avg_speed, fig_full_throttle]
            values = ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'SpeedST', 'TopSpeed', 'MinSpeed', 'AvgSpeed','FullThrottle%']


        def make_text(df, value, percentage=False):
            if percentage:
                percentage = '%'
            else:
                percentage = ''
            
            text_list = []


            for x in df.index:

                if value in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
                    
                    diff = df.loc[x, value] - df.loc[df.index[-1], value]
                    perc = (diff / df.loc[df.index[-1], value]) * 100

                    if value == 'LapTime':
                        time = f'{self.convert_seconds_to_m_s_ms(df.loc[x, 'LapTime'])}'
                    else:
                        time = f'{self.convert_seconds_to_s_ms(df.loc[x, value])}'


                    
                    text = (
                        f'{df.loc[x, 'Driver']} | '
                        f'{time} | '
                        f'{diff:.2f}{percentage} | '
                        f'{perc:.2f}%'
                    )

                    text_list.append(text)
                else:
                
                    val = df.loc[x, value]
                    diff = df.loc[x, value] - df.loc[df.index[-1], value]

                    
                    text = (
                        f'{df.loc[x, 'Driver']} | '
                        f'{self.convert_seconds_to_m_s_ms(df.loc[x, 'LapTime'])} | '
                        f'{val:.2f}{percentage} | '
                        f'{diff:.2f}{percentage} | '
                    )

                    text_list.append(text)

            return text_list

        for value, fig in zip(values, figs):

            if value == 'FullThrottle%':
                boolean = True
            else:
                boolean = False


            df = drivers_df.sort_values(by=value).reset_index(drop=True)
        
            if value in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
                df = df[::-1]


            text = make_text(df, value, percentage=boolean)

            minimum = df[value].min() - (.001 * df[value].min())
            maximum = df[value].max() + (.001 * df[value].max())
            

            self._plot_graphs_tool(df, value, name, fig, text, autoarange=None, 
                xaxis_range=[minimum, maximum]
                )
        
        if show:
            for fig in figs:
                fig.show()
        if return_figs:
            return figs

    def _plot_graphs_tool(
        self, df, x_ax, y_ax, fig, text,
        orientation='h', x_label=None, 
        y_label=None, autoarange='reversed',
        xaxis_range=None, yaxis_range=None

    ):
        
        if not y_label:
            y_label = y_ax
        if not x_label:
            x_label = x_ax

        
        fig.add_trace(go.Bar(
            x=df[x_ax],
            y=df[y_ax],
            marker_color=df['Color'],
            orientation=orientation,
            hovertext=text,
            textposition='none',
            hoverinfo='text'
        ))
        
        fig.update_layout(
            title=f'{self.year} {self.title} {self.type}',
            template='plotly_dark',
            width=1200, height=680,
            xaxis_range=xaxis_range,
            yaxis_range=yaxis_range,
        )
        
        fig.update_yaxes(title_text=y_label, autorange=autoarange)
        fig.update_xaxes(title_text=x_label)

    def _plot_pace_graphs_tool(self, df, fig=None, fig_fc=None):

        if fig:
            
            df = df.sort_values(by='Pace')
            
            text = []

            for x in df.index:
                label = (
                    f'{df.loc[x, 'Driver']} {self.convert_seconds_to_m_s_ms(df.loc[x, 'Pace'])}<br>'
                    f'GAP: +{df.loc[x, 'GapS']:.2f} | '
                    f'+{df.loc[x, 'Gap%']}%'
                    )

                
                text.append(label)
            df = df.sort_values(by='Pace')
            fig.add_trace(go.Bar(
                x=df['Pace'],
                y=df['Driver'],
                marker_color=df['Color'],
                orientation='h',
                hovertext=text,
                textposition='none',
                hoverinfo='text'
                ))
            fig.update_layout(
                title=f'{self.year} {self.title} {self.type} Pace',
                template='plotly_dark',
                width=1200, height=680,
                xaxis_range=[df['Pace'].min() - .25 , df['Pace'].max() + .25]
                )
            fig.update_yaxes(title_text='Drivers', autorange="reversed")
            fig.update_xaxes(title_text='Time (S)')

        if fig_fc:

            df = df.sort_values(by='PaceFc')
            
            text = []

            for x in df.index:
                label = (
                    f'{df.loc[x, 'Driver']} {self.convert_seconds_to_m_s_ms(df.loc[x, 'PaceFc'])}<br>'
                    f'GAP: +{df.loc[x, 'GapFcS']:.2f} | '
                    f'+{df.loc[x, 'GapFc%']}%'
                    )

                
                text.append(label)

            fig_fc.add_trace(go.Bar(
                x=df['PaceFc'],
                y=df['Driver'],
                marker_color=df['Color'],
                orientation='h',
                hovertext=text,
                textposition='none',
                hoverinfo='text'
            ))
            fig_fc.update_layout(
                title=f'{self.year} {self.title} {self.type} Pace Fuel Corrected',
                template='plotly_dark',
                width=1200, height=680,
                xaxis_range=[df['PaceFc'].min() - .25 , df['PaceFc'].max() + .25]
            )
            fig_fc.update_yaxes(title_text='Drivers', autorange="reversed")
            fig_fc.update_xaxes(title_text='Time (S)')
    
    def _gap_to_leader_tool(self, data, drivers):
        
        driver_names = []
        driver_avg_pace = []
        driver_avg_pace_fc = []

        for df in data:
            driver_names.append(df.loc[0, 'Driver'])
            
            try:
                driver_avg_pace.append(df['TimedLapTime'].mean())
            except:
                driver_avg_pace.append(pd.NA)

            try:
                driver_avg_pace_fc.append(df['TimedLapTimeFc'].mean())
            except:
                driver_avg_pace_fc.append(pd.NA)

        gap_to_leader_df = pd.DataFrame()

        gap_to_leader_df['Driver'] = driver_names
        gap_to_leader_df['AvgPace'] = driver_avg_pace
        gap_to_leader_df['AvgPaceFc'] = driver_avg_pace_fc

        gap_to_leader_df = gap_to_leader_df.sort_values(by='AvgPace')
        gap_to_leader_df_fc = gap_to_leader_df.sort_values(by='AvgPaceFc')

        gap_to_leader_df['GapToLeader'] = gap_to_leader_df['AvgPace'] - gap_to_leader_df.loc[0, 'AvgPace']
        gap_to_leader_df_fc['GapToLeader'] = gap_to_leader_df_fc['AvgPaceFc'] - gap_to_leader_df_fc.loc[0, 'AvgPaceFc']

        gap_to_leader_df = gap_to_leader_df.set_index('Driver')
        gap_to_leader_df_fc = gap_to_leader_df_fc.set_index('Driver')

        gap_to_leader_df = gap_to_leader_df.reindex(drivers)
        gap_to_leader_df_fc = gap_to_leader_df_fc.reindex(drivers)

        gap_to_leader = gap_to_leader_df['GapToLeader'].to_list()
        gap_to_leader_fc = gap_to_leader_df_fc['GapToLeader'].to_list()



        label = []
        label_fc = []

        for driver, gap_1, gap_2 in zip(drivers, gap_to_leader, gap_to_leader_fc):

            label.append(f'{driver} {FastF1Analysis.convert_seconds_to_s_ms_short(gap_1)}')
            label_fc.append(f'{driver} {FastF1Analysis.convert_seconds_to_s_ms_short(gap_2)}')
        
        return [label, label_fc]
        
    def plot_race_stint(self, drivers=None, top_ten=False, teams=False, all_drivers=False, order_by_pace=False, gap_to_leader=False, return_figs=False, show_figs=False):
        if drivers:
            if not isinstance(drivers, list):
                drivers = [drivers]
            drivers = self._order_by_finishing_pos(drivers)
    
                
        elif all_drivers:
            drivers = self._get_all_drivers_names()
        
        elif top_ten:
            drivers = self._get_all_drivers_names()[:10]

        elif teams:
            drivers = self._get_lead_driver()

        if order_by_pace:
            drivers = self._order_by_avg_pace(drivers)
        
        data = self._format_session_laps(drivers)

        pace = self._order_by_avg_pace(drivers)
        pace = self._format_session_laps(pace)

        

        if gap_to_leader:
            label = self._gap_to_leader_tool(data, drivers)[0]
            label_fc = self._gap_to_leader_tool(data, drivers)[1]

            label_p = []
            label_fc_p = []
            
            driver_name = []
            pace_ = []
            pace_fc_ = []

            for df in pace:
                driver_name.append(df.loc[0, 'Driver'])
                pace_.append(df['TimedLapTime'].mean())
                pace_fc_.append(df['TimedLapTimeFc'].mean())
                
            pace_df_ = pd.DataFrame({
                'Driver': driver_name,
                'Pace': pace_,
                'PaceFc': pace_fc_
            })

            for x in pace_df_.index:
                label_p.append(f"{pace_df_.loc[x, 'Driver']} {FastF1Analysis.convert_seconds_to_s_ms_short(pace_df_.loc[x, 'Pace'] - pace_df_.loc[0, 'Pace'])}")
                label_fc_p.append(f"{pace_df_.loc[x, 'Driver']} {FastF1Analysis.convert_seconds_to_s_ms_short(pace_df_.loc[x, 'PaceFc'] - pace_df_.loc[0, 'PaceFc'])}")
        else:
            label = []
            label_p = []
            label_fc = []
            label_fc_p = []

            for df, df_p in zip(data, pace):
                label.append(f'{df.loc[0, 'Driver']} {FastF1Analysis.convert_seconds_to_m_s_ms(df['TimedLapTime'].mean())}')
                label_p.append(f'{df_p.loc[0, 'Driver']} {FastF1Analysis.convert_seconds_to_m_s_ms(df_p['TimedLapTime'].mean())}')

                label_fc.append(f'{df.loc[0, 'Driver']} {FastF1Analysis.convert_seconds_to_m_s_ms(df['TimedLapTimeFc'].mean())}')
                label_fc_p.append(f'{df_p.loc[0, 'Driver']} {FastF1Analysis.convert_seconds_to_m_s_ms(df_p['TimedLapTimeFc'].mean())}')

        # figs

        all_laps_df = pd.concat(data).reset_index(drop=True)

        fig_lap_times = make_subplots()
        fig_lap_times_fc = make_subplots()

        fig_lap_times_violin = make_subplots()
        fig_lap_times_fc_violin = make_subplots()

        
        
        fig_pace = make_subplots()
        fig_pace_fc = make_subplots()


        for df, df_p, lab, lab_fc, lab_p, lab_fc_p in zip(data, pace, label, label_fc, label_p, label_fc_p):
            self._plot_lap_times_tool(df, line_plot_fig=fig_lap_times, driver_label=lab)
            self._plot_lap_times_tool(df_p, violin_plot_fig=fig_lap_times_violin, driver_label=lab_p)

            self._plot_lap_times_tool(df, line_plot_fig=fig_lap_times_fc, driver_label=lab_fc, fuel_corrected=True)
            self._plot_lap_times_tool(df_p, violin_plot_fig=fig_lap_times_fc_violin, driver_label=lab_fc_p, fuel_corrected=True)
            
            
        
        self._plot_pace_graphs_tool(self._get_drivers_pace(pace), fig=fig_pace, fig_fc=fig_pace_fc)

        for fig, fc in zip([fig_lap_times, fig_lap_times_fc], ['', 'Fc']):
            fig.update_yaxes(title_text='Time (S)', range=[all_laps_df[f'LapTime{fc}'].min() - 1.5, all_laps_df[all_laps_df['TrackStatus'] == '1']['LapTime'].max() + 1])
            fig.update_xaxes(title_text='Lap', range=[all_laps_df[all_laps_df['TrackStatus'] == '1']['LapNumber'].min() - .5, self.results['Laps'].max() + 1])

        if show_figs:
            for fig in [fig_lap_times, fig_lap_times_fc, fig_lap_times_violin, fig_lap_times_fc_violin, fig_pace, fig_pace_fc]:
                fig.show()

        if return_figs:
            return [fig_lap_times, fig_lap_times_violin , fig_pace, fig_lap_times_fc, fig_lap_times_fc_violin, fig_pace_fc]


    def plot_strategies(self, return_figs=False, show=False):

        formatted_dfs = []

        stints_dfs = []

        stints_summaries = []
        
        formatted_dfs = self._format_session_laps(self.drivers)


        
        for df in formatted_dfs:

            stints = df['Stint'].drop_duplicates().to_list()

            for stint in stints:
                stint_df = df[df['Stint'] == stint].reset_index(drop=True)
                stints_dfs.append(stint_df)

        for df in stints_dfs:
            
            if df.empty:
                continue

            stint_dict = {
                'Driver': [df['Driver'].iloc[0]],
                'AvgLapTime': [df['TimedLapTime'].mean()],
                'AvgLapTimeFc': [df['TimedLapTimeFc'].mean()],
                'Stint': [df['Stint'].iloc[0]],
                'StintStart': [df['LapNumber'].iloc[0]],
                'StintEnd': [df['LapNumber'].iloc[-1]],
                'StintLength': [df['LapNumber'].iloc[-1] - df['LapNumber'].iloc[0]],
                'Compound': [df['Compound'].iloc[0]],
                'FreshTyre': [df['FreshTyre'].iloc[0]],
                'Color': self._get_compound_color(df['Compound'].iloc[0]),
                'Length+1': [(df['LapNumber'].iloc[-1] - df['LapNumber'].iloc[0]) + 1]
            }
            df = pd.DataFrame(stint_dict)
            stints_summaries.append(df)
        
        texts = []

        for df in stints_summaries:
            label = (
                f'{df['Driver'].iloc[0]} | '
                f'AVG: {self.convert_seconds_to_s_ms(df['AvgLapTime'].iloc[0])} | FC: {self.convert_seconds_to_s_ms(df['AvgLapTimeFc'].iloc[0])}<br>' # makes a new line
                f'Tyre: {df['Compound'].iloc[0]} | New Set: {df['FreshTyre'].iloc[0]}<br>'
                f'Stint: {df['Stint'].iloc[0].astype(int)} | '
                f'Length: {df['StintLength'].iloc[0].astype(int) + 1} | '
                f'Range: {df['StintStart'].iloc[0].astype(int)}-{df['StintEnd'].iloc[0].astype(int)} |'
            )    
            texts.append(label)
        
        fig = make_subplots()

        for df, text in zip(stints_summaries, texts):
            fig.add_traces(go.Bar(
                x=df['Length+1'],
                y=df['Driver'],
                name=df['Driver'].iloc[0],
                marker_color=df['Color'].iloc[0],
                orientation='h',
                hovertext=text,
                textposition='none',
                hoverinfo='text'
            ))
        fig.update_layout(
            title=f'{self.year} {self.title} {self.type} Strategies',
            template='plotly_dark',
            width=1200, height=680,
            barmode='stack',
            showlegend=False
            )
        fig.update_yaxes(title_text='Drivers', autorange='reversed')
        fig.update_xaxes(title_text='Laps')
        
        if show:
            fig.show()
        if return_figs:
            return fig
        




    def plot_by_lap_numbers(self, drivers_initials, lap_list=None, lap_ranges=None, lap_range=None, order_by_pace=False, show_figs=False, return_figs=False):
        # NEEDS MORE TESTING
        # FC BROKEN WORKS FOR RACE NOT PRACTICE SESSIONS
        
        def order_dfs_by_pace(df_list):
            dfs_dict = {}

            for df in df_list:
                name = df.loc[0,'Driver']
                dfs_dict[name] = df
            
            drivers = []
            drivers_pace = []

            for df in df_list:
                drivers.append(df.loc[0, 'Driver'])
                drivers_pace.append(df['TimedLapTime'].mean())
            
            pace_df = pd.DataFrame({
                'Driver': drivers,
                'Pace': drivers_pace
            })

            pace_df = pace_df.sort_values(by='Pace').reset_index(drop=True)

            new_df_list = []

            for driver in pace_df['Driver'].to_list():
                new_df_list.append(dfs_dict[driver])
            
            return new_df_list

        if not isinstance(drivers_initials,list):
            drivers_initials = [drivers_initials]
        
        if lap_list:
            if not isinstance(lap_list, list):
                lap_list = [lap_list]
            if len(drivers_initials) != len(lap_list):
                print('drivers_initials and stint_list does not match')
                return
        if lap_ranges:
            lap_list = []
            for laps in lap_ranges:
                if len(laps) != 2:
                    print('stint_ranges needs to be a list of lists of 2 integers. Starting and ending lap')
                    return
                else:
                    lap_list.append(list(range(laps[0], laps[1] + 1)))
            
            if len(drivers_initials) != len(lap_list):
                print('drivers_initials and stint_list does not match')
                return
        
        if lap_range:
            if len(lap_range) != 2:
                print('stint_range needs to be a list of 2 integers. Starting and ending lap')
                return
            else:
                lap_list = []
                for driver in drivers_initials:
                    lap_list.append(list(range(lap_range[0], lap_range[1] + 1)))

        
        driver_data = []

        if self.type != 'Race':

            driver_data = []

            for driver, laps in zip(drivers_initials, lap_list):
                df = self._format_practice_laps(driver, laps)

                driver_data.append(df)

        
            # for driver, laps in zip(drivers_initials, lap_list):
                
                    # driver_df = self._convert_stint_times(driver)
                    # driver_df = driver_df[driver_df['LapNumber'].isin(laps)].copy()
                    # driver_df['StintLaps'] = list(range(1, len(list(driver_df.index)) + 1))
                    # driver_df['LapNumber'] = driver_df['StintLaps'].copy()
                    # driver_df = driver_df.reset_index(drop=True)
                    # driver_df['TimeLoss'] = self._time_loss_calc(laps)
                    # driver_df['LapTimeFc'] = driver_df['LapTime'] - driver_df['TimeLoss']
                    # driver_df['TimedLapTimeFc'] = driver_df['TimedLapTime'] - driver_df['TimeLoss']


                    # driver_data.append(driver_df)
        else:
            
            drivers = self._format_session_laps(drivers_initials)
            
            for df, laps in zip(drivers, lap_list):
                
                df = df[df['LapNumber'].isin(laps)].copy()
                df = df.reset_index(drop=True)
                
                driver_data.append(df)  
        
        if order_by_pace:
            driver_data = order_dfs_by_pace(driver_data)

        
        fig_lap_times = make_subplots()
        fig_lap_times_fc = make_subplots()
        fig_violin_lap_times = make_subplots()
        fig_violin_lap_times_fc = make_subplots()
        
        for stint in driver_data:
            
            self._plot_lap_times_tool(stint, line_plot_fig=fig_lap_times, line_plot_title=f'{self.title} {self.type}')
            self._plot_lap_times_tool(stint, violin_plot_fig=fig_violin_lap_times, violin_plot_title=f'{self.title} {self.type}')
            self._plot_lap_times_tool(stint, line_plot_fig=fig_lap_times_fc, line_plot_title=f'{self.title} {self.type}', fuel_corrected=True)
            self._plot_lap_times_tool(stint, violin_plot_fig=fig_violin_lap_times_fc, violin_plot_title=f'{self.title} {self.type}', fuel_corrected=True)

        if show_figs:
            for fig in [fig_lap_times, fig_violin_lap_times, fig_lap_times_fc, fig_violin_lap_times_fc]:
                fig.show()
        if return_figs:
            return [fig_lap_times, fig_violin_lap_times, fig_lap_times_fc, fig_violin_lap_times_fc]
        
    
    def plot_lap_telem(self, drivers=None,laps=None, same_laps=None,all_drivers=False, teams=False, top_ten=False, show_figs=False, return_figs=False):
        if all_drivers or top_ten:
            drivers = self._get_all_drivers_names()
            name = 'Driver'
            if top_ten:
                drivers = drivers[:10]
        elif drivers:
            name = 'Driver'
            if not isinstance(drivers, list):
                drivers = [drivers] 
        elif teams:
            drivers = self._get_lead_driver()
            name = 'Team'

        
        if not laps:
            driver_initials = self._order_by_finishing_pos(drivers)
        else:
            driver_initials = drivers
        
        drivers_data = []

        if laps:
            if not isinstance(laps, list):
                laps = [laps]
            
            driver_name = []
            driver_lap = []
            driver_time = []
            
            for driver, lap in zip(driver_initials, laps):
                driver_lap.append(lap)
                driver_time.append(self.session.laps.pick_drivers(driver).pick_laps(lap)['LapTime'].dt.total_seconds().item())
                driver_name.append(driver)
                
                # driver_dict = self._convert_fastest_lap(driver, lap=lap)
                # drivers_data.append(driver_dict)
            
            laps_df = pd.DataFrame()

            laps_df['Driver'] = driver_name
            laps_df['Lap'] = driver_lap
            laps_df['Time'] = driver_time

            laps_df = laps_df.sort_values(by='Time')

            driver_initials = laps_df['Driver'].to_list()
            laps = laps_df['Lap'].to_list()

            for driver, lap in zip(driver_initials, laps):
                driver_dict = self._convert_fastest_lap(driver, lap=lap)
                drivers_data.append(driver_dict)

        else:
        
            for driver in driver_initials:
                driver_dict = self._convert_fastest_lap(driver)
                drivers_data.append(driver_dict)

        
        fig = make_subplots(rows=4, cols=1,
                            row_heights=[0.6, 0.15, 0.15, .1],
                            shared_xaxes=True)
        
        for driver_dict in drivers_data:


            details, telem = driver_dict['Details'][0], driver_dict['Details'][1]

            hover_info = []
            for d,s in zip(telem['Distance'], telem['Speed']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}km/h')


            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Speed'],
                name = f'{details[name]} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=True,
                hovertext=hover_info,
                hoverinfo='text'),
                row=1,col=1
                )
            
            hover_info = []
            for d,s in zip(telem['Distance'], telem['Throttle']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}%')
        
            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Throttle'],
                name = f'{details[name]} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=2, col=1
                )

            hover_info = []
            for d,s in zip(telem['Distance'], telem['Brake']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}')
            
            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Brake'],
                name = f'{details[name]} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=3, col=1
                )
            
            hover_info = []
            for d,s in zip(telem['Distance'], telem['nGear']):
                hover_info.append(f'{details['Driver']} {round(d)}m, Gear:{round(s)}')

            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['nGear'],
                name = f'{details[name]} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=4, col=1
                )
        
        fig.update_layout(
            yaxis=dict(tickformat='.0f'),
            title= f'{self.title} {self.type} {self.year}',
            template='plotly_dark', 
            margin=dict(l=5, r=5, t=30, b=40), 
            width=1200, height=900)
        fig.update_yaxes(title_text='Speed km/h', row=1, col=1)
        fig.update_yaxes(title_text='Throttle %', row=2, col=1)
        fig.update_yaxes(title_text='Brake', row=3, col=1)
        fig.update_yaxes(title_text='Gear', row=4, col=1)

        if show_figs:
            fig.show()
        if return_figs:
            return fig

    def plot_qual_session_telem(self, session, return_figs=False, show_figs=False):

        qual_s = self.results_raw[~self.results_raw[session].isna()][['Abbreviation', session]].sort_values(by=session).reset_index(drop=True)
        driver_initials = qual_s['Abbreviation'].to_list()

        drivers_data = []

        for driver in driver_initials:
            df = qual_s[qual_s['Abbreviation'] == driver].reset_index(drop=True)
            driver_lap_time = df[session].iloc[0]

            driver_laps = self.session.laps.pick_drivers(driver)
            driver_lap = driver_laps[driver_laps['LapTime'] == driver_lap_time].reset_index(drop=True)
            lap_number = driver_lap['LapNumber'].iloc[0].item()
            
            
            driver_dict = self._convert_fastest_lap(driver, lap=lap_number)
            drivers_data.append(driver_dict)

        
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.6, 0.15, 0.15, .1],
            shared_xaxes=True
        )
        
        for driver_dict in drivers_data:

            details, telem = driver_dict['Details'][0], driver_dict['Details'][1]

            hover_info = []
            for d,s in zip(telem['Distance'], telem['Speed']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}km/h')


            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Speed'],
                name = f'{details['Driver']} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=True,
                hovertext=hover_info,
                hoverinfo='text'),
                row=1,col=1
                )
            
            hover_info = []
            for d,s in zip(telem['Distance'], telem['Throttle']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}%')
        
            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Throttle'],
                name = f'{details['Driver']} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=2, col=1
                )

            hover_info = []
            for d,s in zip(telem['Distance'], telem['Brake']):
                hover_info.append(f'{details['Driver']} {round(d)}m, {round(s)}')
            
            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['Brake'],
                name = f'{details['Driver']} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=3, col=1
                )
            
            hover_info = []
            for d,s in zip(telem['Distance'], telem['nGear']):
                hover_info.append(f'{details['Driver']} {round(d)}m, Gear:{round(s)}')

            fig.add_trace(go.Scatter(
                x=telem['Distance'], y=telem['nGear'],
                name = f'{details['Driver']} {details['LapTime']}',
                legendgroup=f'{details['Driver']} {details['LapTime']}',
                marker=dict(color=details['Color']),
                line=dict(color=details['Color'],
                    dash=self.driver_line_type[details['Driver']]),
                showlegend=False,
                hovertext=hover_info,
                hoverinfo='text'),
                row=4, col=1
                )
        
        fig.update_layout(
            yaxis=dict(tickformat='.0f'),
            title= f'{self.year} {self.title} {session}',
            template='plotly_dark', 
            margin=dict(l=5, r=5, t=30, b=40), 
            width=1200, height=900)
        fig.update_yaxes(title_text='Speed km/h', row=1, col=1)
        fig.update_yaxes(title_text='Throttle %', row=2, col=1)
        fig.update_yaxes(title_text='Brake', row=3, col=1)
        fig.update_yaxes(title_text='Gear', row=4, col=1)

        if show_figs:
            fig.show()

        if return_figs:
            return fig


    @staticmethod
    def convert_seconds_to_m_s_ms(total_seconds):
        if pd.isna(total_seconds):
            return pd.NA
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int(round((total_seconds - int(total_seconds)) * 1000))
        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"

    @staticmethod
    def convert_seconds_to_s_ms(total_seconds):
        if pd.isna(total_seconds):
            return pd.NA
        seconds = int(total_seconds % 60)
        milliseconds = int(round((total_seconds - int(total_seconds)) * 1000))
        return f"{seconds:02d}.{milliseconds:03d}"

    @staticmethod
    def convert_seconds_to_s_ms_short(total_seconds):
        if pd.isna(total_seconds):
            return pd.NA
        if total_seconds < 0:
            return f"{total_seconds:.2f}"
        seconds = total_seconds % 60
        return f"{seconds:.2f}"