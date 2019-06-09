import argparse
import re
import shutil
import logging
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ElementTree
import xml.etree as etree
import hashlib
from pathlib import Path

COLOR = "rgb(36, 41, 46)"

STYLES = {
  "display": {
    "height": None,
    "unit": "px",
    "color": COLOR,
    "repr": '\n\n<p align="center"><img alt="{code}" src="{path}" /></p>\n\n'
  },
  "inline": {
    "height": 21,
    "unit": "px",
    "color": COLOR,
    "repr": '<sub><sub><img alt="{code}" src="{path}" /></sub></sub>'
  },
  "heading_1": {
    "height": 32,
    "unit": "px",
    "color": COLOR,
    "repr": '<sub><img alt="{code}" src="{path}" /></sub>'
  },
  "heading_2": {
    "height": 24,
    "unit": "px",
    "color": COLOR,
    "repr": '<sub><img alt="{code}" src="{path}" /></sub>'
  },
  "heading_3": {
    "height": 21,
    "unit": "px",
    "color": COLOR,
    "repr": '<sub><img alt="{code}" src="{path}" /></sub>'
  }
}


def split_unit(length):
  m = re.match(r"^(\d+(\.\d+)?)([a-zA-Z\%]+)$", length)
  return float(m.group(1)), m.group(3)


def latex_parse(code, style, inline, image_dir, engine):
  h = hashlib.new('md5')
  h.update((str(style) + code).encode("utf-8"))
  path = Path(image_dir) / (h.hexdigest() + ".svg")

  if path.is_file():
    return style["repr"].format(path=path.as_posix(),
                                code=code)

  if inline:
    args = [engine, code, "--inline"]
  else:
    args = [engine, code]

  process = Popen(args, stdout=PIPE, stderr=PIPE)
  output, err = process.communicate()
  process.wait()

  math_marker = '$' if inline else '$$'

  if len(err):
    logging.error("%s - ignoring", err.decode("utf-8").strip())
    return math_marker + code + math_marker

  ElementTree.register_namespace("","http://www.w3.org/2000/svg")
  ElementTree.register_namespace("xlink","http://www.w3.org/1999/xlink")
  root = ElementTree.fromstring(output)

  if style["height"]:
    height, height_unit = split_unit(root.attrib["height"])
    width, width_unit = split_unit(root.attrib["width"])

    assert width_unit == height_unit, "Units for height and width don't match."

    ratio = width / height
    root.attrib["height"] = str(style["height"]) + style["unit"]
    root.attrib["width"] = str(ratio * style["height"]) + style["unit"]

  for elem in root.getiterator():
      if "fill" in elem.attrib:
          elem.attrib["fill"] = style["color"]
      if "stroke" in elem.attrib:
          elem.attrib["stroke"] = style["color"]

  with open(str(path), "w") as f:
    f.write(ElementTree.tostring(root).decode("utf-8"))

  return style["repr"].format(path=path.as_posix(),
                              code=code)


def walk_latex_code(string, image_dir, engine):
  result = ""

  latex_iter = re.finditer(r"\${1,2}.*?(?<!\\)\${1,2}", string)
  unmatched_frame_start = 0

  for latex in latex_iter:
    malformed = False
    inline = True
    if latex.group(0).startswith("$$"):
      malformed = ~malformed
      inline = False
    if latex.group(0).endswith("$$"):
      malformed = ~malformed
    
    if malformed:
      logging.error("%s is malformed - ignoring", latex.group(0))
      continue

    heading = None
    line_start = string[:latex.start()].split("\n")[-1].strip()
    if line_start.startswith("###"):
      heading = "heading_3"
    elif line_start.startswith("##"):
      heading = "heading_2"
    elif line_start.startswith("#"):
      heading = "heading_1"

    if heading is not None:
      if not inline:
        logging.warning("display not supported in heading")

      svg_repr = latex_parse(latex.group(0)[1:-1],
                             STYLES[heading],
                             True,
                             image_dir,
                             engine)
    elif inline:
      svg_repr = latex_parse(latex.group(0)[1:-1],
                             STYLES["inline"],
                             True,
                             image_dir,
                             engine)
    else:
      svg_repr = latex_parse(latex.group(0)[2:-2],
                             STYLES["display"],
                             False,
                             image_dir,
                             engine)

    result += string[unmatched_frame_start:latex.start()] + svg_repr
    unmatched_frame_start = latex.end()

  return result + string[unmatched_frame_start:]
    

def check_tex2svg(tex2svg):
  if shutil.which(tex2svg) is None:
    logging.error("It seems you don't have tex2svg installed."
                  "You can install it though npm. It is contained"
                  "in the mathjax-node-cli package.\n"
                  "For more information, see the readme.")
    exit()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("markdown_file",
                      help="Path to the Markdown file that should be rendered.")
  parser.add_argument("image_directory",
                      help="Directory where the rendered images are placed in.")
  parser.add_argument("--engine",
                      help="Parameter for selecting which tex2svg to use.",
                      default="tex2svg")
  parser.add_argument("-o", "--output",
                      help="Output file.",
                      default=None)
  args = parser.parse_args()

  check_tex2svg(args.engine)

  with open(args.markdown_file) as f:
    result = walk_latex_code(f.read(), args.image_directory, args.engine)

  output = args.output
  if not output:
    output = args.markdown_file

  with open(output, "w") as f:
    f.write(result)

if __name__ == "__main__":
  main()
