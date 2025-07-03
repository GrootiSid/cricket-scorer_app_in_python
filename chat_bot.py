import streamlit as st
import pandas as pd
from io import BytesIO

# --- Helper Functions ---

def initialize_session_state():
    if 'match_started' not in st.session_state:
        st.session_state.match_started = False
        st.session_state.team1_name = "Team A"
        st.session_state.team2_name = "Team B"
        st.session_state.total_overs = 5
        st.session_state.toss_winner = ""
        st.session_state.toss_decision = ""
        st.session_state.batting_team = ""
        st.session_state.bowling_team = ""
        st.session_state.current_innings = 1
        st.session_state.match_over = False
        st.session_state.batting_team_inn1 = ""
        st.session_state.bowling_team_inn1 = ""
        st.session_state.batting_team_inn2 = ""
        st.session_state.bowling_team_inn2 = ""

        st.session_state.innings1 = {
            'runs': 0,
            'wickets': 0,
            'balls': 0,
            'batting_card': {},
            'bowling_card': {}
        }

        st.session_state.innings2 = {
            'runs': 0,
            'wickets': 0,
            'balls': 0,
            'batting_card': {},
            'bowling_card': {}
        }

        st.session_state.on_strike_batsman = ""
        st.session_state.off_strike_batsman = ""
        st.session_state.current_bowler = ""

def format_overs(balls):
    overs = balls // 6
    balls_in_over = balls % 6
    return f"{overs}.{balls_in_over}"

def create_excel_report():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_bat1 = pd.DataFrame.from_dict(st.session_state.innings1['batting_card'], orient='index')
        df_bat1.index.name = 'Batsman'
        df_bat1.to_excel(writer, sheet_name=f"{st.session_state.batting_team_inn1} Batting")

        df_bowl1 = pd.DataFrame.from_dict(st.session_state.innings1['bowling_card'], orient='index')
        df_bowl1.index.name = 'Bowler'
        df_bowl1.to_excel(writer, sheet_name=f"{st.session_state.bowling_team_inn1} Bowling")

        if st.session_state.innings2['batting_card']:
            df_bat2 = pd.DataFrame.from_dict(st.session_state.innings2['batting_card'], orient='index')
            df_bat2.index.name = 'Batsman'
            df_bat2.to_excel(writer, sheet_name=f"{st.session_state.batting_team_inn2} Batting")

        if st.session_state.innings2['bowling_card']:
            df_bowl2 = pd.DataFrame.from_dict(st.session_state.innings2['bowling_card'], orient='index')
            df_bowl2.index.name = 'Bowler'
            df_bowl2.to_excel(writer, sheet_name=f"{st.session_state.bowling_team_inn2} Bowling")

    return output.getvalue()

def render_setup_page():
    st.title("\U0001F3CF Cricket Match Setup")

    st.session_state.team1_name = st.text_input("Enter Team 1 Name", value=st.session_state.team1_name)
    st.session_state.team2_name = st.text_input("Enter Team 2 Name", value=st.session_state.team2_name)
    st.session_state.total_overs = st.number_input("Enter Total Overs per Innings", min_value=1, value=st.session_state.total_overs)

    st.session_state.toss_winner = st.selectbox("Who won the toss?", [st.session_state.team1_name, st.session_state.team2_name])
    st.session_state.toss_decision = st.radio("Toss Winner decided to:", ["Bat", "Bowl"])

    if st.button("Start Match"):
        st.session_state.match_started = True

        if st.session_state.toss_winner == st.session_state.team1_name:
            other_team = st.session_state.team2_name
        else:
            other_team = st.session_state.team1_name

        if st.session_state.toss_decision == "Bat":
            st.session_state.batting_team = st.session_state.toss_winner
            st.session_state.bowling_team = other_team
        else:
            st.session_state.batting_team = other_team
            st.session_state.bowling_team = st.session_state.toss_winner

        st.session_state.batting_team_inn1 = st.session_state.batting_team
        st.session_state.bowling_team_inn1 = st.session_state.bowling_team

        st.rerun()

