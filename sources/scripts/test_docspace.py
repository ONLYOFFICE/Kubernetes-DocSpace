import os
import sys
import subprocess
import time
import logging

redisConnectorName = 'redis'
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

brokerType = 'rabbitmq'
brokerProto = os.environ.get('RABBIT_PROTO')
brokerHost = os.environ.get('RABBIT_HOST')
brokerPort = os.environ.get('RABBIT_PORT')
brokerUser = os.environ.get('RABBIT_USER_NAME')
brokerPassword = os.environ.get('RABBIT_PASSWORD')
brokerVhost = os.environ.get('AMQP_VHOST')

total_result = {}


def init_logger(name):
    logger = logging.getLogger(name)
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger.setLevel(logging.DEBUG)
    stdout = logging.StreamHandler()
    stdout.setFormatter(logging.Formatter(formatter))
    stdout.setLevel(logging.DEBUG)
    logger.addHandler(stdout)
    logger.info('Running a script to test the availability of DocSpace and dependencies\n')


def install_module(package):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
    except Exception as msg_install_module:
        logger_test_docspace.error(f'Error when trying to install the "{package}" package... {msg_install_module}\n')



def get_redis_status():
    install_module('redis')
    import redis
    global rc
    try:
        rc = redis.Redis(
            host=redisHost,
            port=redisPort,
            db=redisDBNum,
            password=redisPassword,
            username=redisUser,
            socket_connect_timeout=redisConnectTimeout,
            retry_on_timeout=True
        )
        rc.ping()
    except Exception as msg_redis:
        logger_test_docspace.error(f'Failed to check the availability of the Redis... {msg_redis}\n')
        total_result['CheckRedis'] = 'Failed'
    else:
        logger_test_docspace.info('Successful connection to Redis')
        return rc.ping()


def check_redis_key():
    try:
        rc.set('testDocSpace', 'ok')
        test_key = rc.get('testDocSpace').decode('utf-8')
        logger_test_docspace.info(f'Test Key: {test_key}')
    except Exception as msg_check_redis:
        logger_test_docspace.error(f'Error when trying to write a key to Redis... {msg_check_redis}\n')
        total_result['CheckRedis'] = 'Failed'
    else:
        rc.delete('testDocSpace')
        logger_test_docspace.info('The test key was successfully recorded and deleted from Redis\n')
        rc.close()
        total_result['CheckRedis'] = 'Success'


def check_redis():
    logger_test_docspace.info('Checking Redis availability...')
    if redisConnectorName == 'redis':
        if get_redis_status() is True:
            check_redis_key()


def check_db_mysql(tbl_dict):
    install_module('pymysql')
    import pymysql
    try:
        dbc = pymysql.connect(
            host=dbHost,
            port=dbPort,
            database=dbName,
            password=dbPassword,
            user=dbUser,
            connect_timeout=dbConnectTimeout
        )
        logger_test_docspace.info(f'Successful connection to the "{dbName}" database')
        for tbl in dbTable:
            with dbc.cursor() as cursor:
                cursor.execute(f"SELECT EXISTS (SELECT * FROM information_schema.tables WHERE TABLE_NAME='{tbl}' AND TABLE_SCHEMA='{dbName}');")
                table_exists = cursor.fetchone()[0]
                if table_exists == 1:
                    logger_test_docspace.info(f'The table "{tbl}" exists in the "{dbName}" database')
                    tbl_dict[tbl] = 'Exists'
                else:
                    logger_test_docspace.error(f'The table "{tbl}" does not exists in the "{dbName}" database')
                    tbl_dict[tbl] = 'NotExists'
    except Exception as msg_check_dblist:
        logger_test_docspace.error(f'Error when trying to get a list of DocSpace tables in the "{dbName}" database... {msg_check_dblist}\n')
        total_result['CheckMySQL'] = 'Failed'
    else:
        dbc.close()
        logger_test_docspace.info(f'Check of DocSpace tables in "{dbName}" database has been finished\n')
        if 'NotExists' in tbl_dict.values():
            total_result['CheckMySQL'] = 'Failed'
        else:
            total_result['CheckMySQL'] = 'Success'


def check_db():
    logger_test_docspace.info('Checking database availability...')
    tbl_result = {}
    if dbType == 'mysql' or dbType == 'mariadb':
        check_db_mysql(tbl_result)


def check_mq_rabbitmq():
    install_module('pika')
    import pika
    try:
        mqp = pika.URLParameters(f'{brokerProto}://{brokerUser}:{brokerPassword}@{brokerHost}:{brokerPort}{brokerVhost}')
        mqc = pika.BlockingConnection(mqp)
        mq_connect_status = mqc.is_open
        logger_test_docspace.info('Successful connection to RabbitMQ')
    except Exception as msg_check_rabbitmq:
        logger_test_docspace.error(f'Failed to check the availability of the RabbitMQ... {msg_check_rabbitmq}\n')
        total_result['CheckRabbitMQ'] = 'Failed'
    else:
        if mq_connect_status is True:
            try:
                mqchannel = mqc.channel()
                mqchannel.queue_declare(queue='testDocSpace')
            except Exception as msg_check_rabbitmq_queue:
                logger_test_docspace.error(f'Error when trying to create a test queue in RabbitMQ... {msg_check_rabbitmq_queue}\n')
                total_result['CheckRabbitMQ'] = 'Failed'
            else:
                mqchannel.queue_delete(queue='testDocSpace')
                logger_test_docspace.info('The test queue was successfully created and deleted in RabbitMQ\n')
                mqc.close()
                total_result['CheckRabbitMQ'] = 'Success'
        else:
            logger_test_docspace.error('Error when trying to create a test queue in RabbitMQ\n')


def check_mq():
    logger_test_docspace.info('Checking Broker availability...')
    if brokerType == 'rabbitmq':
        check_mq_rabbitmq()

def total_status():
    logger_test_docspace.info('As a result of the check, the following results were obtained:')
    for key, value in total_result.items():
        logger_test_docspace.info(f'{key} = {value}')


init_logger('test')
logger_test_docspace = logging.getLogger('test.docspace')
check_redis()
check_db()
check_mq()
total_status()
