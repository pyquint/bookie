For styling, it is highly recommended to use [Sass](https://sass-lang.com/) with the [libsass](https://sass.github.io/libsass-python/frameworks/flask.html) package.

# Working with Sass
The `.sass` and generated `.scss.css` files are found in the `static/sass` and `static/css` directory, respectively.

[Using `libsass` with Flask](https://sass.github.io/libsass-python/frameworks/flask.html), we do not have to redeploy the application with every change in the `.sass` file. One only needs to reload the webpage, which will compile the Sass file and generate an  `.scss.css` output file, with the same filename as the `.sass` one.

## Creating and linking new stylesheets
Just create a new `.sass` file in the `sass` folder. To link, use the `url_for` function and target the generated CSS file.

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/<filename>.scss.css') }}" type="text/css" />
```

> **Apply styling on the `sass` folder, not on the `css` folder.**
