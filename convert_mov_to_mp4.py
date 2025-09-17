#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации видео из формата MOV в MP4 с сохранением исходного качества
Поддерживает аудиодорожки и оптимизирован для Windows
Совместим с Python 3.13
"""

import os
import sys
from pathlib import Path
from moviepy.editor import VideoFileClip
import time


def format_time(seconds):
    """Форматирует время в читабельный вид"""
    if seconds < 60:
        return f"{seconds:.1f}с"
    elif seconds < 3600:
        return f"{int(seconds//60)}м {int(seconds%60)}с"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours}ч {minutes}м {seconds}с"


def get_unique_mov_files(folder_path):
    """Получает уникальные MOV файлы, избегая дубликатов из-за регистра"""
    folder = Path(folder_path)
    
    # В Windows *.mov и *.MOV находят одни файлы - используем только один паттерн
    mov_files = list(folder.glob('*.mov'))
    
    # Если файлы не найдены, попробуем заглавные буквы (на случай Linux)
    if not mov_files:
        mov_files = list(folder.glob('*.MOV'))
    
    # Дополнительная проверка: убираем возможные дубликаты по абсолютному пути
    unique_files = {}
    for file in mov_files:
        abs_path = str(file.resolve()).lower()  # Приводим к нижнему регистру
        if abs_path not in unique_files:
            unique_files[abs_path] = file
    
    return list(unique_files.values())


def convert_mov_to_mp4_lossless(input_path, output_path=None, method='high_quality'):
    """
    Конвертирует MOV файл в MP4 формат с сохранением исходного качества
    
    Args:
        input_path (str): Путь к исходному MOV файлу
        output_path (str, optional): Путь для выходного MP4 файла
        method (str): Метод конвертации ('lossless', 'high_quality', 'copy_streams')
    
    Returns:
        bool: True если конвертация прошла успешно
    """
    
    try:
        # Проверяем существование входного файла
        if not os.path.exists(input_path):
            print(f"❌ Ошибка: Файл {input_path} не найден")
            return False
        
        # Определяем выходной путь если не задан
        if output_path is None:
            input_file = Path(input_path)
            output_path = str(input_file.with_suffix('.mp4'))
        
        # Проверяем, не существует ли уже выходной файл
        if os.path.exists(output_path):
            response = input(f"⚠️  Файл {os.path.basename(output_path)} уже существует. Перезаписать? (y/n): ").lower()
            if response != 'y':
                print("⏭️  Пропускаем файл")
                return True
        
        print(f"🎬 Начинаем конвертацию: {os.path.basename(input_path)}")
        print(f"📁 Выходной файл: {os.path.basename(output_path)}")
        print(f"🎯 Метод: {method}")
        
        # Загружаем видео файл
        print("📖 Загружаем видео файл...")
        video_clip = VideoFileClip(input_path)
        
        # Показываем информацию о видео
        duration = video_clip.duration
        fps = video_clip.fps
        size = video_clip.size
        print(f"ℹ️  Длительность: {format_time(duration)} | FPS: {fps:.1f} | Разрешение: {size[0]}x{size[1]}")
        
        # Приблизительная оценка времени
        file_size_mb = os.path.getsize(input_path) / 1024 / 1024
        estimated_time = duration * 0.3  # Примерно 30% от длительности видео
        print(f"⏱️  Примерное время конвертации: {format_time(estimated_time)}")
        
        # Настройки для сохранения максимального качества
        if method == 'lossless':
            ffmpeg_params = [
                '-preset', 'slow',
                '-crf', '0',  # Lossless H.264
                '-threads', str(os.cpu_count()),
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p'
            ]
            print("🔧 Режим: Без потери качества (lossless) - файл может стать больше!")
            
        elif method == 'high_quality':
            ffmpeg_params = [
                '-preset', 'slow',
                '-crf', '15',  # Очень высокое качество
                '-threads', str(os.cpu_count()),
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p'
            ]
            print("🔧 Режим: Очень высокое качество (CRF 15)")
            
        elif method == 'copy_streams':
            ffmpeg_params = [
                '-c:v', 'copy',  # Копировать видеопоток
                '-c:a', 'copy',  # Копировать аудиопоток
                '-movflags', '+faststart'
            ]
            print("🔧 Режим: Копирование потоков (без перекодирования)")
            
        else:
            ffmpeg_params = [
                '-preset', 'slow',
                '-crf', '18',  # Высокое качество
                '-threads', str(os.cpu_count()),
                '-movflags', '+faststart'
            ]
            print("🔧 Режим: Высокое качество (CRF 18)")
        
        # Определяем кодеки
        if method == 'copy_streams':
            video_codec = None
            audio_codec = None
        else:
            video_codec = 'libx264'
            audio_codec = 'aac'
        
        print("🚀 Начинаем конвертацию...")
        print("📊 Прогресс будет показан ниже:")
        start_time = time.time()
        
        # Конвертируем с встроенным прогресс-баром MoviePy
        video_clip.write_videofile(
            output_path,
            codec=video_codec,
            audio_codec=audio_codec,
            ffmpeg_params=ffmpeg_params,
            verbose=True,    # Показываем детальный прогресс
            logger='bar'     # Включаем прогресс-бар MoviePy
        )
        
        conversion_time = time.time() - start_time
        
        # Закрываем клип для освобождения памяти
        video_clip.close()
        
        print(f"\n✅ Конвертация завершена успешно!")
        print(f"⏱️  Время конвертации: {format_time(conversion_time)}")
        print(f"📊 Размер исходного файла: {os.path.getsize(input_path) / 1024 / 1024:.2f} МБ")
        print(f"📊 Размер выходного файла: {os.path.getsize(output_path) / 1024 / 1024:.2f} МБ")
        
        # Сравниваем размеры
        original_size = os.path.getsize(input_path)
        converted_size = os.path.getsize(output_path)
        ratio = (converted_size / original_size) * 100
        print(f"📈 Соотношение размеров: {ratio:.1f}% от оригинала")
        
        # Скорость конвертации
        speed_ratio = duration / conversion_time
        print(f"🚀 Скорость: {speed_ratio:.1f}x (1x = реальное время)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при конвертации: {str(e)}")
        return False


def list_mov_files(folder_path):
    """Показывает все MOV файлы в папке для проверки"""
    mov_files = get_unique_mov_files(folder_path)
    
    if mov_files:
        print(f"\n📋 Найденные MOV файлы в папке:")
        total_size = 0
        for i, file in enumerate(sorted(mov_files, key=lambda x: x.name), 1):
            size_mb = file.stat().st_size / 1024 / 1024
            total_size += size_mb
            print(f"   {i}. {file.name} ({size_mb:.2f} МБ)")
        
        print(f"\n📊 Итого: {len(mov_files)} файла(ов), общий размер: {total_size:.2f} МБ")
    
    return mov_files


def batch_convert_lossless(input_folder, output_folder=None, method='high_quality'):
    """
    Конвертирует все MOV файлы в папке с сохранением качества
    """
    
    if output_folder is None:
        output_folder = input_folder
    
    # Создаем выходную папку если не существует
    os.makedirs(output_folder, exist_ok=True)
    
    # Показываем список файлов
    mov_files = list_mov_files(input_folder)
    
    if not mov_files:
        print("❌ MOV файлы не найдены в указанной папке")
        return
    
    print(f"\n🎬 Будет обработано {len(mov_files)} MOV файл(ов)")
    
    # Спрашиваем подтверждение
    response = input("Продолжить? (y/n): ").lower()
    if response != 'y':
        print("❌ Отменено пользователем")
        return
    
    success_count = 0
    start_time = time.time()
    
    for i, mov_file in enumerate(mov_files, 1):
        print(f"\n{'='*60}")
        print(f"📁 Обрабатываем файл {i}/{len(mov_files)}: {mov_file.name}")
        print(f"{'='*60}")
        
        output_file = Path(output_folder) / f"{mov_file.stem}.mp4"
        
        if convert_mov_to_mp4_lossless(str(mov_file), str(output_file), method):
            success_count += 1
            print(f"✅ Файл {i}/{len(mov_files)} завершен")
        else:
            print(f"❌ Файл {i}/{len(mov_files)} не удалось обработать")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Конвертация завершена: {success_count}/{len(mov_files)} файлов успешно")
    print(f"⏱️  Общее время: {format_time(total_time)}")
    
    if success_count == len(mov_files):
        print("🎊 Все файлы успешно сконвертированы!")
    elif success_count > 0:
        print(f"⚠️  {len(mov_files) - success_count} файл(ов) пропущено или не удалось обработать")


def main():
    """Главная функция с интерактивным меню"""
    
    print("🎬 Конвертер MOV → MP4 (Сохранение исходного качества)")
    print("=" * 60)
    
    while True:
        print("\nВыберите режим:")
        print("1. Конвертировать один файл")
        print("2. Конвертировать все файлы в папке")
        print("3. Показать MOV файлы в папке")
        print("4. Выход")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == '1':
            input_file = input("Введите путь к MOV файлу: ").strip().strip('"')
            if input_file:
                print("\nВыберите метод конвертации:")
                print("1. Копирование потоков (быстро, если совместимо)")
                print("2. Очень высокое качество CRF 15 (рекомендуется)")  
                print("3. Без потерь CRF 0 (большой размер)")
                print("4. Высокое качество CRF 18")
                
                method_choice = input("Метод (1-4) [2]: ").strip() or '2'
                
                method_map = {
                    '1': 'copy_streams',
                    '2': 'high_quality', 
                    '3': 'lossless',
                    '4': 'standard_high'
                }
                
                method = method_map.get(method_choice, 'high_quality')
                convert_mov_to_mp4_lossless(input_file, method=method)
        
        elif choice == '2':
            input_folder = input("Введите путь к папке с MOV файлами: ").strip().strip('"')
            if input_folder:
                print("\nВыберите метод конвертации:")
                print("1. Копирование потоков (быстро)")
                print("2. Очень высокое качество CRF 15 (рекомендуется)")  
                print("3. Без потерь CRF 0 (большой размер)")
                
                method_choice = input("Метод (1-3) [2]: ").strip() or '2'
                
                method_map = {
                    '1': 'copy_streams',
                    '2': 'high_quality', 
                    '3': 'lossless'
                }
                
                method = method_map.get(method_choice, 'high_quality')
                batch_convert_lossless(input_folder, method=method)
        
        elif choice == '3':
            input_folder = input("Введите путь к папке: ").strip().strip('"')
            if input_folder:
                list_mov_files(input_folder)
        
        elif choice == '4':
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    main()
