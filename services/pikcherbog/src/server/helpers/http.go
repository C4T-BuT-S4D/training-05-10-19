package helpers

import (
	"database/sql"
	"fmt"
	"github.com/gorilla/context"
	"log"
	"net/http"
	"strconv"
	"time"
)

func GetCurrentUserId(db *sql.DB, req *http.Request) *int {
	sessionCookie, err := req.Cookie("sessionid")
	if err != nil {
		return nil
	}

	sessionId := sessionCookie.Value

	query := fmt.Sprintf("SELECT userId FROM Session WHERE sessionId='%s'", sessionId)

	row := db.QueryRow(query)
	var userId int
	switch err := row.Scan(&userId); err {
	case sql.ErrNoRows:
		return nil
	case nil:
		return &userId
	default:
		log.Fatal(err)
	}
	return nil
}

func RenderTemplateWithFormError(templateName string, field string, message string, w http.ResponseWriter, r *http.Request) {
	currentError := FormError{message, field}
	currentUser, _ := context.Get(r, "currentUser").(User)
	data := FormStruct{currentUser, &currentError}

	RenderTemplate(w, templateName, data)
}

func GetCountFromQuery(r *http.Request, max, def int) int {
	countStr := r.URL.Query().Get("count")
	count := def
	countInt, err := strconv.Atoi(countStr)
	if err == nil && countInt <= max {
		count = countInt
	}
	return count
}

func GetFiltersFromQuery(r *http.Request) []string {
	results := make([]string, 0)
	for key := range r.URL.Query() {
		results = append(results, fmt.Sprintf("%s=%s", key, r.URL.Query().Get(key)))
	}
	return results
}

func GenerateSessionCookie(userId int, db *sql.DB, expire time.Time) http.Cookie {
	sessionId := randomString(32)
	_, err := db.Exec("INSERT INTO Session (sessionId, userId) VALUES (?, ?)", sessionId, userId)
	if err != nil {
		log.Fatal(err)
	}

	cookie := http.Cookie{Name: "sessionid", Value: sessionId, Path: "/", Expires: expire, MaxAge: 86400}
	return cookie
}