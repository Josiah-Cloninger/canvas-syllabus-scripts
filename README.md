# canvas-syllabus-scripts
Scripts using the Canvas API to grab syllabus data.


## Dependencies
I recommend creating a conda environment for all the dependencies

```
$ conda create --name canvas-api python=3.6.2
$ conda activate canvas-api
(canvas-api) $ pip install -r requirements.txt
```


## Usage Example

To audit visibility of syllabi:

```
python audit.py --config your_config.yml  --visibility 
```

To audit and update visibility of syllabi:

```
python audit.py --config your_config.yml --visibility --update
```

To audit course access not matching term start/end:

```
python audit.py --config my_config.yml --access
```

To audit and update course access to match term start/end:

```
python audit.py --config my_config.yml --access --update
```

To scrape syllabi:

```
python scrape.py --config your_config.yml --download path-to-downloads-dir
```