def render_scoring_page():
    innings = st.session_state.current_innings
    innings_data = st.session_state[f'innings{innings}']
    batting_team = st.session_state.batting_team
    bowling_team = st.session_state.bowling_team

    st.title(f"Innings {innings}: {batting_team} vs {bowling_team}")

    overs_str = format_overs(innings_data['balls'])
    st.header(f"{batting_team}: {innings_data['runs']} / {innings_data['wickets']} ({overs_str} Overs)")

    if innings == 2:
        target = st.session_state.innings1['runs'] + 1
        runs_needed = target - innings_data['runs']
        balls_remaining = (st.session_state.total_overs * 6) - innings_data['balls']
        st.subheader(f"Target: {target} | Need {runs_needed} runs in {balls_remaining} balls")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.on_strike_batsman = st.text_input("On-Strike Batsman", key=f"on_strike_{innings}")
    with col2:
        st.session_state.off_strike_batsman = st.text_input("Off-Strike Batsman", key=f"off_strike_{innings}")
    with col3:
        st.session_state.current_bowler = st.text_input("Current Bowler", key=f"bowler_{innings}")

    if st.session_state.on_strike_batsman and st.session_state.on_strike_batsman not in innings_data['batting_card']:
        innings_data['batting_card'][st.session_state.on_strike_batsman] = {'Runs': 0, 'Balls': 0, '4s': 0, '6s': 0, 'Status': 'Not Out'}
    if st.session_state.off_strike_batsman and st.session_state.off_strike_batsman not in innings_data['batting_card']:
        innings_data['batting_card'][st.session_state.off_strike_batsman] = {'Runs': 0, 'Balls': 0, '4s': 0, '6s': 0, 'Status': 'Not Out'}
    if st.session_state.current_bowler and st.session_state.current_bowler not in innings_data['bowling_card']:
        innings_data['bowling_card'][st.session_state.current_bowler] = {'Overs': '0.0', 'Runs': 0, 'Wickets': 0}

    st.markdown("---")
    st.subheader("Record Ball")
    cols = st.columns(7)
    runs_options = [0, 1, 2, 3, 4, 6]
    for i, run in enumerate(runs_options):
        if cols[i].button(str(run), key=f"run_{run}"):
            handle_ball(run)

    st.markdown("---")
    st.subheader("Extras & Wickets")
    extra_cols = st.columns(4)
    if extra_cols[0].button("Wide"):
        handle_ball(1, is_extra=True)
    if extra_cols[1].button("No Ball"):
        handle_ball(1, is_extra=True, is_no_ball=True)
    if extra_cols[2].button("Wicket"):
        handle_ball(0, is_wicket=True)

