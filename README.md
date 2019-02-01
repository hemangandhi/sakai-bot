# Sakai Automation

Because why use sakai from a browser?

## How Install

1. Git clone this
1. Install python dependencies (I recommend using a virtualenv. This is only tested on py 3.6.6.)
1. Install firefox and the geckodriver.

## Running

`python main.py some gibberish` will produce a help message. GL, HF.

## TODO

Make the rest of it:
- Automate grading
- Automate submissions
- Figure out downloading resources
    - Should it be able to re-arrange the filesystem?

Clean up:
- Make it stateful?
- Don't hard-depend on firefox.
- Output more smartly than buffering a huge string.
