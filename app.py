import streamlit as st
import pandas as pd



# Importa as páginas
import home
import painelAdministradora
import ahpGaussian
import ahpGaussian

st.set_page_config(page_title="Painel Administradora", layout="wide")


# Dicionário para mapear as opções do menu com as funções
PAGES = {
    "Home": home,
    "Painel Administradora": painelAdministradora,
    "AHP Gaussiano": ahpGaussian,
}

def main():
    st.sidebar.title("Menu")
    selection = st.sidebar.radio("", list(PAGES.keys()))  
    
    page = PAGES[selection]
    page.show()

if __name__ == "__main__":
    main()