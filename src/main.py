import streamlit as st
import psycopg2
from configparser import ConfigParser
import pandas as pd
import numpy as np
import functions
import matplotlib.pyplot as plt

import planner
import vendor
import manager

# Page Contents
page = st.sidebar.selectbox("Navigation panel:", ["planner", "vendor", "manager"])

if page == "planner":
    planner.show()

elif page == "vendor":
    vendor.show()

elif page == "manager":
    manager.show()