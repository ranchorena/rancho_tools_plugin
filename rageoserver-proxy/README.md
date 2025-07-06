# docker build -t rageoserver-proxy:qa . 
# docker run -d --restart=always -p 8086:80 -d --name rageoserver-proxy-qa rageoserver-proxy:qa