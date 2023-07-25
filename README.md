# uwaterloo-class-slots-notifier
A script compatible with AWS Lambda that uses Selenium to scrape `https://classes.uwaterloo.ca/under.html`, detecting open slots in a given course. 
Current hard-coded for the CS246 course specifically, but can be easily changed to track a different course instead.

## Required Packages
Due to the nature of the Selenium and Chromedriver packages, this script can only be run via AWS Lambda if a very specific set of package versions is used. 
Also, Python versions past 3.7 with these packages do not work with AWS Lambda. The packages needed are as follows:

```
pip3.7 install -t selenium/python/lib/python3.7/site-packages selenium==3.8.0
curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
```

## Running with AWS Lambda
Currently hardcoded to send a start-of-day report and end-of-day report at 10:32 am and 10:32 pm respectively. The AWS Lambda function has two triggers, one running
every 5 minutes and another running the start-of-day and end-of-day reports. No event JSON is needed. Selenium and Chromedriver packages must be added as layers 
for the AWS Lambda function.
