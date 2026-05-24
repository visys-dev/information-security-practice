from cryptography.fernet import Fernet


def main() -> None:
    key = Fernet.generate_key().decode("utf-8")
    print("Generated Fernet key:")
    print(f"ENCRYPTION_KEY={key}")
    print()
    print("Keep this key outside Git. Losing it means losing encrypted data.")


if __name__ == "__main__":
    main()

