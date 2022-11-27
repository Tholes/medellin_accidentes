import streamlit as st
import datetime
import pandas as pd
import holidays
import joblib

model = joblib.load('models/multi_regresion.pkl')
co_holidays = holidays.Colombia()

def is_fortnight(month, day):
    if day == 15 or day == 30:
        return True
    if month == 2 and day == 28:
        return True
    return False


def main():
    st.title('Modelamiento de accidentalidad en Medellín')
    start = st.date_input('Fecha inicial', datetime.date(2022, 1, 1))
    end = st.date_input('Fecha final')
    model_selected = st.selectbox('¿Que tipo de accidente quieres predecir:', 
                        ['Caida Ocupante', 'Choque', 'Atropello', 
                        'Volcamiento', 'Incendio','Otro'])
    window = st.selectbox('¿Que ventana de tiempo desea utilizar?',
                        ['Diaria', 'Semanal', 'Mensual'])
                    
    encoding_kind_accident = {
        'Choque': 'choque',
        'Atropello':'atropello',
        'Caida Ocupante': 'caida',
        'Otro':'otro',
        'Volcamiento':'volcamiento',
        'Incendio':'incendio'
    }
    list_of_data = []
    if st.button('EJECUTAR'):
        for date in pd.date_range(start,end):
            data = {
                'YEAR':date.year,
                'MONTH':date.month,
                'DAY':date.day,
                'IS_HOLIDAY': str(date) in co_holidays,
                'QUARTER':date.quarter,
                'IS_FORTNIGHT': is_fortnight(date.month, date.day),
                'date':date,
                'WEEKOFYEAR': date.isocalendar().week
            }

            list_of_data.append(data)
        df = pd.DataFrame(list_of_data)
        y = model.predict(df.loc[:, ~df.columns.isin(['YEAR','date', 'WEEKOFYEAR'])])
        #st.write(df)
        df = pd.concat([df, pd.DataFrame(y.astype(int))], axis=1)
        df.rename(columns = 
            {
                0:'choque', 1:'atropello', 2:'caida', 
                3:'otro', 4:'volcamiento', 5:'incendio'
            }, 
            inplace=True)
        if window == 'Diaria':
            st.line_chart(data= df, x = 'date',y=encoding_kind_accident[model_selected])
        elif window == 'Semanal':
            groupby = df.groupby(['YEAR', 'WEEKOFYEAR', 'MONTH'])[encoding_kind_accident[model_selected]].sum().reset_index()
            groupby['date'] = groupby.apply(lambda x: f'{x.YEAR}-W{x.WEEKOFYEAR}-1', axis = 'columns')
            groupby['date'] = pd.to_datetime(groupby['date'], format="%Y-W%W-%w")
            st.line_chart(data= groupby, x = 'date',y=encoding_kind_accident[model_selected])
        elif window == 'Mensual':
            groupby = df.groupby(['YEAR', 'MONTH'])[encoding_kind_accident[model_selected]].sum().reset_index()
            groupby['date'] = groupby.apply(lambda x: f'{x.YEAR}/{x.MONTH}/1', axis = 'columns')
            groupby['date'] = pd.to_datetime(groupby['date'])
            st.line_chart(data= groupby, x = 'date',y=encoding_kind_accident[model_selected])
    
if __name__ == '__main__':
    main()
