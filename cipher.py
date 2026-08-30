LOWER_A_N = "abcdefghijklmn"        
LOWER_O_Z = "opqrstuvwxyz"          
UPPER_A_M = "ABCDEFGHIJKLM"         
UPPER_N_Z = "NOPQRSTUVWXYZ"         
DIGITS = "0123456789"               


def _shift_within(ch: str, amount: int, alphabet: str) -> str:
    size = len(alphabet)
    index = alphabet.index(ch)
    new_index = (index + amount) % size
    return alphabet[new_index]


def _encrypt_char(ch: str, shift1: int, shift2: int) -> str:
    if ch in LOWER_A_N:
        return _shift_within(ch, shift1 * shift2, LOWER_A_N)
    if ch in LOWER_O_Z:
        return _shift_within(ch, -(shift1 + shift2), LOWER_O_Z)

    if ch in UPPER_A_M:
        return _shift_within(ch, -shift1, UPPER_A_M)
    if ch in UPPER_N_Z:
        return _shift_within(ch, shift2 ** 2, UPPER_N_Z)

    if ch in DIGITS:
        return _shift_within(ch, shift1 - shift2, DIGITS)

    return ch


def _decrypt_char(ch: str, shift1: int, shift2: int) -> str:
    if ch in LOWER_A_N:
        return _shift_within(ch, -(shift1 * shift2), LOWER_A_N)
    if ch in LOWER_O_Z:
        return _shift_within(ch, shift1 + shift2, LOWER_O_Z)

    if ch in UPPER_A_M:
        return _shift_within(ch, shift1, UPPER_A_M)
    if ch in UPPER_N_Z:
        return _shift_within(ch, -(shift2 ** 2), UPPER_N_Z)

    if ch in DIGITS:
        return _shift_within(ch, -(shift1 - shift2), DIGITS)

    return ch


def encrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    encrypted = ''.join(_encrypt_char(ch, shift1, shift2) for ch in text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(encrypted)


def decrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    decrypted = ''.join(_decrypt_char(ch, shift1, shift2) for ch in text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decrypted)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    with open(original_path, 'r', encoding='utf-8') as f:
        original = f.read()
    with open(decrypted_path, 'r', encoding='utf-8') as f:
        decrypted = f.read()

    success = original == decrypted
    if success:
        print("Verification successful: decrypted text matches the original.")
    else:
        print("Verification failed: decrypted text does NOT match the original.")
    return success


def _prompt_for_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if value < 0:
            print("Please enter a non-negative integer.")
            continue
        return value


def main() -> None:
    shift1 = _prompt_for_int("Enter shift1 (non-negative integer): ")
    shift2 = _prompt_for_int("Enter shift2 (non-negative integer): ")

    raw_path = "raw_text.txt"
    encrypted_path = "encrypted_text.txt"
    decrypted_path = "decrypted_text.txt"

    encrypt_file(shift1, shift2, raw_path, encrypted_path)
    print(f"Encrypted '{raw_path}' -> '{encrypted_path}'")

    decrypt_file(shift1, shift2, encrypted_path, decrypted_path)
    print(f"Decrypted '{encrypted_path}' -> '{decrypted_path}'")

    verify_files(raw_path, decrypted_path)


if __name__ == "__main__":
    main()