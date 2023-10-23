
# Automated Smart City Cleaning System
This is a project aimed to automatically clean the wastes that appear in certin zones of a city/Community. This architecture consits of cameras placed on different zones and using a Machine learning approach detect the garbage and find the nearest Robot present and assign to clean. It uses various Middleware technologies such as HDFS, SpringBoot, MQtt, Rest APIs etc.

Project Done by:Karthika Nair,Changlong Ji
First part:Changlong Ji
1. run IP_preparation.py on MacBook
2. run /Users/jichanglong/Desktop/start_service.sh on MacBook
3. run vm_IP_preaparation.py on virtual machine using 'python3 vm_IP_preparation 1.1.1.1' where 1.1.1.1 is got from MacBook
4. run ./mvnw spring-boot:run on virtual machine at directory hd
5. get IP address on vietual machine to view vedios

Second part:Karthika Nair
Robot middleware: Python script that listens to an MQTT topic for incoming data, sends the data to multiple server URLs(Robots) , and then assigns a robot based on the minimum distance result.Contains several Robot scripts which implments RESTful web API using the Flask framework

