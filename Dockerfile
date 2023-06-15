#FROM ubuntu:latest AS ubuntu-builder
#ENV DEBIAN_FRONTEND noninteractive
#
#RUN apt-get update -y && \
#    apt-get install python3-opencv libopencv-dev -y

# Stage 2: Amazon Linux 2 for the final Lambda image
FROM public.ecr.aws/lambda/python:3.8

# install prerequisites
RUN yum update -y && yum install -y wget tar binutils make
RUN yum install -y cmake3 && ln -s /usr/bin/cmake3 /usr/bin/cmake
RUN yum install -y ninja-build && ln -s /usr/bin/ninja-build /usr/bin/ninja
RUN yum install -y gcc10 gcc10-c++ && ln -s /usr/bin/gcc10-gcc /usr/bin/gcc && ln -s /usr/bin/gcc10-c++ /usr/bin/g++

# building from sources, see https://docs.opencv.org/3.4/dd/dd5/tutorial_py_setup_in_fedora.html
RUN yum install -y python-devel numpy gtk2-devel libdc1394-devel libv4l-devel ffmpeg-devel gstreamer-plugins-base-devel && \
    yum install -y libpng-devel libjpeg-turbo-devel jasper-devel openexr-devel libtiff-devel libwebp-devel eigen3-devel

WORKDIR /usr/src/

ARG OPENCV_VERSION=4.5.1
ARG OPENCV_RELEASE=opencv-$OPENCV_VERSION
RUN wget -O $OPENCV_RELEASE.tar.gz https://github.com/opencv/opencv/archive/refs/tags/$OPENCV_VERSION.tar.gz && \
    tar xzf $OPENCV_RELEASE.tar.gz

WORKDIR /usr/src/$OPENCV_RELEASE
RUN mkdir build
WORKDIR /usr/src/$OPENCV_RELEASE/build

RUN cmake -D PYTHON_DEFAULT_EXECUTABLE=$(which python) \
    -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local/opencv \
    -D WITH_TBB=ON -D WITH_EIGEN=ON BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF \
    -D WITH_OPENCL=OFF -D BUILD_opencv_gpu=OFF -D BUILD_opencv_gpuarithm=OFF -D BUILD_opencv_gpubgsegm=OFF \
    -D BUILD_opencv_gpucodec=OFF -D BUILD_opencv_gpufeatures2d=OFF -D BUILD_opencv_gpufilters=OFF \
    -D BUILD_opencv_gpuimgproc=OFF -D BUILD_opencv_gpulegacy=OFF -D BUILD_opencv_gpuoptflow=OFF \
    -D BUILD_opencv_gpustereo=OFF -D BUILD_opencv_gpuwarping=OFF ..

# build with just a single process using make; building in parallel either make -jN or ninja fails with
# "g++: fatal error: Killed signal terminated program cc1plus" — according to the internet, due to not enough RAM
RUN make
RUN make install


#COPY --from=ubuntu-builder /usr/include/opencv4/* /usr/include/opencv/
#COPY --from=ubuntu-builder /usr/include/opencv4/imgcodecs.hpp /usr/include/opencv/
##COPY --from=ubuntu-builder /usr/share/opencv4/* /usr/share/opencv/
#COPY --from=ubuntu-builder /usr/lib/x86_64-linux-gnu/* /usr/lib/x86_64-linux-gnu/

COPY requirements.txt  .
COPY app.py .
COPY Makefile .
COPY patch_match.py .
COPY csrc csrc
##COPY build build
COPY travis.sh .
##COPY libpatchmatch.so .
#
##RUN yum update -y
##RUN yum install make -y
##RUN yum install gcc-c++ -y
##RUN yum install pkgconfig -y
RUN make
# RUN pip3 install -r requirements.txt
#
ENTRYPOINT ["python"]
CMD ["app.py"]
#
#CMD ["app.handler"]
