import streamlit as st
from gemini_client import ask_gemini, verify_output
from citations import render_citations
from citations import render_list_with_citations
st.set_page_config(page_title="Briefing Assistant", layout="centered")

st.title("Client Briefing Assistant")
st.caption(
    "Paste a client briefing below. The AI will summarise it, find missing "
    "information, and propose a basic structure (requirements / user stories). "
)

briefing = st.text_area(
    "Client briefing",
    height=220,
    placeholder="Paste the client's email or document text here",
)

submitted = st.button("Analyse briefing", type="primary")

if submitted:
    if not briefing.strip():
        st.warning("Please paste a briefing first.")
    else:
        with st.spinner("Analysing briefing..."):
            try:
                result = ask_gemini(briefing)
                error = None
            except Exception as e:
                result = None
                error = str(e)

        st.divider()

        if error:
            st.error(f"Something went wrong calling the AI: {error}")
        else:
            st.info("AI-generated response. Check quality control to verify accuracy and review details by a professional.")
 
            st.subheader("Summary")
            st.markdown(render_citations(result.summary), unsafe_allow_html=True)
 
            st.subheader("Open questions")
            st.markdown(render_list_with_citations(result.open_questions), unsafe_allow_html=True)
 
            st.subheader("Requirements")
            st.markdown(render_list_with_citations(result.requirements), unsafe_allow_html=True)

            with st.spinner("Running quality control check..."):
                try:
                    qc = verify_output(briefing, result)
                    qc_error = None
                except Exception as e:
                    qc = None
                    qc_error = str(e)

            st.divider()
            st.subheader("Quality control")

            if qc_error:
                st.warning(f"Quality control check failed: {qc_error}")
            else:
                st.caption(
                    "A second AI pass checking the analysis above."
                    "This is not a substitute for human review and still needs to be reviewed by a professional"
                )

                st.markdown("**Verified claims**")
                if qc.verified_claims:
                    st.markdown(render_list_with_citations(qc.verified_claims), unsafe_allow_html=True)
                else:
                    st.caption("Nothing verified.")    

                st.markdown("**Flagged claims**")
                if qc.flagged_claims:
                    st.markdown(render_list_with_citations(qc.flagged_claims), unsafe_allow_html=True)
                else:
                    st.caption("Nothing flagged.")

                st.markdown("**Polish notes**")
                if qc.polish_notes:
                    st.markdown(render_list_with_citations(qc.polish_notes), unsafe_allow_html=True)
                else:
                    st.caption("Nothing to add.")