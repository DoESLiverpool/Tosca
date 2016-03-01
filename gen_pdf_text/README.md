# Generate pdf display text

Using [pandoc](http://pandoc.org/) to generate an output pdf for further conversion to svg, use:

pandoc --to=beamer --template=template.tex --output=output.pdf test.md

or:

pandoc --to=beamer --template=template.tex --output=output.pdf < test.md

or:

echo test.md | pandoc --to=beamer --template=template.tex --output=output.pdf

Alternatively, any required text can be piped from echo:

echo "This is a test" | pandoc --to=beamer --template=template.tex --output=output.pdf

## Template

The included template is almost identical to the standard pandoc template, except
that a few lines are added to [suppress the default beamer footer](http://tex.stackexchange.com/questions/223200/how-to-completely-remove-footer-in-beamer) that contains 
controls relevant to use in a slideshow.
