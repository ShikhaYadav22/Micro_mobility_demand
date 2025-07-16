# Test all major imports
try:
    import pandas as pd
    import numpy as np
    import sklearn
    import xgboost as xgb
    import lightgbm as lgb
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px
    import streamlit as st
    import fastapi
    import requests
    
    print("✅ All packages imported successfully!")
    print(f"✅ Pandas version: {pd.__version__}")
    print(f"✅ NumPy version: {np.__version__}")
    print(f"✅ Scikit-learn version: {sklearn.__version__}")
    print(f"✅ XGBoost version: {xgb.__version__}")
    print(f"✅ LightGBM version: {lgb.__version__}")
    print("🎉 Environment setup complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your installation.")