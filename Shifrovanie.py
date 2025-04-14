import base64
from collections import Counter
import ast                         # Позволяет безопасно оценивать строки, кот-ые содержат Python выражения
import re

class HuffmanNode:                   #Класс для представления узлов дерева Хаффмана
     def __init__(self, char, freq):
        self.char = char  # Символ
        self.freq = freq  # Частота встречаемости символа
        self.left = None  # Ссылка на левого потомка
        self.right = None  # Ссылка на правого потомка

     def __lt__(self, other):      #Метод сравнения для сортировки узлов по частоте
        return self.freq < other.freq


def build_huffman_tree(text):  #Построение дерева Хаффмана для текста
    frequency = Counter(text) #Подсчет частот символов
    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()] #Создание начального списка узлов
    heap.sort()  # Сортировка узлов по возрастанию частот

    #Построение дерева путем объединения узлов
    while len(heap) > 1:
        left = heap.pop(0)  #Извлечение двух узлов с наименьшими частотами
        right = heap.pop(0)

        #Создание нового узла сумма частот
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        #Добавление нового узла обратно в кучу
        heap.append(merged)
        heap.sort()

    return heap[0]  # Возвращаем корень дерева


def generate_huffman_codes(node, prefix="", codebook=None):   #Рекурсивная генерация кодов Хаффмана для символов
    if codebook is None:
        codebook = {}  # Инициализация словаря кодов

    if node is not None:
        if node.char is not None: # Если узел содержит символ
            codebook[node.char] = prefix  # Сохраняем код для символа
        generate_huffman_codes(node.left, prefix + "0", codebook) # Рекурсивный обход поддерева (добавляем '0' к префиксу)
        generate_huffman_codes(node.right, prefix + "1", codebook)

    return codebook


def huffman_encode(text):  #Кодирование текста алгоритма Хаффмана и построение
    root = build_huffman_tree(text)
    huffman_codes = generate_huffman_codes(root) #Генерация кодов для символов
    encoded_text = ''.join(huffman_codes[char] for char in text) # Кодирование текст

    return encoded_text, huffman_codes


def huffman_decode(encoded_text, huffman_codes):  #Декодирование текста, закодированного методом Хаффмана
    reverse_codes = {v: k for k, v in huffman_codes.items()}  # Создаем обратное отображение код: символ

    current_code = ""  # Накопление текущего кода
    decoded_text = ""  # Результирующий декодированный текст

    # Последовательный анализ битов
    for bit in encoded_text:
        current_code += bit  # Добавляем очередной бит

        # Проверяем, соответствует ли текущий код символу
        if current_code in reverse_codes:
            decoded_text += reverse_codes[current_code]  # Добавляем символ
            current_code = ""  # Сбрасываем код для следующего символа

    return decoded_text


def xor_encrypt_decrypt_bytes(data_bytes, key):  #Функция шифрования дешифрования
    key_length = len(key)
    decrypted_bytes = bytearray()

    # Применяем XOR для каждого байта с соответствующим символом
    for i, byte in enumerate(data_bytes):
        decrypted_byte = byte ^ ord(key[i % key_length]) # Циклическое использование ключа
        decrypted_bytes.append(decrypted_byte)

    return bytes(decrypted_bytes)


def pad_text(text):  #Добавление паддинга (дополнения) к битовой строке
    padding_length = 8 - (len(text) % 8) # Вычисление количество битов для дополнения

    # Длина кратна 8 паддинг не нужен
    if padding_length == 8:
        padding_length = 0

    # Добавляем нули в конец строки
    padded_text = text + '0' * padding_length

    return padded_text, padding_length


def unpad_text(padded_text, padding_length):  # Удаление паддинга из битовой строки
    if padding_length > 0:
        return padded_text[:-padding_length]  # Последние length битов
    return padded_text  # Возвращаем  если паддинга нет


def validate_base64(data): # Проверка корректности строки в формате base64
    pattern = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')

    # Проверка соответствия формату и длины кратна 4
    return bool(pattern.match(data)) and len(data) % 4 == 0


def save_to_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Результат успешно сохранен в файл '{filename}'")
    except Exception as e:
        print(f"Ошибка при сохранении в файл: {e}")


