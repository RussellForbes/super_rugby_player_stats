import numpy as np
import pandas as pd
import glob
import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Data Import
stats_path = '/Users/russellforbes/Downloads/Super Rugby Player Reports/Stats'
stats_csv_files = glob.glob(stats_path + '/*.csv')

minutes_path = '/Users/russellforbes/Downloads/Super Rugby Player Reports/Playing Minutes'
minutes_csv_files = glob.glob(minutes_path + '/*.csv')

stats_list = (pd.read_csv(file) for file in stats_csv_files)
stats_df = pd.concat(stats_list, ignore_index=True)

minutes_list = (pd.read_csv(file) for file in minutes_csv_files)
minutes_df = pd.concat(minutes_list, ignore_index=True)
minutes_df.replace({'Brumbies 40 36 Waratahs': 'ACT Brumbies 40 36 NSW Waratahs',
                    'Blues 41 12 Waratahs': 'Blues 41 12 NSW Waratahs',
                    'Chiefs 19 6 Brumbies': 'Chiefs 19 6 ACT Brumbies',
                    'Hurricanes 45 42 Force': 'Hurricanes 45 42 Western Force',
                    'Drua 41 17 Reds': 'Fijian Drua 41 17 Queensland Reds',
                    'Moana 33 43 Rebels': 'Moana Pasifika 33 43 Melbourne Rebels',
                    'Chiefs 29 20 Reds': 'Chiefs 29 20 Queensland Reds',
                    'Crusaders 49 8 Drua': 'Crusaders 49 8 Fijian Drua',
                    'Force 19 43 Chiefs': 'Western Force 19 43 Chiefs',
                    'Reds 26 45 Blues': 'Queensland Reds 26 45 Blues'}, inplace=True)

stats_df.replace({'Brumbies 40 36 Waratahs': 'ACT Brumbies 40 36 NSW Waratahs',
                  'Blues 41 12 Waratahs': 'Blues 41 12 NSW Waratahs',
                  'Chiefs 19 6 Brumbies': 'Chiefs 19 6 ACT Brumbies',
                  'Hurricanes 45 42 Force': 'Hurricanes 45 42 Western Force',
                  'Drua 41 17 Reds': 'Fijian Drua 41 17 Queensland Reds',
                  'Moana 33 43 Rebels': 'Moana Pasifika 33 43 Melbourne Rebels',
                  'Chiefs 29 20 Reds': 'Chiefs 29 20 Queensland Reds',
                  'Crusaders 49 8 Drua': 'Crusaders 49 8 Fijian Drua',
                  'Force 19 43 Chiefs': 'Western Force 19 43 Chiefs',
                  'Reds 26 45 Blues': 'Queensland Reds 26 45 Blues'}, inplace=True)

fixtures_df = pd.read_csv('/Users/russellforbes/Downloads/super_rugby_full_fixtures.csv')
fixtures_df['Fixture'] = fixtures_df['Home Team'] + " " + fixtures_df['Home Score'].astype(str) + " " + fixtures_df[
    'Away Score'].astype(str) + " " + fixtures_df['Away Team']
fixtures_s = fixtures_df[['Fixture', 'Round']]
fixtures_s.set_index('Fixture', inplace=True)
fixtures_ss = fixtures_s.squeeze()

minutes_df['Round'] = minutes_df['Fixture'].map(fixtures_ss)
minutes_df['Round N'] = minutes_df['Round'].str.replace('round', '').astype(float)
minutes_df['Player Team'] = minutes_df['Player Name'] + " (" + minutes_df['Team'] + ")"

stats_df['Round'] = stats_df['Fixture'].map(fixtures_ss)
stats_df['Round N'] = stats_df['Round'].str.replace('round', '').astype(float)
stats_df['Player Team'] = stats_df['Player Name'] + " (" + stats_df['Team'] + ")"

# LIST OF PLAYERS TO START 10

tens = minutes_df[minutes_df['Starting Position'] == 10]
tens_total = tens.groupby('Player Team')['Minutes Played Total'].sum().reset_index()
tens_players = tens_total[tens_total['Minutes Played Total'] >= 160]['Player Team'].unique().tolist()

