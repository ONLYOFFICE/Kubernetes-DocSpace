import os
import sys
import subprocess
import time
import logging

redisHost = os.environ.get('REDIS_HOST')
redisPort = os.environ.get('REDIS_PORT')
redisUser = os.environ.get('REDIS_USER_NAME')
redisPassword = os.environ.get('REDIS_PASSWORD')
redisDBNum = '0'
redisConnectTimeout = 15

dbType = 'mysql'
dbHost = os.environ.get('MYSQL_HOST')
dbPort = int(os.environ.get('MYSQL_PORT'))
dbUser = os.environ.get('MYSQL_USER')
dbPassword = os.environ.get('MYSQL_PASSWORD')
dbName = os.environ.get('MYSQL_DATABASE')
dbConnectTimeout = 15
dbTable = ['tenants_tenants', 'core_user']

brokerProto = os.environ.get('RABBIT_PROTO')
brokerHost = os.environ.get('RABBIT_HOST')
brokerPort = os.environ.get('RABBIT_PORT')
brokerUser = os.environ.get('RABBIT_USER_NAME')
brokerPassword = os.environ.get('RABBIT_PASSWORD')
brokerVhost = os.environ.get('AMQP_VHOST')

total_result = {}
