import streamlit as st
import pandas as pd
import io

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="M.Tech Project Allocation", layout="wide")
st.title("M.Tech Project Allocation System")

# -------------------------
# PASSWORD
# -------------------------
password = st.text_input("Enter Admin Password", type="password")

if password != "admin123":
    st.warning("Enter correct password to continue")
    st.stop()

# -------------------------
# SESSION STATE INIT
# -------------------------
if "allocated" not in st.session_state:
    st.session_state.allocated = {}

if "used_projects" not in st.session_state:
    st.session_state.used_projects = set()

if "stage" not in st.session_state:
    st.session_state.stage = 0

if "r2_stage" not in st.session_state:
    st.session_state.r2_stage = 0

if "r2_df" not in st.session_state:
    st.session_state.r2_df = None

if "df_round1" not in st.session_state:
    st.session_state.df_round1 = None

# -------------------------
# ROUND 1 UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload Round 1 Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    st.session_state.df_round1 = df

    st.subheader("Round 1 Data")
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # START ROUND 1
    # -------------------------
    if st.session_state.stage == 0:
        if st.button("Start Round 1 Allocation"):
            st.session_state.stage = 1

    # -------------------------
    # ALLOCATION FUNCTION
    # -------------------------
    def allocation_stage(data, pref_col, stage_name):

        st.subheader(stage_name)

        remaining = data[
            ~data['Roll Number'].isin(st.session_state.allocated.keys())
        ]

        remaining = remaining[
            ~remaining[pref_col].isin(st.session_state.used_projects)
        ]

        remaining = remaining.dropna(subset=[pref_col])

        if remaining.empty:
            st.info("No students left in this stage.")
            return {}

        grouped = remaining.groupby(pref_col, sort=False)

        selections = {}

        for project, group in grouped:

            if project in st.session_state.used_projects:
                continue

            if len(group) == 1:
                row = group.iloc[0]
                selections[project] = row['Roll Number']

            else:
                st.warning(f"Conflict for: {project}")

                options = [
                    f"{row['Name']} ({row['Roll Number']})"
                    for _, row in group.iterrows()
                ]

                choice = st.selectbox(
                    f"Select student for '{project}'",
                    options,
                    key=f"{stage_name}_{project}"
                )

                selected_roll = choice.split("(")[-1].replace(")", "").strip()
                selections[project] = selected_roll

        return selections

    # -------------------------
    # ROUND 1 STAGES
    # -------------------------
    if st.session_state.stage == 1:

        selections = allocation_stage(df, 'Preference 1', "Round 1 - Preference 1")

        if st.button("Finalize Round 1 - Preference 1"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)
            st.session_state.stage = 2

    elif st.session_state.stage == 2:

        selections = allocation_stage(df, 'Preference 2', "Round 1 - Preference 2")

        if st.button("Finalize Round 1 - Preference 2"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)
            st.session_state.stage = 3

    elif st.session_state.stage == 3:

        selections = allocation_stage(df, 'Preference 3', "Round 1 - Preference 3")

        if st.button("Finalize Round 1 - Preference 3"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)
            st.session_state.stage = 4

    # -------------------------
    # ROUND 1 RESULT
    # -------------------------
    elif st.session_state.stage == 4:

        st.success("Round 1 Completed")

        result = []

        for _, row in df.iterrows():
            roll = row['Roll Number']

            if roll in st.session_state.allocated:
                result.append({
                    "Name": row['Name'],
                    "Roll Number": roll,
                    "Allocated Project": st.session_state.allocated[roll],
                    "Round": 1
                })
            else:
                result.append({
                    "Name": row['Name'],
                    "Roll Number": roll,
                    "Allocated Project": "Not Allocated",
                    "Round": "-"
                })

        result_df = pd.DataFrame(result)

        st.subheader("Round 1 Allocation")
        st.dataframe(result_df, use_container_width=True)

        # -------------------------
        # EXCEL DOWNLOAD
        # -------------------------
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not result_df.empty:
                result_df.to_excel(writer, index=False, sheet_name='Round1')
            else:
                pd.DataFrame({"Message": ["No data"]}).to_excel(writer)

        st.download_button(
            "Download Round 1 Excel",
            output.getvalue(),
            "Round1.xlsx"
        )

        # -------------------------
        # ROUND 2 UPLOAD
        # -------------------------
        st.subheader("Round 2 Allocation")

        round2_file = st.file_uploader("Upload Round 2 Excel", type=["xlsx"], key="r2")

        if round2_file:
            st.session_state.r2_df = pd.read_excel(round2_file)

            st.dataframe(st.session_state.r2_df)

            if st.session_state.r2_stage == 0:
                if st.button("Start Round 2"):
                    st.session_state.r2_stage = 1

    # -------------------------
    # ROUND 2 STAGES
    # -------------------------
    if st.session_state.r2_df is not None:

        df2 = st.session_state.r2_df

        if st.session_state.r2_stage == 1:

            selections = allocation_stage(df2, 'Preference 1', "Round 2 - Preference 1")

            if st.button("Finalize Round 2 - Preference 1"):
                for project, roll in selections.items():
                    st.session_state.allocated[roll] = project
                    st.session_state.used_projects.add(project)
                st.session_state.r2_stage = 2

        elif st.session_state.r2_stage == 2:

            selections = allocation_stage(df2, 'Preference 2', "Round 2 - Preference 2")

            if st.button("Finalize Round 2 - Preference 2"):
                for project, roll in selections.items():
                    st.session_state.allocated[roll] = project
                    st.session_state.used_projects.add(project)
                st.session_state.r2_stage = 3

        elif st.session_state.r2_stage == 3:

            selections = allocation_stage(df2, 'Preference 3', "Round 2 - Preference 3")

            if st.button("Finalize Round 2 - Preference 3"):
                for project, roll in selections.items():
                    st.session_state.allocated[roll] = project
                    st.session_state.used_projects.add(project)
                st.session_state.r2_stage = 4

        # -------------------------
        # FINAL RESULT
        # -------------------------
        elif st.session_state.r2_stage == 4:

            df1 = st.session_state.df_round1

            combined = pd.concat([df1, df2]).drop_duplicates(subset=['Roll Number'])

            final = []

            for _, row in combined.iterrows():
                roll = row['Roll Number']

                if roll in st.session_state.allocated:
                    final.append({
                        "Name": row['Name'],
                        "Roll Number": roll,
                        "Allocated Project": st.session_state.allocated[roll],
                        "Round": 1 if roll in df1['Roll Number'].values else 2
                    })
                else:
                    final.append({
                        "Name": row['Name'],
                        "Roll Number": roll,
                        "Allocated Project": "Not Allocated",
                        "Round": 2
                    })

            final_df = pd.DataFrame(final)

            st.subheader("Final Allocation After Round 2")
            st.dataframe(final_df, use_container_width=True)

            # -------------------------
            # FINAL DOWNLOAD
            # -------------------------
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Final')

            st.download_button(
                "Download Final Allocation",
                output.getvalue(),
                "Final_Allocation.xlsx"
            )

# -------------------------
# RESET BUTTON
# -------------------------
if st.button("Reset Allocation"):
    st.session_state.allocated = {}
    st.session_state.used_projects = set()
    st.session_state.stage = 0
    st.session_state.r2_stage = 0
    st.session_state.r2_df = None
    st.session_state.df_round1 = None
