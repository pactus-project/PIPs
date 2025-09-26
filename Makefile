install:
	bundle install

build: install
	bundle exec jekyll build

serve: install
	bundle exec jekyll serve

check: build
	mdl --style=./config/.mdlrc.rb ./PIPs
	htmlproofer --enforce-https=false --ignore-missing-alt=true --ignore-status-codes "999,429,403" --ignore-urls="" ./_site

exif:
	for i in $(shell find ./assets -name "*.png" -o -name "*.gif" -o -name "*.jpg" -o -name "*.jpeg"); do \
		echo "Processing $$i"; \
		exiftool -all= "$$i"; \
	done

