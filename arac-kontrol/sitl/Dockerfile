# ArduSub SITL (ArduPilot yazılım-içi simülasyon)
# Derleme:  docker build -t ardusub-sitl sitl
# Çalıştırma: docker run --rm -it -p 5760:5760 --name ardusub ardusub-sitl
FROM ubuntu:22.04

ARG ARDUPILOT_REF=Sub-4.7.3
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates build-essential g++ make pkg-config \
        python3 python3-pip python3-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
        empy==3.3.4 future pexpect lxml pymavlink dronecan setuptools

WORKDIR /ardupilot
RUN git clone --depth 1 --branch ${ARDUPILOT_REF} https://github.com/ArduPilot/ardupilot.git . \
    && git submodule update --init --recursive --depth 1

RUN ./waf configure --board sitl && ./waf sub

# Varsayılan sub parametreleri + vectored (BlueROV2 benzeri) gövde modeli.
# SERIAL0 → TCP 5760 (MAVProxy buraya bağlanır).
EXPOSE 5760
CMD ["build/sitl/bin/ardusub", "--model", "vectored", "-I0", \
     "--defaults", "Tools/autotest/default_params/sub.parm", \
     "--home", "33.810313,-118.393867,0,185"]
