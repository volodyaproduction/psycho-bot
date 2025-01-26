"""
Модуль для создания графиков на основе данных измерений.
Использует библиотеку plotly для построения интерактивных графиков.
"""

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def create_measurement_plot(measurements: list, period: str = 'day') -> str:
    """
    Создает график измерений за указанный период.
    
    Args:
        measurements: Список кортежей (timestamp, measurement)
        period: Период группировки данных ('day', 'week', 'month')
    
    Returns:
        str: Путь к сохраненному HTML-файлу с графиком
    """
    if not measurements:
        return None
    
    # Преобразуем данные в DataFrame
    df = pd.DataFrame(measurements, columns=['timestamp', 'measurement'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Группируем данные по периоду
    if period == 'week':
        df = df.groupby(pd.Grouper(key='timestamp', freq='W')).mean().reset_index()
    elif period == 'month':
        df = df.groupby(pd.Grouper(key='timestamp', freq='M')).mean().reset_index()
    
    # Создаем график
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['measurement'],
        mode='lines+markers',
        name='Измерения'
    ))
    
    # Настраиваем внешний вид
    fig.update_layout(
        title='Динамика психологического состояния',
        xaxis_title='Время',
        yaxis_title='Состояние',
        yaxis=dict(
            ticktext=['Очень плохо', 'Плохо', 'Немного плохо', 'Нейтрально', 
                     'Немного хорошо', 'Хорошо', 'Отлично'],
            tickvals=[-3, -2, -1, 0, 1, 2, 3]
        )
    )
    
    # Сохраняем график
    filename = f'plot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(filename)
    return filename 