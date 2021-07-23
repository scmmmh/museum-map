FROM python:3.9

ARG MM_USER="museum-map"
ARG MM_UID="10000"
ARG MM_GID="10000"

# Create the user
RUN groupadd --gid $MM_GID $MM_USER && \
    useradd --gid $MM_GID --no-log-init --shell /bin/bash --uid $MM_UID $MM_USER

# Install base dependencies
RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y tini

# Copy the application and configuration file
COPY museum_map-0.1.0-py3-none-any.whl /tmp/
COPY production.ini /etc/museum-map/production.ini

# Install the application
RUN python -m pip install /tmp/museum_map-0.2.2-py3-none-any.whl[postgres]
COPY start_museum_map.sh /usr/bin/
RUN chmod a+x /usr/bin/start_museum_map.sh && \
    mkdir /var/lib/museum-map && \
    chmod 0755 /var/lib/museum-map && \
    chown -R ${MM_USER}:${MM_USER} /etc/museum-map && \
    chown -R ${MM_USER}:${MM_USER} /var/lib/museum-map

# Setup the running environment
USER ${MM_UID}:${MM_GID}
VOLUME [ "/var/lib/museum-map" ]
ENV LC_ALL=C
WORKDIR /var/lib/museum-map
EXPOSE 8080
ENTRYPOINT [ "tini", "--" ]
CMD [ "/usr/bin/start_museum_map.sh" ]
