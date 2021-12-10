import streamlit as st
import psycopg2
from configparser import ConfigParser
import pandas
import numpy as np
import functions
import matplotlib.pyplot as plt

import planner
import vendor
import ceo

# Page Contents
page = st.sidebar.selectbox("Navigation panel:", ["Planner", "Vendor", "CEO"])

if page == "Planner":
    planner.show()

elif page == "Vendor":
    vendor.show()

elif page == "CEO":
    ceo.show()
