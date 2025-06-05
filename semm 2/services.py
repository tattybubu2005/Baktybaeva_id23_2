from collections import Counter
import heapq

from app.schemas import EncodeResponse

class Node:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


class Coding:
    def __init__(self):
        self.codebook = {}

    def compress_and_encrypt(self, model):
        text = model.text
        key = model.key
        frequency = Counter(text).most_common()
        huffman_tree = self.build_tree(frequency)
        self.codebook = self.generate_codes(huffman_tree)
        encoded_text = self.encode(text)

        padding = (8 - len(encoded_text) % 8) % 8
        if padding > 0:
            encoded_text += '0' * padding

        encoded_data = self.xor_encrypt(encoded_text, key)

        return EncodeResponse(encoded_data=encoded_data,
                              key=key,
                              huffman_codes=self.codebook,
                              padding=padding)

    def decrypt_and_decompress(self, model):
        encoded_data = model.encoded_data
        key = model.key
        self.codebook = model.huffman_codes
        padding = model.padding
        encoded_text = self.xor_decrypt(encoded_data, key, padding)
        huffman_tree = self.build_tree_from_codebook()
        decoded_text = self.decode(encoded_text, huffman_tree)
        return {"decoded_text": decoded_text}

    def build_tree(self, frequency):
        heap = [Node(symbol, freq) for symbol, freq in frequency]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(None, left.frequency + right.frequency)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)

        return heap[0]

    def generate_codes(self, node, prefix=""):
        if node is not None:
            if node.symbol is not None:
                self.codebook[node.symbol] = prefix
            self.generate_codes(node.left, prefix + "0")
            self.generate_codes(node.right, prefix + "1")
        return self.codebook

    def encode(self, text):
        return ''.join(self.codebook[symbol] for symbol in text)

    def decode(self, encoded_text, huffman_tree):
        decoded_text = []
        current_node = huffman_tree
        for bit in encoded_text:
            if current_node is None:
                raise ValueError("Ошибка декодирования: достигнут конец дерева.")
            current_node = current_node.left if bit == '0' else current_node.right
            if current_node.symbol is not None:
                decoded_text.append(current_node.symbol)
                current_node = huffman_tree
        return ''.join(decoded_text)

    def xor_encrypt(self, text, key):
        encoded_bytes = bytes([int(text[i:i+8], 2) for i in range(0, len(text), 8)])
        key_bytes = key.encode()
        encrypted_bytes = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encoded_bytes))
        return encrypted_bytes.hex()

    def xor_decrypt(self, text, key, padding):
        encrypted_bytes = bytes.fromhex(text)
        key_bytes = key.encode()
        decrypted_bytes = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted_bytes))
        decoded_text = ''.join(f'{b:08b}' for b in decrypted_bytes)
        decoded_text = decoded_text[:len(decoded_text)-padding]
        return decoded_text

    def build_tree_from_codebook(self):
        reverse_codebook = {v: k for k, v in self.codebook.items()}
        root = Node(None, 0)

        for code, symbol in reverse_codebook.items():
            current_node = root
            for bit in code:
                if bit == '0':
                    if current_node.left is None:
                        current_node.left = Node(None, 0)
                    current_node = current_node.left
                else:
                    if current_node.right is None:
                        current_node.right = Node(None, 0)
                    current_node = current_node.right
            current_node.symbol = symbol

        return root
