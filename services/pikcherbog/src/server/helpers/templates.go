package helpers

import (
	"fmt"
	"github.com/oxtoacart/bpool"
	"html/template"
	"log"
	"net/http"
	"path/filepath"
)

var templates map[string]*template.Template
var bufpool *bpool.BufferPool

const mainTmpl = `{{ define "main" }} {{ template "base" . }} {{ end }}`

func LoadTemplates() {
	if templates == nil {
		templates = make(map[string]*template.Template)
	}

	layoutFiles, err := filepath.Glob("templates/layout/*.html")
	if err != nil {
		log.Fatal(err)
	}

	includeFiles, err := filepath.Glob("templates/*.html")
	if err != nil {
		log.Fatal(err)
	}

	mainTemplate := template.New("main")

	mainTemplate, err = mainTemplate.Parse(mainTmpl)
	if err != nil {
		log.Fatal(err)
	}

	for _, file := range includeFiles {
		fileName := filepath.Base(file)
		files := append(layoutFiles, file)
		templates[fileName], err = mainTemplate.Clone()
		if err != nil {
			log.Fatal(err)
		}
		templates[fileName] = template.Must(templates[fileName].ParseFiles(files...))
	}

	log.Println("Templates loading successful")

	bufpool = bpool.NewBufferPool(64)
	log.Println("Buffer allocation successful")
}

func RenderTemplate(w http.ResponseWriter, name string, data interface{}) {
	tmpl, ok := templates[name]
	if !ok {
		log.Fatal(fmt.Sprintf("The template %s does not exist.", name))
	}

	buf := bufpool.Get()
	defer bufpool.Put(buf)

	err := tmpl.Execute(buf, data)
	if err != nil {
		log.Fatal(err)
	}

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, err = buf.WriteTo(w)
	if err != nil {
		log.Fatal(err)
	}
}
