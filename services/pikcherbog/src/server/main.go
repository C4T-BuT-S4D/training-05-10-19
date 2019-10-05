package main

import (
	"context"
	"database/sql"
	"flag"
	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
	"log"
	"net/http"
	"os"
	"os/signal"
	"server/helpers"
	"time"
)

func serve(server *http.Server) {
	log.Println("Serving on http://0.0.0.0:8000")

	if err := server.ListenAndServe(); err != nil {
		log.Println(err)
	}
}

func registerRoutes(router *mux.Router, db *sql.DB) {
	router.Handle("/", withCurrentUser(db, http.HandlerFunc(mainPage)))

	router.Handle("/register", withCurrentUser(db, http.HandlerFunc(registerGet))).Methods(http.MethodGet)
	router.Handle("/register", withCurrentUser(db, registerPostHandler(db))).Methods(http.MethodPost)

	router.Handle("/login", withCurrentUser(db, http.HandlerFunc(loginGet))).Methods(http.MethodGet)
	router.Handle("/login", withCurrentUser(db, loginPostHandler(db))).Methods(http.MethodPost)

	router.Handle("/logout", logoutHandler(db)).Methods(http.MethodGet)

	router.Handle("/create_post",
		withCurrentUser(db, loginRequired(http.HandlerFunc(createPostGet))),
	).Methods(http.MethodGet)

	router.Handle("/create_post",
		withCurrentUser(db, loginRequired(createPostPostHandler(db))),
	).Methods(http.MethodPost)

	router.Handle("/post/{postId:[0-9]+}",
		withCurrentUser(db, loginRequired(viewPostHandler(db))),
	).Methods(http.MethodGet)

	router.Handle("/post/{postId:[0-9]+}/edit",
		withCurrentUser(db, loginRequired(editPostGetHandler(db))),
	).Methods(http.MethodGet)

	router.Handle("/post/{postId:[0-9]+}/edit",
		withCurrentUser(db, loginRequired(editPostPostHandler(db))),
	).Methods(http.MethodPost)

	router.Handle("/post/{postId:[0-9]+}/delete",
		withCurrentUser(db, loginRequired(deletePostPostHandler(db))),
	).Methods(http.MethodGet)

	router.Handle("/last", withCurrentUser(db, listLastPostsHandler(db))).Methods(http.MethodGet)
	router.Handle("/my", withCurrentUser(db, listMyPostsHandler(db))).Methods(http.MethodGet)
	router.Handle("/random", withCurrentUser(db, listRandomPostsHandler(db))).Methods(http.MethodGet)

	router.Handle("/user/{username}", withCurrentUser(db, viewProfileHandler(db))).Methods(http.MethodGet)

	router.Use(requestsLogging)

	log.Println("Routes registration successful")
}

func main() {
	var wait time.Duration

	flag.DurationVar(
		&wait,
		"graceful-timeout",
		time.Second*15,
		"the duration for which the server gracefully wait for existing connections to finish - e.g. 15s or 1m",
	)

	flag.Parse()

	db, err := sql.Open("sqlite3", "./data/db.sqlite3")
	if err != nil {
		log.Fatal(err)
	}

	helpers.InitializeDatabase(db)

	router := mux.NewRouter()
	registerRoutes(router, db)

	helpers.LoadTemplates()

	helpers.InitRandom()

	server := &http.Server{
		Addr:         "0.0.0.0:8000",
		ReadTimeout:  time.Second * 15,
		WriteTimeout: time.Second * 15,
		IdleTimeout:  time.Second * 30,
		Handler:      router,
	}

	go serve(server)

	c := make(chan os.Signal, 1)

	signal.Notify(c, os.Interrupt)
	signal.Notify(c, os.Kill)

	<-c

	ctx, cancel := context.WithTimeout(context.Background(), wait)
	defer cancel()

	_ = server.Shutdown(ctx)

	log.Println("Exiting")
	os.Exit(0)
}
