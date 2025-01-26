"""
Обработчик команды /load_data.
Позволяет загрузить исторические данные измерений.
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import add_measurement
from datetime import datetime
import pytz

router = Router()

class LoadDataState(StatesGroup):
    """Состояния для FSM при загрузке данных."""
    waiting_for_data = State()

@router.message(Command("load_data"))
async def cmd_load_data(message: types.Message, state: FSMContext):
    """
    Обработчик команды /load_data.
    Запрашивает исторические данные у пользователя.
    """
    await state.set_state(LoadDataState.waiting_for_data)
    await message.answer(
        "Пожалуйста, отправьте ваши исторические данные в формате:\n"
        "ГГГГ-ММ-ДД, оценка\n\n"
        "Например:\n"
        "2024-01-01, 3\n"
        "2024-01-02, 2\n"
        "2024-01-01, 3\n"
        "2024-01-01, 1\n\n"
        "Примечание:\n"
        "- Можно указать несколько измерений за один день\n"
        "- Дата обрабатывается в UTC (12:00 UTC для указанной даты)"
    )

@router.message(LoadDataState.waiting_for_data)
async def process_data(message: types.Message, state: FSMContext):
    """
    Обработчик загрузки исторических данных.
    Парсит данные и сохраняет их в базу данных.
    """
    try:
        # Разбиваем сообщение на строки
        lines = message.text.strip().split('\n')
        successful_imports = 0
        errors = []

        for line_number, line in enumerate(lines, 1):
            try:
                # Разбираем строку на дату и значение
                date_str, measurement_str = map(str.strip, line.split(','))
                
                # Преобразуем дату в datetime с UTC
                # Устанавливаем время на полдень UTC
                date = datetime.strptime(date_str, '%Y-%m-%d')
                date = date.replace(hour=12, minute=0, second=0)
                date = pytz.UTC.localize(date)
                
                # Преобразуем значение в целое число
                measurement = int(measurement_str)
                
                # Проверяем диапазон значений
                if not -3 <= measurement <= 3:
                    errors.append(f"Строка {line_number}: значение должно быть от -3 до 3")
                    continue
                
                # Сохраняем измерение
                await add_measurement(message.from_user.id, measurement, timestamp=date)
                successful_imports += 1
                
            except ValueError as e:
                errors.append(f"Строка {line_number}: неверный формат данных")
            except Exception as e:
                errors.append(f"Строка {line_number}: {str(e)}")
        
        # Формируем отчет
        report = [f"✅ Успешно импортировано измерений: {successful_imports}"]
        if errors:
            report.append("\n❌ Ошибки:")
            report.extend(errors)
        
        await message.answer("\n".join(report))
        await state.clear()
        
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при обработке данных.\n"
            "Убедитесь, что данные соответствуют формату:\n"
            "ГГГГ-ММ-ДД, оценка"
        )
        await state.clear() 