#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации конкретных MOV файлов в MP4 без звука
"""

import os
import sys
from pathlib import Path
from convert_mov_to_mp4 import convert_mov_to_mp4_lossless
import time

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    """Конвертирует указанные файлы в MP4 без звука"""

    # Список файлов для конвертации
    files_to_convert = [
        "16_9.MOV",
        "1_1.MOV",
        "9_16.MOV"
    ]

    # Получаем текущую директорию
    current_dir = Path(__file__).parent

    print("🎬 Конвертация MOV → MP4 без звука")
    print("=" * 60)
    print(f"📁 Рабочая папка: {current_dir}")
    print(f"🔇 Аудио будет удалено из всех файлов")
    print(f"🎯 Метод: Очень высокое качество (CRF 15)")
    print()

    # Проверяем наличие файлов
    missing_files = []
    for file in files_to_convert:
        file_path = current_dir / file
        if not file_path.exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Не найдены следующие файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return

    print(f"✅ Все {len(files_to_convert)} файла найдены")
    print()

    # Выполняем конвертацию
    success_count = 0
    start_time = time.time()

    for i, filename in enumerate(files_to_convert, 1):
        print(f"\n{'='*60}")
        print(f"📁 Обрабатываем файл {i}/{len(files_to_convert)}: {filename}")
        print(f"{'='*60}")

        input_path = str(current_dir / filename)
        output_filename = Path(filename).stem + ".mp4"
        output_path = str(current_dir / output_filename)

        # Конвертируем с удалением аудио
        if convert_mov_to_mp4_lossless(
            input_path,
            output_path,
            method='high_quality',
            remove_audio=True
        ):
            success_count += 1
            print(f"✅ Файл {i}/{len(files_to_convert)} завершен")
        else:
            print(f"❌ Файл {i}/{len(files_to_convert)} не удалось обработать")

    # Итоги
    total_time = time.time() - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)

    print(f"\n{'='*60}")
    print(f"🎉 Конвертация завершена: {success_count}/{len(files_to_convert)} файлов успешно")

    if total_time < 60:
        print(f"⏱️  Общее время: {total_time:.1f}с")
    elif total_time < 3600:
        print(f"⏱️  Общее время: {minutes}м {seconds}с")
    else:
        print(f"⏱️  Общее время: {hours}ч {minutes}м {seconds}с")

    if success_count == len(files_to_convert):
        print("🎊 Все файлы успешно сконвертированы без звука!")
    elif success_count > 0:
        print(f"⚠️  {len(files_to_convert) - success_count} файл(ов) не удалось обработать")
    else:
        print("❌ Не удалось обработать ни один файл")


if __name__ == "__main__":
    main()
