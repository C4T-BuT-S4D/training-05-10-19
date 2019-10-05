package helpers

import (
	"crypto/sha1"
	"fmt"
	"math/rand"
)

func InitRandom() {
	rand.Seed(0)
}

var alphabet = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

func randomString(length int) string {
	result := make([]rune, length)
	for i := range result {
		result[i] = alphabet[rand.Intn(len(alphabet))]
	}
	return string(result)
}


func GeneratePasswordHash(password string) (result string, salt string) {
	salt = randomString(10)

	h := sha1.New()
	h.Write([]byte(password + salt))
	result = fmt.Sprintf("%x", h.Sum(nil))
	return
}


func GetPasswordHash(password string, salt string) string {
	h := sha1.New()
	h.Write([]byte(password + salt))
	result := fmt.Sprintf("%x", h.Sum(nil))
	return result
}
