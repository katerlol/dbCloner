import asyncio
import subprocess
import threading
import MySQLdb
import sshtunnel


def test_connection(server):
    connection_successful = True
    message = "Connection successful.\n\n"
    error = None

    try:
        results = do_queries(server, None, [
            "select schema_name from information_schema.schemata where schema_name = '" + server["db"] + "'",
            "select VERSION();",
        ])

        if len(results[0][1]) > 0:
            message += "Found existing database '" + server["db"] + "'\n\n"
        else:
            message += "database with name '" + server["db"] + "' does not exist .\n\n"
        message += "Found MySQL-version: " + results[1][1][0][0] + "\n"

    except Exception as e:
        connection_successful = False
        error = e

    return {
        "success": connection_successful,
        "error": error,
        "message": message,
    }


def start_connection(server, tunnel=None, database=None):
    if "Standard (TCP/IP)" == server["server_type"]:
        if database is None:
            return MySQLdb.connect(
                host=server["host"],
                port=server["port"],
                user=server["user"],
                password=server["passwd"])
        else:
            return MySQLdb.connect(
                host=server["host"],
                port=server["port"],
                user=server["user"],
                password=server["passwd"],
                database=server["db"])
    else:  # elif "TCP/IP over SSH" == server["server_type"]:
        if database is None:
            return MySQLdb.connect(
                host="127.0.0.1",
                database=server["db"],
                user=server["user"],
                password=server["passwd"],
                port=tunnel.local_bind_port)
        else:
            return MySQLdb.connect(
                host="127.0.0.1",
                user=server["user"],
                password=server["passwd"],
                port=tunnel.local_bind_port)


def build_tunnel(server):
    tunnel = sshtunnel.SSHTunnelForwarder((server["ssh_host"], server["ssh_port"]),
                                          ssh_username=server["ssh_user"],
                                          remote_bind_address=(server["host"], server["port"]))

    if "Password" == server["ssh_auth_method"]:
        tunnel.ssh_password = server["ssh_auth_value"]
    else:
        tunnel.ssh_pkey = server["ssh_auth_value"]
    return tunnel


def do_queries(server, database, queries):
    tunnel = None
    connection = None
    results = []
    if "Standard (TCP/IP)" == server["server_type"]:
        connection = start_connection(server, database)
    else:  # elif "TCP/IP over SSH" == server["server_type"]:
        tunnel = build_tunnel(server)
        tunnel.start()
        connection = start_connection(server, tunnel)

    cursor = connection.cursor()
    for query in queries:
        cursor.execute(query)
        m = cursor.fetchall()
        results.append([query, m])

    if connection is not None:
        connection.close()
    if tunnel is not None:
        tunnel.close()

    return results


def delete_db_if_exists(server, database):
    results = do_queries(server, database, [
        "select schema_name from information_schema.schemata where schema_name = '" + database + "'"
    ])

    if len(results[0][1]) > 0:
        print("database exists: ", results[0][1][0][0], ". deleting... ")
        do_queries(server, None, ["Drop database " + database])
    else:
        print("database does not exist")


def create_db_if_not_exists(server, database):
    results = do_queries(server, None, [
        "select schema_name from information_schema.schemata where schema_name = '" + database + "'"
    ])

    if len(results[0][1]) > 0:
        print("database exists: ", results[0][1][0][0])
    else:
        do_queries(server, None, [
            "create schema if not exists " + database
        ])
        print("database did not exist yet. created database '" + database + "'")


def db_exists(server, database):
    results = do_queries(server, None, [
        "select schema_name from information_schema.schemata where schema_name = '" + database + "'"
    ])
    return len(results[0][1]) > 0


def start_backup(server, backup_path, conf, backup_callback):
    error = None
    conf.set_defaults_file(server["passwd"])
    try:
        server_type = server["server_type"]

        if "Standard (TCP/IP)" == server_type:
            asyncio.run(_do_backup(
                host=server["host"],
                user=server["user"],
                port=str(server["port"]),
                db=server["db"],
                file_name=backup_path,
                conf=conf,
                callback=backup_callback))
        else:  # elif "TCP/IP over SSH" == server["server_type"]:
            tunnel = build_tunnel(server)
            tunnel.start()
            print("Tunnel opened to: " + str(tunnel.local_bind_port))

            asyncio.run(_do_backup(
                host="127.0.0.1",
                user=server["user"],
                port=str(tunnel.local_bind_port),
                db=server["db"],
                file_name=backup_path,
                conf=conf,
                callback=backup_callback,
                tunnel=tunnel))

    except Exception as e:
        print(e)
        error = e

    return error


def run_thread(on_exit, tunnel, args):
    proc = subprocess.Popen(args, shell=True)
    proc.wait()
    on_exit()
    if tunnel is not None:
        tunnel.close()
    return


async def _do_backup(host, user, port, db, file_name, conf, callback, tunnel=None):
    cmd = [
        'mysqldump',
        '--defaults-file=' + conf.get_defaults_file_path(),
        '--host=' + host,
        '--port=' + port,
        '--default-character-set=utf8',
        '--user=' + user,
        '--lock-tables=FALSE',
        '--no-tablespaces',
        '"' + db + '"',
        '>',
        file_name,
    ]
    thread = threading.Thread(target=run_thread, args=(callback, tunnel, ' '.join(cmd)))
    thread.start()


async def _do_restore(host, user, port, db, file_name, conf, callback, tunnel=None):
    cmd = [
        'mysql',
        '--defaults-file=' + conf.get_defaults_file_path(),
        '--host=' + host,
        '--port=' + port,
        '--default-character-set=utf8',
        '--user=' + user,
        '"' + db + '"',
        '<',
        file_name,
    ]
    thread = threading.Thread(target=run_thread, args=(callback, tunnel, ' '.join(cmd)))
    thread.start()


def start_restore(server, backup_path, conf, backup_callback):
    error = None
    conf.set_defaults_file(server["passwd"])
    try:
        server_type = server["server_type"]

        if "Standard (TCP/IP)" == server_type:
            asyncio.run(_do_restore(
                host=server["host"],
                user=server["user"],
                port=str(server["port"]),
                db=server["db"],
                file_name=backup_path,
                conf=conf,
                callback=backup_callback))
        else:  # elif "TCP/IP over SSH" == server["server_type"]:
            tunnel = build_tunnel(server)
            tunnel.start()
            print("Tunnel opened to: " + str(tunnel.local_bind_port))

            asyncio.run(_do_restore(
                host="127.0.0.1",
                user=server["user"],
                port=str(tunnel.local_bind_port),
                db=server["db"],
                file_name=backup_path,
                conf=conf,
                callback=backup_callback,
                tunnel=tunnel))

    except Exception as e:
        print(e)
        error = e

    return error
