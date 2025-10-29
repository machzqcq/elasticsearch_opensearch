# Stage 1: Download backup files using a minimal image with curl
FROM alpine:latest AS downloader

RUN apk add --no-cache curl && \
    curl -L -o /tmp/AdventureWorks2019.bak \
    https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2019.bak && \
    curl -L -o /tmp/AdventureWorksDW2019.bak \
    https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorksDW2019.bak

# Stage 2: SQL Server with AdventureWorks databases
FROM rapidfort/microsoft-sql-server-2019-ib:latest

# Switch to root to fix permissions
USER root

ENV SA_PASSWORD=Welcome@123
ENV ACCEPT_EULA=Y

# Create directories and set permissions
RUN mkdir -p /var/opt/mssql/data && \
    chmod -R 777 /var/opt/mssql

# Copy downloaded backup files from downloader stage
COPY --from=downloader /tmp/AdventureWorks2019.bak /var/opt/mssql/data/
COPY --from=downloader /tmp/AdventureWorksDW2019.bak /var/opt/mssql/data/

# Fix ownership of copied files
RUN chmod -R 777 /var/opt/mssql/data/

RUN /opt/mssql/bin/sqlservr --accept-eula & sleep 30 \
    && /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Welcome@123' -Q 'RESTORE DATABASE AdventureWorksDW2019 FROM DISK = "/var/opt/mssql/data/AdventureWorksDW2019.bak" WITH MOVE "AdventureWorksDW2019" TO "/var/opt/mssql/data/AdventureWorksDW2019.mdf", MOVE "AdventureWorksDW2019_log" TO "/var/opt/mssql/data/AdventureWorksDW2019_log.ldf"' \
    && /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Welcome@123' -Q 'RESTORE DATABASE AdventureWorks2019 FROM DISK = "/var/opt/mssql/data/AdventureWorks2019.bak" WITH MOVE "AdventureWorks2019" TO "/var/opt/mssql/data/AdventureWorks2019.mdf", MOVE "AdventureWorks2019_log" TO "/var/opt/mssql/data/AdventureWorks2019_log.ldf"'