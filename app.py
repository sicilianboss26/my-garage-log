import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Garage Hub")

# MASTER CODE: SECURE LOGIN + FLEET + MAINTENANCE + RECORDS
garage_secure_master = """
<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        body {
            background-color: #0b0b0b;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
            justify-content: center;
            align-items: center;
        }
        #login-screen {
            text-align: center;
            background: #111;
            padding: 50px;
            border-radius: 20px;
            border: 1px solid #ff9d00;
            box-shadow: 0 0 30px rgba(255, 157, 0, 0.2);
        }
        .pin-input {
            background: #222;
            border: 1px solid #444;
            color: #ff9d00;
            font-size: 2rem;
            text-align: center;
            width: 150px;
            padding: 10px;
            border-radius: 10px;
            margin: 20px 0;
            letter-spacing: 5px;
        }
        #dashboard {
            display: none;
            width: 100%;
            height: 100%;
            flex-direction: row;
        }
        #sidebar {
            width: 300px;
            background-color: #111111;
            height: 100%;
            border-right: 1px solid #333;
            padding: 30px 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        .logo {
            font-size: 1.5rem;
            font-weight: 900;
            color: #ff9d00;
            text-transform: uppercase;
            border-bottom: 2px solid #ff9d00;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .nav-label { color: #555; font-size: 0.7rem; text-transform: uppercase; margin: 20px 0 10px 0; }
        .nav-item {
            display: block; width: 100%; padding: 10px; color: #bbb;
            background: none; border: none; text-align: left; cursor: pointer;
            border-radius: 6px; transition: 0.2s;
        }
        .nav-item:hover { background: #222; color: #ff9d00; }
        .records-vault { margin-top: auto; background: #181818; border-radius: 8px; border: 1px solid #333; }
        summary { padding: 12px; color: #ff9d00; font-weight: bold; cursor: pointer; list-style: none; }
        #main { flex: 1; padding: 40px; background: radial-gradient(circle at top left, #1a1a1a, #0b0b0b); overflow-y: auto; }
        .card { background: #141414; padding: 30px; border-radius: 15px; border: 1px solid #333; max-width: 80
