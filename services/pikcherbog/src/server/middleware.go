package main

import (
	"database/sql"
	"github.com/gorilla/context"
	"log"
	"net/http"
	"server/helpers"
)


func requestsLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%s to %s\n", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

func withCurrentUser(db *sql.DB, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer next.ServeHTTP(w, r)

		userId := helpers.GetCurrentUserId(db, r)

		if userId == nil {
			return
		}

		row := db.QueryRow("SELECT username FROM User WHERE id=?", userId)
		var username string

		switch err := row.Scan(&username); err {
		case sql.ErrNoRows:
			return
		case nil:
			user := helpers.User{UserId: *userId, LoggedIn: true, Username: username}
			context.Set(r, "currentUser", user)
		default:
			log.Fatal(err)
		}
	})
}

func loginRequired(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, ok := context.Get(r, "currentUser").(helpers.User)
		if !ok {
			http.Redirect(w, r, "/login", 302)
			return
		}
		next.ServeHTTP(w, r)
	})
}