# MAP ON MINUTES TO STATS
minutes_s = minutes_df.groupby('Player Team')['Minutes Played Total'].sum().sort_values(ascending=False)

# print(stats_df.groupby('Player Team')['Tries'].sum().sort_values(ascending=False))


per_80_cols = ['Tries', 'Metres carried', 'Carries', 'Defenders beaten', 'Clean breaks', 'Passes', 'Offloads',
               'Turnovers conceded',
               'Try assists', 'Points', 'Tackles', 'Missed tackles', 'Turnovers won', 'Kicks in play', 'Conversions',
               'Penalty goals',
               'Drop goals', 'Throws won', 'Lineouts won', 'Penalties conceded']

# Making DF For 10s
tens_df = stats_df[stats_df['Player Team'].isin(tens_players)]
grouped_tens = tens_df.groupby(['Player Team', 'Player Name']).sum(numeric_only=True).reset_index()
grouped_tens['Minutes Played'] = grouped_tens['Player Team'].map(minutes_s)

for r in per_80_cols:
    grouped_tens[r + " per 80"] = grouped_tens[r] / grouped_tens['Minutes Played'] * 80
    loop_means = grouped_tens[r + " per 80"].mean()
    grouped_tens[r + " mean (per 80)"] = loop_means
    loop_std = grouped_tens[r + " per 80"].std()
    grouped_tens[r + " std (per 80)"] = loop_std
    grouped_tens[r + " std from mean"] = (grouped_tens[r + " per 80"] - loop_means) / loop_std

# print(grouped_tens[['Player Team', 'Minutes Played']].sort_values('Minutes Played', ascending=False).to_string())
# GROUPED DF FOR ALL PLAYERS
grouped_df = stats_df.groupby(['Player Team', 'Player Name']).sum(numeric_only=True).reset_index()
grouped_df['Minutes Played'] = grouped_df['Player Team'].map(minutes_s)
grouped_df = grouped_df[grouped_df['Minutes Played'] >= 160]

for r in per_80_cols:
    grouped_df[r + " per 80"] = grouped_df[r] / grouped_df['Minutes Played'] * 80
    loop_means = grouped_df[r + " per 80"].mean()
    grouped_df[r + " mean (per 80)"] = loop_means
    loop_std = grouped_df[r + " per 80"].std()
    grouped_df[r + " std (per 80)"] = loop_std
    grouped_df[r + " std from mean"] = (grouped_df[r + " per 80"] - loop_means) / loop_std

    grouped_df = grouped_df.copy()
    grouped_df[r + " Percentile"] = grouped_df[r].rank(pct=True)
    grouped_df[r + " per 80 Percentile"] = grouped_df[r + " per 80"].rank(pct=True)

# --------------------------------------------------------------------------------------------------------------------
team_list = minutes_df['Team'].unique().tolist()

st.set_page_config(page_title="2023 Super Rugby")
st.subheader('2023 Super Rugby Player Stats')

team_selection = st.selectbox('Team:', team_list)

team_players = minutes_df[minutes_df['Team'] == team_selection]['Player Name'].unique().tolist()

player_1_selection = st.selectbox('Player:', team_players)
single_player_df = grouped_df[grouped_df['Player Name'] == player_1_selection]
single_player_df['Y Position'] = np.random.uniform(-0.05, 0.05)

#st.dataframe(grouped_df[grouped_df['Player Name'] == player_1_selection][
#                 ['Player Name', 'Tries', 'Metres carried', 'Carries', 'Defenders beaten', 'Clean breaks', 'Passes',
#                  'Offloads', 'Turnovers conceded',
#                  'Try assists', 'Points', 'Tackles', 'Missed tackles', 'Turnovers won', 'Kicks in play']])

# y_position_list = np.linspace(0, 0, len(grouped_df['Player Name']))
y_position_list = np.random.uniform(-0.05, 0.05, len(grouped_df['Player Name']))

fig = make_subplots(rows=4, cols=1, vertical_spacing=0.1)

