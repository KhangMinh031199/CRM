#Build docker image
docker build -t crm:latest .

#Run image
docker run -d -p 8096:8096 crm:latest

#Go to localhost:8096

