def combine_files_to_txt(file_paths, output_file="combined_output.txt"):
    """
    Объединяет содержимое нескольких файлов в один текстовый файл и добавляет
    фиксированный блок с данными сохранения в конец.

    :param file_paths: Список путей к файлам, которые нужно объединить.
    :param output_file: Имя выходного файла (по умолчанию "combined_output.txt").
    """
    # Фиксированный блок данных для сохранения
    save_data = """=== Начало файла: save/save.json ===
{
    "version": 4,
    "name": "\\u0442\\u0435\\u0441\\u04421",
    "level": 11,
    "health_points": 712,
    "attack_power": 110,
    "defence": 71,
    "experience": 72600,
    "exp_base": 102400,
    "count_kill": 377,
    "location": "\\u0417\\u0430\\u0447\\u0430\\u0440\\u043e\\u0432\\u0430\\u043d\\u043d\\u044b\\u0439 \\u043b\\u0435\\u0441",
    "class_character": "Human",
    "inventory": [{"id": 2,"quantity": 1},{"id": 1,"quantity": 10},{"id": 7,"quantity": 1},{"id": 4,"quantity": 1}],
    "equipment": [4,null,10,7,null,9],
    "money": 8422,
    "active_quests": [
        {
            "id": 1,
            "current_amount": 0,
            "is_completed": false,
            "completion_date": null
        }
    ],
    "completed_quests": [],
    "now_time": 1746999469
}
"""

    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Записываем все указанные файлы
            for file_path in file_paths:
                try:
                    with open(file_path, 'r', encoding='utf-8') as in_file:
                        out_file.write(f"=== Начало файла: {file_path} ===\n\n")
                        out_file.write(in_file.read())
                        out_file.write(f"\n=== Конец файла: {file_path} ===\n\n")
                        print(f"Файл {file_path} успешно обработан.")
                except FileNotFoundError:
                    print(f"Ошибка: файл {file_path} не найден.")
                except Exception as e:
                    print(f"Ошибка при чтении файла {file_path}: {e}")

            # Добавляем фиксированный блок с данными сохранения
            out_file.write("\n\n" + save_data)
            print("\nДанные сохранения успешно добавлены в конец файла.")

        print(f"\nВсе файлы успешно объединены в {output_file}")
    except Exception as e:
        print(f"Ошибка при создании выходного файла: {e}")


# Пример использования:
if __name__ == "__main__":
    # Список файлов для объединения (можно расширять)
    files_to_combine = [
        "main.py",
        "game\\character.py",
        "game\\items.py",
        "game\\locations.py",
        "game\\quests.py",
        "game\\utils.py",
        "save\\action_bindings.json",
        # Добавьте другие файлы по необходимости
    ]
    
    combine_files_to_txt(files_to_combine)