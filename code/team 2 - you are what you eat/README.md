# Jongvee Challenge


## The challenge

Currently calfs who eventually become milk cows are selected purely based on genetics. The calf whose mother gave a lot of milk is expected to also give a lot of milk. In this project, we research whether there are other factors that influence future milk production, for example the growth of the calf in its first year, of the amount of milk and water it consumed.

## The data

We used sensor data from farm devices such as feeding robots, scales, etc. And MPR data from CRV regarding genetics and eventual milk production of the calfs

## The problem - 60% of time spent on data cleaning

As usual in data science projects, the biggest problem was data preprocessing and cleaning. The format of the data delivered by the farm robots is not very handy: the data is delivered as a large collection of TSV files in an intricate directory structure. We've created a Python script (`LoadDairyCampus.py`) that crawl this directory structure and loads the data into a PostgreSQL database. We merge data from multiple TSV files into larger tables containing measurements from all cows. For this challenge, we created the following tables:

* `gewicht` (colums: `animal_number`, `timestamp`, `wcorr`)
* `melkopname` (columns: `animal_number`, `timestamp`, `soll`, `soll_rm`, `abruf`)
* `wateropname` (columns: `animal_number`, `daytikscounter`, `tiks`)

The `LoadDairyCampus.py` script can be easily adapted to import similar datasets.

We also imported the MPR data into the database, which luckily was quite easy, because data was delivered in Excel format which can easily be transformed into CSV.

The only problems here were:
* The animal number contains space between 'NL' and the rest of the number while sensor data doesn't. We needed to fix it before we could join the datasets
* The real numbers are stored in Dutch format - with a ',' rather than '.'. Databases prefer dots.

Once we got the data in the database and started playing with it, we realized that some data is of really low quality. Some examples:

* milk intake data (`melkopname`) contains a lot of zeros. For some calfs we could only find 2 days in which they were actually drinking milk, according to the data. Since it's probably a data-collection problem, we needed to discard all calfs which didn't have enough data on their milk intake

* weight data quality depends on how the calf was standing on the scales. If the calf put only their front legs on the scales, the weight measurement gets suddenly much lower. Also the sensors seem to break sometimes. For some cows we saw the weight fluctuating between 20 and 6000 kg.

After removing all the faulty data, we ended up with only 41 cows to train our model on (initially there were 140 cows in the dataset).

To clean and join all the tables, we used our (Rax)[http://www.raxdb.com] tool which is a language for data processing. It is much easier to use than SQL, but eventually compiles to SQL queries which are then run directly in the database. Since the processed dataset is very small, Rax eventually generates a CSV file that can be used by Python or R. The following Rax scripts are used to create the eventual dataset:

* `import.rax`
* `create_features.rax`

To run them, install Rax and then use:

`./run_rax create_features.rax`

Rax is free for non-commercial uses. (Contact us)[mailto:info@codersco.com] for a free copy.

## The model
Since the sample size of the data is rather small we can't use sophisticated from machine learning. We opted for a well-known simple linear regression.

The idea of this model is simple. Suppose you have a target variable Y and an explanatory variable X. We can formulate the model, as follows
Y= a+ b*X, where a and b are the parameters of the model. a is called the intercept or constant and b is the slope. The model easily generalizes to allow for multiple explanatory variables.

For this hackathon, we created 3 models to explain milk, fat and protein production for the first 305 days of cows based on calfs data. Our explanatory variables were weight of calfs after when they were 60 days old, 120 days old, average milk intake of calfs between 40 and 80 days old (the interval was chosen to keep as many calfs in the sample yet to have comparable data between calfs), genetic data, water intake.

It turned out, that for the 40 calfs we considered, the milk production is determined mostly by genetic factors, milk intake and the weight of calfs. Milk intake is more important for fat production and the weight affects more the protein production. Check out cows.ipynb for data exploration and the details of our models. 
