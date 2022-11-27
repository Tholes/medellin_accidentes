import streamlit as st

def main():
    st.title('Predicción de incidentes viales en la ciudad de Medellin')
    home = open('markdown/home.md', 'r')
    for line in home.readlines():
        st.write(line)
if __name__ == '__main__':
    main()