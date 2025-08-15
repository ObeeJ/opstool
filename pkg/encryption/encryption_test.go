package encryption

import (
	"testing"
)

func TestEncryptDecrypt(t *testing.T) {
	// Test basic encryption and decryption
	plaintext := "Hello, World! This is a test message."
	key := "test-key-32-characters-long-123"

	// Create encryptor
	encryptor := NewEncryptor(key)

	// Encrypt the plaintext
	encrypted, err := encryptor.Encrypt(plaintext)
	if err != nil {
		t.Fatalf("Failed to encrypt: %v", err)
	}

	if encrypted == "" {
		t.Error("Encrypted text should not be empty")
	}

	if encrypted == plaintext {
		t.Error("Encrypted text should be different from plaintext")
	}

	// Decrypt the ciphertext
	decrypted, err := encryptor.Decrypt(encrypted)
	if err != nil {
		t.Fatalf("Failed to decrypt: %v", err)
	}

	if decrypted != plaintext {
		t.Errorf("Decrypted text doesn't match original. Expected: %s, Got: %s", plaintext, decrypted)
	}
}

func TestEncryptWithDifferentKeys(t *testing.T) {
	plaintext := "Secret message"
	key1 := "key1-32-characters-long-abcdef"
	key2 := "key2-32-characters-long-ghijkl"

	// Create encryptors with different keys
	encryptor1 := NewEncryptor(key1)
	encryptor2 := NewEncryptor(key2)

	// Encrypt with first key
	encrypted, err := encryptor1.Encrypt(plaintext)
	if err != nil {
		t.Fatalf("Failed to encrypt with key1: %v", err)
	}

	// Try to decrypt with wrong key
	_, err = encryptor2.Decrypt(encrypted)
	if err == nil {
		t.Error("Expected error when decrypting with wrong key")
	}
}

func TestEncryptEmptyString(t *testing.T) {
	key := "test-key-32-characters-long-123"
	encryptor := NewEncryptor(key)

	// Test encrypting empty string
	encrypted, err := encryptor.Encrypt("")
	if err != nil {
		t.Errorf("Failed to encrypt empty string: %v", err)
	}

	// Test decrypting back to empty string
	decrypted, err := encryptor.Decrypt(encrypted)
	if err != nil {
		t.Errorf("Failed to decrypt empty string: %v", err)
	}

	if decrypted != "" {
		t.Errorf("Expected empty string, got: %s", decrypted)
	}
}