def handle_ball(runs, is_extra=False, is_no_ball=False, is_wicket=False):
    if not st.session_state.on_strike_batsman or not st.session_state.current_bowler:
        st.warning("Please enter names for the on-strike batsman and current bowler.")
        return

    innings = st.session_state.current_innings
    innings_data = st.session_state[f'innings{innings}']
    batsman = st.session_state.on_strike_batsman
    bowler = st.session_state.current_bowler

    innings_data['runs'] += runs
    innings_data['bowling_card'][bowler]['Runs'] += runs

    if not is_extra:
        innings_data['balls'] += 1
        innings_data['batting_card'][batsman]['Balls'] += 1
        innings_data['batting_card'][batsman]['Runs'] += runs
        if runs == 4:
            innings_data['batting_card'][batsman]['4s'] += 1
        if runs == 6:
            innings_data['batting_card'][batsman]['6s'] += 1
        if runs in [1, 3]:
            st.session_state.on_strike_batsman, st.session_state.off_strike_batsman = st.session_state.off_strike_batsman, st.session_state.on_strike_batsman

    if is_no_ball:
        innings_data['batting_card'][batsman]['Runs'] += (runs - 1)

    if is_wicket:
        innings_data['balls'] += 1
        innings_data['wickets'] += 1
        innings_data['bowling_card'][bowler]['Wickets'] += 1
        innings_data['batting_card'][batsman]['Status'] = f"Out b. {bowler}"
        st.info(f"WICKET! {batsman} is out!")
        st.session_state[f"on_strike_{innings}"] = ""

    bowler_balls = innings_data['balls'] - sum(
        int(float(bowler_data['Overs'].split('.')[0])) * 6 + int(float(bowler_data['Overs'].split('.')[1]))
        for name, bowler_data in innings_data['bowling_card'].items() if name != bowler
    )
    innings_data['bowling_card'][bowler]['Overs'] = format_overs(bowler_balls)

    if innings_data['balls'] % 6 == 0 and innings_data['balls'] > 0 and not is_extra:
        st.success("Over Complete!")
        st.session_state.on_strike_batsman, st.session_state.off_strike_batsman = st.session_state.off_strike_batsman, st.session_state.on_strike_batsman

    check_for_end_of_innings()
    st.rerun()

def check_for_end_of_innings():
    innings = st.session_state.current_innings
    innings_data = st.session_state[f'innings{innings}']

    if innings_data['wickets'] == 10 or innings_data['balls'] >= st.session_state.total_overs * 6 or \
       (innings == 2 and innings_data['runs'] > st.session_state.innings1['runs']):

        if innings == 1:
            st.session_state.current_innings = 2
            st.session_state.batting_team_inn2 = st.session_state.bowling_team_inn1
            st.session_state.bowling_team_inn2 = st.session_state.batting_team_inn1
            st.session_state.batting_team, st.session_state.bowling_team = st.session_state.bowling_team, st.session_state.batting_team
            st.success(f"End of Innings 1. {st.session_state.batting_team} needs {st.session_state.innings1['runs'] + 1} to win.")
        else:
            st.session_state.match_over = True

        st.session_state.on_strike_batsman = ""
        st.session_state.off_strike_batsman = ""
        st.session_state.current_bowler = ""

def render_result_page():
    st.title("Match Result")

    score1 = st.session_state.innings1['runs']
    wickets1 = st.session_state.innings1['wickets']
    score2 = st.session_state.innings2['runs']
    wickets2 = st.session_state.innings2['wickets']

    team1 = st.session_state.batting_team_inn1
    team2 = st.session_state.batting_team_inn2

    st.header("Final Scores")
    st.write(f"**{team1}:** {score1}/{wickets1}")
    st.write(f"**{team2}:** {score2}/{wickets2}")
    st.markdown("---")

    if score1 > score2:
        st.success(f"**{team1} won by {score1 - score2} runs!**")
    elif score2 > score1:
        st.success(f"**{team2} won by {10 - wickets2} wickets!**")
    else:
        st.warning("**The match is a Tie!**")

    st.markdown("---")
    st.subheader(f"{team1} Batting Scorecard")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.innings1['batting_card'], orient='index'))

    st.subheader(f"{st.session_state.bowling_team_inn1} Bowling Scorecard")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.innings1['bowling_card'], orient='index'))

    st.subheader(f"{team2} Batting Scorecard")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.innings2['batting_card'], orient='index'))

    st.subheader(f"{st.session_state.bowling_team_inn2} Bowling Scorecard")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.innings2['bowling_card'], orient='index'))

    excel_data = create_excel_report()
    st.download_button(
        label="\U0001F4C5 Download Match Report (Excel)",
        data=excel_data,
        file_name="cricket_match_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Main App Execution ---

st.set_page_config(layout="wide")
initialize_session_state()

if not st.session_state.match_started:
    render_setup_page()
elif st.session_state.match_over:
    render_result_page()
else:
    render_scoring_page()
