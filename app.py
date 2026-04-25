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

# -------------------------
# FILE UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload Round 1 Excel", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # START
    # -------------------------
    if st.session_state.stage == 0:
        if st.button("Start Allocation"):
            st.session_state.stage = 1

    # -------------------------
    # FUNCTION
    # -------------------------
    def allocation_stage(pref_col, stage_name):

        st.subheader(stage_name)

        remaining = df[~df['Roll Number'].isin(st.session_state.allocated.keys())]
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
    # STAGE 1
    # -------------------------
    if st.session_state.stage == 1:

        selections = allocation_stage('Preference 1', "Preference 1")

        if st.button("Finalize Preference 1"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)

            st.session_state.stage = 2

    # -------------------------
    # STAGE 2
    # -------------------------
    elif st.session_state.stage == 2:

        selections = allocation_stage('Preference 2', "Preference 2")

        if st.button("Finalize Preference 2"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)

            st.session_state.stage = 3

    # -------------------------
    # STAGE 3
    # -------------------------
    elif st.session_state.stage == 3:

        selections = allocation_stage('Preference 3', "Preference 3")

        if st.button("Finalize Preference 3"):
            for project, roll in selections.items():
                st.session_state.allocated[roll] = project
                st.session_state.used_projects.add(project)

            st.session_state.stage = 4

    # -------------------------
    # FINAL RESULT
    # -------------------------
    elif st.session_state.stage == 4:

        result = []

        for _, row in df.iterrows():
            roll = row['Roll Number']

            if roll in st.session_state.allocated:
                project = st.session_state.allocated[roll]

                if row['Preference 1'] == project:
                    pref_used = "Preference 1"
                elif row['Preference 2'] == project:
                    pref_used = "Preference 2"
                elif row['Preference 3'] == project:
                    pref_used = "Preference 3"
                else:
                    pref_used = "Manual"

                result.append({
                    "Name": row['Name'],
                    "Roll Number": roll,
                    "Allocated Project": project,
                    "Preference Allotted": pref_used,
                    "Round": 1
                })
            else:
                result.append({
                    "Name": row['Name'],
                    "Roll Number": roll,
                    "Allocated Project": "Not Allocated",
                    "Preference Allotted": "-",
                    "Round": 2
                })

        result_df = pd.DataFrame(result)

        st.subheader("Final Allocation")
        st.dataframe(result_df, use_container_width=True)

        # -------------------------
        # FIXED EXCEL EXPORT
        # -------------------------
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:

            if not result_df.empty:
                result_df.to_excel(writer, index=False, sheet_name='Allocation')
            else:
                pd.DataFrame({"Message": ["No allocation data available"]}).to_excel(
                    writer, index=False, sheet_name='Allocation'
                )

        excel_data = output.getvalue()

        st.download_button(
            label="Download Allocation Excel",
            data=excel_data,
            file_name="Project_Allocation_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("Allocation Completed Successfully!")

        # -------------------------
        # ROUND 2 UPLOAD
        # -------------------------
# -------------------------
# ROUND 2 SECTION (CORRECT VERSION)
# -------------------------
st.subheader("Round 2 Allocation")

round2_file = st.file_uploader("Upload Round 2 Excel", type=["xlsx"], key="round2")

if round2_file:
    st.session_state.r2_df = pd.read_excel(round2_file)

    st.write("### Round 2 Data")
    st.dataframe(st.session_state.r2_df)

    if st.session_state.r2_stage == 0:
        if st.button("Start Round 2 Allocation"):
            st.session_state.r2_stage = 1

# -------------------------
# ROUND 2 FUNCTION
# -------------------------
def round2_stage(pref_col, stage_name):

    st.subheader(stage_name)

    df2 = st.session_state.r2_df

    remaining = df2[
        ~df2['Roll Number'].isin(st.session_state.allocated.keys())
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
            st.warning(f"Round 2 Conflict: {project}")

            options = [
                f"{row['Name']} ({row['Roll Number']})"
                for _, row in group.iterrows()
            ]

            choice = st.selectbox(
                f"Select student for '{project}'",
                options,
                key=f"r2_{stage_name}_{project}"
            )

            selected_roll = choice.split("(")[-1].replace(")", "").strip()
            selections[project] = selected_roll

    return selections

# -------------------------
# ROUND 2 STAGES
# -------------------------
if st.session_state.r2_stage == 1:

    selections = round2_stage('Preference 1', "Round 2 - Preference 1")

    if st.button("Finalize Round 2 - Preference 1"):
        for project, roll in selections.items():
            st.session_state.allocated[roll] = project
            st.session_state.used_projects.add(project)

        st.session_state.r2_stage = 2

elif st.session_state.r2_stage == 2:

    selections = round2_stage('Preference 2', "Round 2 - Preference 2")

    if st.button("Finalize Round 2 - Preference 2"):
        for project, roll in selections.items():
            st.session_state.allocated[roll] = project
            st.session_state.used_projects.add(project)

        st.session_state.r2_stage = 3

elif st.session_state.r2_stage == 3:

    selections = round2_stage('Preference 3', "Round 2 - Preference 3")

    if st.button("Finalize Round 2 - Preference 3"):
        for project, roll in selections.items():
            st.session_state.allocated[roll] = project
            st.session_state.used_projects.add(project)

        st.session_state.r2_stage = 4

# -------------------------
# FINAL RESULT AFTER ROUND 2
# -------------------------
elif st.session_state.r2_stage == 4:

    final_result = []

    # Combine Round 1 + Round 2
    combined_df = pd.concat([df, st.session_state.r2_df], ignore_index=True)

    for _, row in combined_df.iterrows():
        roll = row['Roll Number']

        if roll in st.session_state.allocated:
            final_result.append({
                "Name": row['Name'],
                "Roll Number": roll,
                "Allocated Project": st.session_state.allocated[roll],
                "Round": 1 if roll in df['Roll Number'].values else 2
            })
        else:
            final_result.append({
                "Name": row['Name'],
                "Roll Number": roll,
                "Allocated Project": "Not Allocated",
                "Round": 2
            })

    final_df = pd.DataFrame(final_result)

    st.subheader("Final Allocation After Round 2")
    st.dataframe(final_df)
    
        # -------------------------
        # RESET
        # -------------------------
        if st.button("Reset Allocation"):
            st.session_state.allocated = {}
            st.session_state.used_projects = set()
            st.session_state.stage = 0
