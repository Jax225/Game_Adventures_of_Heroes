import json
import os

def update_old_saves():
    try:
        # Проверяем, существует ли файл с хорошими сохранениями
        if not os.path.isfile('save/save.json'):
            print("Файл с хорошими сохранениями не найден.")
            return

        # Считываем хорошие сохранения
        with open('save/save.json', 'r', encoding='utf-8') as file:
            content = file.read()
            good_saves = content.split("₽")  # Разбиваем по разделителю
            good_saves_dicts = []

            for save in good_saves:
                if save.strip():  # Игнорируем пустые строки
                    try:
                        dict_character = json.loads(save)
                        good_saves_dicts.append(dict_character)
                    except json.JSONDecodeError as e:
                        print("Ошибка при декодировании JSON:", e)

        # Проверяем, существует ли файл со старыми сохранениями
        if not os.path.isfile('save/old_save.json'):
            print("Файл со старыми сохранениями не найден.")
            return

        # Считываем старые сохранения
        with open('save/old_save.json', 'r', encoding='utf-8') as file:
            content = file.read()
            old_saves = content.split("₽")  # Разбиваем по разделителю
            updated_saves = []

            for old_save in old_saves:
                if old_save.strip():  # Игнорируем пустые строки
                    try:
                        dict_character = json.loads(old_save)
                        # Создаем новый словарь на основе хорошего сохранения
                        for good_save in good_saves_dicts:
                            # Создаем новый словарь с полями из хорошего сохранения
                            updated_character = {key: None for key in good_save.keys()}

                            # Обновляем поля из старого сохранения, если они существуют
                            for key in good_save.keys():
                                if key in dict_character:
                                    updated_character[key] = dict_character[key]

                            # Обработка поля equipment
                            if "equipment" in good_save:
                                if "equipment" in dict_character and dict_character["equipment"] is not None:
                                    # Если equipment существует и не null, копируем его
                                    updated_character["equipment"] = dict_character["equipment"]
                                else:
                                    # Если equipment отсутствует или null, создаем новый список
                                    updated_character["equipment"] = [None] * len(good_save["equipment"])

                            # Проверка и установка стартовой локации
                            location_name = dict_character.get("location", None)
                            if location_name is None or location_name == "" or location_name != "Город":
                                updated_character["location"] = "Город"  # Устанавливаем "Город", если локация недействительна
                            else:
                                updated_character["location"] = location_name  # Оставляем существующую локацию

                            updated_saves.append(updated_character)
                            print(f"Обновлено сохранение для: {updated_character['name']}")
                            break  # Переходим к следующему старому сохранению
                    except json.JSONDecodeError as e:
                        print("Ошибка при декодировании JSON:", e)

        # Проверяем, были ли обновлены сохранения
        if not updated_saves:
            print("Нет обновленных сохранений.")
            return

        # Сохраняем обновленные данные в old_save.json
        with open('save/old_save.json', 'w', encoding='utf-8') as file:
            for updated_save in updated_saves:
                # Преобразуем локацию "Город" в Unicode-формат
                if updated_save["location"] == "Город":
                    updated_save["location"] = json.dumps("Город", ensure_ascii=True)[1:-1]  # Убираем кавычки
                json.dump(updated_save, file, ensure_ascii=False, indent=4)
                file.write("₽")  # Добавляем разделитель

        # Открываем файл для замены двойных слешей
        with open('save/old_save.json', 'r+', encoding='utf-8') as file:
            content = file.read()
            # Заменяем двойные слеши на одинарные
            content = content.replace("\\\\", "\\")
            # Перемещаем указатель в начало файла
            file.seek(0)
            # Записываем измененное содержимое обратно в файл
            file.write(content)
            # Очищаем оставшуюся часть файла, если она длиннее нового содержимого
            file.truncate()

        print("Обновление старых сохранений завершено.")

    except FileNotFoundError:
        print("Файл сохранения не найден.")

if __name__ == "__main__":
    update_old_saves()