# Latex renderer for Github

Ever wanted to display latex expressions in your Readme file on GitHub? Just writing the latex code within dollar signs won't get you there as MathJax is not included on Github and no rendering is done server-side. There are a couple of workarounds for that issue

* Embed images that are part of the repository
* Use sites [codecogs](https://www.codecogs.com/latex/eqneditor.php) to request a rendered image of the equation you want to display

Both approaches have their downsides however. The former one is cumbersome can be a mess if you have a lot of equations. The latter one lacks customization abilities and you need to rely on an external website to work.

This script helps you with generating images from Latex code within the Readme file.

## Setup

To render the Latex code, this script relies on `tex2svg`. You can install it via `npm`:

```bash
npm install mathjax-node-cli
```

Regarding `npm` you probably find it through your package manager if you work on Linux. On Windows and maxOS, check out [nodejs.org](https://nodejs.org/en/download/).

## Usage

The script can be run in the command line. The first argument is the markdown file that should be rendered. The second argument is the folder where all the rendered SVGs are placed in. If your `tex2svg` binary is not placed in any of the folder that are listed in your `PATH` environment variable, you can explicitly specify the path to the binary with the `--engine` argument. The result is by default written back to the input file, or if explicitly specified by the `-o` argument to a different file. The latex code is retained in the `alt` attribute of the HTML image element.

Example:
```
python github-mathdown.py README.md images
```

## Showcase ($V\oplus W$)

This section contains some math to showcase the script. You can of course use inline expressions like $f(x)=\sqrt{x}$ for $x\in\mathbb{R}^+\cup \{0\}$. The script also correctly detects double dollar signs correctly as display elements, like so: $$\int_\epsilon^1 f(x) {\rm d}\! x > 0.$$

## Possible issues

* There is still work to do. Headings are only detected when written with sharp symbols and not if the next line containes equal or minus signs.
* The alignment is not perfect. GitHub does not allow custom css styles and therefore `vertical-align` cannot be used. The somewhat hackish solution is to use the HTML sub tag to lower the image.
