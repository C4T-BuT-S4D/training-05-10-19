package main

import (
	"database/sql"
	"fmt"
	"github.com/gorilla/context"
	"github.com/gorilla/mux"
	"gopkg.in/russross/blackfriday.v2"
	"html/template"
	"log"
	"net/http"
	"server/helpers"
	"strconv"
	"strings"
	"time"
)

func mainPage(w http.ResponseWriter, r *http.Request) {
	user := context.Get(r, "currentUser")
	helpers.RenderTemplate(w, "index.html", user)
}

func registerGet(w http.ResponseWriter, _ *http.Request) {
	helpers.RenderTemplate(w, "register.html", nil)
}

func registerPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		username := r.FormValue("username")
		password := r.FormValue("password")

		if len(username) == 0 || len(password) == 0 {
			helpers.RenderTemplateWithFormError(
				"register.html",
				"",
				"Need to provide username and password",
				w,
				r,
			)
			return
		}

		passwordHash, salt := helpers.GeneratePasswordHash(password)

		row := db.QueryRow(
			"SELECT id FROM User WHERE username=? AND passwordHash=? ORDER BY id DESC LIMIT 1",
			username,
			passwordHash,
		)
		var userId int
		switch err := row.Scan(&userId); err {
		case nil:
			helpers.RenderTemplateWithFormError(
				"register.html",
				"",
				"User exists",
				w,
				r,
			)
			return
		case sql.ErrNoRows:

		default:
			log.Fatal(err)
		}

		_, err := db.Exec(
			"INSERT INTO User (username, passwordHash, salt) VALUES (?, ?, ?)",
			username,
			passwordHash,
			salt,
		)
		if err != nil {
			log.Fatal(err)
		}

		http.Redirect(w, r, "/", 302)
	})
}

func loginGet(w http.ResponseWriter, _ *http.Request) {
	helpers.RenderTemplate(w, "login.html", nil)
}

func loginPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		username := r.FormValue("username")
		password := r.FormValue("password")

		row := db.QueryRow(
			"SELECT id, salt, passwordHash FROM User WHERE username=? ORDER BY id DESC LIMIT 1",
			username,
		)
		var salt, realHash string
		var userId int
		switch err := row.Scan(&userId, &salt, &realHash); err {
		case nil:
		case sql.ErrNoRows:
			helpers.RenderTemplateWithFormError(
				"login.html",
				"",
				"Invalid credentials",
				w,
				r,
			)
			return
		default:
			log.Fatal(err)
		}

		passwordHash := helpers.GetPasswordHash(password, salt)

		if passwordHash != realHash {
			helpers.RenderTemplateWithFormError(
				"login.html",
				"",
				"Invalid credentials",
				w,
				r,
			)
			return
		}

		cookie := helpers.GenerateSessionCookie(userId, db, time.Now().Add(1440*time.Minute))

		http.SetCookie(w, &cookie)
		http.Redirect(w, r, "/", 302)
	})
}

func logoutHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer http.Redirect(w, r, "/", 302)

		prevCookie, err := r.Cookie("sessionid")
		if err != nil {
			return
		}
		_, _ = db.Exec("DELETE FROM Session WHERE sessionId=?", prevCookie.Value)

		expire := time.Unix(0, 0)
		cookie := http.Cookie{Name: "sessionid", Value: "", Path: "/", Expires: expire, MaxAge: 86400}
		http.SetCookie(w, &cookie)
	})
}

func createPostGet(w http.ResponseWriter, r *http.Request) {
	user := context.Get(r, "currentUser").(helpers.User)
	helpers.RenderTemplate(w, "createPost.html", helpers.FormStruct{CurrentUser: user})
}

func createPostPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		title := r.FormValue("title")
		body := r.FormValue("body")
		publish := r.FormValue("publish")

		if len(title) == 0 {
			helpers.RenderTemplateWithFormError(
				"createPost.html",
				"",
				"Title mustn't be empty",
				w,
				r,
			)
			return
		}

		var status string
		if len(publish) == 0 {
			status = "draft"
		} else {
			status = "published"
		}

		user := context.Get(r, "currentUser").(helpers.User)

		res, err := db.Exec(
			"INSERT INTO Post (authorId, title, body, status) VALUES (?, ?, ?, ?)",
			user.UserId,
			title,
			body,
			status,
		)
		if err != nil {
			log.Fatal(err)
		}
		newPostId, err := res.LastInsertId()
		if err != nil {
			log.Fatal(err)
		}
		redirectUrl := fmt.Sprintf("/post/%d", newPostId)
		http.Redirect(w, r, redirectUrl, 302)
	})
}

func viewPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		postId, err := strconv.Atoi(mux.Vars(r)["postId"])
		if err != nil {
			log.Fatal(err)
		}
		post := helpers.GetPostById(db, r, postId)

		if post == nil {
			redirectUrl := "/"
			http.Redirect(w, r, redirectUrl, 302)
		} else {
			mdBody := blackfriday.Run([]byte(post.Body))
			renderedPost := helpers.PostMDViewStruct{
				CurrentUser:    post.CurrentUser,
				AuthorUsername: post.AuthorUsername,
				PostId:         post.PostId,
				Title:          post.Title,
				Body:           template.HTML(string(mdBody)),
				Status:         post.Status,
			}

			helpers.RenderTemplate(w, "viewPost.html", renderedPost)
		}
	})
}

func editPostGetHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		postId, err := strconv.Atoi(mux.Vars(r)["postId"])
		if err != nil {
			log.Fatal(err)
		}
		post := helpers.GetPostById(db, r, postId)
		postWithoutErrors := helpers.PostEditFormStruct{
			Error:          nil,
			CurrentUser:    post.CurrentUser,
			AuthorUsername: post.AuthorUsername,
			Title:          post.Title,
			Body:           post.RawBody,
			Status:         post.Status,
		}

		helpers.RenderTemplate(w, "editPost.html", postWithoutErrors)
	})
}

func editPostPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		postId := mux.Vars(r)["postId"]
		row := db.QueryRow(
			`SELECT username FROM User INNER JOIN Post 
  						ON User.id=Post.authorId WHERE Post.id=? ORDER BY User.id DESC LIMIT 1`,
			postId,
		)
		var authorUsername string
		switch err := row.Scan(&authorUsername); err {
		case nil:
		case sql.ErrNoRows:
			http.NotFound(w, r)
			return
		default:
			log.Fatal(err)
		}

		user := context.Get(r, "currentUser").(helpers.User)

		if authorUsername != user.Username {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		title := r.FormValue("title")
		body := r.FormValue("body")
		published := r.FormValue("publish")

		var status string
		if len(published) == 0 {
			status = "draft"
		} else {
			status = "published"
		}

		if len(title) == 0 {
			postWithErrors := helpers.PostEditFormStruct{
				Error:          &(helpers.FormError{Field: "Title cannot be empty"}),
				CurrentUser:    user,
				AuthorUsername: authorUsername,
				Title:          title,
				Body:           body,
				Status:         status,
			}
			helpers.RenderTemplate(w, "editPost", postWithErrors)
			return
		}

		_, err := db.Exec(
			"UPDATE Post SET authorId=?, title=?, body=?, status=?  WHERE id=?",
			user.UserId,
			title,
			body,
			status,
			postId,
		)
		if err != nil {
			log.Fatal(err)
		}

		redirectUrl := fmt.Sprintf("/post/%s", postId)
		http.Redirect(w, r, redirectUrl, 302)
	})
}

func deletePostPostHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		postId := mux.Vars(r)["postId"]
		row := db.QueryRow(
			`SELECT username FROM User INNER JOIN Post 
  						ON User.id=Post.authorId WHERE Post.id=? ORDER BY User.id DESC LIMIT 1`,
			postId,
		)
		var authorUsername string
		switch err := row.Scan(&authorUsername); err {
		case nil:
		case sql.ErrNoRows:
			http.NotFound(w, r)
			return
		default:
			log.Fatal(err)
		}

		user := context.Get(r, "currentUser").(helpers.User)

		if authorUsername != user.Username {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		_, _ = db.Exec("DELETE FROM Post WHERE id=?", postId)

		http.Redirect(w, r, "/", 302)
	})
}

func listLastPostsHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		count := helpers.GetCountFromQuery(r, 100, 20)
		rows, err := db.Query(
			`SELECT u.username, p.id, p.title, p.body, p.status FROM Post p
					INNER JOIN User u on u.id = p.authorId
					WHERE status='published'
					ORDER BY p.id DESC LIMIT ?`,
			count,
		)

		if err != nil {
			log.Fatal(err)
		}

		defer rows.Close()

		result := helpers.GetPostList(r, rows)
		helpers.RenderTemplate(w, "postList.html", result)
	})
}

func listRandomPostsHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		count := helpers.GetCountFromQuery(r, 100, 20)

		filters := helpers.GetFiltersFromQuery(r)

		sqlFilter := strings.Join(filters, " and ")

		if len(sqlFilter) != 0 {
			sqlFilter = fmt.Sprintf("and %s", sqlFilter)
		}

		// Secure printf
		query := fmt.Sprintf(`SELECT u.username, p.id, p.title, p.body, p.status FROM Post p
					INNER JOIN User u on u.id = p.authorId 
					WHERE status='published' %s ORDER BY RANDOM() LIMIT ?`, sqlFilter)

		rows, err := db.Query(query, count)

		if err != nil {
			http.Error(w, "Bad filter", http.StatusBadRequest)
			return
		}

		defer rows.Close()

		result := helpers.GetPostList(r, rows)
		helpers.RenderTemplate(w, "postList.html", result)
	})
}

func listMyPostsHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		count := helpers.GetCountFromQuery(r, 100, 20)
		rows, err := db.Query(
			`SELECT u.username, p.id, p.title, p.body, p.status FROM Post p
					INNER JOIN User u on u.id = p.authorId
					WHERE authorId=?
					ORDER BY p.id DESC LIMIT ?`,
			context.Get(r, "currentUser").(helpers.User).UserId,
			count,
		)

		if err != nil {
			log.Fatal(err)
		}

		defer rows.Close()

		result := helpers.GetPostList(r, rows)
		helpers.RenderTemplate(w, "postList.html", result)
	})
}

func viewProfileHandler(db *sql.DB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		username := mux.Vars(r)["username"]

		row := db.QueryRow("SELECT id from User where username=?", username)

		var userId int
		switch err := row.Scan(&userId); err {
		case sql.ErrNoRows:
			http.NotFound(w, r)
			return
		case nil:
		default:
			log.Fatal(err)
		}

		rows, err := db.Query(
			`SELECT u.username, p.id, p.title, p.body, p.status FROM Post p
					INNER JOIN User u on u.id = p.authorId
					WHERE authorId=?
					ORDER BY p.id DESC LIMIT 20`,
			userId,
		)

		if err != nil {
			log.Fatal(err)
		}

		defer rows.Close()

		posts := helpers.GetPostList(r, rows)

		result := helpers.ProfileView{ListView: posts, Username: username}
		helpers.RenderTemplate(w, "profile.html", result)
	})
}