# TRACE 1
fig.add_trace(go.Scatter(y=y_position_list, x=grouped_df['Tries per 80'],
                         hovertext=grouped_df['Player Name'] + " " + round(grouped_df['Tries per 80'],
                                                                           2).astype(str),
                         hoverinfo='text',
                         mode='markers',
                         marker=dict(color='grey', size=20, opacity=0.25)),
              row=1, col=1)

fig.add_trace(go.Scatter(y=single_player_df['Y Position'], x=single_player_df['Tries per 80'],
                         hovertext=single_player_df['Player Name'], hoverinfo='text',
                         mode='markers+text',
                         text=round(single_player_df['Tries per 80'].iloc[0], 1).astype(
                             str) + " Tries per 80",
                         textposition='top center',
                         marker=dict(color='aqua', size=20,
                                     line=dict(width=2,
                                               color='black')
                                     ),
                         textfont=dict(color='white')), row=1, col=1)

# TRACE 2
fig.add_trace(go.Scatter(y=y_position_list, x=grouped_df['Clean breaks per 80'],
                         hovertext=grouped_df['Player Name'] + " " + round(grouped_df['Clean breaks per 80'],
                                                                           1).astype(str),
                         hoverinfo='text',
                         mode='markers', marker=dict(color='grey', size=20, opacity=0.25)), row=2, col=1)

fig.add_trace(go.Scatter(y=single_player_df['Y Position'], x=single_player_df['Clean breaks per 80'],
                         hovertext=single_player_df['Player Name'],
                         hoverinfo='text',
                         mode='markers+text',
                         text=round(single_player_df['Clean breaks per 80'].iloc[0], 1).astype(
                             str) + " Clean breaks per 80",
                         textposition='top center',
                         marker=dict(color='aqua', size=20,line=dict(width=2,
                                               color='black')),
                         textfont=dict(color='white')), row=2, col=1)

# TRACE 3
fig.add_trace(go.Scatter(y=y_position_list, x=grouped_df['Metres carried per 80'],
                         hovertext=grouped_df['Player Name'] + " " + round(grouped_df['Metres carried per 80'],
                                                                           1).astype(str),
                         hoverinfo='text',
                         mode='markers',
                         text=round(single_player_df['Metres carried per 80'].iloc[0], 1).astype(str),
                         marker=dict(color='grey', size=20, opacity=0.25)), row=3, col=1)

fig.add_trace(go.Scatter(y=single_player_df['Y Position'], x=single_player_df['Metres carried per 80'],
                         hovertext=single_player_df['Player Name'], hoverinfo='text',
                         mode='markers+text',
                         text=round(single_player_df['Metres carried per 80'].iloc[0], 1).astype(
                             str) + " Metres carried per 80",
                         textposition='top center',
                         marker=dict(color='aqua', size=20,line=dict(width=2,
                                               color='black')),
                         textfont=dict(color='white')), row=3, col=1)


# TRACE 4
fig.add_trace(go.Scatter(y=y_position_list, x=grouped_df['Defenders beaten per 80'],
                         hovertext=grouped_df['Player Name'] + " " + round(grouped_df['Defenders beaten per 80'],
                                                                           1).astype(str),
                         hoverinfo='text',
                         mode='markers',
                         text=round(single_player_df['Defenders beaten per 80'].iloc[0], 1).astype(str),
                         marker=dict(color='grey', size=20, opacity=0.25)), row=4, col=1)

fig.add_trace(go.Scatter(y=single_player_df['Y Position'], x=single_player_df['Defenders beaten per 80'],
                         hovertext=single_player_df['Player Name'], hoverinfo='text',
                         mode='markers+text',
                         text=round(single_player_df['Defenders beaten per 80'].iloc[0], 1).astype(
                             str) + " Defenders beaten per 80",
                         textposition='top center',
                         marker=dict(color='aqua', size=20,line=dict(width=2,
                                               color='black')),
                         textfont=dict(color='white')), row=4, col=1)

fig.update_layout(
    showlegend=False,
    xaxis=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    xaxis2=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    xaxis3=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    xaxis4=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    yaxis=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    yaxis2=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    yaxis3=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    yaxis4=dict(
        showline=False,
        showgrid=False,
        showticklabels=False
    ),
    title='Player Stats',
    height=600
)

st.plotly_chart(fig)
