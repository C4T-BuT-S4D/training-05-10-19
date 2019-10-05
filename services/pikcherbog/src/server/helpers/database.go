package helpers

import (
	"database/sql"
	"github.com/gorilla/context"
	"gopkg.in/russross/blackfriday.v2"
	"html/template"
	"log"
	"net/http"
)

func InitializeDatabase(db *sql.DB) {
	_, err := db.Exec("CREATE TABLE IF NOT EXISTS Session(sessionId varchar(32), userId integer)")
	if err != nil {
		log.Fatal(err)
	}
	_, err = db.Exec(
		`CREATE TABLE IF NOT EXISTS 
  					User(
  				  		id integer primary key, 
  				  		username varchar(25), 
  				  		passwordHash varchar(40),
  				  		salt varchar(10)
  					)`,
	)
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec(
		`CREATE TABLE IF NOT EXISTS 
  					Post(
  				  		id integer primary key, 
  				  	  	authorId integer,
  				  	  	title varchar(255) not null default '',
  				  	  	body text,
  				  	  	status varchar(10) not null default 'draft'
  					)`,
	)
	if err != nil {
		log.Fatal(err)
	}

	//noinspection SqlWithoutWhere
	_, err = db.Exec("DELETE FROM Session")
	if err != nil {
		log.Fatal(err)
	}
}

func GetPostById(db *sql.DB, r *http.Request, postId int) *PostMDViewStruct {
	row := db.QueryRow(
		`SELECT u.username, p.title, p.body, p.status FROM Post p
					INNER JOIN User u on u.id = p.authorId 
					WHERE p.id=?`, postId)
	var authorUsername, title, body, status string
	switch err := row.Scan(&authorUsername, &title, &body, &status); err {
	case sql.ErrNoRows:
		return nil
	case nil:
	default:
		log.Fatal(err)
	}

	user := context.Get(r, "currentUser").(User)

	if authorUsername != user.Username && status != "published" {
		return nil
	}

	mdBody := blackfriday.Run([]byte(body))
	renderedPost := PostMDViewStruct{
		CurrentUser:    user,
		PostId:         postId,
		AuthorUsername: authorUsername,
		Title:          title,
		Body:           template.HTML(string(mdBody)),
		Status:         status,
		RawBody:        body,
	}

	return &renderedPost
}

func GetPostList(r *http.Request, rows *sql.Rows) PostListView {
	user, ok := context.Get(r, "currentUser").(User)
	if !ok {
		user = User{LoggedIn: false}
	}

	result := PostListView{CurrentUser: user}

	for rows.Next() {
		var cur PostMDViewStruct
		err := rows.Scan(
			&cur.AuthorUsername,
			&cur.PostId,
			&cur.Title,
			&cur.RawBody,
			&cur.Status,
		)
		if err != nil {
			log.Fatal(err)
		}
		mdBody := blackfriday.Run([]byte(cur.RawBody))
		cur.Body = template.HTML(string(mdBody))
		result.Posts = append(result.Posts, cur)
	}
	err := rows.Err()
	if err != nil {
		log.Fatal(err)
	}

	return result
}
