# Marvel Legendary Dividers Generator

## Example
![](https://github.com/ruler501/LegendaryDividers/raw/master/example.png)

## Setup
Install poppler for your system and add it to your PATH.

Windows users will have to install [poppler for Windows](http://blog.alivate.com.au/poppler-windows/), then add the `bin/` folder to [Path](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/).

Mac users will have to install [poppler for Mac](http://macappstore.org/poppler/).

Linux users will have both tools pre-installed with Ubuntu 16.04+ and Archlinux. If it's not, run `sudo apt install poppler-utils`

Ensure Python 3.6 is installed and added to the system PATH.

Then run `virtualenv .env && source .env/bin/activate && pip install -r requirements.txt` and all the required packages will install.

## Use

Customize `cards.yaml` with the cards you want dividers for. Then you can run `python divider.py` to generate a double sided pdf for the dividers. For themes it will search the `resources/icons` directory for a png file with the same name and use that instead of text if available.

You can extract the images from finnsea15's dividers which can be found at <https://boardgamegeek.com/geeklist/191904/item/3925465>. All credit for the images used goes to him. The tool to extract them can be run with `python extract_images.py` and customized through `image_sources.yaml`. Traversal order is left to right, top to bottom.

You can further customize the parameters in the file to get the precise layout you want. It should even be capable of supporting vertical dividers if someone figures out the measurements for them.