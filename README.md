# GBA Hotels
A course project for Database Systems (CSC3170), 2021 Spring at CUHK-Shenzhen.

## Group Members:
* **Zhu Chuyan 119010486@link.cuhk.edu.cn** (Leading)
* Xiao Wenli 119010346@link.cuhk.edu.cn
* Xu Xuanyang 119010361@link.cuhk.edu.cn
* Wang Chongrui 119020049@link.cuhk.edu.cn
* Zhang Yizhan 119010450@link.cuhk.edu.cn

## Introduction
GBA Hotels, short for Greater Bay Area Hotels, is a hotel reservation and management system. You can both login as a guest user or a management user from different portals. It supports hotel reservation for the guest user and management for the management user.
The application is built by Zhu Chuyan (Philip) based on Django framework and SQLite3 databse engine.

### Where are the embedded SQL queries
You can refer to https://github.com/philipzhux/gba-hotel/blob/main/reservations/views.py and https://github.com/philipzhux/gba-hotel/blob/main/home/views.py to check how we embed the SQL queries into the web application.

## How to test
For the ease of deployment we have encapsulated the whole application into a docker image, you can choose either one of the two methods below to run, note that for either way you need to first ```cd``` to the root directory of our project folder first.

### Run via docker
```shell
docker load -i gbahotels.tar
docker run -p 3170:8000 gbahotels
```
### Run directly
If you prefer to run directly on your local machine, you go to the root directory of our project and run:
```shell
pip install -r requirements.txt
python manage.py runserver 127.0.0.1:3170
```
### Visit the site
* Visit http://127.0.0.1:3170 on your local machine to test our system after you run either directly or via docker as is shown above. 
* You can also choose to visit http://philipnetwork.com:3170 so that you do not need to run on your local machine by yourself.

### Test account:
#### Guest users:
Username: 1_Sara-ann_Fellon Password: 0 <br>
Username: 23_Innis_cornhill Password: 0 <br>
Username: 422_Lucina_Arkell Password: 0 <br>

#### Management(Employee) Account:
Username: Gwenora Mattussevich Password: 111111 <br>
Username: Karl McCreary Password: 111111 <br>
Username: Avictor Cranage Password: 111111 <br>
You need to login the management account from the management portal, you can visit it by clicking the image in the upper right corner of the homepage:
[<img src="https://user-images.githubusercontent.com/62172698/116790986-fd609800-aae9-11eb-9442-d89c20d07b97.png">](http://philipnetwork.com:3170/office/)
