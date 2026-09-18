from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["https://oczgkdnxzlfxpkoraljd.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_CNmpqw5XA151VAaaJP9pPw_4T4VKONc"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
