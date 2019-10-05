package helpers

import "html/template"

type User struct {
	UserId int
	LoggedIn bool
	Username string
}

type FormError struct {
	Message string
	Field   string
}

type FormStruct struct {
	CurrentUser User
	Error *FormError
}

type PostEditFormStruct struct {
	CurrentUser User
	AuthorUsername string
	PostId int
	Title string
	Body string
	Status string
	Error *FormError
}

type PostMDViewStruct struct {
	CurrentUser User
	AuthorUsername string
	PostId int
	Title string
	Body template.HTML
	Status string
	RawBody string
}

type PostListView struct {
	CurrentUser User
	Posts []PostMDViewStruct
}

type Filter struct {
	Key string
	Value string
}

type ProfileView struct {
	Username string
	ListView PostListView
}