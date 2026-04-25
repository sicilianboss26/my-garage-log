    elif mode == "Oil Change":
        entry["Oil_M"] = st.text_input("Engine Oil Grade")
        if active_cat == "Motorcycle":
            c_p, c_t = st.columns(2)
            with c_p: entry["Oil_P"] = st.text_input("Primary Oil")
            with c_t: entry["Oil_T"] = st.text_input("Trans Oil")
        entry["Notes"] = st.text_input("Filter/Notes")