def main():
    while True:
        # Вывод меню
        print("\nВыберите действие:")
        print("1. Сжать и зашифровать текст")
        print("2. Расшифровать и распаковать текст")
        print("3. Выйти")

        # Получение выбора пользователя
        choice = input("Введите номер действия (1, 2 или 3): ").strip()

        # Опция 1: Сжатие и шифрование
        if choice == '1':
            print("\n[Режим сжатия и шифрования]")

            # Ввод текста для обработки
            text = input("Введите текст для сжатия и шифрования: ").strip()
            if not text:
                print("Ошибка: Введен пустой текст.")
                continue

            # Ввод ключа шифрования
            key = input("Введите ключ для шифрования: ").strip()
            if not key:
                print("Ошибка: Введен пустой ключ.")
                continue

            try:
                # Шаг 1: Кодирование Хаффманом
                encoded_text, huffman_codes = huffman_encode(text)

                # Шаг 2: Добавление паддинга
                padded_text, padding_length = pad_text(encoded_text)

                # Шаг 3: Шифрование XOR
                encrypted_data_bytes = xor_encrypt_decrypt_bytes(
                    padded_text.encode('utf-8'), key)

                # Шаг 4: Кодирование в base64
                encoded_data_b64 = base64.b64encode(encrypted_data_bytes).decode('utf-8')

                # Вывод результатов
                print("\nРезультаты:")
                print(f"Зашифрованные данные (base64): {encoded_data_b64}")
                print(f"Ключ: {key}")
                print(f"Коды Хаффмана: {huffman_codes}")
                print(f"Паддинг: {padding_length}")

                # Сохранение всех данных в файл
                save_content = f"""Зашифрованные данные (base64): {encoded_data_b64}
Ключ: {key}
Коды Хаффмана: {huffman_codes}
Длина паддинга: {padding_length}"""
                save_to_file('encrypted_data.txt', save_content)

            except Exception as e:
                print(f"Произошла ошибка при обработке: {e}")

        # Опция 2: Расшифровка и распаковка
        elif choice == '2':
            print("\n[Режим расшифровки и распаковки]")

            # Ввод зашифрованных данных
            encoded_data_b64 = input("Введите зашифрованные данные (base64): ").strip()
            if not encoded_data_b64:
                print("Ошибка: Введены пустые данные.")
                continue

            # Проверка и корректировка base64
            if not validate_base64(encoded_data_b64):
                mod = len(encoded_data_b64) % 4
                if mod:
                    encoded_data_b64 += '=' * (4 - mod)
                if not validate_base64(encoded_data_b64):
                    print("Ошибка: Некорректный формат base64.")
                    continue

            # Ввод ключа дешифровки
            key = input("Введите ключ для расшифровки: ").strip()
            if not key:
                print("Ошибка: Введен пустой ключ.")
                continue

            # Ввод длины паддинга
            try:
                padding_length = int(input("Введите длину паддинга (0-7): ").strip())
                if padding_length < 0 or padding_length > 7:
                    print("Ошибка: Длина паддинга должна быть от 0 до 7.")
                    continue
            except ValueError:
                print("Ошибка: Введите число от 0 до 7 для длины паддинга.")
                continue

            try:
                # Ввод кодов Хаффмана
                huffman_codes_input = input("Введите коды Хаффмана в формате Python-словаря: ").strip()
                huffman_codes = ast.literal_eval(huffman_codes_input)
                if not isinstance(huffman_codes, dict):
                    raise ValueError("Введенные данные не являются словарем")

                # Декодирование base64
                encrypted_data_bytes = base64.b64decode(encoded_data_b64)

                # Дешифровка XOR
                padded_text_bytes = xor_encrypt_decrypt_bytes(encrypted_data_bytes, key)

                # Преобразование в строку
                try:
                    # Декодирование как UTF-8 текст
                    padded_text = padded_text_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    # Если не UTF-8, обрабатываем как бинарные данные
                    padded_text = ''.join(f'{byte:08b}' for byte in padded_text_bytes)


                encoded_text = unpad_text(padded_text, padding_length)


                decoded_text = huffman_decode(encoded_text, huffman_codes)


                print("\nРезультаты:")
                print(f"Расшифрованный текст: {decoded_text}")
                save_to_file('decrypted_result.txt', decoded_text)

            except Exception as e:
                print(f"Произошла ошибка при обработке: {e}")


        elif choice == '3':
            print("Выход из программы.")
            break


        else:
            print("Неверный выбор. Пожалуйста, выберите 1, 2 или 3.")

if __name__ == "__main__":
    main()