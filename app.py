        elif l_t == "Tires":
            if active_cat == "Motorcycle":
                # Motorcycle specific logic we discussed
                data["F_Tire"] = st.text_input("Front Size")
                data["R_Tire"] = st.text_input("Rear Size")
                data["Notes"] = st.text_input("PSI / Torque")
            else:
                # Professional Vehicle Layout
                col_a, col_b = st.columns(2)
                with col_a:
                    data["F_Tire"] = st.text_input("Front Size (e.g. 235/55R18)")
                    f_psi = st.text_input("Front PSI")
                with col_b:
                    data["R_Tire"] = st.text_input("Rear Size")
                    r_psi = st.text_input("Rear PSI")
                
                tq = st.text_input("Lug Nut Torque (lb-ft)")
                data["Notes"] = f"PSI: {f_psi}/{r_psi} | Torque: {tq}"
