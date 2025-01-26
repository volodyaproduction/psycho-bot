"""
Обработчик команды /plot.
Создает и отправляет график измерений пользователя.
"""

from aiogram import Router, types
from aiogram.filters import Command
from utils.database import get_user_measurements
from utils.plotting import create_measurement_plot
import os

router = Router()

@router.message(Command("plot"))
async def cmd_plot(message: types.Message):
    """
    Обработчик команды /plot.
    Создает и отправляет график измерений пользователя.
    """
    # Получаем измерения пользователя
    measurements = await get_user_measurements(message.from_user.id)
    
    if not measurements:
        await message.answer("❌ У вас пока нет измерений для построения графика.")
        return
    
    # Создаем график
    plot_file = create_measurement_plot(measurements)
    
    if not plot_file:
        await message.answer("❌ Не удалось создать график. Попробуйте позже.")
        return
    
    # Отправляем файл
    try:
        with open(plot_file, 'rb') as f:
            await message.answer_document(
                types.BufferedInputFile(
                    f.read(),
                    filename="psychological_state.html"
                ),
                caption="📊 График вашего психологического состояния"
            )
    finally:
        # Удаляем временный файл
        if os.path.exists(plot_file):
            os.remove(plot_file) 