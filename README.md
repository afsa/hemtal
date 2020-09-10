# hemtal

Script to move peergrade solutions from individual dirs to a combined dir and sending email to students.

## Installation

Clone this repository and make the script `hemtal.py` executable.

```shell script
git clone git@github.com:afsa/hemtal.git
cd hemtal
chmod +x hemtal.py
```


## How to move solutions

```shell script
./hemtal move <PATH TO SOLUTIONS> <DESTINATION PATH>
```

## How to send emails to students

```shell script
./hemtal email <PATH TO SOLUTIONS>
```